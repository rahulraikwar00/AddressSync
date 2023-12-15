
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from db.sendsms import send_sms
from db.database import cr_db
from db.crud import register_users, syncUp, get_all_agencies, getreq, ag_res, get_name
from db.schemas import agency, user_req_agency_form, response_form
from auth.user import (
    get_u,
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

app = FastAPI(
    title="Adlink API",
    description="This API provides endpoints for registering agencies, updating requests for users, and responding to those requests for agencies.",
    version="0.0.1",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

prefix = ""


@app.on_event("startup")
async def create_db():
    cr_db()


@app.get(prefix + "/get_data_of_agencies", tags=["Admin"])
def get_data_of_agencies():
    """Get data of all agencies."""
    return get_all_agencies()


@app.post(prefix + "/register", tags=["Agencies"])
def register_agency(form_data: agency = Depends()):
    """Register new agency."""
    if form_data.cnfpass == form_data.password:
        register_users(form_data)
        return "data uploaded"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")


@app.get(prefix + "/send_update_request", tags=["User"])
def send_update_request(form_data: user_req_agency_form = Depends()):
    """Send update request for user's address."""
    req = syncUp(form_data)
    try:
        send_sms(f"Dear Applicant, we have received your request to update your address and will be sending you a notification as soon as there is any update from the agency. Request details: Request id: '{req.reqid}', Agency id: '{req.agencyid}', Account number of customer id: '{req.custid}', Status: '{req.status}'")
    except Exception as e:
        return "request has been initiated"


@app.get(prefix + "/get_request", tags=["Agencies", "User"])
def get_request():
    """Get all update requests."""
    return getreq()


@app.get(prefix + "/ag_response", tags=["Agencies"])
def ag_response(data: response_form = Depends()):
    """Respond to user's update request."""
    req = ag_res(data)
    try:
        if req:
            req = req[0]
            name = get_name(req.agencyid)
            if req.status == "1":
                send_sms(f"Dear Applicant, your request to update your address has been approved by '{name}'. Request details: Request id: '{req.reqid}', Agency id: '{req.agencyid}', Account number of customer id: '{req.custid}', Status: APPROVED")
            else:
                send_sms(f"Dear Applicant, your request to update your address has been declined by '{name}'. Request details: Request id: '{req.reqid}', Agency id: '{req.agencyid}', Account number of customer id: '{req.custid}', Status: DECLINED")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Your request was declined by the agency")
    except Exception as e:
        return "response has been sent to the applicant"


@app.post(prefix + "/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Get access token."""
    try:
        fake_users_db = get_u()
        user = authenticate_user(fake_users_db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))