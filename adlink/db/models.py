from .schemas import *

class User_data(SQLModel,table=True): #storing user info in db
    Adhaar : str= Field(primary_key=True)
    username:str
    hashed_password: str 
    disabled: bool

class Bank(SQLModel,table=True): #storing organisation info in db
    ifsc:str= Field(primary_key=True)
    bank_Name:str
    password:str

class agency_data(SQLModel,table=True): #storing organisation info in db
    agency_id:str = Field(primary_key=True)
    agency_Name:str
    password:str

class user_req_bank(SQLModel,table=True):  #user requesting bank (relationship table)
    reqid:str = Field(primary_key=True)
    ifsc:str = Field(foreign_key = True)
    adhaar:str = Field(foreign_key = True)
    custid:str
    status:str

class user_req_agency(SQLModel,table=True): #user requesting any agency (relationship table)
    reqid:str = Field(primary_key=True)
    agencyid:str = Field(foreign_key = True)
    adhaar:str = Field(foreign_key = True)
    custid:str
    status:str