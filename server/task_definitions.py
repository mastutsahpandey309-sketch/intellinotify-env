from typing import List, Dict
from .models import PhoneEvent, IntelliNotifyAction
from pydantic import BaseModel

class IntelliNotifyReward(BaseModel):
    score: float
    reasoning: str

def grade_action(
    action: IntelliNotifyAction,
    expected_priority_id: int,
    expected_threat_level: str,
    expected_threat_type: str,
) -> IntelliNotifyReward:
    score = 0.0
    parts = []

    if action.highest_priority_id == expected_priority_id:
        score += 0.5
        parts.append(f"Correct priority ID {expected_priority_id} (+0.5).")
    else:
        parts.append(f"Wrong priority ID.")

    if action.threat_type == expected_threat_type:
        score += 0.3
        parts.append(f"Correct threat type '{expected_threat_type}' (+0.3).")

    if action.threat_level == expected_threat_level:
        score += 0.1
        parts.append(f"Correct threat level (+0.1).")
    else:
        score -= 0.1

    if 10 <= len(action.two_line_advice) <= 150:
        score += 0.1
    
    final = max(0.01, min(0.99, score))
    return IntelliNotifyReward(score=final, reasoning=" | ".join(parts))

class TaskDefinition:
    def __init__(self, task_id, events, expected_id, expected_level, expected_type):
        self.task_id = task_id
        self.events = events
        self.expected_id = expected_id
        self.expected_level = expected_level
        self.expected_type = expected_type

TASKS: Dict[str, TaskDefinition] = {}

TASKS["task_1_easy_blatant_scam"] = TaskDefinition(
    task_id="task_1_easy_blatant_scam",
    events=[
        PhoneEvent(id=1, source="WhatsApp", text="Call me."),
        PhoneEvent(id=3, source="SMS", text="WINNER! Click http://scam.xyz"),
    ],
    expected_id=3, expected_level="high", expected_type="spam",
)

# CRITICAL: This function must exist for environment.py to import it
def get_task(task_id: str) -> TaskDefinition:
    return TASKS.get(task_id, TASKS["task_1_easy_blatant_scam"])
