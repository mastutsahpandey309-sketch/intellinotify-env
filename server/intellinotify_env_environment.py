"""IntelliNotify Environment — security notification triage."""
from typing import Optional, Dict, List
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import IntelliNotifyAction, IntelliNotifyObservation, PhoneEvent
except ImportError:
    from models import IntelliNotifyAction, IntelliNotifyObservation, PhoneEvent


# ── Task definitions ───────────────────────────────────────────────

class _Task:
    def __init__(self, task_id, events, expected_id, expected_level, expected_type):
        self.task_id = task_id
        self.events = events
        self.expected_id = expected_id
        self.expected_level = expected_level
        self.expected_type = expected_type


TASKS: Dict[str, _Task] = {
    "task_1_easy_blatant_scam": _Task(
        task_id="task_1_easy_blatant_scam",
        events=[
            PhoneEvent(id=1, source="WhatsApp", text="Mom: Call me when free."),
            PhoneEvent(id=2, source="Uber", text="Your driver is 2 min away."),
            PhoneEvent(id=3, source="SMS", text="CONGRATS!! Won iPhone 15. Claim: http://free-gifts-claim.xyz"),
        ],
        expected_id=3, expected_level="high", expected_type="spam",
    ),
    "task_2_medium_productivity_vs_security": _Task(
        task_id="task_2_medium_productivity_vs_security",
        events=[
            PhoneEvent(id=10, source="Calendar", text="Meeting: Q3 Planning in 15 mins"),
            PhoneEvent(id=11, source="Gmail", text="Boss: URGENT! Need Q3 report NOW."),
            PhoneEvent(id=12, source="SMS", text="Amazon: Account suspended. Verify: http://amazon-verify-account.com"),
        ],
        expected_id=12, expected_level="critical", expected_type="phishing",
    ),
    "task_3_hard_multi_vector": _Task(
        task_id="task_3_hard_multi_vector",
        events=[
            PhoneEvent(id=20, source="System", text="Battery at 15%. Turn on battery saver?"),
            PhoneEvent(id=21, source="Clipboard", text="upi://pay?pa=fraudster@ybl", is_clipboard=True),
            PhoneEvent(id=22, source="Chrome", text="sbi-secure-login.xyz/verify"),
            PhoneEvent(id=23, source="SMS", text="YONO SBI: OTP for Rs 49,999 is 847291. Do not share."),
        ],
        expected_id=23, expected_level="critical", expected_type="financial_fraud",
    ),
    "task_4_medium_fake_bank_alert": _Task(
        task_id="task_4_medium_fake_bank_alert",
        events=[
            PhoneEvent(id=30, source="Gmail", text="Newsletter: Top travel spots 2025."),
            PhoneEvent(id=31, source="SMS", text="HDFC Bank: Rs 12,000 debited. Not you? Call 1800-XXX-FAKE."),
            PhoneEvent(id=32, source="SMS", text="HDFC OTP 293847. Share with agent to reverse transaction."),
        ],
        expected_id=32, expected_level="critical", expected_type="phishing",
    ),
    "task_5_hard_malware_install": _Task(
        task_id="task_5_hard_malware_install",
        events=[
            PhoneEvent(id=40, source="Chrome", text="Page loaded: free-movies-hd-apk.net/download"),
            PhoneEvent(id=41, source="System", text="Install: 'Netflix_Premium_Unlocked.apk' from unknown source."),
            PhoneEvent(id=42, source="System", text="App requesting Accessibility permissions."),
            PhoneEvent(id=43, source="Gmail", text="Team standup in 10 minutes."),
        ],
        expected_id=41, expected_level="critical", expected_type="malware",
    ),
}


def _grade(action: IntelliNotifyAction, task: _Task) -> float:
    """Deterministic grader — score strictly in (0.01, 0.99)."""
    score = 0.0
    if action.highest_priority_id == task.expected_id:
        score += 0.50
    if action.threat_type == task.expected_type:
        score += 0.30
    if action.threat_level == task.expected_level:
        score += 0.10
    else:
        score -= 0.10
    if 10 <= len(action.two_line_advice) <= 150:
        score += 0.10
    return max(0.01, min(0.99, score))


# ── Environment ────────────────────────────────────────────────────

class IntelliNotifyEnvironment(Environment):
    """
    Mobile OS notification security benchmark.
    Agent triages phone events to identify threats.
    Each episode = one reset() + one step().
    """
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        super().__init__()
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task: Optional[_Task] = None
        self._done = False

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_id: Optional[str] = None,
        task: Optional[str] = None,
        **kwargs,
    ) -> IntelliNotifyObservation:
        chosen = task_id or task
        self._task = TASKS.get(chosen, TASKS["task_1_easy_blatant_scam"]) if chosen else TASKS["task_1_easy_blatant_scam"]
        self._done = False
        self._state = State(episode_id=episode_id or str(uuid4()), step_count=0)

        return IntelliNotifyObservation(
            step_number=1,
            total_steps=1,
            events=self._task.events,
            last_action_feedback=None,
            task_id=self._task.task_id,
            done=False,
            reward=None,
        )

    def step(self, action: IntelliNotifyAction) -> IntelliNotifyObservation:  # type: ignore[override]
        if self._task is None or self._done:
            return IntelliNotifyObservation(
                step_number=1, total_steps=1, events=[],
                last_action_feedback="Call reset() first.",
                task_id=None, done=True, reward=0.05,
            )

        score = _grade(action, self._task)
        self._done = True
        self._state.step_count += 1

        return IntelliNotifyObservation(
            step_number=1, total_steps=1, events=[],
            last_action_feedback=f"Score: {score:.2f}",
            task_id=self._task.task_id,
            done=True,
            reward=score,
        )

    @property
    def state(self) -> State:
        return self._state

    def close(self):
        pass
