from .database import *
from .crud import *
from .models import *
from .schemas import *
from sqlmodel import Session, select
import hashlib
from features.dropdown import *
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = Session(engine)
    return db

def register_users(data:User):
    with get_db() as db:
        user = User_data(username=data.username,hashed_password = pwd_context.hash(data.password),disabled = False)
        db.add(user)
        db.commit()

#get user data for authentication
def get_all_users()->dict:
    with get_db() as db:
        res = db.exec(
            "SELECT * FROM user_data;"
        ).fetchall()
        return res