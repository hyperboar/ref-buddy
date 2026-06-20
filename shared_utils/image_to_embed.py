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
        if cls.DEVICE == '':
            cls.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

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

            if cname in ignored_collections:
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
                printer(f'\r(~{time_end_estimate}m left. {time_diff:.2f}s) Batch {offset}-{offset+step} of {max_count}...')

                offset += step
                images = {im.image_id: im.path_abs for im in imgs}

                start_time = datetime.now().timestamp()
                count = generate_embeds(images, client, collection_name)
                empty_embeds_count += 1 if count > 0 else 0
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

def search_by_text(prompt:str, limit:int) -> [(int, float)]:
    printer('Searching by text...', end='')
    coll_idx = prompt.find(' ')
    cname = prompt[:coll_idx]
    prompt = prompt[coll_idx+1:]

    printer('\Searching by text... Loadout init ', end='')
    Loadout.load()
    client = Loadout.QCLIENT

    if cname is None or cname == '' or cname not in COLLECTIONS:
        printer(f'Collection with name "{cname}" not found')
        return []

    cname = COLLECTIONS[cname]['collection_name']

    printer('\Searching by text... Checking collection ', end='')
    coll = client.get_collection(cname)
    if coll is None or (coll.status != CollectionStatus.GREEN and coll.status != CollectionStatus.GREY):
        printer(f'Collection "{cname}" is busy')
        return []
    printer('\Searching by text... Encoding text ', end='')
    vector = encode_text(prompt)
    hits = client.query_points(
        collection_name=cname,
        query=vector,
        limit=limit
    )
    printer(f'\Searching by text... Done. Found {len(hits.points)} ')
    if len(hits.points) == 0:
        return []

    return [(s.id, s.score) for s in hits.points]

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

    # process_my_database(ignored_collections=['ai','porn_set', 'academic'], force_full_scan=True)
    process_my_database(ignored_collections=['ai','porn','academic'], force_full_scan=True)
    pass