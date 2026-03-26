# # main.py
# from fastapi import FastAPI
# from fastapi.responses import FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# from routers import users, agencies, requests
# from core.database import engine, Base

# # Create tables
# Base.metadata.create_all(bind=engine)

# app = FastAPI(title="Address Sync Service")

# # CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Routes
# app.include_router(users.router)
# app.include_router(agencies.router)
# app.include_router(requests.router)

# # @app.get("/")
# # def root():
# #     return {"message": "Address Sync API is running"}


# @app.get("/", include_in_schema=False)
# async def read_root():
#     return FileResponse('static/home.html')


# @app.get("/health")
# def health():
#     return {"status": "healthy"}


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import users, agencies, requests
from core.database import engine, Base
from core.config import settings
import os

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(users.router)
app.include_router(agencies.router)
app.include_router(requests.router)


@app.get("/")
async def root():
    """Serve the main HTML page"""
    if os.path.exists("static/home.html"):
        return FileResponse('static/home.html')
    return {"message": "Address Sync API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": settings.APP_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
