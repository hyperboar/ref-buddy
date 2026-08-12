from quart import Blueprint, jsonify, render_template

from app.common.dto_basic import EmptyResponse


routes_crud_path = Blueprint('routes_crud_path', __name__, url_prefix='/path')


# @routes_crud_path.route('/path/html', method=['GET'])
# async def get_html():
#     return await render_template('crud/tpl_path.html')
#
# @routes_crud_path.route('/path/get/<int:item_id>', method=['GET'])
# async def get_item(item_id):
#     jsonify(EmptyResponse())
#
# @routes_crud_path.route('/path/update', method=['POST'])
# async def update_item():
#     jsonify(EmptyResponse())
#
# @routes_crud_path.route('/path/delete', method=['POST'])
# async def delete_item():
#     jsonify(EmptyResponse())