import logging
import os.path
from datetime import datetime

import torch
from PIL import Image
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, CollectionStatus
from transformers import AutoProcessor, AutoModel


import warnings
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    message=".*Local mode is not recommended for collections with more than 20,000 points..*"
)

logging.getLogger("transformers").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

EMPTY_EMBEDS_THRESHOLD = 10

COLLECTIONS = {
    'ai': {
        'tags': '-animated,ai',
        'collection_name': 'hoarded_images2'
    },
    'academic': {
        'tags': '-animated,academic',
        'collection_name': 'academic'
    },
    'porn_set': {
        'tags': '-animated,-academic,-ai,-frames,-manga,set',
        'collection_name': 'pron_set'
    },
    'porn': {
        'tags': '-animated,-academic,-ai,-set,-frames',
        'collection_name': 'pron_and_2d'
    },
    'manga': {
        'tags': '-animated,manga',
        'collection_name': 'manga'
    }
}


printer = print

class Loadout:
    MODEL_NAME = "./venv/models/siglip2-base-patch16-224"

    PROCESSOR = None
    MODEL = None
    DEVICE: str = ''
    QCLIENT: QdrantClient = None

    @classmethod
    def load(cls):

        logger.info('Loadout... Begin')

        if cls.DEVICE == '':
            cls.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loadout. Using device: {cls.DEVICE}")

        if cls.PROCESSOR is None:
            cls.PROCESSOR = AutoProcessor.from_pretrained(cls.MODEL_NAME, local_files_only=True)

        if cls.MODEL is None:
            cls.MODEL = AutoModel.from_pretrained(cls.MODEL_NAME, local_files_only=True).to(cls.DEVICE).eval()
        if cls.QCLIENT is None:
            from shared_utils.env import Env
            if not Env.IS_LOADED_ONCE:
                from shared_utils.env import ENV_USER
                Env.apply_config(ENV_USER)
            cls.QCLIENT = QdrantClient(path=Env.DB_EMBED_FILE)

        logger.info('Loadout... Done')

def process_my_database(ignored_collections:[str]=None, force_full_scan=False):

    from shared_utils.env import Env
    if not Env.IS_LOADED_ONCE:
        from shared_utils.env import ENV_USER
        Env.apply_config(ENV_USER)

    from app.models import DatabaseEnvironment, Session
    from app.common.folder_dtos import FilterRequestDto
    from app.services.image_metadata_controller import ImageMetadataController
    from app.models.models_lump import ImageMetadata

    from PIL import ImageFile
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    Loadout.load()

    client = Loadout.QCLIENT

    DatabaseEnvironment.update_db_connection()
    with Session() as session:
        for cname, coll_data in COLLECTIONS.items():
            printer('Processing collection ' + cname)

            if ignored_collections is not None and cname in ignored_collections:
                printer('Skipping collection ' + cname)
                continue

            collection_name = coll_data['collection_name']

            init_collection(client, collection_name)

            data = {'tags': coll_data['tags']}
            filter_dto = FilterRequestDto.model_validate(data)

            max_count = ImageMetadataController.get_query_images_new4(filter_dto, session=session).count()
            offset = 0
            step = 100
            time_diff:float = 0
            empty_embeds_count = 0
            while True:
                q = ImageMetadataController.get_query_images_new4(filter_dto, session=session)
                q = q.order_by(ImageMetadata.imported_at.desc()).offset(offset).limit(step)
                imgs = q.all()
                if len(imgs) == 0:
                    break
                if not force_full_scan and empty_embeds_count > EMPTY_EMBEDS_THRESHOLD:
                    break

                time_end_estimate = int((max_count - offset - step)/step * time_diff / 60)
                printer(f'\r(~{time_end_estimate}m left. {time_diff:.2f}s {empty_embeds_count}) Batch {offset}-{offset+step} of {max_count}...')

                offset += step
                images = {im.image_id: im.path_abs for im in imgs}

                start_time = datetime.now().timestamp()
                count = generate_embeds(images, client, collection_name)
                empty_embeds_count += 0 if count > 0 else 1
                time_diff = datetime.now().timestamp() - start_time

    printer('Done generating embeds!')


def init_collection(client, collection_name):
    if client.collection_exists(collection_name): return

    dummy = Image.new("RGB", (224, 224))
    with torch.no_grad():
        vector = encode_image(dummy)[0].tolist()

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=len(vector),
                distance=Distance.COSINE
            ),
        )

def generate_embeds(images:dict, client:QdrantClient, collection_name:str) -> int:
    '''
    :param images: { id: img.path_abs}
    '''
    existing_points = client.retrieve(
        collection_name=collection_name,
        ids=images.keys()
    )

    if len(existing_points):
        # printer(f'Already processed {[p.id for p in existing_points]}')
        [images.pop(p.id, None) for p in existing_points]

    if len(images.keys()) == 0: return 0

    points = []
    ids = list(images.keys())
    paths:[str] = list(images.values())
    printer(f'\rGenerating embeds...', end='')


    vectors = encode_images_by_paths(paths)
    if vectors is None or len(vectors) == 0: return 0

    for i in range(len(ids)):
        points.append(PointStruct(
            id=ids[i],
            vector=vectors[i].tolist()
        ))

    client.upsert(
        collection_name=collection_name,
        points=points
    )

    return len(points)

