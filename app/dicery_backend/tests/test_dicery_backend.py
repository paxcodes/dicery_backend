from dicery_backend import __version__


def test_version():
    """`__version__` attribute exists."""
    assert isinstance(__version__, str)
