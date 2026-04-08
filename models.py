from typing import Optional

from pydantic import BaseModel, Field


class TradingAction(BaseModel):
    action_type: str = Field(description="The type of trading action to perform (e.g., 'buy', 'sell', 'hold').")


class TradingObservation(BaseModel):
    price: float = Field(description="The current market price of the asset at this step.")
    balance: float = Field(description="The agent's current cash balance in the portfolio.")
    holdings: int = Field(description="The number of asset units currently held by the agent.")
    step_count: int = Field(description="The current step number within the episode.")
    difficulty: str = Field(description="The difficulty level of the current episode (e.g., 'easy', 'medium', 'hard').")
    done: bool = Field(description="Whether the episode has ended after this observation.")
    reward: Optional[float] = Field(default=None, description="The reward signal received for the previous action, if available.")


class TradingState(BaseModel):
    episode_id: str = Field(description="A unique identifier for the current trading episode.")
    step_count: int = Field(description="The current step number within the episode.")
    current_price: float = Field(description="The current market price of the asset.")
    balance: float = Field(description="The agent's current cash balance in the portfolio.")
    holdings: int = Field(description="The number of asset units currently held by the agent.")
    difficulty: str = Field(description="The difficulty level of the current episode (e.g., 'easy', 'medium', 'hard').")
    total_fees_paid: float = Field(description="The cumulative transaction fees paid by the agent over the episode so far.")
    total_tax_paid: float = Field(description="The cumulative taxes paid by the agent on profitable trades over the episode so far.")
