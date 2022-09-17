from ast import main
from re import A
from typing import Union
from urllib import response
from fastapi import FastAPI,Depends,HTTPException,status
# import local database file
from db.database import *
from db.crud import *
from db.models import *
from db.schemas import *
from auth.user import *
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

app = FastAPI()

@app.on_event("startup")
async def createDb():
    cr_db()

@app.get("/")
async def create():
    cr_db()
    return {"message":" database created"}

@app.get("/data")
def get_u(current_user: User_data = Depends(get_current_active_user)):
    users_db = get_all_users()
    res = {}
    for i in users_db:
        res[i['username']] = i
    print("get data: ", res)
    return res

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        fake_users_db = get_u()
        user = authenticate_user(fake_users_db, form_data.username, form_data.password)
        # print(user)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username /or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        # create access token
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires 
        )
        

        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        return e
    return access_token

@app.get('/register')
def reg(form_data: User = Depends()):
    if(form_data.confirmpass==form_data.password):
        register_users(form_data)
        return 'data uploaded' 
    else:
        return 'wrong confirm pass'


@app.get("/users/me/")
async def read_users_me(current_user: User_data = Depends(get_current_active_user)):
    return current_user