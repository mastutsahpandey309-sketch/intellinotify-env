"""IntelliNotify Environment — security notification triage."""
from typing import Optional, Dict, List
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import IntelliNotifyAction, IntelliNotifyObservation, PhoneEvent
except ImportError:
    from models import IntelliNotifyAction, IntelliNotifyObservation, PhoneEvent


# ── Advice keywords per threat type ───────────────────────────────
_ADVICE_KEYWORDS: Dict[str, List[str]] = {
    "phishing":        ["phishing", "fake", "scam", "fraud", "suspicious", "ignore", "avoid", "block"],
    "malware":         ["malware", "virus", "apk", "install", "permission", "unsafe", "block", "deny"],
    "financial_fraud": ["otp", "fraud", "share", "bank", "block", "report", "transaction", "suspicious"],
    "spam":            ["spam", "scam", "fake", "ignore", "delete", "block", "prize"],
    "distraction":     ["distraction", "ignore", "dismiss", "focus", "later", "postpone"],
    "none":            ["safe", "normal", "ignore", "legitimate", "benign", "no threat"],
}


# ── Task definition ────────────────────────────────────────────────
class _Task:
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


# ── Task catalogue ─────────────────────────────────────────────────
TASKS: Dict[str, _Task] = {

    "task_1_easy_blatant_scam": _Task(
        task_id="task_1_easy_blatant_scam",
        events=[
            PhoneEvent(id=1, source="WhatsApp", text="Mom: Call me when free."),
            PhoneEvent(id=2, source="Uber",     text="Your driver is 2 min away."),
            PhoneEvent(id=3, source="SMS",      text="CONGRATS!! Won iPhone 15. Claim: http://free-gifts-claim.xyz"),
        ],
        expected_id=3, expected_level="high", expected_type="spam",
    ),

    "task_2_medium_productivity_vs_security": _Task(
        task_id="task_2_medium_productivity_vs_security",
        events=[
            PhoneEvent(id=10, source="Calendar", text="Meeting: Q3 Planning in 15 mins"),
            PhoneEvent(id=11, source="Gmail",    text="Boss: URGENT! Need Q3 report NOW."),
            PhoneEvent(id=12, source="SMS",      text="Amazon: Account suspended. Verify: http://amazon-verify-account.com"),
        ],
        expected_id=12, expected_level="critical", expected_type="phishing",
    ),

    "task_3_hard_multi_vector": _Task(
        task_id="task_3_hard_multi_vector",
        events=[
            PhoneEvent(id=20, source="System",    text="Battery at 15%. Turn on battery saver?"),
            PhoneEvent(id=21, source="Clipboard", text="upi://pay?pa=fraudster@ybl", is_clipboard=True),
            PhoneEvent(id=22, source="Chrome",    text="sbi-secure-login.xyz/verify"),
            PhoneEvent(id=23, source="SMS",       text="YONO SBI: OTP for Rs 49,999 is 847291. Do not share."),
        ],
        expected_id=23, expected_level="critical", expected_type="financial_fraud",
    ),

    "task_4_medium_fake_bank_alert": _Task(
        task_id="task_4_medium_fake_bank_alert",
        events=[
            PhoneEvent(id=30, source="Gmail", text="Newsletter: Top travel spots 2025."),
            PhoneEvent(id=31, source="SMS",   text="HDFC Bank: Rs 12,000 debited. Not you? Call 1800-XXX-FAKE."),
            PhoneEvent(id=32, source="SMS",   text="HDFC OTP 293847. Share with agent to reverse transaction."),
        ],
        expected_id=32, expected_level="critical", expected_type="phishing",
    ),

    "task_5_hard_malware_install": _Task(
        task_id="task_5_hard_malware_install",
        events=[
            PhoneEvent(id=40, source="Chrome", text="Page loaded: free-movies-hd-apk.net/download"),
            PhoneEvent(id=41, source="System", text="Install: 'Netflix_Premium_Unlocked.apk' from unknown source."),
            PhoneEvent(id=42, source="System", text="App requesting Accessibility permissions."),
            PhoneEvent(id=43, source="Gmail",  text="Team standup in 10 minutes."),
        ],
        expected_id=41, expected_level="critical", expected_type="malware",
    ),

    "task_6_fake_2fa_prompt": _Task(
        task_id="task_6_fake_2fa_prompt",
        events=[
            PhoneEvent(id=60, source="Spotify",  text="New release: Taylor Swift — The Tortured Poets Department"),
            PhoneEvent(id=61, source="WhatsApp", text="Priya: Hey, free this weekend?"),
            PhoneEvent(id=62, source="SMS",      text="Google: Your security code is 847291. Enter at google-security-verify.net to protect your account."),
        ],
        expected_id=62, expected_level="critical", expected_type="phishing",
    ),

    "task_7_whatsapp_impersonation": _Task(
        task_id="task_7_whatsapp_impersonation",
        events=[
            PhoneEvent(id=70, source="Instagram", text="@cricket_fan liked your post."),
            PhoneEvent(id=71, source="WhatsApp",  text="Unknown (+91-XXXXX): Bro this is Rahul, new number. Emergency — send Rs 5000 on GPay, will return tonight."),
            PhoneEvent(id=72, source="Gmail",     text="HR: Please submit your timesheet by 5 PM today."),
        ],
        expected_id=71, expected_level="high", expected_type="financial_fraud",
    ),

    "task_8_fake_app_update": _Task(
        task_id="task_8_fake_app_update",
        events=[
            PhoneEvent(id=80, source="Play Store", text="Update available: WhatsApp 2.24.11 — bug fixes and performance improvements."),
            PhoneEvent(id=81, source="SMS",        text="DHL: Your parcel is held. Re-schedule delivery: dhl-redelivery-india.xyz/track"),
            PhoneEvent(id=82, source="Chrome",     text="SECURITY ALERT: Adobe Flash update required. Install now: flash-security-patch.net/update.apk"),
        ],
        expected_id=82, expected_level="critical", expected_type="malware",
    ),

    "task_9_none_all_benign": _Task(
        task_id="task_9_none_all_benign",
        events=[
            PhoneEvent(id=90, source="Gmail",    text="Amazon: Your order #408-2937 has shipped. Expected delivery: Thursday."),
            PhoneEvent(id=91, source="Calendar", text="Reminder: Doctor appointment tomorrow at 10:00 AM — City Hospital"),
            PhoneEvent(id=92, source="WhatsApp", text="Dad: Happy birthday beta! Have a great day 🎂"),
        ],
        expected_id=91, expected_level="none", expected_type="none",
    ),

    "task_10_ransomware": _Task(
        task_id="task_10_ransomware",
        events=[
            PhoneEvent(id=100, source="Calendar", text="Team lunch today at 1:00 PM — Olive Garden"),
            PhoneEvent(id=101, source="System",   text="YOUR FILES HAVE BEEN ENCRYPTED. Send 0.5 BTC to 1FakeWallet39x to recover. Timer: 23:47:12"),
            PhoneEvent(id=102, source="SMS",      text="Netflix: Your subscription has expired. Renew now: netflix-payment-secure.xyz"),
        ],
        expected_id=101, expected_level="critical", expected_type="malware",
    ),

    "task_11_distractor_overload": _Task(
        task_id="task_11_distractor_overload",
        events=[
            PhoneEvent(id=110, source="Swiggy",  text="Your order is out for delivery! Track it live."),
            PhoneEvent(id=111, source="YouTube", text="New video from MrBeast: 'I Survived 100 Days...'"),
            PhoneEvent(id=112, source="SMS",     text="PayTM: Rs 1 credited to your wallet. Refer friends to earn more!"),
            PhoneEvent(id=113, source="SMS",     text="SBI: Dear customer, your KYC expires today. Update immediately: sbi-kyc-update.net/verify or account will be blocked."),
            PhoneEvent(id=114, source="Gmail",   text="Project brief from client — please review before EOD."),
        ],
        expected_id=113, expected_level="critical", expected_type="phishing",
    ),
}


