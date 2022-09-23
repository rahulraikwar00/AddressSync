from http import server
import re
from urllib import request
from xml.sax import default_parser_list
from fastapi import FastAPI, Depends, HTTPException, status

# import local database file
from db.sendsms import *
from db.database import *
from db.crud import *
from db.models import *
from db.schemas import *
from auth.user import *

# from auth.user import *
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext


# add prefix to all routes
app = FastAPI(
    title="Adlink API",
    description="Adlink API",
    version="0.0.1",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# add prefix to all endpoints
prefix = ""


@app.on_event("startup")
async def createDb():
    cr_db()


# *****************  Admin  *****************


@app.get(prefix + "/get_data_of_agencies", tags=["Admin"])
def data():
    """_summary_: Get data of agencies

    Returns:
        _type_: _description_
    """
    return get_all_agencies()


# *****************  Agencies  *****************


@app.post(prefix + "/register", tags=["Agencies"])
def reg(form_data: agency = Depends()):
    if form_data.cnfpass == form_data.password:
        register_users(form_data)
        return "data uploaded"
    else:
        return "wrong confirm pass"


@app.get(prefix + "/get_request", tags=["Agencies", "User"])
def disreq():
    return getreq()


@app.get(prefix + "/ag_response", tags=["Agencies"])
def agresp(data: response_form = Depends()):
    req = ag_res(data)
    if req:
        req = req[0]
        name = get_name(req.agencyid)
        if req.status == "1":
            send_sms(
                f"Dear Applicant, your request to update your address has been approved by '{name}'. Request details: Request id :'{req.reqid}', Agency id : '{req.agencyid}' ,Account number of customer id : '{req.custid}', Status : APPROVED"
            )
        else:
            send_sms(
                f"Dear Applicant, your request to update your address has been declined by '{name}'. Request details: Request id :'{req.reqid}', Agency id : '{req.agencyid}' ,Account number of customer id : '{req.custid}', Status : DECLINED"
            )
    else:
        return "your request was declined by the agency"
    return "response has been sent to the applicant"



# *****************  User  *****************

@app.get(prefix + "/send_update_request", tags=["User"])
def reqUp(form_data: user_req_agency_form = Depends(oauth2_scheme)):
    req = syncUp(form_data)
    send_sms(
        f" Dear Applicant , we have received your request to update your address and will be sending you a notification as soon as there is any update from the agency. Request details: Request id :'{req.reqid}', Agency id : '{req.agencyid}' ,Account number of customer id : '{req.custid}', Status : '{req.status}'"
    )
    return "request has been initiated"


# @app.get("/data")
# def get_u(current_user: User_data = Depends(get_current_active_user)):
#     users_db = get_all_users()
#     res = {}
#     for i in users_db:
#         res[i['username']] = i
#     print("get data: ", res)
#     return res


@app.post(prefix + "/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        users_db = get_db()
        user = authenticate_user(users_db, form_data.username, form_data.password)
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
    finally:
        return access_token


# @app.get("/users/me/")
# async def read_users_me(current_user: User_data = Depends(get_current_active_user)):
#     return current_user


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# def fake_hash_password(password: str):
#     return "fakehashed" + password

# class User(SQLModel):  #creating a sqlmodel will give user a form to enter username and password
#     username: str
#     email: Union[str,None]
#     full_name: Union[str,None]
#     disabled: Union[bool,None]


# class UserInDB(User):
#     hashed_password: str


# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)


# def fake_decode_token(token):
#     # This doesn't provide any security at all
#     # Check the next version
#     user = get_user(fake_users_db, token)
#     return user


# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     user = fake_decode_token(token)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return user


# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


# @app.post("/token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user_dict = fake_users_db.get(form_data.username)
#     if not user_dict:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     user = UserInDB(**user_dict)
#     hashed_password = fake_hash_password(form_data.password)
#     if not hashed_password == user.hashed_password:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     return {"access_token": user.username, "token_type": "bearer"}


# @app.get("/users/me")
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user


# class me:
#     nm=''
#     def __init__(self):
#         self.nm = 'pooja'

# @app.get("/items/user")
# async def get_current_user(token: str = Depends(oauth2_scheme)):# oauth2_scheme is called and converted to string by depends
#     user = fake_decode_token(token)
#     return user

# @app.get("/items/me")
# async def read_items_me(token :me= Depends()): #depends without any parameter returns the default request body of type
#     # 'me' that is a user defined class whose values are initialized by the constructor. In case no constructor
#     #is provided empty dict will be returned
#     # current output :
#     # {nm:pooja}
#     return token
# @app.get("/items/user")
# async def read_items_user(token :User= Depends()): #depends without any parameter returns the default request body of type
#     # 'me' that is a user defined class whose values are initialized by the constructor. In case no constructor
#     #is provided empty dict will be returned
#     # current output :
#     # {nm:pooja}
#     return token
