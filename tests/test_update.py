from jolaos import update


def test_parse_version_ignores_prefix_and_suffix():
    assert update.parse_version("v0.1.2") == (0, 1, 2)
    assert update.parse_version("Jolaos 1.10.0-beta") == (1, 10, 0)
    assert update.parse_version("") == (0,)


def test_is_newer_compares_numerically():
    assert update.is_newer("0.1.10", "0.1.2")
    assert not update.is_newer("0.1.2", "0.1.2")
    assert not update.is_newer("0.0.9", "0.1.2")
    assert update.is_newer("v1.0.0", "0.9.9")
