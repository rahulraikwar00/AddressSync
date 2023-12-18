# main.py
from fastapi import FastAPI
from routers import agencies, users, requests

app = FastAPI()
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}
app.include_router(requests.router, prefix='/requests', tags=["requests"])
app.include_router(agencies.router, prefix="/agency", tags=["agencies"])
app.include_router(users.router, prefix="/users", tags=["users"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
