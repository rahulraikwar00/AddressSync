from typing import Optional,Union
import datetime
from sqlmodel import Field, SQLModel

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    username: Union[str, None] = None

class User(SQLModel): #User registeration form
    username: str
    password:str 
    confirmpass: str
    disabled: Union[bool, None] = None

class agency(SQLModel): #organisation registeration form
    agencyName:str
    agency_type:str  #(options : bank or any other agency)
    agencyid:str   #(ifsc if bank else its uniqueid)
    password:str
    cnfpass:str

class user_req_bank_form(SQLModel): 
    Adhaar:str
    ifsc:str
    custid:str

class user_req_agency_form(SQLModel): 
    Adhaar:str
    agencyid:str
    custid:str

