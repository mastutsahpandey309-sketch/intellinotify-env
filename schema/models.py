from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class PhoneEvent(BaseModel):
    id: int = Field(..., description="Unique event ID")
    source: str = Field(..., description="App or system source")
    text: str = Field(..., description="Notification content")
    is_clipboard: bool = Field(default=False)


class IntelliNotifyAction(BaseModel):
    highest_priority_id: int = Field(..., description="ID of most critical event")
    threat_level: Literal["none", "low", "medium", "high", "critical"]
    threat_type: Literal["none", "phishing", "malware", "distraction", "spam", "financial_fraud"]
    two_line_advice: str = Field(..., description="Advice under 150 chars")


class IntelliNotifyObservation(BaseModel):
    step_number: int = 0
    total_steps: int = 0
    events: List[PhoneEvent] = []
    last_action_feedback: Optional[str] = None
    reward: Optional[float] = None
    done: bool = False
