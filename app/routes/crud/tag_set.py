from quart import Blueprint, jsonify, render_template

from app.common.dto_basic import EmptyResponse

routes_crud_tag_set = Blueprint('routes_crud_tag_set', __name__)


@routes_crud_tag_set.route('/tag-set', method=['GET'])
async def get_html():
    return await render_template('crud/tpl_tag_set.html')

@routes_crud_tag_set.route('/tag-set/get/<int:item_id>', method=['GET'])
async def get_item(item_id):
    jsonify(EmptyResponse())

@routes_crud_tag_set.route('/tag-set/update', method=['POST'])
async def update_item():
    jsonify(EmptyResponse())

@routes_crud_tag_set.route('/tag-set/delete', method=['POST'])
async def delete_item():
    jsonify(EmptyResponse())