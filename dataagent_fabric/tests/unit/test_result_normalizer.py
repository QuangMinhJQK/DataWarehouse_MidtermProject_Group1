from dataagent.result_normalizer import ResultNormalizer


def test_normalizer_labels_columns_and_caps_rows(catalog):
    normalizer = ResultNormalizer(catalog, max_rows=1)
    rows = [
        {"product[category_name]": "Bikes", "[Net Sales]": 100.0},
        {"product[category_name]": "Accessories", "[Net Sales]": 50.0},
    ]

    result = normalizer.normalize(rows)

    assert result.rows == [{"Danh mục": "Bikes", "Doanh thu thuần": 100.0}]
    assert result.truncated is True
    assert result.warnings
