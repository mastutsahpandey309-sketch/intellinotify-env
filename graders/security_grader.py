from schema.models import IntelliNotifyAction, IntelliNotifyReward

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
        parts.append(f"Correct priority ID (+0.5).")
    else:
        parts.append(f"Wrong priority ID.")

    if action.threat_type == expected_threat_type:
        score += 0.3
        parts.append(f"Correct threat type (+0.3).")

    if action.threat_level == expected_threat_level:
        score += 0.1
        parts.append(f"Correct threat level (+0.1).")
    else:
        score -= 0.1

    if 10 <= len(action.two_line_advice) <= 150:
        score += 0.1
    
    # Strictly bound to pass validation
    final = max(0.01, min(0.99, score))
    return IntelliNotifyReward(score=final, reasoning=" | ".join(parts))
