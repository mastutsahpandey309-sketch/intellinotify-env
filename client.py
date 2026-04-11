"""IntelliNotify environment HTTP client."""
from typing import Dict, Optional
import httpx


class IntelliNotifyEnv:
    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=30.0)

    def reset(self, task_id: Optional[str] = None):
        body = {"task_id": task_id} if task_id else {}
        r = self._client.post(f"{self.base_url}/reset", json=body)
        r.raise_for_status()
        return r.json()

    def step(self, action: Dict):
        r = self._client.post(f"{self.base_url}/step", json=action)
        r.raise_for_status()
        return r.json()

    def state(self):
        r = self._client.get(f"{self.base_url}/state")
        r.raise_for_status()
        return r.json()

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
