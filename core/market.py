import random


class Market:
    def __init__(self, initial_price=100, market_type="trend", total_steps=50, difficulty="easy"):
        self.initial_price = initial_price
        self.market_type = market_type
        self.total_steps = total_steps
        self.difficulty = difficulty
        self.price = 100.0
        self.current_price = initial_price
        self.step_count = 0
        self.price_history = [initial_price]

    def next_price(self):
        self.step_count += 1

        if self.difficulty == "easy":
            drift = 0.2
            volatility = 0.8
        elif self.difficulty == "medium":
            drift = 0.0
            volatility = 1.0
        else:  # hard
            drift = 0.0
            volatility = 1.5

        price_change = drift + random.uniform(-volatility, volatility)

        self.price = max(1, self.price + price_change)

        self.current_price = round(self.price, 2)
        self.price_history.append(self.current_price)
        return self.current_price

    def reset(self):
        self.current_price = self.initial_price
        self.step_count = 0
        self.price_history = [self.initial_price]