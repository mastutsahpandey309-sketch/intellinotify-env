from typing import List, Literal, Optional
from pydantic import Field
from openenv.core.env_server.types import Action, Observation

# -------------------------------------------------------------------
# Sub-components
# -------------------------------------------------------------------
from pydantic import BaseModel

class PhoneEvent(BaseModel):
    id: int = Field(..., description="Unique integer ID for this event.")
    source: str = Field(..., description="App or system generating the event (e.g. 'WhatsApp', 'SMS').")
    text: str = Field(..., description="Content of the notification or event.")
    is_clipboard: bool = Field(default=False, description="True if this represents clipboard contents.")

# -------------------------------------------------------------------
# Action — what the agent outputs
# -------------------------------------------------------------------
class IntelliNotifyAction(Action):
    highest_priority_id: int = Field(..., description="ID of the single most critical event.")
    threat_level: Literal["none", "low", "medium", "high", "critical"] = Field(..., description="Assessed threat level.")
    threat_type: Literal["none", "phishing", "malware", "distraction", "spam", "financial_fraud"] = Field(..., description="Threat categorization.")
    two_line_advice: str = Field(..., description="Concise advice under 150 characters.")

# -------------------------------------------------------------------
# Observation — what the agent sees
# -------------------------------------------------------------------
class IntelliNotifyObservation(Observation):
    step_number: int = Field(default=0, description="Current step in the notification queue.")
    total_steps: int = Field(default=0, description="Total steps in this episode.")
    events: List[PhoneEvent] = Field(default_factory=list, description="Current phone events to analyse.")
    last_action_feedback: Optional[str] = Field(default=None, description="Feedback on the previous action.")

# -------------------------------------------------------------------
# Reward (internal grader result, not part of OpenEnv Observation)
# -------------------------------------------------------------------
class IntelliNotifyReward(BaseModel):
    score: float = Field(..., description="Reward score strictly between 0.0 and 1.0.")
    reasoning: str = Field(..., description="Explanation of the score.")
