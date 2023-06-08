import os
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey, TIMESTAMP, func, TypeDecorator
from sqlalchemy.orm import relationship, declarative_base, object_session, sessionmaker

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
    __tablename__ = 'paths'

    id = Column(Integer, primary_key=True)
    path = Column(Text, nullable=False, unique=True)

class StudyType(Base):
    __tablename__ = 'study_types'

    id = Column(Integer, primary_key=True)
    type = Column(Text, nullable=False, unique=True)


class ImageMetadata(Base):
    __tablename__ = 'image_metadata'

    image_id = Column(Integer, name='id', primary_key=True)
    filename = Column(Text, nullable=False)
    study_type_id = Column(Integer, ForeignKey('study_types.id'), name='study_type', nullable=False)
    path_id = Column(Integer, ForeignKey('paths.id'), name='path', nullable=False)
    fav = Column(Integer, default=0)
    count = Column(Integer, default=0)
    rating = Column(Integer, default=0)
    lost = Column(Integer, default=0)
    last_viewed = Column(MyTIMESTAMP, default='1999-01-01 00:00:00')
    imported_at = Column(MyTIMESTAMP, default=datetime.now)
    image_hash = Column(Text, name='hash')

    study_type_ref = relationship('StudyType')
    path_ref = relationship('Path')

    @property
    def is_fav(self):
        return self.fav

    @property
    def study_type(self):
        return self.study_type_ref.type

    @property
    def path(self):
        return os.path.join(self.study_type_ref.type, self.path_ref.path, self.filename)

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


    def __str__(self):
        return f"{self.image_id}({self.last_viewed}): {self.path} fav({self.fav})"

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    tag = Column(Text, unique=True)

class ImageTag(Base):
    __tablename__ = 'image_tags'

    image_id = Column(Integer, ForeignKey('image_metadata.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)

    image = relationship('ImageMetadata', backref='tags')
    tag = relationship('Tag', backref='image_tags')

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