import pytest

from face_api.database.database import SessionLocal, engine
from face_api.database import models, crud


@pytest.fixture
def db():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


def test_get_users(db):
    print(crud.get_all_users(db))


