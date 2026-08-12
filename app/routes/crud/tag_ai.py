from quart import Blueprint, jsonify, render_template

from app.common.dto_basic import EmptyResponse

routes_crud_tag_ai = Blueprint('routes_crud_tag_ai', __name__)


@routes_crud_tag_ai.route('/tag_ai', method=['GET'])
async def get_html():
    return await render_template('crud/tpl_tag_ai.html')

@routes_crud_tag_ai.route('/tag_ai/get/<int:item_id>', method=['GET'])
async def get_item(item_id):
    jsonify(EmptyResponse())

@routes_crud_tag_ai.route('/tag_ai/update', method=['POST'])
async def update_item():
    jsonify(EmptyResponse())

@routes_crud_tag_ai.route('/tag_ai/delete', method=['POST'])
async def delete_item():
    jsonify(EmptyResponse())