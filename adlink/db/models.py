
from .schemas import *
from sqlalchemy import UniqueConstraint
import uuid
# class User_data(SQLModel,table=True): #storing user info in db
#     Adhaar : str= Field(primary_key=True)
#     username:str
#     hashed_password: str 
#     disabled: bool

class agency_data(SQLModel,table=True): 
    __table_args__ =(UniqueConstraint('ag_uniq_id',name='ag_uniq_id'),)
    agency_id:str = Field(primary_key=True)
    ag_uniq_id:str
    hashedpass:str

class user_req_agency(SQLModel,table=True): #user requesting any agency 
    reqid:str = Field(primary_key=True)
    agencyid:str = Field(foreign_key = "agency_data.agency_id")
    adhaar:str 
    custid:str
    fetched_data:str = Field(default = "new address")
    status:str = Field(default = "0")

