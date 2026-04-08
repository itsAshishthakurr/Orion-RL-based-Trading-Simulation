from openenv.server.environment import TradingEnvironment
from core.grader import Grader
from agents.random_agent import RandomAgent
from agents.safe_agent import SafeAgent
from agents.smart_agent import SmartAgent
from agents.learning_agent import LearningAgent


class SimulationRunner:
    def __init__(self, difficulty="easy"):
        self.difficulty = difficulty
        self.grader = Grader()
        self.agents = {
            "Random": RandomAgent(),
            "Safe": SafeAgent(),
            "Smart": SmartAgent(),
            "Learning": LearningAgent(),
        }

    def _reset_agent(self, agent):
        if hasattr(agent, "previous_price"):
            agent.previous_price = None
        if hasattr(agent, "last_buy_price"):
            agent.last_buy_price = None
        if hasattr(agent, "steps"):
            agent.steps = 0
        if hasattr(agent, "buy_count"):
            agent.buy_count = 0
        if hasattr(agent, "reset") and callable(agent.reset):
            agent.reset()

    def run_episode(self):
        results = []

        for name, agent in self.agents.items():
            self._reset_agent(agent)
            env = TradingEnvironment(difficulty=self.difficulty)
            observation = env.reset()
            total_reward = 0
            step_log = []
            step_rewards = []
            action_log = []
            invalid_count = 0

            while True:
                action = agent.select_action(observation)
                prev_observation = observation
                observation, reward, done = env.step(action)

                # Enable real learning for agents that support it
                if hasattr(agent, "update_reward"):
                    agent.update_reward(action, reward)

                # Track invalid actions using the authoritative flag from the env
                if env.last_action_invalid:
                    invalid_count += 1

                total_reward += reward
                step_rewards.append(reward)
                action_log.append(action)
                step_log.append({
                    "step": int(env.step_count),
                    "action": action,
                    "price": observation["price"],
                    "holdings": observation["holdings"],
                    "balance": observation["balance"],
                    "reward": reward,
                })
                if done:
                    break

            stats = env.get_final_stats()
            # Attach per-episode data for the grader
            stats["step_rewards"] = step_rewards
            stats["action_log"] = action_log
            stats["invalid_count"] = invalid_count

            grade = self.grader.evaluate(name, env.initial_balance, stats)
            grade["total_reward"] = round(total_reward, 2)
            grade["step_log"] = step_log
            results.append(grade)

        return results
