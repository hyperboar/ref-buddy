from app.models.models_lump import Path, ImageMetadata


def add_4_images_1_path(session) -> None:
    session.merge(Path(id=1, path="everything"))
    session.flush()

    new_image = lambda s, imid, fn: s.add(ImageMetadata(image_id=imid,
                              filename=fn,
                              path_id=1,
                              source_type_id=1,
                              category_id=1))
    new_image(session, 1, "Lenna_1.jpg")
    new_image(session, 2, "Lenna_2.jpg")
    new_image(session, 3, "Lenna_3.jpg")
    new_image(session, 4, "Lenna_4.jpg")
    session.commit()

def add_1_mp4_1_path(session) -> None:
    session.merge(Path(id=1, path="everything"))
    session.flush()

    session.add(ImageMetadata(image_id=5,
                              filename='Lenna_5_source_mp4.mp4.gif',
                              path_id=1,
                              source_type_id=3,
                              category_id=1))
    session.commit()

def add_1_gif_1_path(session) -> None:
    session.merge(Path(id=1, path="everything"))
    session.flush()

    session.add(ImageMetadata(image_id=6,
                              filename='Lenna_6_source_gif.gif',
                              path_id=1,
                              source_type_id=2,
                              category_id=1))
    session.commit()