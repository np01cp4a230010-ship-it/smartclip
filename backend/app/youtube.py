# Placeholder for YouTube OAuth helpers
from fastapi import APIRouter

router = APIRouter()

@router.get('/start')
async def start_oauth():
    return {"message": "Start OAuth (placeholder)"}
