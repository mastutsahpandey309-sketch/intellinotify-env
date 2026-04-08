from typing import List, Literal, Optional
from pydantic import BaseModel, Field

# -------------------------------------------------------------------
# 1. Sub-components of the Observation
# -------------------------------------------------------------------

class PhoneEvent(BaseModel):
    id: int = Field(..., description="Unique integer ID for this event.")
    source: str = Field(..., description="The app or system generating the event (e.g., 'WhatsApp', 'System', 'SMS').")
    text: str = Field(..., description="The content of the notification or event.")
    is_clipboard: bool = Field(default=False, description="True if this text represents the current clipboard contents.")

# -------------------------------------------------------------------
# 2. The Observation Model (What the agent sees)
# -------------------------------------------------------------------

class IntelliNotifyObservation(BaseModel):
    step_number: int = Field(..., description="The current step in the notification queue.")
    total_steps: int = Field(..., description="The total number of steps in this episode.")
    events: List[PhoneEvent] = Field(..., description="The list of current phone events to analyze.")
    last_action_feedback: Optional[str] = Field(
        default=None, 
        description="Feedback on the previous action, if applicable."
    )

# -------------------------------------------------------------------
# 3. The Action Model (What the agent MUST output)
# -------------------------------------------------------------------

class IntelliNotifyAction(BaseModel):
    highest_priority_id: int = Field(
        ..., 
        description="The ID of the single most critical event requiring user attention."
    )
    threat_level: Literal["none", "low", "medium", "high", "critical"] = Field(
        ..., 
        description="The assessed threat level of the selected priority event."
    )
    threat_type: Literal["none", "phishing", "malware", "distraction", "spam", "financial_fraud"] = Field(
        ..., 
        description="The categorization of the threat."
    )
    two_line_advice: str = Field(
        ..., 
        description="A concise, two-line advice string advising the user on what to do. Must be under 150 characters."
    )

# -------------------------------------------------------------------
# 4. The Reward/State Models (Required by OpenEnv)
# -------------------------------------------------------------------

class IntelliNotifyReward(BaseModel):
    score: float = Field(..., description="Reward score between 0.0 and 1.0 for the current step.")
    reasoning: str = Field(..., description="Explanation of why this score was given (useful for debugging).")

class IntelliNotifyState(BaseModel):
    current_step: int
    max_steps: int
    cumulative_reward: float
    is_done: bool
    current_task_id: str
