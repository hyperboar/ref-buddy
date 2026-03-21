from quart import Quart, jsonify

from app.common.exceptions import EntityNotFoundError, FileEntityNotFoundError


def register_error_handlers(app:Quart):
    app.register_error_handler(EntityNotFoundError, smth_not_found_handler)
    app.register_error_handler(FileEntityNotFoundError, smth_not_found_handler)

def smth_not_found_handler(error):
    return jsonify(error), 404
