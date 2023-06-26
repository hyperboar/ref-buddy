PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS image_metadata (
    id INTEGER PRIMARY KEY,
    filename TEXT NOT NULL,
    path INTEGER NOT NULL,
    study_type INTEGER NOT NULL,
    fav INTEGER DEFAULT 0,
    count INTEGER DEFAULT 0,
    rating INTEGER DEFAULT 0,
    lost INTEGER DEFAULT 0,
    last_viewed TIMESTAMP DEFAULT '1999-01-01 00:00:00',
    imported_at TIMESTAMP DEFAULT (datetime('now')),
    hash TEXT,
    FOREIGN KEY (path) REFERENCES paths (id),
    FOREIGN KEY (study_type) REFERENCES study_types (id)
);

CREATE INDEX fn_index ON image_metadata (filename);

CREATE TABLE IF NOT EXISTS paths (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS study_types (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL UNIQUE
);

INSERT INTO study_types (type) VALUES ('academic');
INSERT INTO study_types (type) VALUES ('pron');
INSERT INTO study_types (type) VALUES ('artists');
INSERT INTO study_types (type) VALUES ('the_bits');
INSERT INTO study_types (type) VALUES ('frames');


CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    tag TEXT UNIQUE
);

CREATE TABLE  IF NOT EXISTS image_tags (
    image_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY (image_id) REFERENCES image_metadata(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id),
    PRIMARY KEY (image_id, tag_id)
);

INSERT INTO tags (tag) VALUES ('futanari');

INSERT INTO tags (tag) VALUES ('academic');
INSERT INTO tags (tag) VALUES ('pron');
INSERT INTO tags (tag) VALUES ('artists');
INSERT INTO tags (tag) VALUES ('the_bits');
Insert into tags (tag) values ('video');

INSERT INTO tags (tag) VALUES ('face');

INSERT INTO tags (tag) VALUES ('pose_stand');
INSERT INTO tags (tag) VALUES ('pose_sit');
INSERT INTO tags (tag) VALUES ('pose_lay');
INSERT INTO tags (tag) VALUES ('pose_stand_bent');

INSERT INTO tags (tag) VALUES ('view_body_front');
INSERT INTO tags (tag) VALUES ('view_body_back');
INSERT INTO tags (tag) VALUES ('view_body_side');
INSERT INTO tags (tag) VALUES ('view_body_3-4');
INSERT INTO tags (tag) VALUES ('view_body_top');
INSERT INTO tags (tag) VALUES ('view_body_bottom');

CREATE TABLE IF NOT EXISTS dupes (
    image1 INTEGER,
    image2 INTEGER,
    found_at TIMESTAMP DEFAULT (datetime('now')),
    fp INTEGER DEFAULT 0,
    r  INTEGER DEFAULT 0,
    PRIMARY KEY (image1, image2)
);
