import random


class LearningAgent:
    def __init__(self):
        self.steps = 0
        self.epsilon = 1.0
        self.epsilon_decay = 0.95
        self.epsilon_min = 0.1
        self.last_reward = 0
        self.last_action = None
        self.good_actions = {"BUY": 0, "SELL": 0, "HOLD": 0}

    def select_action(self, observation):
        price = observation["price"]
        holdings = observation["holdings"]
        balance = observation["balance"]
        step_count = observation["step_count"]

        trend = observation.get("trend", 0)

        self.steps += 1
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        # force exit near end
        if step_count >= 40 and holdings > 0:
            return "SELL"

        # exploration
        if random.random() < self.epsilon:
            action = random.choice(["BUY", "SELL", "HOLD"])

            if action == "SELL" and holdings == 0:
                return "HOLD"
            if action == "BUY" and balance < price:
                return "HOLD"

            return action

        # exploitation
        if holdings == 0:
            if trend > 0:
                if balance < price * 1.02:
                    return "HOLD"
                return "BUY"
            return "HOLD"

        if trend < 0:
            if holdings == 0:
                return "HOLD"
            return "SELL"

        return "HOLD"

    def update_reward(self, action, reward):
        self.good_actions[action] += reward
        self.last_reward = reward
        self.last_action = action

    def reset(self):
        self.steps = 0
        self.epsilon = 1.0
        self.last_reward = 0
        self.last_action = None
        self.good_actions = {"BUY": 0, "SELL": 0, "HOLD": 0}