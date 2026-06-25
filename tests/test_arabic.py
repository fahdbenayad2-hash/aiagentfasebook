from app.utils.arabic import normalize_arabic, normalize_list


def test_normalize_alef_variants():
    assert normalize_arabic("ابيض") == normalize_arabic("أبيض")


def test_teh_marbuta():
    assert normalize_arabic("وردة") == normalize_arabic("ورده")


def test_alif_maqsura():
    assert normalize_arabic("رمى") == normalize_arabic("رمي")


def test_tashkeel_removed():
    assert normalize_arabic("كَيْفَ") == normalize_arabic("كيف")


def test_case_insensitive_latin():
    assert normalize_arabic("XL") == normalize_arabic("xl")


def test_strip_whitespace():
    assert normalize_arabic("  أبيض  ") == normalize_arabic("أبيض")


def test_all_colors_normalized():
    colors = ["أبيض", "أسود", "وردي", "رمادي", "أزرق", "أحمر"]
    normalized = normalize_list(colors)
    assert len(normalized) == 6
    assert all(isinstance(c, str) for c in normalized)


def test_normalize_list_empty():
    assert normalize_list([]) == []


def test_mixed_hamza():
    assert normalize_arabic("آدم") == normalize_arabic("ادم")
    assert normalize_arabic("ٱدم") == normalize_arabic("ادم")


class _FakeProduct:
    def __init__(self, name):
        self.name = name


def test_find_product_exact():
    from app.utils.arabic import find_product
    products = [_FakeProduct("بجامة نسائية"), _FakeProduct("فستان")]
    result = find_product("بجامة نسائية", products)
    assert result is not None
    assert result.name == "بجامة نسائية"


def test_find_product_fuzzy():
    from app.utils.arabic import find_product
    products = [_FakeProduct("بجامة نسائية"), _FakeProduct("فستان")]
    result = find_product("حاب بجامة", products)
    assert result is not None
    assert result.name == "بجامة نسائية"


def test_find_product_not_found():
    from app.utils.arabic import find_product
    products = [_FakeProduct("بجامة نسائية")]
    result = find_product("سيارة", products)
    assert result is None


def test_find_product_empty():
    from app.utils.arabic import find_product
    result = find_product("بجامة", [])
    assert result is None
