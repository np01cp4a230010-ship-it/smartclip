from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.oauth import router as youtube_router

app = FastAPI(title="SmartClip API")

app.include_router(youtube_router)

@app.get("/")
async def read_root():
    return {"service": "smartclip", "status": "ok"}

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

