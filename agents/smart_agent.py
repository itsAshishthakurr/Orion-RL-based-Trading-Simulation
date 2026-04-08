class SmartAgent:
    def __init__(self):
        self.previous_price = None
        self.buy_count = 0

    def select_action(self, observation):
        price = observation["price"]
        holdings = observation["holdings"]
        balance = observation["balance"]
        step_count = observation["step_count"]

        trend = observation.get("trend", 0)

        if step_count >= 40:
            if holdings > 0:
                return "SELL"
            return "HOLD"

        # prevent overbuying
        if holdings >= 5:
            return "SELL" if trend < 0 else "HOLD"

        if trend > 0:
            if balance < price * 1.02:
                return "HOLD"
            return "BUY"

        if trend < 0:
            if holdings == 0:
                return "HOLD"
            return "SELL"

        return "HOLD"

    def reset(self):
        self.previous_price = None
        self.buy_count = 0