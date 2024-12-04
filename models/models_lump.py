import os
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey, TIMESTAMP, func, TypeDecorator, Float
from sqlalchemy.orm import relationship, declarative_base, object_session, sessionmaker

from PIL import Image

from Env import Env

# Create an in-memory SQLite database
engine = create_engine(f'sqlite:///{Env.DB_FILE}') # , echo=True
Session = sessionmaker(bind=engine)

# Create a base class for declarative models
Base = declarative_base()


class MyTIMESTAMP(TypeDecorator):
    """
    Crutch for SQLAlchemy's inability to handle SQLite TIMESTAMP and DateTime as a string
    """
    impl = TIMESTAMP
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if type(value) is str:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return value

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

class StudyType(Base):
    __tablename__ = 'study_types'

    id = Column(Integer, primary_key=True)
    type = Column(Text, nullable=False, unique=True)


class ImageMetadata(Base):
    __tablename__ = 'image_metadata'

    image_id = Column(Integer, name='id', primary_key=True)
    filename = Column(Text, nullable=False)
    study_type_id = Column(Integer, ForeignKey('study_types.id'), name='study_type', nullable=False)
    source_type_id = Column(Integer, name='source_type', default=0, nullable=False)
    path_id = Column(Integer, ForeignKey('paths.id'), name='path', nullable=False)
    fav = Column(Integer, default=0)
    count = Column(Integer, default=0)
    rating = Column(Integer, default=0)
    lost = Column(Integer, default=0)
    removed = Column(Integer, default=0, nullable=False)
    last_viewed = Column(MyTIMESTAMP, default='1999-01-01 00:00:00')
    imported_at = Column(MyTIMESTAMP, default=datetime.now)
    image_hash = Column(Text, name='hash')

    study_type_ref = relationship('StudyType')
    path_ref = relationship('Path', backref='images')

    @property
    def is_fav(self):
        return self.fav

    def is_removed(self):
        return self.removed

    @property
    def study_type(self):
        return self.study_type_ref.type

    @property
    def path(self):
        return os.path.join(self.path_ref.path, self.filename)

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

    image_id = Column(Integer, ForeignKey('image_metadata.id'), primary_key=True)
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

    image_id = Column(Integer, ForeignKey('image_metadata.id'), primary_key=True)
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

    image_id = Column(Integer, ForeignKey('image_metadata.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags_ai.id'), primary_key=True)
    rating = Column(Integer, name='rating', default=0, nullable=False)
    imported_at = Column(MyTIMESTAMP, name='imported_at', default=0, nullable=False)

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
        auto_close = False
        if session is None:
            auto_close = True
            session = Session()

        tags = [str(t.id) for t in session.query(Tag).filter(Tag.tag.in_(pos)).all()] + \
               ['-'+str(t.id) for t in session.query(Tag).filter(Tag.tag.in_(neg)).all()]

        if auto_close:
            session.close()
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

    image_id = Column(Integer, ForeignKey('image_metadata.id'), primary_key=True)
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

    image_id    = Column(Integer, ForeignKey('image_metadata.id'), primary_key=True)
    last_active = Column(MyTIMESTAMP, default=datetime.now)

    image = relationship('ImageMetadata')


class ImageDupe(Base):
    __tablename__ = 'dupes'

    image1 = Column(Integer, name='image1', default=0, primary_key=True)
    image2 = Column(Integer, name='image2', default=0, primary_key=True)
    false_positive = Column(Integer, name='fp', default=0)
    resolved = Column(Integer, name='r', default=0)
    found_at = Column(MyTIMESTAMP, default=datetime.now)

class Board(Base):
    __tablename__ = 'boards'

    id = Column(Integer, primary_key=True)
    title = Column(Text)

class BoardImage(Base):
    __tablename__ = 'board_images'

    board_id = Column(Integer, ForeignKey('boards.id'), primary_key=True)
    image_id = Column(Integer, ForeignKey('image_metadata.id'), primary_key=True)

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

# Create the tables
# Base.metadata.create_all(engine, checkfirst=True)

if __name__ == '__main__':
    print('main!')

    session = Session()

    paths = session.query(Path).all()

    # for p in paths:
    #     print(f'{p.id} {p.path}')

    image_metadata = session.query(ImageMetadata).filter(
        ImageMetadata.rating > 3,
        ImageMetadata.fav == 1
    ).limit(1).all()

    for p in image_metadata:
        print(f'{p.image_id} {p.path.path}/{p.filename} {",".join([t.tag for t in p.tags])}')