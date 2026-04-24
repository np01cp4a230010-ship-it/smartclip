import json
import os

class Store:
    def __init__(self, path='data/channels.json'):
        # path is relative to repo root; ensure directory exists
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
        d['channels'][channel_id] = data
        self._write(d)

    def append_notification(self, payload):
        d = self._read()
        d['notifications'].append({ 'payload': payload })
        self._write(d)