@torch.no_grad()
def encode_image(path:str):
    if not os.path.exists(path):
        printer(f'Image does not exist at path: {path}')
        return None
    try:
        image = Image.open(path).convert('RGB')
    except Exception as e:
        printer(f'Error during PIL at path: {path}. Msg: {e}')
        return None

    return encode_images([image])

@torch.no_grad()
def encode_image(image:Image.Image):
    return encode_images([image])

@torch.no_grad()
def encode_images_by_paths(paths:[str]):
    images = []
    for p in paths:
        if not os.path.exists(p):
            printer(f'Image does not exist at path: {p}')
            continue
        try:
            image = Image.open(p).convert('RGB')
        except Exception as e:
            printer(f'Error during PIL at path: {p}. Msg: {e}')
            continue
        images.append(image)

    return encode_images(images)

@torch.no_grad()
def encode_images(images:[Image.Image]):
    inputs = Loadout.PROCESSOR(images=images, return_tensors="pt", padding="max_length", max_length=64).to(Loadout.DEVICE)
    features = Loadout.MODEL.get_image_features(**inputs).pooler_output
    features = features / features.norm(p=2, dim=-1, keepdim=True)
    return features.cpu()


@torch.no_grad()
def encode_text(text: str) -> list[float]:
    inputs = Loadout.PROCESSOR(text=[text], return_tensors="pt", padding="max_length", max_length=64).to(Loadout.DEVICE)
    features = Loadout.MODEL.get_text_features(**inputs).pooler_output
    features = features / features.norm(p=2, dim=-1, keepdim=True)
    return features[0].cpu().tolist()

class SearchByPrompt:
    def __init__(self, prompt:str, limit:int, image_id=None, c1:float=None, c2:float=None):

        logger.info('Search by prompt... init')

        Loadout.load()

        self.is_ok:bool = True

        self.limit:int = limit
        self.offset:int = 0

        self.cname:str = ''
        self.cname_images:[str] = ''
        self.prompt:str = ''
        self.prompt_images:[int] = None
        self.search_vector:[float] = None
        self.c1 = c1
        self.c2 = c2

        self.image_id = image_id # self.prompt_images

        self._client:QdrantClient = Loadout.QCLIENT

        coll_idx = prompt.find(' ')
        self.cname = prompt[:coll_idx]
        self.prompt = prompt[coll_idx + 1:]

        if self.cname is None or self.cname == '' or self.cname not in COLLECTIONS:
            logger.error(f'Collection with name "{self.cname}" not found')
            self.is_ok = False

        self.cname = COLLECTIONS[self.cname]['collection_name']

        self.search_vector = self._evaluate_vector()

    def _evaluate_vector(self) -> [float]:
        logger.info('Searching by prompt... Encoding text ')

        vector = encode_text(self.prompt)

        images_vector = self._evaluate_images_vector()
        if images_vector is not None:
            self._evaluate_text_to_image_prompt_weights()
            import numpy as np
            v1 = np.array(vector, dtype=np.float32)
            v2 = np.array(images_vector, dtype=np.float32)
            vector = (self.c1 * v1 + self.c2 * v2).tolist()
            logger.info(f'Using image vector with text-{self.c1} image-{self.c2}) ')

        return vector

    def _evaluate_images_vector(self) -> [float]:
        if self.image_id is None:
            return None

        pair = self.image_id.split('-')

        cname_image_id = COLLECTIONS[pair[0]]['collection_name']

        result = self._client.retrieve(collection_name=cname_image_id, ids=[int(pair[1])], with_vectors=True)
        if len(result) == 0:
            logger.error(f'Prompt id image not found for "{self.image_id}" ')
            return None

        return result[0].vector

    def _evaluate_text_to_image_prompt_weights(self):
        if self.c1 is None or self.c1 < 0.001 or self.c2 is None or self.c2 < 0.001:
            logger.warning(f'Weights are not correct ({self.c1};{self.c2}) ')
            self.c1 = 0.5
            self.c2 = 0.5
        s = self.c1 + self.c2
        self.c1 = self.c1 / s
        self.c2 = self.c2 / s

    def next_batch(self) -> dict[int, float]:
        logger.info('Search by prompt... Requesting next batch, offset:%s, limit:%d', self.offset, self.limit)
        if not self.is_ok:
            return {}

        hits = self._client.query_points(
            collection_name=self.cname,
            query=self.search_vector,
            limit=self.limit,
            offset=self.offset
        )

        self.offset += self.limit

        return {s.id: s.score for s in hits.points}


if __name__ == "__main__":
    printer(f'Starting main at {__file__} ...')
    # # inference
    # from shared_utils.env import Env
    # from shared_utils.env import ENV_USER
    # Env.apply_config(ENV_USER)
    # qclient = QdrantClient(path=Env.DB_EMBED_FILE)
    #
    # coll_name = COLLECTIONS['ai']['collection_name']
    # coll = qclient.get_collection(coll_name)
    # result = search_by_embed('goblin', 10, client, COLLECTION_NAME)
    #
    # for r in result:
    #     printer(r)
    #     printer(f'http://localhost:7071/study-image/{r[0]}')

    process_my_database()
    # process_my_database(ignored_collections=['ai','porn','academic'], force_full_scan=True)
    pass