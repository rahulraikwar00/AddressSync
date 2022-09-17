import os
from sqlmodel import SQLModel, create_engine
import sqlalchemy_utils as sa_utils
from dotenv import load_dotenv
load_dotenv()


SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")


if not sa_utils.functions.database_exists(SQLALCHEMY_DATABASE_URL):
    sa_utils.functions.create_database(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)


def cr_db():
    SQLModel.metadata.create_all(engine)


def drop_db():
    SQLModel.metadata.drop_all(engine)
