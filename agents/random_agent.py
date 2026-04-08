import random


class RandomAgent:
    def select_action(self, observation):
        price = observation["price"]
        balance = observation["balance"]
        holdings = observation["holdings"]
        actions = ["BUY", "SELL", "HOLD"]
        action = random.choice(actions)
        if action == "BUY" and balance < price * 1.02:
            return "HOLD"
        if action == "SELL" and holdings == 0:
            return "HOLD"
        return action
