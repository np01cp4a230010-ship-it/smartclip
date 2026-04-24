from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="SmartClip API")

@app.get("/")
async def read_root():
    return {"service": "smartclip", "status": "ok"}

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

# Placeholder endpoint for YouTube connect (OAuth)
@app.get("/youtube/connect")
async def youtube_connect():
    return {"message": "TODO: implement Google OAuth flow for YouTube channel connect"}
