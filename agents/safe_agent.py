import random


class SafeAgent:
    def __init__(self):
        self.last_buy_price = None

    def select_action(self, observation):
        price = observation["price"]
        balance = observation["balance"]
        holdings = observation["holdings"]
        trend = observation.get("trend", 0)

        if holdings == 0:
            # buy occasionally in uptrend
            if trend > 0:
                if balance < price * 1.02:
                    return "HOLD"
                return "BUY"
            return "HOLD"

        # sell if small profit or trend reverses
        if trend < 0:
            if holdings == 0:
                return "HOLD"
            return "SELL"

        if self.last_buy_price and price >= self.last_buy_price + 1:
            self.last_buy_price = None
            return "SELL"

        return "HOLD"