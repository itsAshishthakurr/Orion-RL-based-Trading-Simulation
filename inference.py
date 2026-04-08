import os
import sys
import requests
import random
from openai import OpenAI

ENV_BASE_URL = os.environ.get("ENV_BASE_URL", "http://localhost:7860")

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN:
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
else:
    client = None

TASKS = [
    {"name": "easy-trend-trading", "difficulty": "easy", "max_steps": 50},
    {"name": "medium-volatile-trading", "difficulty": "medium", "max_steps": 75},
    {"name": "hard-sideways-trading", "difficulty": "hard", "max_steps": 100},
]

SYSTEM_PROMPT = """You are a trading agent.

Choose ONE action: BUY, SELL, or HOLD.

Respond ONLY with BUY, SELL, or HOLD.
"""

def call_env(endpoint, method="GET", payload=None):
    url = f"{ENV_BASE_URL}{endpoint}"
    try:
        if method == "POST":
            resp = requests.post(url, json=payload, timeout=30)
        else:
            resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None

def get_action(observation):
    if client is None:
        return random.choice(["BUY", "SELL", "HOLD"])

    try:
        obs_text = (
            f"price={observation.get('price')} "
            f"balance={observation.get('balance')} "
            f"holdings={observation.get('holdings')} "
            f"step={observation.get('step_count')} "
            f"difficulty={observation.get('difficulty')}"
        )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": obs_text},
            ],
            temperature=0.0,
            max_tokens=5,
        )

        action = response.choices[0].message.content.strip().upper()

        if action not in ("BUY", "SELL", "HOLD"):
            return random.choice(["BUY", "SELL", "HOLD"])

        return action

    except Exception:
        return random.choice(["BUY", "SELL", "HOLD"])

def run_task(task):
    task_name = task["name"]
    difficulty = task["difficulty"]
    max_steps = task["max_steps"]

    print(f"[START] task={task_name} env=orion-trading-simulation model={MODEL_NAME}")
    sys.stdout.flush()

    reset_data = call_env("/reset", method="POST", payload={"difficulty": difficulty})

    if reset_data is None:
        print("[END] success=false steps=0 rewards=")
        return

    observation = reset_data["observation"]
    rewards = []
    step_num = 0
    done = False
    error_msg = None

    while not done and step_num < max_steps:
        action = get_action(observation)

        step_data = call_env("/step", method="POST", payload={"action": action})

        if step_data is None:
            reward = 0.00
            done = True
            error_msg = "env_call_failed"
        else:
            observation = step_data["observation"]
            reward = round(float(step_data.get("reward", 0.0)), 2)
            done = step_data.get("done", False)
            error_msg = None

        rewards.append(reward)
        step_num += 1

        print(
            f"[STEP] step={step_num} action={action} reward={reward:.2f} done={str(done).lower()} error={error_msg if error_msg else 'null'}"
        )
        sys.stdout.flush()

    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    success = error_msg is None

    print(f"[END] success={str(success).lower()} steps={step_num} rewards={rewards_str}")
    sys.stdout.flush()

def main():
    health = call_env("/health") or call_env("/state")

    if health is None:
        print("[END] success=false steps=0 rewards=")
        return

    for task in TASKS:
        run_task(task)

if __name__ == "__main__":
    main()