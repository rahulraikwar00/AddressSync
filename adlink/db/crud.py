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

def add_ag_login(data:agency_data):
    pass

def register_users(data:agency):
    with get_db() as db:
        ag = agency_data(ag_uniq_id = data.ag_uniq_id,agencyName = data.agencyName)
        db.add(ag)
        add_ag_login(ag)  #function to add login details of agency
        db.commit()

#get user data for authentication
def get_all_users()->dict:
    with get_db() as db:
        res = db.exec(
            "SELECT * FROM users_data;"
        ).fetchall()
        return res