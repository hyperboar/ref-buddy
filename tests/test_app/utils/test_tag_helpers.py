from app.utils.tags_helpers import handle_tags


def test_handle_tags_1(raw_tags_both, proc_tags_pos_only, proc_tags_neg_only):
    tag_pos, tag_neg = handle_tags(raw_tags_both)

    pos_intersect = set(tag_pos).intersection(set(proc_tags_pos_only))
    neg_intersect = set(tag_neg).intersection(set(proc_tags_neg_only))
    assert len(tag_pos) == len(pos_intersect)
    assert len(tag_neg) == len(neg_intersect)

def test_handle_tags_2(raw_tags_pos_only, raw_tags_neg_only, proc_tags_pos_only, proc_tags_neg_only):
    tag_pos, tag_neg = handle_tags(raw_tags_pos_only)
    assert len(tag_pos) > 0
    assert len(tag_neg) == 0
    pos_intersect = set(tag_pos).intersection(set(proc_tags_pos_only))
    assert len(tag_pos) == len(pos_intersect)

    tag_pos, tag_neg = handle_tags(raw_tags_neg_only)
    assert len(tag_pos) == 0
    assert len(tag_neg) > 0
    neg_intersect = set(tag_neg).intersection(set(proc_tags_neg_only))
    assert len(tag_neg) == len(neg_intersect)