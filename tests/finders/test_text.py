import urlfinderlib.finders as finders


def test_create_text():
    assert finders.TextUrlFinder("test")
