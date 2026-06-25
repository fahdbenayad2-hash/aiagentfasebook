from app.models import Product


def test_get_colors_empty():
    p = Product(name="test", price=100)
    assert p.get_colors() == []


def test_get_colors():
    p = Product(name="test", price=100, colors="أبيض,أسود,وردي")
    assert p.get_colors() == ["أبيض", "أسود", "وردي"]


def test_set_colors_normalizes():
    p = Product(name="test", price=100)
    p.set_colors(["أبيض", "أسود", "وردي"])
    assert p.colors == "ابيض,اسود,وردي"


def test_get_sizes_empty():
    p = Product(name="test", price=100)
    assert p.get_sizes() == []


def test_get_sizes():
    p = Product(name="test", price=100, sizes="S,M,L,XL")
    assert p.get_sizes() == ["S", "M", "L", "XL"]


def test_set_sizes_uppercases():
    p = Product(name="test", price=100)
    p.set_sizes(["s", "m", "l", "xl"])
    assert p.sizes == "S,M,L,XL"


def test_has_color_normalized():
    p = Product(name="test", price=100, colors="ابيض,اسود,وردي")
    assert p.has_color("أبيض")
    assert not p.has_color("أحمر")


def test_has_size():
    p = Product(name="test", price=100, sizes="S,M,L")
    assert p.has_size("s")
    assert p.has_size("S")
    assert not p.has_size("XL")
