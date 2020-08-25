from typing import Generator

import debugpy
from pytest import fixture

from dicery_backend.database import SessionLocal


@fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


@fixture(scope="session")
def use_debugpy():
    debugpy.listen(("0.0.0.0", 5678))
    debugpy.wait_for_client()
