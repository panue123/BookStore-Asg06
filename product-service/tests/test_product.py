"""Unit tests for Product domain entity."""
import pytest
from modules.catalog.domain.entities.product import Product


def make_product(**kwargs):
    defaults = dict(id=1, name="Test Book", category_id=1, price=100000, stock=10)
    defaults.update(kwargs)
    return Product(**defaults)


def test_product_in_stock():
    p = make_product(stock=5)
    assert p.is_in_stock() is True


def test_product_out_of_stock():
    p = make_product(stock=0)
    assert p.is_in_stock() is False


def test_apply_discount():
    p = make_product(price=100000)
    assert p.apply_discount(10) == 90000.0


def test_get_attribute():
    p = make_product(attributes={"author": "Nguyễn Du", "pages": 256})
    assert p.get_attribute("author") == "Nguyễn Du"
    assert p.get_attribute("missing", "default") == "default"


def test_product_category_is_data():
    """Category là dữ liệu (int ID), không phải enum cứng."""
    p = make_product(category_id=5)
    assert isinstance(p.category_id, int)
    assert p.category_id == 5
