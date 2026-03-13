from app.models import DatabaseEnvironment, Session
from app.models.models_lump import ImageMetadata, Path

if __name__ == '__main__':
    print('main!')

    DatabaseEnvironment.update_db_connection()
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