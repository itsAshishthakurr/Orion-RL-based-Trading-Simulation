# 🚀 Orion Trading Simulation

A **multi-agent reinforcement learning environment** for stock trading, built with realistic market mechanics, financial constraints, and evaluation metrics.

> This is not a trading bot.
> This is a **training ground** where agents learn to make decisions under pressure.

---

# 🧠 Why This Exists

Most “trading environments” are either:

* too simple (no fees, no penalties)
* or too complex (not usable for RL)

This environment sits in the middle:

✔ Realistic enough to matter
✔ Simple enough to train agents
✔ Structured enough to evaluate performance

---

# ⚙️ Core Design

The system follows a clean RL loop:

```
Agent → Environment → Market → Reward → Grader → Score
```

---

# 🧩 Environment Overview

The environment is implemented in
`openenv/server/environment.py` 

### State (Observation)

* `price`
* `balance`
* `holdings`
* `step_count`
* `difficulty`
* `trend`

### Actions

* `BUY`
* `SELL`
* `HOLD`

---

# 📊 Market Simulation

Implemented in `core/market.py` 

| Difficulty | Behavior                    |
| ---------- | --------------------------- |
| Easy       | Upward trend                |
| Medium     | Volatile                    |
| Hard       | Sideways (noisy, punishing) |

---

# 💰 Realistic Trading Constraints

Each difficulty introduces real-world friction:

| Feature      | Easy | Medium     | Hard                 |
| ------------ | ---- | ---------- | -------------------- |
| Brokerage    | %    | % + min ₹2 | same                 |
| Tax          | None | 10% profit | STCG 20%, LTCG 12.5% |
| DP Charges   | No   | No         | Yes                  |
| Max Holdings | 20   | 10         | 5                    |

👉 This prevents unrealistic strategies like infinite buying.

---

# 🎯 Reward Design (Key Strength)

Reward is **not random** and not flat.

It combines:

### 1. Portfolio Change

* Loss → low reward
* Profit → high reward

### 2. Action Validity

* Invalid actions → 0.0

### 3. Behavioral Signals

* HOLD punished when useless
* Trend-aligned actions rewarded

### 4. Profit Awareness (Critical)

```python
if profit > 0:
    reward += 0.1
else:
    reward -= 0.1
```

👉 This ensures:

> Agents are rewarded for actually making money, not just reacting to price.

---

# 🏆 Evaluation System

Grader implemented in `core/grader.py` 

### Final Score =

```
0.75 × Profit
+ 0.15 × Consistency
+ 0.10 × Risk Control
```

### What this means:

* Profit matters most
* Stable performance matters
* Bad behavior is penalized

---

# 🤖 Agents

Located in `agents/`

| Agent    | Behavior          |
| -------- | ----------------- |
| Random   | Baseline noise    |
| Safe     | Conservative      |
| Smart    | Trend-following   |
| Learning | Epsilon-greedy RL |

Example (Smart Agent): 

👉 Designed to show **performance differentiation**, not perfection.

---

# 🏃 Simulation

Run full evaluation:

```bash
python main.py --difficulty easy
```

This uses:

* `SimulationRunner` 
* `Leaderboard` 

Outputs:

* ranked agents
* profit, fees, tax
* step-by-step logs

---

# 🌐 API (OpenEnv Compatible)

Defined in:

* `openenv/server/app.py` 
* `openenv.yaml` 

### Endpoints

| Endpoint | Description       |
| -------- | ----------------- |
| `/reset` | Start new episode |
| `/step`  | Take action       |
| `/state` | Current state     |
| `/stats` | Final results     |
| `/tasks` | Task definitions  |

---

# ⚡ Run Locally

## 1. Install

```bash
pip install -r requirements.txt
```

## 2. Start API

```bash
uvicorn openenv.server.app:app --host 0.0.0.0 --port 7860
```

## 3. Run Simulation

```bash
python main.py --difficulty easy
```

## 4. Run Inference

```bash
python inference.py
```

---

# 📦 Project Structure

```
openenv/
  server/
    app.py
    environment.py

core/
  market.py
  grader.py

agents/
  random_agent.py
  safe_agent.py
  smart_agent.py
  learning_agent.py

simulation/
  runner.py
  leaderboard.py

inference.py
main.py
client.py
openenv.yaml
```

---

# 🧠 What Makes This Strong

✔ Reward aligned with **profit, not noise**
✔ Difficulty scaling actually changes behavior
✔ Multiple agents for comparison
✔ Clean API for external evaluation
✔ Realistic constraints (fees, taxes, limits)

---

# ⚠️ Limitations (Honest Section)

* Not a real market model
* No order book / slippage
* Learning agent is simple (not deep RL)

👉 This is a **training environment**, not a production system.

---

# 🎯 Goal

To create a **balanced RL environment** where:

* Agents must make meaningful decisions
* Passive strategies fail
* Risk, cost, and timing all matter

---

# 🧨 Final Thought

This environment is designed to answer one question:

> Can an agent make **good decisions under realistic constraints**, not just chase price?

---

## 🔚
