from quart import Quart, jsonify

from app.common.exceptions import ImageNotFoundError, TagNotFoundError, ImageFileNotFoundError, ThumbNotFoundError, \
    AnimationDataNotFoundError


def register_error_handlers(app:Quart):
    app.register_error_handler(ImageNotFoundError, smth_not_found_handler)
    app.register_error_handler(TagNotFoundError, smth_not_found_handler)
    app.register_error_handler(ImageFileNotFoundError, smth_not_found_handler)
    app.register_error_handler(ThumbNotFoundError, smth_not_found_handler)
    app.register_error_handler(AnimationDataNotFoundError, smth_not_found_handler)

def smth_not_found_handler(error):
    return jsonify(error), 404
