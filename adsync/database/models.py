import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, ForeignKey,create_engine, CheckConstraint
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import hashlib
from datetime import datetime
Base = declarative_base()

# Create the SQLAlchemy engine (replace 'sqlite:///:memory:' with your actual database URL)
# DATABASE_URL = 'sqlite:///:memory:'
load_dotenv()
database_url = os.environ.get("DATABASE_URL")
print(database_url)
engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'users'

    aadhaarnumber = Column(Integer, primary_key=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    new_address = Column(String)

class Agency(Base):
    __tablename__ = 'agencies'

    agency_id = Column(String, primary_key=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    active_requests = relationship('ActiveRequest', back_populates='agency')

class ActiveRequest(Base):
    __tablename__ = 'active_requests'

    requid = Column(String(length=32), primary_key=True)  # Adjust the length as needed
    user_aadhaarnumber = Column(Integer, ForeignKey('users.aadhaarnumber'))
    agency_id = Column(String, ForeignKey('agencies.agency_id'))
    new_address = Column(String)
    status = Column(String, default="pending")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name='check_valid_status'
        ),
        CheckConstraint(
            "(status = 'pending' AND user_aadhaarnumber IS NOT NULL AND agency_id IS NOT NULL) OR status <> 'pending'",
            name='conditional_unique_user_agency_request'
        ),
    )

    user = relationship('User')
    agency = relationship('Agency', back_populates='active_requests')

    def __init__(self, user_aadhaarnumber, agency_id, new_address, status="pending"):
        self.requid = self.generate_request_id(user_aadhaarnumber, agency_id)
        self.user_aadhaarnumber = user_aadhaarnumber
        self.agency_id = agency_id
        self.new_address = new_address
        self.status = status

    @staticmethod
    def generate_request_id(aadhaarnumber, agency_id):
        # Combine Aadhaar number and agency ID as a string
        combined_string = f"{str(aadhaarnumber)}-{agency_id}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        # Initialize hashlib object
        sha256_hash = hashlib.sha256()

        # Update the hash with the combined string
        sha256_hash.update(combined_string.encode())

        # Use hexdigest to get the hexadecimal string
        hashed_string = sha256_hash.hexdigest()

        return hashed_string


# Create all tables in the database
Base.metadata.create_all(engine)
