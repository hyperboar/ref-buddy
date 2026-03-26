import json
import os
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, model_validator
from sqlalchemy import exists, inspect

from app.models.models_lump import TagAi, ImageTagAi
from shared_utils.env import Env

EXPORTED_URLS_FILENAME = 'exported_urls.json'
AI_TAGS_DIRNAME = 'output_' + EXPORTED_URLS_FILENAME


class ImportedAiImageTags(BaseModel):
    tag_local_id:str
    rating:int

class ImportedAiImage(BaseModel):
    id:int
    timestamp:Annotated[int, BeforeValidator(lambda x: int(x))]
    tags:list[ImportedAiImageTags]

    @model_validator(mode='before')
    @classmethod
    def convert_tags(cls, values):
        values['tags'] = list(map(lambda key: {'tag_local_id': int(key), 'rating':values['tags'][key]}, values['tags']))
        return values

class ImportedAiFile(BaseModel):
    tags:list[str]
    images:list[ImportedAiImage]


def suck_folder_in(session):
    path = os.path.join(Env.TMP_PATH, AI_TAGS_DIRNAME)

    files = os.listdir(path)
    files_count = 0
    max = len(files)

    for file in files:
        print(f"({files_count}/{max}) Checking file {os.path.join(path, file)}...", flush=True)
        with open(os.path.join(path, file), 'r') as f:
            files_count += 1

            data_dict = json.load(f)

            data = ImportedAiFile.model_validate(data_dict)

            # import new tags
            new_tags = []
            for tag in data.tags:
                query = session.query(exists().where(TagAi.tag == tag))
                has_tag = session.scalar(query)
                if has_tag: continue
                new_tags.append(TagAi(tag=tag))

            if len(new_tags) > 0:
                session.add_all(new_tags)
                session.commit()

            # build mapping for internal tag id to db tag id
            tags_to_db = {}
            for i in range(len(data.tags)):
                tag_id = session.query(TagAi.id).filter(TagAi.tag == data.tags[i]).one()[0]
                tags_to_db[str(i)] = tag_id

            # import image-tag + rating
            count_new = 0
            for img in data.images:
                for t in img.tags:
                    result = session.merge(ImageTagAi(image_id=img.id, tag_id=tags_to_db[t.tag_local_id], rating=t.rating, imported_at=img.timestamp))
                    if inspect(result).pending:
                        count_new += 1
            if count_new > 0:
                session.commit()