import urlfinderlib.finders as finders


def test_create_text():
    assert finders.CsvUrlFinder('test,test,test\ntest2,test2,test2')
