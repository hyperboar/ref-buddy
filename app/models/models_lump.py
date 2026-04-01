import os
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, Text, ForeignKey, TypeDecorator, Float
from sqlalchemy.orm import relationship, object_session, declarative_base

from PIL import Image

from shared_utils.env import Env

# Create a base class for declarative models
Base = declarative_base()

class UnixTimestamp(TypeDecorator):
    impl = Integer
    cache_ok = True

    def process_bind_param(self, value, dialect) -> int:
        if type(value) == datetime:
            if value == datetime.min: return 0
            return int(value.timestamp())
        elif type(value) == str:
            return int(datetime.strptime(value, '%Y-%m-%d %H:%M:%S').timestamp())
        elif type(value) == int:
            return value
        return 0

    def process_result_value(self, value, dialect) -> datetime:
        return datetime.fromtimestamp(value, tz=timezone.utc) if value is not None else None

    @staticmethod
    def default() -> datetime:
        return datetime.fromtimestamp(0, tz=timezone.utc)

class Path(Base):
    """
    Paths are serialized with forward (/) slashes as separators.
    """
    __tablename__ = 'paths'

    id = Column(Integer, primary_key=True)
    path_raw = Column(Text, nullable=False, name='path', unique=True)
    preview = Column(Integer, nullable=False, default=0)
    hidden = Column(Integer, nullable=False, default=0)
    ord = Column(Integer, nullable=False, default=0)
    last_updated = Column(UnixTimestamp, nullable=False, default=UnixTimestamp.default())

    @property
    def tags_plain(self) -> [str]:
        return [t.tag.tag for t in self.tags]

    @property
    def path(self) -> str:
        """Returns OS specific path."""
        return os.path.normpath(self.path_raw)

    @path.setter
    def path(self, value:str):
        """Sets value of path_raw. Accepts path as an argument and replaces separators by forward (/) slashes."""
        self.path_raw = Path.path_serialize(value)

    @staticmethod
    def path_serialize(value:str) -> str:
        return value.replace(os.sep, '/')

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    category = Column(Text, nullable=False, unique=True)


class ImageMetadata(Base):
    __tablename__ = 'images'

    image_id = Column(Integer, name='id', primary_key=True)
    filename = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), name='category', nullable=False)
    source_type_id = Column(Integer, name='source_type', default=0, nullable=False)
    path_id = Column(Integer, ForeignKey('paths.id'), name='path', nullable=False)
    fav = Column(Integer, default=0)
    count = Column(Integer, default=0)
    rating = Column(Integer, default=0)
    lost = Column(Integer, default=0)
    removed = Column(Integer, default=0, nullable=False)
    last_viewed = Column(UnixTimestamp, nullable=False, default=UnixTimestamp.default())
    imported_at = Column(UnixTimestamp, nullable=False, default=datetime.now(tz=timezone.utc))

    category_ref = relationship('Category')
    path_ref = relationship('Path', backref='images')

    @property
    def is_fav(self):
        return self.fav

    @property
    def is_animated(self):
        return self.source_type_id == 2 or self.source_type_id == 3

    @property
    def is_video(self):
        return self.source_type_id == 3

    def is_removed(self):
        return self.removed

    @property
    def category(self):
        return self.category_ref.category

    @property
    def path(self):
        return Path.path_serialize(os.path.join(self.path_ref.path, self.filename))

    @property
    def path_abs(self):
        return os.path.join(Env.IMAGES_PATH, self.path)

    def mark_as_lost(self, session=None, auto_commit=True):
        self.lost = 1
        if session is None:
            session = object_session(self)
            session.commit()
            return

        if auto_commit:
            session.commit()
            return

        session.flush()

    def mark_removed(self, session=None, auto_commit=True):
        self.removed = 1
        if session is None:
            session = object_session(self)
            session.commit()
            return

        if auto_commit:
            session.commit()
            return

        session.flush()

    def mark_restored(self, session=None, auto_commit=True):
        self.removed = 0
        if session is None:
            session = object_session(self)
            session.commit()
            return

        if auto_commit:
            session.commit()
            return

        session.flush()

    @staticmethod
    def source_type_by_path(path:str) -> int:
        """
        0 - not set, need update
        1 - static image
        2 - animation
        3 - video
        """
        if path.endswith('.mp4.gif') or path.endswith('.webm'):
            return 3
        elif path.endswith('.gif'):
            return 2

        if path.endswith('.webp'):
            with Image.open(path) as img:
                if hasattr(img, 'is_animated') and img.is_animated:
                    return 2

        return 1 # simple image

    def __str__(self):
        return f"{self.image_id}({self.last_viewed}): {self.path} fav({self.fav}) r({self.rating}) c({self.count}))"

    def __repr__(self):
        return str(self)

class ImageExtra(Base):
    __tablename__ = 'image_extra'

    image_id = Column(Integer, ForeignKey('images.id'), primary_key=True)
    data = Column(Text, default='')

    image = relationship('ImageMetadata', backref='extras')

    # @property
    # def as_json(self):
    #     return self.data


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    tag = Column(Text, unique=True, nullable=False)
    color_id = Column(Integer, ForeignKey('colors.id'), name='color', nullable=False, default=1)

    @property
    def hex(self):
        return self.color

    def __lt__(self, other):
        return self.tag < other.tag

    def __gt__(self, other):
        return self.tag > other.tag

    def __eq__(self, other):
        return self.tag == other.tag

    def __str__(self):
        return f"({self.id}:{self.tag})"

    def __repr__(self):
        return str(self)

