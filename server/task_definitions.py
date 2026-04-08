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
    """
    Deterministic grader. Score strictly in (0.01, 0.99).
    Weights: priority_id 0.5 | threat_type 0.3 | threat_level ±0.1 | advice 0.1
    """
    score = 0.0
    parts = []

    if action.highest_priority_id == expected_priority_id:
        score += 0.5
        parts.append(f"Correct priority ID {expected_priority_id} (+0.5).")
    else:
        parts.append(f"Wrong priority ID (expected {expected_priority_id}, got {action.highest_priority_id}).")

    if action.threat_type == expected_threat_type:
        score += 0.3
        parts.append(f"Correct threat type '{expected_threat_type}' (+0.3).")
    else:
        parts.append(f"Wrong threat type (expected '{expected_threat_type}', got '{action.threat_type}').")

    if action.threat_level == expected_threat_level:
        score += 0.1
        parts.append(f"Correct threat level '{expected_threat_level}' (+0.1).")
    else:
        score -= 0.1
        parts.append(f"Wrong threat level (expected '{expected_threat_level}', got '{action.threat_level}') (-0.1).")

    if 10 <= len(action.two_line_advice) <= 150:
        score += 0.1
        parts.append("Valid advice (+0.1).")
    else:
        parts.append(f"Advice length {len(action.two_line_advice)} out of range (10-150).")

    # Strictly between 0 and 1 — never 0.0 or 1.0
    final = max(0.01, min(0.99, score))
    return IntelliNotifyReward(score=final, reasoning=" | ".join(parts))


class TaskDefinition:
    def __init__(
        self,
        task_id: str,
        events: List[PhoneEvent],
        expected_id: int,
        expected_level: str,
        expected_type: str,
    ):
        self.task_id = task_id
        self.events = events
        self.expected_id = expected_id
        self.expected_level = expected_level
        self.expected_type = expected_type


TASKS: Dict[str, TaskDefinition] = {}

# Task 1 — Easy: Blatant Scam
TASKS["task_1_easy_blatant_scam"] = TaskDefinition(
    task_id="task_1_easy_blatant_scam",
    events=[
        PhoneEvent(id=1, source="WhatsApp", text="Mom: Call me when you are free."),
        PhoneEvent(id=2, source="Uber", text="Your driver is 2 minutes away."),
        PhoneEvent(id=3, source="SMS", text="CONGRATS!! You won an iPhone 15. Click: http://free-gifts-claim.xyz"),
    ],
    expected_id=3, expected_level="high", expected_type="spam",
)

# Task 2 — Medium: Phishing vs Urgent Work Email
TASKS["task_2_medium_productivity_vs_security"] = TaskDefinition(
    task_id="task_2_medium_productivity_vs_security",
    events=[
        PhoneEvent(id=10, source="Calendar", text="Meeting: Q3 Planning in 15 mins"),
        PhoneEvent(id=11, source="Gmail", text="Boss: URGENT! I need the Q3 report attached NOW."),
        PhoneEvent(id=12, source="SMS", text="Amazon: Your account is suspended. Verify: http://amazon-verify-account.com"),
    ],
    expected_id=12, expected_level="critical", expected_type="phishing",
)

# Task 3 — Hard: Multi-Vector UPI Fraud
TASKS["task_3_hard_multi_vector"] = TaskDefinition(
    task_id="task_3_hard_multi_vector",
    events=[
        PhoneEvent(id=20, source="System", text="Battery at 15%. Turn on battery saver?"),
        PhoneEvent(id=21, source="Clipboard", text="upi://pay?pa=fraudster@ybl", is_clipboard=True),
        PhoneEvent(id=22, source="Chrome", text="sbi-secure-login.xyz/verify"),
        PhoneEvent(id=23, source="SMS", text="YONO SBI: OTP for Rs 49,999 is 847291. Do not share."),
    ],
    expected_id=23, expected_level="critical", expected_type="financial_fraud",
)

# Task 4 — Medium: Fake Bank Alert + OTP Scam
TASKS["task_4_medium_fake_bank_alert"] = TaskDefinition(
    task_id="task_4_medium_fake_bank_alert",
    events=[
        PhoneEvent(id=30, source="Gmail", text="Newsletter: Top 10 travel destinations 2025."),
        PhoneEvent(id=31, source="SMS", text="HDFC Bank: Rs 12,000 debited. Not you? Call 1800-XXX-FAKE."),
        PhoneEvent(id=32, source="SMS", text="Your HDFC OTP is 293847. Share with our agent to reverse the transaction."),
    ],
    expected_id=32, expected_level="critical", expected_type="phishing",
)

# Task 5 — Hard: Malware Install Trap
TASKS["task_5_hard_malware_install"] = TaskDefinition(
    task_id="task_5_hard_malware_install",
    events=[
        PhoneEvent(id=40, source="Chrome", text="Page loaded: free-movies-hd-apk.net/download"),
        PhoneEvent(id=41, source="System", text="Install request: 'Netflix_Premium_Unlocked.apk' from unknown source."),
        PhoneEvent(id=42, source="System", text="App 'Netflix_Premium_Unlocked' requesting Accessibility permissions."),
        PhoneEvent(id=43, source="Gmail", text="Team standup in 10 minutes."),
    ],
    expected_id=41, expected_level="critical", expected_type="malware",
)


def get_task(task_id: str) -> TaskDefinition:
    return TASKS.get(task_id, TASKS["task_1_easy_blatant_scam"])
