import pytest

from grading.store import connect


@pytest.fixture
def conn():
    c = connect()
    yield c
    c.close()
