-- ASSIGN IMAGE TO ITS STUDY TYPE
-- academic
INSERT OR IGNORE INTO image_tags (image_id, tag_id)
SELECT id, 2
FROM image_metadata
WHERE study_type = 1;
-- pron and the-bits
INSERT OR IGNORE INTO image_tags (image_id, tag_id)
SELECT id, 3
FROM image_metadata
WHERE study_type in (2, 3);
-- the_bits
INSERT OR IGNORE INTO image_tags (image_id, tag_id)
SELECT id, 5
FROM image_metadata
WHERE study_type = 4;
-- artists
INSERT OR IGNORE INTO image_tags (image_id, tag_id)
SELECT id, 4
FROM image_metadata
WHERE study_type = 3;
-- video
INSERT OR IGNORE INTO image_tags (image_id, tag_id)
SELECT id, 6
FROM image_metadata
WHERE study_type = 5;


