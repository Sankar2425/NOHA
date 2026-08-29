from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from bridge.api.routes import router
from bridge.websocket.manager import websocket_router

app = FastAPI(title="NOHA Runtime")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(websocket_router)

@app.get("/")
async def root():
    return {"status": "NOHA ONLINE"}
