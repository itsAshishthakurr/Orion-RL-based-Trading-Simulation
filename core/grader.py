class Grader:
    def evaluate(self, agent_name, initial_balance, stats):
        net_profit = stats["net_profit"]
        return_percent = round((net_profit / initial_balance) * 100, 2)

        # --- profit_score: smooth continuous score ---
        # Normalizes return_percent over a ±20% window.
        # +20% return  => 1.0,  0% return => 0.5,  -20% return => 0.0
        profit_score = 0.5 + (return_percent / 10.0)
        profit_score = max(0.0, min(1.0, profit_score))

        # --- consistency_score: reward stable positive rewards across steps ---
        step_rewards = stats.get("step_rewards", [])
        if step_rewards:
            above_neutral = sum(1 for r in step_rewards if r > 0.5)
            consistency_score = round(above_neutral / len(step_rewards), 4)
        else:
            consistency_score = 0.5

        # --- risk_score: penalize invalid actions and excessive trading ---
        total_steps = max(len(step_rewards), 1)
        invalid_count = stats.get("invalid_count", 0)
        invalid_ratio = invalid_count / total_steps

        # count trade actions (BUY + SELL) from step log if available
        action_log = stats.get("action_log", [])
        if action_log:
            trade_count = sum(1 for a in action_log if a in ("BUY", "SELL"))
            trade_ratio = trade_count / total_steps
            # penalize: >60% steps are trades is considered overtrading
            overtrade_penalty = max(0.0, trade_ratio - 0.6)
        else:
            overtrade_penalty = 0.0

        risk_score = round(max(0.0, 1.0 - (invalid_ratio * 2) - overtrade_penalty), 4)

        # --- composite score ---
        score = (
            0.75 * profit_score +
            0.15 * consistency_score +
            0.10 * risk_score
        )

        if return_percent > 10:
            result = "Excellent"
        elif return_percent > 0:
            result = "Good"
        elif return_percent > -2:
            result = "Neutral"
        elif return_percent >= -5:
            result = "Poor"
        else:
            result = "Bad"

        return {
            "agent": agent_name,
            "final_balance": stats["final_balance"],
            "net_profit": net_profit,
            "return_percent": return_percent,
            "total_fees_paid": stats["total_fees_paid"],
            "total_tax_paid": stats["total_tax_paid"],
            "result": result,
            "score": round(score, 2),
            "difficulty": stats["difficulty"],
        }
