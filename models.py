from typing import List, Literal, Optional
from pydantic import BaseModel, Field

# This was missing and caused your error
class IntelliNotifyReward(BaseModel):
    score: float
    reasoning: str

class PhoneEvent(BaseModel):
    id: int = Field(..., description="Unique integer ID for this event.")
    source: str = Field(..., description="App or system generating the event.")
    text: str = Field(..., description="Content of the notification or event.")
    is_clipboard: bool = Field(default=False, description="True if clipboard contents.")

class IntelliNotifyAction(BaseModel):
    highest_priority_id: int = Field(..., description="ID of the most critical event.")
    threat_level: Literal["none", "low", "medium", "high", "critical"] = Field(..., description="Assessed threat level.")
    threat_type: Literal["none", "phishing", "malware", "distraction", "spam", "financial_fraud"] = Field(..., description="Threat category.")
    two_line_advice: str = Field(..., description="Concise advice under 150 characters.")

class IntelliNotifyObservation(BaseModel):
    step_number: int = Field(default=0)
    total_steps: int = Field(default=0)
    events: List[PhoneEvent] = Field(default_factory=list)
    last_action_feedback: Optional[str] = Field(default=None)
    reward: Optional[float] = None
    done: bool = Field(default=False)
