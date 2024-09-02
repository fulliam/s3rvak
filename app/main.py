from fastapi import FastAPI
from app.api.websocket import router as websocket_router
from app.api.auth import router as auth_router

app = FastAPI()

app.include_router(websocket_router)
app.include_router(auth_router)