# ── Grader ─────────────────────────────────────────────────────────

def _grade(action: IntelliNotifyAction, task: _Task) -> float:
    """
    Deterministic grader — score strictly in (0.01, 0.99).

    Weight breakdown (matches V2 proven format):
      highest_priority_id : 0.50
      threat_type         : 0.30
      threat_level        : ±0.10
      two_line_advice     : 0.10  (keyword match for threat type)
    """
    score = 0.0

    if action.highest_priority_id == task.expected_id:
        score += 0.50
    if action.threat_type == task.expected_type:
        score += 0.30
    if action.threat_level == task.expected_level:
        score += 0.10
    else:
        score -= 0.10

    # Advice quality: check for a threat-relevant keyword
    keywords = _ADVICE_KEYWORDS.get(task.expected_type, [])
    if any(kw in action.two_line_advice.lower() for kw in keywords):
        score += 0.10

    return max(0.01, min(0.99, score))


# ── Environment ────────────────────────────────────────────────────

class IntelliNotifyEnvironment(Environment):
    """
    Mobile OS notification security benchmark.
    Agent triages phone events to identify the most critical threat.
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
        self._task = (
            TASKS.get(chosen, TASKS["task_1_easy_blatant_scam"])
            if chosen
            else TASKS["task_1_easy_blatant_scam"]
        )
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
