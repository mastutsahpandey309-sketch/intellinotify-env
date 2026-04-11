"""Data models for the IntelliNotify Environment."""
from typing import List, Literal, Optional
from openenv.core.env_server.types import Action, Observation
from pydantic import BaseModel, Field


class PhoneEvent(BaseModel):
    id: int = Field(..., description="Unique event ID")
    source: str = Field(..., description="App or system source")
    text: str = Field(..., description="Notification content")
    is_clipboard: bool = Field(default=False)


class IntelliNotifyAction(Action):
    """Agent identifies the most critical phone notification."""
    highest_priority_id: int = Field(..., description="ID of most critical event")
    threat_level: Literal["none", "low", "medium", "high", "critical"]
    threat_type: Literal["none", "phishing", "malware", "distraction", "spam", "financial_fraud"]
    two_line_advice: str = Field(..., description="Advice under 150 chars")


class IntelliNotifyObservation(Observation):
    """What the agent sees: a list of phone events to triage."""
    step_number: int = Field(default=0)
    total_steps: int = Field(default=0)
    events: List[PhoneEvent] = Field(default_factory=list)
    last_action_feedback: Optional[str] = Field(default=None)
    task_id: Optional[str] = Field(default=None)
