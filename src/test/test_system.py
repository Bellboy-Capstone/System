import pytest

from src.system import add

pytestmark = pytest.mark.django_db


def test_add():
    assert add(1, 2) == 3
