
from .schemas import *

# class User_data(SQLModel,table=True): #storing user info in db
#     Adhaar : str= Field(primary_key=True)
#     username:str
#     hashed_password: str 
#     disabled: bool

class agency_data(SQLModel,table=True): #storing organisation info in db
    agency_id:str = Field(primary_key=True)
    ag_uniq_id:str
    agency_Name:str

class ag_login_det(SQLModel,table=True): #login credentials of agencies
    agency_id:str = Field(foreign_key=True) 
    hashedpass:str

class user_req_agency(SQLModel,table=True): #user requesting any agency 
    reqid:str = Field(primary_key=True)
    agencyid:str = Field(foreign_key = True)
    adhaar:str = Field(foreign_key = True)
    custid:str
    fetched_data:str
    status:str