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
    removed INTEGER DEFAULT 0,
    image_type INTEGER DEFAULT 0,
    last_viewed TIMESTAMP DEFAULT '1999-01-01 00:00:00',
    imported_at TIMESTAMP DEFAULT (datetime('now')),
    hash TEXT,
    FOREIGN KEY (path) REFERENCES paths (id),
    FOREIGN KEY (study_type) REFERENCES study_types (id)
);

CREATE INDEX fn_index ON image_metadata (filename);

CREATE TABLE IF NOT EXISTS paths (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE,
    preview INTEGER DEFAULT 0 NOT NULL,
    ord INTEGER DEFAULT 0 NOT NULL,
    hidden  INTEGER DEFAULT 0 NOT NULL
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
    tag TEXT NOT NULL UNIQUE,
    color_id INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (color_id) REFERENCES colors(id)
);

CREATE TABLE  IF NOT EXISTS image_tags (
    image_id INTEGER,
    tag_id INTEGER,
    FOREIGN KEY (image_id) REFERENCES image_metadata(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id),
    PRIMARY KEY (image_id, tag_id)
);

CREATE TABLE IF NOT EXISTS path_tags (
    path_id INTEGER,
    tag_id INTEGER,

    PRIMARY KEY (path_id, tag_id),
    FOREIGN KEY (path_id) REFERENCES paths(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);


CREATE TABLE IF NOT EXISTS tag_sets (
    id INTEGER PRIMARY KEY,
    set_name TEXT NOT NULL UNIQUE,
    set_alias TEXT NOT NULL UNIQUE,
    tag_list TEXT
);

CREATE TABLE  IF NOT EXISTS discover (
    image_id INTEGER,
    last_active TIMESTAMP DEFAULT (datetime('now')),
    FOREIGN KEY (image_id) REFERENCES image_metadata(id),
    PRIMARY KEY (image_id)
);

CREATE TABLE IF NOT EXISTS dupes (
    image1 INTEGER,
    image2 INTEGER,
    found_at TIMESTAMP DEFAULT (datetime('now')),
    fp INTEGER DEFAULT 0,
    r  INTEGER DEFAULT 0,
    PRIMARY KEY (image1, image2)
);

CREATE TABLE IF NOT EXISTS colors (
    id INTEGER PRIMARY KEY,
    hex TEXT NOT NULL DEFAULT '#000000',
    color_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS image_colors (
    image_id INTEGER,
    color_id INTEGER,
    x REAL NOT NULL,
    y REAL NOT NULL,
    FOREIGN KEY (image_id) REFERENCES image_metadata(id),
    FOREIGN KEY (color_id) REFERENCES colors(id),
    PRIMARY KEY (image_id, color_id)
);

CREATE TABLE  IF NOT EXISTS image_extra (
    image_id INTEGER,
    data TEXT DEFAULT '',
    FOREIGN KEY (image_id) REFERENCES image_metadata(id),
    PRIMARY KEY (image_id)
);

CREATE TABLE IF NOT EXISTS boards (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    tr TEXT DEFAULT '{tx:0.0, ty:0.0, rx:0.0, ry:0.0, s:1.0}' -- json transform
);

CREATE TABLE IF NOT EXISTS board_images (
    board_id INTEGER,
    image_id INTEGER,
    tr TEXT DEFAULT '{tx:0.0, ty:0.0, rx:0.0, ry:0.0, s:1.0}', -- json transform

    PRIMARY KEY (board_id, image_id),
    FOREIGN KEY (image_id) REFERENCES image_metadata(id),
    FOREIGN KEY (board_id) REFERENCES boards(id)
);

INSERT INTO colors (id, color_name) VALUES (1, 'default');

INSERT INTO tags (id, tag) VALUES (1, 'futanari');
INSERT INTO tags (id, tag) VALUES (2, 'academic');
INSERT INTO tags (id, tag) VALUES (3, 'pron');
INSERT INTO tags (id, tag) VALUES (4, 'artists');
INSERT INTO tags (id, tag) VALUES (5, 'the_bits');
INSERT INTO tags (id, tag) VALUES (6, 'frames');
INSERT INTO tags (id, tag) VALUES (7, 'portrait');
INSERT INTO tags (id, tag) VALUES (8, 'pose_stand');
INSERT INTO tags (id, tag) VALUES (9, 'pose_sit');
INSERT INTO tags (id, tag) VALUES (10, 'pose_lay');
INSERT INTO tags (id, tag) VALUES (11, 'pose_stand_bent');
INSERT INTO tags (id, tag) VALUES (12, 'view_body_front');
INSERT INTO tags (id, tag) VALUES (13, 'view_body_rear');
INSERT INTO tags (id, tag) VALUES (14, 'view_body_side');
INSERT INTO tags (id, tag) VALUES (15, 'view_body_3-4');
INSERT INTO tags (id, tag) VALUES (16, 'view_body_upper');
INSERT INTO tags (id, tag) VALUES (17, 'view_body_lower');
INSERT INTO tags (id, tag) VALUES (18, 'hands');
INSERT INTO tags (id, tag) VALUES (19, 'gt_penis');
INSERT INTO tags (id, tag) VALUES (20, 'belly');
INSERT INTO tags (id, tag) VALUES (21, 'pussy');
INSERT INTO tags (id, tag) VALUES (22, 'male');
INSERT INTO tags (id, tag) VALUES (23, 'female');
INSERT INTO tags (id, tag) VALUES (24, 'ai');
INSERT INTO tags (id, tag) VALUES (25, 'easy');
INSERT INTO tags (id, tag) VALUES (26, 'hard');
INSERT INTO tags (id, tag) VALUES (27, 'still_life');
INSERT INTO tags (id, tag) VALUES (28, 'gt_breasts');
INSERT INTO tags (id, tag) VALUES (29, 'growth');
INSERT INTO tags (id, tag) VALUES (30, 'ass');
INSERT INTO tags (id, tag) VALUES (31, 'view_cam_wide');
INSERT INTO tags (id, tag) VALUES (32, 'pinup');
INSERT INTO tags (id, tag) VALUES (33, 'legs');
INSERT INTO tags (id, tag) VALUES (34, 'act_bj');
INSERT INTO tags (id, tag) VALUES (35, 'multi_person');
INSERT INTO tags (id, tag) VALUES (36, 'buff');
INSERT INTO tags (id, tag) VALUES (37, 'b_plus_size');
INSERT INTO tags (id, tag) VALUES (38, 'b_skinny');
INSERT INTO tags (id, tag) VALUES (39, 'view_cam_top');
INSERT INTO tags (id, tag) VALUES (40, 'view_cam_low');
INSERT INTO tags (id, tag) VALUES (41, 'pose_kneel');
INSERT INTO tags (id, tag) VALUES (42, 'gt_pose');
INSERT INTO tags (id, tag) VALUES (43, 'asian');
INSERT INTO tags (id, tag) VALUES (44, 'milking_bucket');
INSERT INTO tags (id, tag) VALUES (45, 'test_1');
INSERT INTO tags (id, tag) VALUES (46, 'penis_only');
INSERT INTO tags (id, tag) VALUES (47, 'underboob');
INSERT INTO tags (id, tag) VALUES (48, 'tutorial');
INSERT INTO tags (id, tag) VALUES (49, 'penis_bulge');
INSERT INTO tags (id, tag) VALUES (50, 'cum');
INSERT INTO tags (id, tag) VALUES (51, 'manga');
INSERT INTO tags (id, tag) VALUES (52, 'furry');
INSERT INTO tags (id, tag) VALUES (53, 'futa_real');
INSERT INTO tags (id, tag) VALUES (54, 'penis_horse');
INSERT INTO tags (id, tag) VALUES (55, 'ppl_busty_alli');
INSERT INTO tags (id, tag) VALUES (56, 'art_line');
INSERT INTO tags (id, tag) VALUES (57, 'art_shading_basic');
INSERT INTO tags (id, tag) VALUES (58, 'props');
INSERT INTO tags (id, tag) VALUES (59, 'clothes');
INSERT INTO tags (id, tag) VALUES (60, 'lingerie');
INSERT INTO tags (id, tag) VALUES (61, 'thick');
INSERT INTO tags (id, tag) VALUES (62, 'view_body_full');
INSERT INTO tags (id, tag) VALUES (63, 'emotion');
INSERT INTO tags (id, tag) VALUES (64, 'pose_fly');
INSERT INTO tags (id, tag) VALUES (65, 'act_walk');
INSERT INTO tags (id, tag) VALUES (66, 'pose_crawl');
INSERT INTO tags (id, tag) VALUES (67, 'pose_gop');
INSERT INTO tags (id, tag) VALUES (68, 'tagme');
INSERT INTO tags (id, tag) VALUES (69, 'act_sex');
INSERT INTO tags (id, tag) VALUES (70, 'act_self_suck');
INSERT INTO tags (id, tag) VALUES (71, 'act_paizuri');
INSERT INTO tags (id, tag) VALUES (72, 'rori');
INSERT INTO tags (id, tag) VALUES (73, 'ai_mine');
INSERT INTO tags (id, tag) VALUES (74, 'gt_comp');
INSERT INTO tags (id, tag) VALUES (75, 'gt_thumb');
INSERT INTO tags (id, tag) VALUES (76, 'slime');
INSERT INTO tags (id, tag) VALUES (77, 'size_diff');
INSERT INTO tags (id, tag) VALUES (78, 'penis_boob_side');
INSERT INTO tags (id, tag) VALUES (79, 'gt_balls');

INSERT INTO tag_sets (set_name, tag_list) VALUES ('all', '');
INSERT INTO tag_sets (set_name, tag_list) VALUES ('academic', '1');
INSERT INTO tag_sets (set_name, tag_list) VALUES ('artists', '4');
INSERT INTO tag_sets (set_name, tag_list) VALUES ('pron', '3');
INSERT INTO tag_sets (set_name, tag_list) VALUES ('the_bits', '5');
INSERT INTO tag_sets (set_name, tag_list) VALUES ('frames', '6');