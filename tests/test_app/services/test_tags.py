from app.models.models_lump import Tag, TagSet
from app.services.tags import get_tag_names, get_tags_by_names, get_all_tags, get_tags_by_set


def test_get_tag_names_1(session_mock):
    tag1 = Tag(id=1, tag='tag1')

    session_mock.query.return_value.filter.return_value.all.return_value = [tag1]
    result = get_tag_names([1], session=session_mock)
    assert len(result) == 1
    assert result[0] == tag1.tag

def test_get_tag_names_2(session_mock):
    session_mock.query.return_value.filter.return_value.all.return_value = []
    result = get_tag_names([], session=session_mock)
    assert len(result) == 0

    result = get_tag_names(None, session=session_mock)
    assert len(result) == 0

def test_get_tags_by_names_1(session_mock):
    tag1 = Tag(id=1, tag='tag1')
    session_mock.query.return_value.filter.return_value.all.return_value = [tag1]
    result = get_tags_by_names(['test'], session=session_mock)
    assert len(result) == 1
    assert result[0] == tag1.id

def test_get_tags_by_names_2(session_mock):
    session_mock.query.return_value.filter.return_value.all.return_value = []
    result = get_tags_by_names([], session=session_mock)
    assert len(result) == 0

    result = get_tags_by_names(None, session=session_mock)
    assert len(result) == 0

def test_get_all_tags_1(session_mock):
    tag1 = Tag(id=1, tag='tag1')
    tag2 = Tag(id=2, tag='tag2')
    session_mock.query.return_value.all.return_value = [tag1, tag2]
    result = get_all_tags(session=session_mock)
    assert len(result) == 2

def test_get_tags_by_set_1(session_mock):
    tagset1 = TagSet(id=1, set_name='set1', set_alias='alias1', tag_list='1,2,-3,-4')

    session_mock.query.return_value.filter.return_value.all.return_value = []
    session_mock.query.return_value.filter.return_value.first.return_value = tagset1
    res_pos, res_neg = get_tags_by_set(1, session=session_mock)
    assert len(res_pos) == 2
    assert len(res_neg) == 2

    # dupe pos
    session_mock.query.return_value.filter.return_value.all.return_value = [Tag(id=1)]
    res_pos, res_neg = get_tags_by_set(1, session=session_mock, add_pos=[1])
    assert len(res_pos) == 2
    assert len(res_neg) == 2

    # dupe neg
    session_mock.query.return_value.filter.return_value.all.return_value = [Tag(id=3)]
    res_pos, res_neg = get_tags_by_set(1, session=session_mock, add_neg=[3])
    assert len(res_pos) == 2
    assert len(res_neg) == 2

    # add pos
    session_mock.query.return_value.filter.return_value.all.return_value = [Tag(id=5)]
    res_pos, res_neg = get_tags_by_set(1, session=session_mock, add_pos=[5])
    assert len(res_pos) == 3
    assert len(res_neg) == 2

    # add neg
    session_mock.query.return_value.filter.return_value.all.return_value = [Tag(id=6)]
    res_pos, res_neg = get_tags_by_set(1, session=session_mock, add_neg=[6])
    assert len(res_pos) == 2
    assert len(res_neg) == 3