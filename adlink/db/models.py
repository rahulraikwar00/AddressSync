
from .schemas import *
import uuid
# class User_data(SQLModel,table=True): #storing user info in db
#     Adhaar : str= Field(primary_key=True)
#     username:str
#     hashed_password: str 
#     disabled: bool

class agency_data(SQLModel,table=True): #storing organisation info in db
    agency_id:str = Field(default =uuid.uuid1() ,primary_key=True)
    ag_uniq_id:str
    agency_Name:str
    hashedpass:str

class user_req_agency(SQLModel,table=True): #user requesting any agency 
    reqid:str = Field(default = uuid.uuid1(),primary_key=True)
    agencyid:str = Field(foreign_key = "agency_data.agency_id")
    adhaar:str 
    custid:str
    fetched_data:str = Field(default = "new address")
    status:int = Field(default = 0)

