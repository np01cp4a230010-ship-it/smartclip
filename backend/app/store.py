import json
import os
from app.crypto import encrypt, decrypt

class Store:
    def __init__(self, path='data/channels.json'):
        self.path = os.path.abspath(path)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump({'channels': {}, 'notifications': []}, f, indent=2)

    def _read(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write(self, data):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def save_channel(self, channel_id, data):
        d = self._read()
        # Normalize and encrypt any refresh_token in token_response or top-level
        data_copy = dict(data)
        tr = data_copy.get('token_response')
        if isinstance(tr, dict) and 'refresh_token' in tr and tr['refresh_token']:
            try:
                tr_enc = dict(tr)
                tr_enc['refresh_token'] = encrypt(tr_enc['refresh_token'])
                data_copy['token_response'] = tr_enc
            except Exception:
                # fallback to storing as-is
                pass
        elif 'refresh_token' in data_copy and data_copy['refresh_token']:
            try:
                data_copy['refresh_token'] = encrypt(data_copy['refresh_token'])
            except Exception:
                pass
        d['channels'][channel_id] = data_copy
        self._write(d)

    def get_channel(self, channel_id):
        d = self._read()
        ch = d['channels'].get(channel_id)
        if not ch:
            return None
        # Decrypt refresh_token in token_response if present
        tr = ch.get('token_response')
        if isinstance(tr, dict) and 'refresh_token' in tr and tr['refresh_token']:
            try:
                tr_dec = dict(tr)
                tr_dec['refresh_token'] = decrypt(tr_dec['refresh_token'])
                ch['token_response'] = tr_dec
            except Exception:
                pass
        elif 'refresh_token' in ch and ch['refresh_token']:
            try:
                ch['refresh_token'] = decrypt(ch['refresh_token'])
            except Exception:
                pass
        return ch

    def update_channel_tokens(self, channel_id, token_resp):
        d = self._read()
        ch = d['channels'].get(channel_id, {})
        tr = dict(token_resp)
        if 'refresh_token' in tr and tr['refresh_token']:
            try:
                tr['refresh_token'] = encrypt(tr['refresh_token'])
            except Exception:
                pass
        # merge into channel
        ch['token_response'] = tr
        d['channels'][channel_id] = ch
        self._write(d)

    def append_notification(self, payload):
        d = self._read()
        d['notifications'].append({ 'payload': payload })
        self._write(d)
