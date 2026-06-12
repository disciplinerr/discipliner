from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = hash_password("correct horse battery staple")
    assert verify_password("correct horse battery staple", hashed)
    assert not verify_password("wrong password", hashed)


def test_access_token_roundtrip():
    token = create_access_token("42")
    assert decode_token(token, expected_type="access") == "42"


def test_token_type_mismatch_rejected():
    refresh = create_refresh_token("42")
    assert decode_token(refresh, expected_type="access") is None


def test_garbage_token_rejected():
    assert decode_token("not.a.token") is None
