from typing import List, Dict
from schema.models import PhoneEvent

class TaskDefinition:
    def __init__(self, task_id: str, events: List[PhoneEvent], expected_id: int, expected_level: str, expected_type: str):
        self.task_id = task_id
        self.events = events
        self.expected_id = expected_id
        self.expected_level = expected_level
        self.expected_type = expected_type

TASKS: Dict[str, TaskDefinition] = {}

TASKS["task_1_easy_blatant_scam"] = TaskDefinition(
    task_id="task_1_easy_blatant_scam",
    events=[
        PhoneEvent(id=1, source="WhatsApp", text="Mom: Call me when you are free."),
        PhoneEvent(id=3, source="SMS", text="CONGRATS!! You won an iPhone. Click http://scam.xyz"),
    ],
    expected_id=3, expected_level="high", expected_type="spam",
)

TASKS["task_2_medium_productivity_vs_security"] = TaskDefinition(
    task_id="task_2_medium_productivity_vs_security",
    events=[PhoneEvent(id=12, source="SMS", text="Amazon: Account suspended. Verify link.")],
    expected_id=12, expected_level="critical", expected_type="phishing",
)

TASKS["task_3_hard_multi_vector"] = TaskDefinition(
    task_id="task_3_hard_multi_vector",
    events=[PhoneEvent(id=23, source="SMS", text="YONO SBI: OTP for Rs 49,999 is 847291.")],
    expected_id=23, expected_level="critical", expected_type="financial_fraud",
)

def get_task(task_id: str) -> TaskDefinition:
    return TASKS.get(task_id, TASKS["task_1_easy_blatant_scam"])
