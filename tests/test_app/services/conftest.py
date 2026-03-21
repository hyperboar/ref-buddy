import pytest
from unittest.mock import MagicMock

from app.models import Session


@pytest.fixture(scope="module")
def session_real():
    return Session

@pytest.fixture
def raw_tags_pos_only():
    return "pos_1,pos_2,pos_3"
@pytest.fixture
def raw_tags_neg_only():
    return "-neg_4,-neg_5,-neg_6"
@pytest.fixture
def raw_tags_both(raw_tags_pos_only, raw_tags_neg_only):
    return raw_tags_pos_only + ',' + raw_tags_neg_only

@pytest.fixture
def proc_tags_pos_only():
    return ["pos_1","pos_2","pos_3"]
@pytest.fixture
def proc_tags_neg_only():
    return ["neg_4","neg_5","neg_6"]
@pytest.fixture
def proc_tags_both(proc_tags_pos_only, proc_tags_neg_only):
    return proc_tags_pos_only + proc_tags_neg_only

@pytest.fixture
def session_mock():
    return MagicMock()