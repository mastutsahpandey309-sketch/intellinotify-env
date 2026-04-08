from typing import List, Dict
from models import PhoneEvent, IntelliNotifyAction, IntelliNotifyReward

# -------------------------------------------------------------------
# 1. The Deterministic Grader
# -------------------------------------------------------------------
def grade_action(
    action: IntelliNotifyAction,
    expected_priority_id: int,
    expected_threat_level: str,
    expected_threat_type: str
) -> IntelliNotifyReward:
    """
    Evaluates the agent's action completely deterministically.
    Total possible score = 1.0
    - Correct priority ID: +0.5
    - Correct threat type: +0.3
    - Advice exists & valid length: +0.2
    - Incorrect threat level: -0.1 penalty (optional nuance)
    """
    score = 0.0
    reasoning_parts = []

    # 1. Check Priority ID (Weight: 50%)
    if action.highest_priority_id == expected_priority_id:
        score += 0.5
        reasoning_parts.append("Correct priority ID (+0.5).")
    else:
        reasoning_parts.append(f"Failed priority ID (Expected {expected_priority_id}, got {action.highest_priority_id}).")

    # 2. Check Threat Type (Weight: 30%)
    if action.threat_type == expected_threat_type:
        score += 0.3
        reasoning_parts.append(f"Correct threat type '{expected_threat_type}' (+0.3).")
    else:
        reasoning_parts.append(f"Failed threat type (Expected '{expected_threat_type}', got '{action.threat_type}').")

    # 3. Check Advice formatting (Weight: 20%)
    advice_len = len(action.two_line_advice)
    if 10 <= advice_len <= 150:
        score += 0.2
        reasoning_parts.append("Valid advice provided (+0.2).")
    else:
        reasoning_parts.append(f"Advice length {advice_len} out of bounds (10-150 chars).")

    # Ensure score stays strictly bounded [0.0, 1.0]
    final_score = max(0.0, min(1.0, score))
    
    return IntelliNotifyReward(
        score=final_score,
        reasoning=" | ".join(reasoning_parts)
    )

# -------------------------------------------------------------------
# 2. Scenario Data Structures
# -------------------------------------------------------------------
class StepDefinition:
    def __init__(self, events: List[PhoneEvent], expected_id: int, expected_level: str, expected_type: str):
        self.events = events
        self.expected_id = expected_id
        self.expected_level = expected_level
        self.expected_type = expected_type

class TaskDefinition:
    def __init__(self, task_id: str, steps: List[StepDefinition]):
        self.task_id = task_id
        self.steps = steps

# -------------------------------------------------------------------
# 3. The Tasks (Multi-Step Queues)
# -------------------------------------------------------------------

TASKS: Dict[str, TaskDefinition] = {}

# --- TASK 1: The Blatant Scam (Easy) ---
# Step 1: Normal WhatsApp message
# Step 2: Obvious Spam SMS mixed with Uber notification
TASKS["task_1_easy_blatant_scam"] = TaskDefinition(
    task_id="task_1_easy_blatant_scam",
    steps=[
        StepDefinition(
            events=[
                PhoneEvent(id=1, source="WhatsApp", text="Mom: Call me when you are free.", is_clipboard=False)
            ],
            expected_id=1, expected_level="none", expected_type="none"
        ),
        StepDefinition(
            events=[
                PhoneEvent(id=2, source="Uber", text="Your driver is 2 minutes away.", is_clipboard=False),
                PhoneEvent(id=3, source="SMS", text="CONGRATS!! You won an iPhone 15. Click here: http://free-gifts-claim.xyz", is_clipboard=False)
            ],
            expected_id=3, expected_level="high", expected_type="spam"
        )
    ]
)

# --- TASK 2: Productivity vs. Security (Medium) ---
# Step 1: Normal work calendar
# Step 2: Urgent work email + sneaky Phishing link
TASKS["task_2_medium_productivity_vs_security"] = TaskDefinition(
    task_id="task_2_medium_productivity_vs_security",
    steps=[
        StepDefinition(
            events=[
                PhoneEvent(id=10, source="Calendar", text="Meeting: Q3 Planning in 15 mins", is_clipboard=False)
            ],
            expected_id=10, expected_level="none", expected_type="none"
        ),
        StepDefinition(
            events=[
                PhoneEvent(id=11, source="Gmail", text="Boss: URGENT! I need the Q3 report attached NOW.", is_clipboard=False),
                PhoneEvent(id=12, source="SMS", text="Amazon: Your account is suspended. Verify immediately at http://amazon-verify-account.com", is_clipboard=False)
            ],
            # Agent MUST prioritize security (12) over productivity (11)
            expected_id=12, expected_level="critical", expected_type="phishing"
        )
    ]
)

# --- TASK 3: Multi-Vector Context Attack (Hard) ---
# Step 1: Normal state, malicious link copied to clipboard
# Step 2: OTP arrives that correlates with the malicious clipboard payload
TASKS["task_3_hard_multi_vector"] = TaskDefinition(
    task_id="task_3_hard_multi_vector",
    steps=[
        StepDefinition(
            events=[
                PhoneEvent(id=20, source="System", text="Battery at 15%. Turn on battery saver?", is_clipboard=False),
                PhoneEvent(id=21, source="Clipboard", text="upi://pay?pa=fraudster@ybl", is_clipboard=True)
            ],
            expected_id=21, expected_level="medium", expected_type="financial_fraud"
        ),
        StepDefinition(
            events=[
                PhoneEvent(id=22, source="Clipboard", text="upi://pay?pa=fraudster@ybl", is_clipboard=True),
                PhoneEvent(id=23, source="Chrome", text="sbi-secure-login.xyz/verify", is_clipboard=False),
                PhoneEvent(id=24, source="SMS", text="YONO SBI: Your OTP for transaction of Rs 49,999 is 847291. Do not share this.", is_clipboard=False)
            ],
            # Agent must connect the fake domain + copied UPI + OTP and flag the OTP/transaction as critical fraud.
            expected_id=24, expected_level="critical", expected_type="financial_fraud"
        )
    ]
)

def get_task(task_id: str) -> TaskDefinition:
    if task_id not in TASKS:
        # Default to easy if an unknown task is requested (safety fallback)
        return TASKS["task_1_easy_blatant_scam"]
    return TASKS[task_id]