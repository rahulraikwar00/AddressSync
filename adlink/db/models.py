#user table for api authentication
from .schemas import *

class User_data(SQLModel,table=True): #model for storing user info in db
    username : str= Field(primary_key=True)
    hashed_password: str 
    disabled: bool

class Org_data(SQLModel,table=True): #model for storing organisation info in db
    orgid:str= Field(primary_key=True)
    orgName:str
    password:str

class user_req(user_req_form,table=True): #store user req info
    id:Optional[int] = Field(primary_key=True)