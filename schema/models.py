from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class PhoneEvent(BaseModel):
    id: int
    source: str
    text: str
    is_clipboard: bool = False

class IntelliNotifyAction(BaseModel):
    highest_priority_id: int
    threat_level: Literal["none", "low", "medium", "high", "critical"]
    threat_type: Literal["none", "phishing", "malware", "distraction", "spam", "financial_fraud"]
    two_line_advice: str

class IntelliNotifyObservation(BaseModel):
    step_number: int = 0
    total_steps: int = 0
    events: List[PhoneEvent] = []
    last_action_feedback: Optional[str] = None
    reward: Optional[float] = None
    done: bool = False

class IntelliNotifyReward(BaseModel):
    score: float
    reasoning: str
