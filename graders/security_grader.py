"""
IntelliNotify Deterministic Grader.
Score strictly in (0.01, 0.99) — never 0.0 or 1.0.
Weights: priority_id=0.50 | threat_type=0.30 | threat_level=+/-0.10 | advice=0.10
"""
from schema.models import IntelliNotifyAction
from pydantic import BaseModel


class GradeResult(BaseModel):
    score: float
    reasoning: str
    components: dict


def grade_action(
    action: IntelliNotifyAction,
    expected_priority_id: int,
    expected_threat_level: str,
    expected_threat_type: str,
) -> GradeResult:
    score = 0.0
    parts = []
    components = {}

    # Priority ID — 50%
    if action.highest_priority_id == expected_priority_id:
        score += 0.50
        parts.append(f"Correct priority ID {expected_priority_id} (+0.50).")
        components["priority_id"] = 0.50
    else:
        parts.append(f"Wrong priority ID (expected {expected_priority_id}, got {action.highest_priority_id}).")
        components["priority_id"] = 0.0

    # Threat type — 30%
    if action.threat_type == expected_threat_type:
        score += 0.30
        parts.append(f"Correct threat type '{expected_threat_type}' (+0.30).")
        components["threat_type"] = 0.30
    else:
        parts.append(f"Wrong threat type (expected '{expected_threat_type}', got '{action.threat_type}').")
        components["threat_type"] = 0.0

    # Threat level — +/-10%
    if action.threat_level == expected_threat_level:
        score += 0.10
        parts.append(f"Correct threat level '{expected_threat_level}' (+0.10).")
        components["threat_level"] = 0.10
    else:
        score -= 0.10
        parts.append(f"Wrong threat level (expected '{expected_threat_level}', got '{action.threat_level}') (-0.10).")
        components["threat_level"] = -0.10

    # Advice quality — 10%
    advice_len = len(action.two_line_advice)
    if 10 <= advice_len <= 150:
        score += 0.10
        parts.append("Valid advice (+0.10).")
        components["advice"] = 0.10
    else:
        parts.append(f"Advice length {advice_len} out of range (10-150).")
        components["advice"] = 0.0

    final = max(0.01, min(0.99, score))
    return GradeResult(score=final, reasoning=" | ".join(parts), components=components)


class IntelliNotifyGrader:
    """Grader class — called directly by the validator."""

    def grade(self, action_dict: dict, task_id: str) -> GradeResult:
        from tasks.registry import get_task
        task = get_task(task_id)
        action = IntelliNotifyAction(**action_dict)
        return grade_action(
            action=action,
            expected_priority_id=task.expected_id,
            expected_threat_level=task.expected_level,
            expected_threat_type=task.expected_type,
        )

    def grade_episode(self, actions: list, task_id: str) -> float:
        """Grade a full episode and return a score in (0.0, 1.0)."""
        if not actions:
            return 0.05
        scores = [self.grade(a, task_id).score for a in actions]
        return max(0.01, min(0.99, sum(scores) / len(scores)))
