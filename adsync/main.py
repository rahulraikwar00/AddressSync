# main.py
from fastapi import FastAPI
from routers import agencies, users, requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Hello, World! and iam working"}
app.include_router(requests.router, prefix='/requests', tags=["requests"])
app.include_router(agencies.router, prefix="/agency", tags=["agencies"])
app.include_router(users.router, prefix="/users", tags=["users"])

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)