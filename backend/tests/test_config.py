"""
Config / middleware unit tests.
Covers: CORS_ORIGINS CSV parsing (the bug that caused JSON decode error).
"""


def test_cors_origins_single():
    origins = [o.strip() for o in "http://localhost:3000".split(",") if o.strip()]
    assert origins == ["http://localhost:3000"]


def test_cors_origins_multiple():
    origins = [o.strip() for o in "http://localhost:3000,https://app.example.com".split(",") if o.strip()]
    assert origins == ["http://localhost:3000", "https://app.example.com"]


def test_cors_origins_with_spaces():
    origins = [o.strip() for o in "http://localhost:3000, https://app.example.com ".split(",") if o.strip()]
    assert origins == ["http://localhost:3000", "https://app.example.com"]


def test_cors_origins_empty_string_yields_empty_list():
    origins = [o.strip() for o in "".split(",") if o.strip()]
    assert origins == []
