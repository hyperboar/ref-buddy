from typing import Annotated

from pydantic import BaseModel, AfterValidator, Field
from quart import Blueprint, jsonify, render_template, request

from app.common.dto_basic import EmptyResponse
from app.models import Session
from app.models.models_lump import Tag

routes_crud_tag = Blueprint('routes_crud_tag', __name__, url_prefix='/tags')

class TagDto(BaseModel):
    id:int|None = None
    name:Annotated[str, AfterValidator(lambda v: v.strip())]
    color_id:int
    color_hex:str|None = Field(alias='hex', default=None)


@routes_crud_tag.route('', methods=['GET'])
async def get_html():
    return await render_template('crud/tpl_tags_list.html')

@routes_crud_tag.route('get/all', methods=['GET'])
async def get_all_items():
    with Session() as session:
        tags = session.query(Tag).all()
        out = {'colors': {}, 'tags': []}
        for tag in tags:
            out['tags'].append({'id': tag.id, 'name': tag.tag, 'c': tag.color_id})
            out['colors'][tag.color_id] = tag.color.hex
        return jsonify(out)

@routes_crud_tag.route('get/<int:item_id>', methods=['GET'])
async def get_item(item_id):
    with Session() as session:
        tag = session.get(Tag, item_id)
        return jsonify(tag)

@routes_crud_tag.route('/add', methods=['POST'])
async def add_tag():
    d = await request.json
    print(d)
    data = TagDto.model_validate(d)
    with Session() as session:
        new_tag = Tag(tag=data.name, color_id=data.color_id)
        session.add(new_tag)
        session.commit()
        return jsonify({'id': new_tag.id})

@routes_crud_tag.route('/update', methods=['POST'])
async def update_item():
    d = await request.json
    data = TagDto.model_validate(d)
    with Session() as session:
        tag = session.get(Tag, data.id)
        tag.tag = data.name
        tag.color_id = data.color_id
        session.commit()
        return jsonify(EmptyResponse())

@routes_crud_tag.route('/delete/<int:tag_id>', methods=['GET'])
async def delete_tag(tag_id):
    with Session() as session:
        tag = session.get(Tag, tag_id)
        session.delete(tag)
        session.commit()
        return jsonify(EmptyResponse())
