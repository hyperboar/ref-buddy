-- ASSIGN IMAGE TO ITS STUDY TYPE
-- academic
INSERT OR IGNORE INTO image_tags (image_id, tag_id)
SELECT id, 2
FROM images
WHERE category = 1;
-- pron and the-bits
INSERT OR IGNORE INTO image_tags (image_id, tag_id)
SELECT id, 3
FROM images
WHERE category in (2, 4);
-- the_bits
INSERT OR IGNORE INTO image_tags (image_id, tag_id)
SELECT id, 5
FROM images
WHERE category = 4;
-- artists
INSERT OR IGNORE INTO image_tags (image_id, tag_id)
SELECT id, 4
FROM images
WHERE category = 3;
-- video
INSERT OR IGNORE INTO image_tags (image_id, tag_id)
SELECT id, 6
FROM images
WHERE category = 5;


-- -- hash duplicates
-- select im.id, p.path, im.filename
-- from images as im
--     join paths p on im.path = p.id
-- where im.id in
--       (
--       select im1.id
--       from images as im1
--           join images as im2
--       where im1.id <> im2.id AND
--             im2.lost = 0 AND im1.lost = 0 AND
--             im1.hash = im2.hash
--       )
-- order by im.hash, p.path;
