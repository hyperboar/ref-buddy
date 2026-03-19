import os

from app.models import Session
from app.models.models_lump import Color, Tag, Category, TagSet, Base
from shared_utils.env import Env


class DatabaseUtil:
    @staticmethod
    def create_if_not_exist(engine):
        if not (os.path.exists(Env.DB_FILE)):
            os.makedirs(os.path.split(Env.DB_FILE)[0], exist_ok=True)
            Base.metadata.create_all(engine)
            DatabaseUtil.add_predefined_data(Session)

    @staticmethod
    def drop_and_create(engine):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        DatabaseUtil.add_predefined_data(Session)

    @staticmethod
    def add_predefined_data(session_maker):

        session = session_maker()

        # COLORS
        color = Color(color_name='default')
        session.add(color)

        session.commit()

        # TAGS
        tag_tagme = Tag(id=1, tag='tagme', color_id=color.id)
        tag_anim = Tag(tag='animated', color_id=color.id)
        tag_vid = Tag(tag='video', color_id=color.id)
        session.add(tag_tagme)
        session.add(tag_anim)
        session.add(tag_vid)

        session.commit()

        # CATEGORIES
        category_1 = Category(category="everything")
        session.add(category_1)

        session.commit()

        if not os.path.exists(os.path.join(Env.IMAGES_PATH, "everything")):
            os.makedirs(os.path.join(Env.IMAGES_PATH, "everything"))

        # TAG SET
        tag_set = TagSet(set_name='All Images', set_alias='all')
        session.add(tag_set)

        session.commit()
        session.close()