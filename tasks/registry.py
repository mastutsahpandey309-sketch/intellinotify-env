from typing import List, Dict
from schema.models import PhoneEvent


class TaskDefinition:
    def __init__(self, task_id, name, description, difficulty,
                 events, expected_id, expected_level, expected_type):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.events = events
        self.expected_id = expected_id
        self.expected_level = expected_level
        self.expected_type = expected_type


TASKS: Dict[str, TaskDefinition] = {}

TASKS["task_1_easy_blatant_scam"] = TaskDefinition(
    task_id="task_1_easy_blatant_scam",
    name="Task 1: Blatant Scam",
    description="Identify an obvious spam SMS among normal notifications.",
    difficulty="easy",
    events=[
        PhoneEvent(id=1, source="WhatsApp", text="Mom: Call me when you are free."),
        PhoneEvent(id=2, source="Uber", text="Your driver is 2 minutes away."),
        PhoneEvent(id=3, source="SMS", text="CONGRATS!! You won iPhone 15. Claim: http://free-gifts-claim.xyz"),
    ],
    expected_id=3, expected_level="high", expected_type="spam",
)

TASKS["task_2_medium_productivity_vs_security"] = TaskDefinition(
    task_id="task_2_medium_productivity_vs_security",
    name="Task 2: Productivity vs. Security",
    description="Prioritize a phishing link over an urgent work email.",
    difficulty="medium",
    events=[
        PhoneEvent(id=10, source="Calendar", text="Meeting: Q3 Planning in 15 mins"),
        PhoneEvent(id=11, source="Gmail", text="Boss: URGENT! I need the Q3 report NOW."),
        PhoneEvent(id=12, source="SMS", text="Amazon: Account suspended. Verify: http://amazon-verify-account.com"),
    ],
    expected_id=12, expected_level="critical", expected_type="phishing",
)

TASKS["task_3_hard_multi_vector"] = TaskDefinition(
    task_id="task_3_hard_multi_vector",
    name="Task 3: Multi-Vector Financial Attack",
    description="Detect coordinated UPI fraud via clipboard and OTP correlation.",
    difficulty="hard",
    events=[
        PhoneEvent(id=20, source="System", text="Battery at 15%. Turn on battery saver?"),
        PhoneEvent(id=21, source="Clipboard", text="upi://pay?pa=fraudster@ybl", is_clipboard=True),
        PhoneEvent(id=22, source="Chrome", text="sbi-secure-login.xyz/verify"),
        PhoneEvent(id=23, source="SMS", text="YONO SBI: OTP for Rs 49,999 is 847291. Do not share."),
    ],
    expected_id=23, expected_level="critical", expected_type="financial_fraud",
)

TASKS["task_4_medium_fake_bank_alert"] = TaskDefinition(
    task_id="task_4_medium_fake_bank_alert",
    name="Task 4: Fake Bank Alert",
    description="Identify social-engineering SMS impersonating a bank.",
    difficulty="medium",
    events=[
        PhoneEvent(id=30, source="Gmail", text="Newsletter: Top 10 travel destinations 2025."),
        PhoneEvent(id=31, source="SMS", text="HDFC Bank: Rs 12,000 debited. Not you? Call 1800-XXX-FAKE."),
        PhoneEvent(id=32, source="SMS", text="Your HDFC OTP is 293847. Share with agent to reverse transaction."),
    ],
    expected_id=32, expected_level="critical", expected_type="phishing",
)

TASKS["task_5_hard_malware_install"] = TaskDefinition(
    task_id="task_5_hard_malware_install",
    name="Task 5: Malware Install Trap",
    description="Detect a malicious APK install disguised as a streaming app.",
    difficulty="hard",
    events=[
        PhoneEvent(id=40, source="Chrome", text="Page loaded: free-movies-hd-apk.net/download"),
        PhoneEvent(id=41, source="System", text="Install request: 'Netflix_Premium_Unlocked.apk' from unknown source."),
        PhoneEvent(id=42, source="System", text="App requesting Accessibility permissions."),
        PhoneEvent(id=43, source="Gmail", text="Team standup in 10 minutes."),
    ],
    expected_id=41, expected_level="critical", expected_type="malware",
)


def get_task(task_id: str) -> TaskDefinition:
    return TASKS.get(task_id, TASKS["task_1_easy_blatant_scam"])
