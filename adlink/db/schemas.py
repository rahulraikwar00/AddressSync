from typing import Optional,Union
import datetime
from sqlmodel import Field, SQLModel

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    username: Union[str, None] = None

class User(SQLModel): #model for User registeration
    username: str
    password:str 
    confirmpass: str
    disabled: Union[bool, None] = None

class Org(SQLModel): #model for organisation registeration
    orgName:str
    orgid:str
    password:str
    cnfpass:str

class user_req_form(SQLModel): 
    user_aadhar:str
    orgid:str
    custid:str