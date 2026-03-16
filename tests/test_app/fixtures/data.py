from app.models.models_lump import Path, ImageMetadata


def add_4_images_1_path(session) -> None:
    session.add(Path(id=1, path="everything"))
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