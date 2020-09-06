from typing import Generator

import debugpy
from fastapi.testclient import TestClient
from pytest import fixture

from dicery_backend.database import SessionLocal
from dicery_backend.main import app


@fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


@fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@fixture(scope="session")
def use_debugpy():
    debugpy.listen(("0.0.0.0", 5678))
    debugpy.wait_for_client()
