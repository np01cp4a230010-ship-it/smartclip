from fastapi import APIRouter, HTTPException
import os
import requests
from app.store import Store

router = APIRouter(prefix="/youtube", tags=["youtube"])
STORE = Store('data/channels.json')

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
TOKEN_URL = 'https://oauth2.googleapis.com/token'

@router.get('/refresh')
def refresh(channel_id: str):
    """Refresh access token for a connected channel using stored refresh token."""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth client not configured")
    ch = STORE.get_channel(channel_id)
    if not ch:
        raise HTTPException(status_code=404, detail='Channel not found')
    tr = ch.get('token_response') or {}
    refresh_token = tr.get('refresh_token') or ch.get('refresh_token')
    if not refresh_token:
        raise HTTPException(status_code=400, detail='No refresh token available for this channel')
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    resp = requests.post(TOKEN_URL, data=data, timeout=30)
    if not resp.ok:
        raise HTTPException(status_code=502, detail='Token refresh failed')
    token_resp = resp.json()
    # Ensure refresh_token preserved if provider doesn't return a new one
    if 'refresh_token' not in token_resp:
        token_resp['refresh_token'] = refresh_token
    STORE.update_channel_tokens(channel_id, token_resp)
    # Return limited token info (do not return refresh_token)
    masked = dict(token_resp)
    if 'refresh_token' in masked:
        masked['refresh_token'] = 'REDACTED'
    return { 'status': 'refreshed', 'token_response': masked }
