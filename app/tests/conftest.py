import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{settings.POSTGRESQL_USERNAME}:{settings.POSTGRESQL_PASSWORD}@{settings.POSTGRESQL_HOSTNAME}:{settings.POSTGRESQL_PORT}/hr_test_db"

# global application scope.  create Session class, engine
Session = sessionmaker()

engine = create_engine(SQLALCHEMY_DATABASE_URL)

faker = Faker()

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


@pytest.fixture
def session():
    # connect to the database
    connection = engine.connect()

    # begin a non-ORM transaction
    trans = connection.begin()

    # bind an individual Session to the connection, selecting
    # "create_savepoint" join_transaction_mode
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session

    session.close()

    # rollback - everything that happened with the
    # Session above (including calls to commit())
    # is rolled back.
    trans.rollback()

    # return connection to the Engine
    connection.close()


# A fixture for the fastapi test client which depends on the
# previous session fixture. Instead of creating a new session in the
# dependency override as before, it uses the one provided by the
# session fixture.
@pytest.fixture()
def client(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]
