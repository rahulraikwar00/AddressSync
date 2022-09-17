import imp
from .database import *
from .crud import *
from .models import *
from .schemas import *
from sqlmodel import Session, select
import hashlib
import uuid
from features.dropdown import *
from passlib.context import CryptContext
from uuid import uuid1
from fastapi.security import OAuth2PasswordRequestForm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = Session(engine)
    return db

# def add_ag_login(data:agency_data):
#     pass

def register_users(data:agency):
    # return uuid.uuid1()
    with get_db() as db:
        ag = agency_data(agency_id=str(uuid.uuid1()),ag_uniq_id = data.ag_uniq_id,agency_Name = data.agency_Name,hashedpass = pwd_context.hash(data.password))
        db.add(ag)
        # add_ag_login(ag)  #function to add login details of agency
        db.commit()

#get user data for authentication
def get_all_agencies()->dict:
    with get_db() as db:
        res = db.exec(
            "SELECT * FROM agency_data;"
        ).fetchall()
        return res

def getagid(agunid):
    with get_db() as db:
        res = db.exec(
            f"SELECT agency_id FROM agency_data WHERE ag_uniq_id = '{agunid}';"
        ).one()
        return res.agency_id

def syncUp(data:user_req_agency_form):
    with get_db() as db:
        agenid = getagid(data.ag_uniq_id)
        req = user_req_agency(reqid= str(uuid.uuid1()), agencyid = agenid,adhaar = data.Adhaar,custid = data.custid)
        db.add(req)
        db.commit()

def getreq():
    with get_db() as db:
        reqs = db.exec(
            "SELECT * FROM user_req_agency;"
        ).fetchall()
        return reqs


def ag_res(data:response_form):
    with get_db() as db:
        res = db.exec(
            # update user agency set status = * where reqid = *;
            f"UPDATE user_req_agency SET status = '{data.status}' WHERE reqid = '{data.request_id}';"
        )
        db.commit()
        ls = db.exec(f"SELECT * from user_req_agency Where reqid='{data.request_id}';").fetchall()
        if(not len(ls)):
            return "request id not found, please check the request id"
        else:
            return ls
        
