"""Unit tests for Category domain entity."""
import pytest
from modules.catalog.domain.entities.category import Category


def test_root_category():
    cat = Category(id=1, name="Lập trình", slug="lap-trinh")
    assert cat.is_root() is True


def test_child_category():
    cat = Category(id=2, name="Python", slug="python", parent_id=1)
    assert cat.is_root() is False


def test_category_is_data_not_enum():
    """12 danh mục là dữ liệu trong DB, không phải enum."""
    categories = [
        "lập trình", "khoa học", "lịch sử", "tiểu thuyết", "toán học",
        "kinh doanh", "kỹ năng sống", "văn học", "triết học", "tâm lý",
        "nghệ thuật", "thiếu nhi",
    ]
    assert len(categories) == 12
    for name in categories:
        cat = Category(id=None, name=name, slug=name.replace(" ", "-"))
        assert cat.name == name
