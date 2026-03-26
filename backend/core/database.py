# # core/database.py
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from .config import settings
# import os

# # Ensure the data directory exists
# data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
# os.makedirs(data_dir, exist_ok=True)

# # Use absolute path for database
# db_path = os.path.join(data_dir, "address_sync.db")
# DATABASE_URL = f"sqlite:///{db_path}"

# # Create engine with proper settings
# engine = create_engine(
#     DATABASE_URL,
#     connect_args={"check_same_thread": False},  # Needed for SQLite
#     echo=False  # Set to True to see SQL queries
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# backend/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import os

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
