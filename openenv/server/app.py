import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from openenv.server.environment import TradingEnvironment


app = FastAPI(title="Orion Trading Simulation", version="1.0.0")

env = TradingEnvironment(difficulty="easy")


class ResetRequest(BaseModel):
    difficulty: str = "easy"


class StepRequest(BaseModel):
    action: str


@app.get("/health")
def health():
    return {"status": "healthy", "environment": "Orion-Trading-Simulation", "version": "1.0.0"}


@app.get("/tasks")
def tasks():
    return [
        {
            "name": "easy-trend-trading",
            "description": "Trade on a trending market over 50 steps. Brokerage fees apply. Rewards are normalised to [0.0, 1.0].",
            "difficulty": "easy",
            "max_steps": 50,
            "market_type": "trend",
            "reward_range": [0.0, 1.0],
        },
        {
            "name": "medium-volatile-trading",
            "description": "Trade on a volatile market over 75 steps. Standard brokerage fees plus 10% tax on profits apply.",
            "difficulty": "medium",
            "max_steps": 75,
            "market_type": "volatile",
            "reward_range": [0.0, 1.0],
        },
        {
            "name": "hard-sideways-trading",
            "description": (
                "Trade on a sideways market over 100 steps. "
                "STCG at 20% and LTCG at 12.5% apply on gains; "
                "a Depository Participant (DP) charge of Rs. 15 is levied per sell transaction."
            ),
            "difficulty": "hard",
            "max_steps": 100,
            "market_type": "sideways",
            "reward_range": [0.0, 1.0],
        },
    ]


@app.post("/reset")
def reset(request: ResetRequest):
    global env
    if request.difficulty not in ("easy", "medium", "hard"):
        raise HTTPException(status_code=400, detail="difficulty must be easy, medium, or hard")
    env = TradingEnvironment(difficulty=request.difficulty)
    observation = env.reset()
    return {
        "observation": observation,
        "episode_id": env.episode_id,
        "difficulty": env.difficulty,
        "max_steps": env.max_steps,
    }


@app.post("/step")
def step(request: StepRequest):
    global env
    if request.action.upper() not in ("BUY", "SELL", "HOLD"):
        raise HTTPException(status_code=400, detail="action must be BUY, SELL, or HOLD")
    observation, reward, done = env.step(request.action)
    return {"observation": observation, "reward": reward, "done": done}


@app.get("/state")
def state():
    return {
        "episode_id": env.episode_id,
        "step_count": env.step_count,
        "current_price": env.current_price,
        "balance": env.current_balance,
        "holdings": env.holdings,
        "difficulty": env.difficulty,
        "total_fees_paid": env.total_fees_paid,
        "total_tax_paid": env.total_tax_paid,
        "done": env.done,
    }


@app.get("/stats")
def stats():
    return env.get_final_stats()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
