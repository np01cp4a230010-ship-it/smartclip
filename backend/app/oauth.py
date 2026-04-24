from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, PlainTextResponse, JSONResponse
import os
import httpx
import urllib.parse
from app.store import Store

router = APIRouter(prefix="/youtube", tags=["youtube"])
STORE = Store('data/channels.json')

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
SCOPES = "https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.upload"

@router.get('/connect')
async def connect(channel_url: str = None):
    """Redirects user to Google's OAuth consent screen."""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth client not configured")
    redirect_uri = f"{BASE_URL}/youtube/callback"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": SCOPES,
        "redirect_uri": redirect_uri,
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return RedirectResponse(auth_url)

@router.get('/callback')
async def callback(request: Request):
    code = request.query_params.get('code')
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    token_url = 'https://oauth2.googleapis.com/token'
    redirect_uri = f"{BASE_URL}/youtube/callback"
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=data, timeout=30)
        resp.raise_for_status()
        token_resp = resp.json()
        access_token = token_resp.get('access_token')
        refresh_token = token_resp.get('refresh_token')
        # fetch channel id
        headers = { 'Authorization': f"Bearer {access_token}" }
        r = await client.get('https://www.googleapis.com/youtube/v3/channels?part=id&mine=true', headers=headers, timeout=30)
        r.raise_for_status()
        items = r.json().get('items', [])
        if not items:
            raise HTTPException(status_code=400, detail='No YouTube channel found for account')
        channel_id = items[0]['id']
        STORE.save_channel(channel_id, { 'access_token': access_token, 'refresh_token': refresh_token, 'token_response': token_resp })
    return JSONResponse({ 'status': 'connected', 'channel_id': channel_id })

@router.get('/webhook')
async def webhook_verify(request: Request):
    # PubSubHubbub verification - respond with hub.challenge
    challenge = request.query_params.get('hub.challenge') or request.query_params.get('challenge')
    if challenge:
        return PlainTextResponse(challenge)
    return PlainTextResponse('ok')

@router.post('/webhook')
async def webhook_receive(request: Request):
    body = await request.body()
    try:
        STORE.append_notification(body.decode('utf-8'))
    except Exception as e:
        return JSONResponse({'status': 'error', 'detail': str(e)}, status_code=500)
    return PlainTextResponse('received')
