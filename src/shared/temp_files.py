import tempfile
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def temporary_file(suffix: str):
    """Create a temporary file path and delete it when done."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    Path(path).unlink(missing_ok=True)
    try:
        yield path
    finally:
        Path(path).unlink(missing_ok=True)