class ImageTag(Base):
    __tablename__ = 'image_tags'

    image_id = Column(Integer, ForeignKey('images.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
    by_ai = Column(Integer, name='ai', default=0, nullable=False)

    image = relationship('ImageMetadata', backref='tags') # ?? tag. should it be images?
    tag = relationship('Tag', backref='image_tags')

class TagAi(Base):
    __tablename__ = 'tags_ai'

    id = Column(Integer, primary_key=True)
    tag = Column(Text, unique=True, nullable=False)

    def __lt__(self, other):
        return self.tag < other.tag

    def __gt__(self, other):
        return self.tag > other.tag

    def __eq__(self, other):
        return self.tag == other.tag

    def __str__(self):
        return f"({self.id}:{self.tag})"

    def __repr__(self):
        return str(self)

class ImageTagAi(Base):
    __tablename__ = 'image_tags_ai'

    image_id = Column(Integer, ForeignKey('images.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags_ai.id'), primary_key=True)
    rating = Column(Integer, default=0, nullable=False)
    imported_at = Column(UnixTimestamp, default=UnixTimestamp.default(), nullable=False)

    images = relationship('ImageMetadata')

class TagAiToTag(Base):
    __tablename__ = 'tags_ai_to_tags'

    real_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)
    ai_id = Column(Integer, ForeignKey('tags_ai.id'), primary_key=True)

    real_tag = relationship('Tag')
    ai_tag = relationship('TagAi')

class PathTag(Base):
    __tablename__ = 'path_tags'

    path_id = Column(Integer, ForeignKey('paths.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)

    path = relationship('Path', backref='tags') # ?? tag. should it be images?
    tag = relationship('Tag', backref='paths')

class TagSet(Base):
    __tablename__ = 'tag_sets'

    id = Column(Integer, primary_key=True)
    set_name = Column(Text, nullable=False, unique=True)
    set_alias = Column(Text, nullable=False, unique=True)
    tag_list = Column(Text)

    def get_tags(self) -> ([int],[int]):
        tags_all = list(map(lambda t: t.strip(), self.tag_list.split(','))) if self.tag_list else []
        tags_pos = [int(t) for t in tags_all if not t.startswith('-')]
        tags_neg = [int(t[1:]) for t in tags_all if t.startswith('-')]
        return tags_pos, tags_neg

    def get_tags_names(self) -> ([str],[str]):
        tags_pos, tags_neg = self.get_tags()
        session = object_session(self)
        tags_pos = [t.tag for t in session.query(Tag).filter(Tag.id.in_(tags_pos))]
        tags_neg = [t.tag for t in session.query(Tag).filter(Tag.id.in_(tags_neg))]

        return tags_pos, tags_neg

    def names_to_tag_list(self, pos, neg):
        session = object_session(self)

        tags = [str(t.id) for t in session.query(Tag).filter(Tag.tag.in_(pos)).all()] + \
               ['-'+str(t.id) for t in session.query(Tag).filter(Tag.tag.in_(neg)).all()]

        return ','.join(tags)

    @property
    def tag_names_pos_str(self):
        tags, _ = self.get_tags_names()
        return ', '.join(tags)

    @property
    def tag_names_neg_str(self):
        _, tags = self.get_tags_names()
        return ', '.join(tags)

class Color(Base):
    __tablename__ = 'colors'

    id = Column(Integer, primary_key=True)
    color_name = Column(Text)
    hex = Column(Text, default='#000000')

    tags = relationship('Tag', backref='color')

    def __str__(self):
        return self.hex

    def __repr__(self):
        return str(self)

class ImageColor(Base):
    __tablename__ = 'image_colors'

    image_id = Column(Integer, ForeignKey('images.id'), primary_key=True)
    color_id = Column(Integer, ForeignKey('colors.id'), primary_key=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)

    image = relationship('ImageMetadata', backref='colors')
    color = relationship('Color', backref='images')

    @property
    def position(self):
        return self.x, self.y


class Discover(Base):
    __tablename__ = 'discover'

    image_id    = Column(Integer, ForeignKey('images.id'), primary_key=True)
    last_active = Column(UnixTimestamp, nullable=False, default=datetime.now(tz=timezone.utc))

    image = relationship('ImageMetadata')

class Board(Base):
    __tablename__ = 'boards'

    id = Column(Integer, primary_key=True)
    title = Column(Text)

class BoardImage(Base):
    __tablename__ = 'board_images'

    board_id = Column(Integer, ForeignKey('boards.id'), primary_key=True)
    image_id = Column(Integer, ForeignKey('images.id'), primary_key=True)

    tr = Column(Text, default='{tx:0.0, ty:0.0, rx:0.0, ry:0.0, s:1.0}')

    board = relationship('Board', backref='board_images')
    image = relationship('ImageMetadata', backref='board_images')

    @property
    def tr_json(self):
        return self.tr\
            .replace('tx', '"tx"')\
            .replace('ty', '"ty"')\
            .replace('rx', '"rx"')\
            .replace('ry', '"ry"')\
            .replace('s', '"s"')