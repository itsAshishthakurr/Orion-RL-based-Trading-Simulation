class Leaderboard:
    def display(self, results, difficulty):
        difficulty_map = {
            "easy":   ("trend",    50,  20),
            "medium": ("volatile", 75,  10),
            "hard":   ("sideways", 100,  5),
        }
        market_type, max_steps, max_holdings = difficulty_map.get(
            difficulty, ("unknown", 0, 0)
        )

        sep = "-" * 88

        sorted_results = sorted(results, key=lambda r: r["score"], reverse=True)

        print()
        print("=" * 88)
        print(f"  ORION TRADING SIMULATION")
        print(f"  Difficulty : {difficulty.upper()}")
        print(f"  Market     : {market_type.capitalize()}")
        print(f"  Steps      : {max_steps}    Max Holdings : {max_holdings}")
        print("=" * 88)
        print()
        print(f"  {'Rank':<6} {'Agent':<12} {'Net Profit':>12} {'Fee Paid':>10} {'Tax Paid':>10} {'Return%':>9} {'Score':>7}  {'Result'}")
        print(sep)

        for i, r in enumerate(sorted_results, start=1):
            rank       = f"[{i}]"
            agent      = r["agent"]
            net_profit = r["net_profit"]
            fees       = r["total_fees_paid"]
            tax        = r["total_tax_paid"]
            ret_pct    = r["return_percent"]
            score      = r["score"]
            result     = r["result"]

            profit_str = f"Rs{net_profit:+.2f}"
            fees_str   = f"Rs{fees:.2f}"
            tax_str    = f"Rs{tax:.2f}"
            ret_str    = f"{ret_pct:.2f}%"
            score_str  = f"{score:.2f}"

            print(
                f"  {rank:<6}"
                f"{agent:<12}"
                f"{profit_str:>12}"
                f"{fees_str:>10}"
                f"{tax_str:>10}"
                f"{ret_str:>9}"
                f"{score_str:>7}"
                f"    {result}"
            )

        print(sep)
        print()
        print("  Reward Scale:  0.00 = Poor   0.25 = Weak   0.50 = Neutral   0.75 = Good   1.00 = Excellent")
        print()

        for r in sorted_results:
            agent_name = r["agent"]
            logs = r.get("step_log", [])
            print("=" * 88)
            print(f"  STEP LOG - Agent: {agent_name}")
            print(sep)
            print(f"  {'Step':>5}  {'Action':<6}  {'Price':>8}  {'Holdings':>9}  {'Balance':>11}  {'Reward':>7}")
            print(sep)
            for entry in logs:
                print(
                    f"  {entry['step']:>5}  "
                    f"{entry['action']:<6}  "
                    f"{entry['price']:>8.2f}  "
                    f"{entry['holdings']:>9.0f}  "
                    f"Rs{entry['balance']:>9.2f}  "
                    f"{entry['reward']:>7.2f}"
                )
            print(sep)
            print(f"  Agent: {agent_name}  |  Net Profit: Rs{r['net_profit']:+.2f}  |  Score: {r['score']:.2f}  |  Result: {r['result']}")
            print()
