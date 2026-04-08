import uuid
from core.market import Market


class TradingEnvironment:
    def __init__(self, difficulty="easy"):
        self.difficulty = difficulty
        self.initial_balance = 10000

        if difficulty == "easy":
            self.market_type = "trend"
            self.max_steps = 50
            self.min_brokerage = 0
            self.brokerage_rate = 0.0003
            self.tax_rate = 0
            self.max_holdings = 20
            self.dp_charge = 0
            self.use_stcg_ltcg = False
        elif difficulty == "medium":
            self.market_type = "volatile"
            self.max_steps = 75
            self.min_brokerage = 2
            self.brokerage_rate = 0.0003
            self.tax_rate = 0.10
            self.max_holdings = 8
            self.dp_charge = 0
            self.use_stcg_ltcg = False
        elif difficulty == "hard":
            self.market_type = "sideways"
            self.max_steps = 100
            self.min_brokerage = 2
            self.brokerage_rate = 0.0003
            self.tax_rate = 0
            self.max_holdings = 5
            self.dp_charge = 20
            self.use_stcg_ltcg = True
            self.stcg_rate = 0.20
            self.ltcg_rate = 0.125
            self.stcg_threshold = 50

        self.current_balance = 0
        self.holdings = 0
        self.current_price = 0
        self.step_count = 0
        self.done = False
        self.market = None
        self.episode_id = None
        self.total_fees_paid = 0
        self.total_tax_paid = 0
        self.buy_step_log = []
        self.average_buy_price = 0
        self.last_action_invalid = False  # set each step; readable by runner

    def reset(self):
        self.current_balance = self.initial_balance
        self.holdings = 0
        self.step_count = 0
        self.done = False
        self.total_fees_paid = 0
        self.total_tax_paid = 0
        self.buy_step_log = []
        self.average_buy_price = 0
        self.last_action_invalid = False
        self.market = Market(market_type=self.market_type, total_steps=self.max_steps)
        self.current_price = self.market.current_price
        self.prev_price = self.current_price
        self.episode_id = str(uuid.uuid4())
        return self._get_observation()

    def _get_observation(self):
        trend = self.current_price - self.prev_price if hasattr(self, "prev_price") else 0
        self.prev_price = self.current_price
        return {
            "price": round(self.current_price, 2),
            "balance": round(self.current_balance, 2),
            "holdings": round(self.holdings, 2),
            "step_count": round(self.step_count, 2),
            "difficulty": self.difficulty,
            "trend": round(trend, 2),
        }

    def _calculate_brokerage(self, price):
        fee = price * self.brokerage_rate
        return round(max(fee, self.min_brokerage), 2)

    def _calculate_tax_on_sell(self, profit_per_share):
        if profit_per_share <= 0:
            return 0

        if self.use_stcg_ltcg:
            steps_held = self.step_count - self.buy_step_log[0]
            if steps_held < self.stcg_threshold:
                rate = self.stcg_rate
            else:
                rate = self.ltcg_rate
            return round(profit_per_share * rate, 2)

        if self.tax_rate > 0:
            return round(profit_per_share * self.tax_rate, 2)

        return 0

    def _normalize_reward(self, portfolio_change, is_invalid_action):
        change_pct = (portfolio_change / self.initial_balance) * 100
        # INVALID = worst
        if is_invalid_action:
            reward = 0.0
        # LOSS ZONES
        elif change_pct < -2:
            reward = 0.0
        elif change_pct < 0:
            reward = 0.25
        # NEUTRAL
        elif change_pct < 1:
            reward = 0.50
        # PROFIT ZONES
        elif change_pct < 2:
            reward = 0.60
        elif change_pct < 5:
            reward = 0.75
        elif change_pct < 7:
            reward = 0.90
        else:
            reward = 1.00
        return round(max(0.0, min(1.0, reward)), 2)

    def step(self, action):
        if self.done:
            self.last_action_invalid = False
            return self._get_observation(), 0.50, True

        prev_portfolio = self.current_balance + (self.holdings * self.current_price)
        is_invalid = False
        action = str(action).upper()

        if action == "BUY":
            brokerage = self._calculate_brokerage(self.current_price)
            total_cost = self.current_price + brokerage
            if self.current_balance >= total_cost and self.holdings < self.max_holdings:
                self.current_balance -= total_cost
                self.holdings += 1
                self.total_fees_paid += brokerage
                self.buy_step_log.append(self.step_count)
                self.average_buy_price = (
                    (self.average_buy_price * (self.holdings - 1)) + self.current_price
                ) / self.holdings
            else:
                is_invalid = True

        elif action == "SELL":
            if self.holdings > 0:
                brokerage = self._calculate_brokerage(self.current_price)
                profit_per_share = self.current_price - self.average_buy_price
                tax = self._calculate_tax_on_sell(profit_per_share)
                total_gain = self.current_price - brokerage - tax - self.dp_charge
                self.current_balance += total_gain
                self.holdings -= 1
                self.total_fees_paid += brokerage + self.dp_charge
                self.total_tax_paid += tax
                self.buy_step_log.pop(0)
                if self.holdings == 0:
                    self.average_buy_price = 0
            else:
                is_invalid = True

        elif action == "HOLD":
            pass

        else:
            is_invalid = True

        if self.current_balance < 0:
            self.current_balance = 0
        if self.holdings < 0:
            self.holdings = 0

        self.current_price = self.market.next_price()
        self.step_count += 1

        new_portfolio = self.current_balance + (self.holdings * self.current_price)
        portfolio_change = new_portfolio - prev_portfolio
        reward = self._normalize_reward(portfolio_change, is_invalid)

        # discourage useless HOLD
        if action == "HOLD":
            if self.holdings > 0:
                if self.current_price > self.prev_price:
                    reward = 0.60   # reward holding profit
                else:
                    reward = 0.05   # punish holding loss HARD
            else:
                reward = 0.10       # idle penalty

        # directional reward boost for correct trend-aligned actions
        trend = self.current_price - self.prev_price
        if action == "BUY" and trend > 0:
            reward = min(1.0, reward + 0.1)
        if action == "SELL" and trend < 0:
            reward = min(1.0, reward + 0.1)

        self.last_action_invalid = is_invalid  # expose for runner

        # --- PROFIT AWARENESS FIX ---
        portfolio_value = self.current_balance + (self.holdings * self.current_price)
        profit = portfolio_value - self.initial_balance

        if profit > 0:
            reward += 0.05
        else:
            reward -= 0.05

        # clamp
        reward = max(0.0, min(1.0, reward))

        if self.step_count >= self.max_steps:
            self.done = True

        self.prev_price = self.current_price
        self.prev_net_worth = portfolio_value

        return self._get_observation(), round(reward, 2), self.done

    def get_final_stats(self):
        final_portfolio = self.current_balance + (self.holdings * self.current_price)
        net_profit = final_portfolio - self.initial_balance
        return {
            "final_balance": round(self.current_balance, 2),
            "net_profit": round(net_profit, 2),
            "total_fees_paid": round(self.total_fees_paid, 2),
            "total_tax_paid": round(self.total_tax_paid, 2),
            "difficulty": self.difficulty,
        }