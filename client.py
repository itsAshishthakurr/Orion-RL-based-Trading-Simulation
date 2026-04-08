import requests
from typing import Optional


class TradingEnvClient:
    def __init__(self, base_url="http://localhost:8000", difficulty="easy"):
        self.base_url = base_url.rstrip("/")
        self.difficulty = difficulty

    def reset(self, difficulty=None):
        if difficulty is None:
            difficulty = self.difficulty
        response = requests.post(f"{self.base_url}/reset", json={"difficulty": difficulty})
        return response.json()

    def step(self, action):
        response = requests.post(f"{self.base_url}/step", json={"action": action})
        return response.json()

    def state(self):
        response = requests.get(f"{self.base_url}/state")
        return response.json()

    def health(self):
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def stats(self):
        response = requests.get(f"{self.base_url}/stats")
        return response.json()
