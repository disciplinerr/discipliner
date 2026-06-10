import pytest

from app.services.challenge_generator import _extract_json


def test_extract_plain_json():
    data = _extract_json('{"result": "PASS", "reason": "ok"}')
    assert data["result"] == "PASS"


def test_extract_json_with_fences():
    data = _extract_json('```json\n{"result": "FAIL", "reason": "no"}\n```')
    assert data["result"] == "FAIL"


def test_extract_json_with_preamble():
    data = _extract_json('Here is the object: {"title": "X"}')
    assert data["title"] == "X"


def test_extract_json_rejects_garbage():
    with pytest.raises(ValueError):
        _extract_json("no json here")
