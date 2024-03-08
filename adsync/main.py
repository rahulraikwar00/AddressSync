# main.py
from fastapi import FastAPI
from fastapi.responses import FileResponse
from routers import agencies, users, requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
async def read_root():
    return FileResponse('static/home.html')

app.include_router(requests.router, prefix='/requests', tags=["Requests"])
app.include_router(agencies.router, prefix="/agency", tags=["Agencies"])
app.include_router(users.router, prefix="/users", tags=["Users"])

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
