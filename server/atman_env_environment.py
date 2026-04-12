"""ATMAN Environment v3 — context-aware mobile OS agent benchmark.

v3 additions over v2:
  - manipulation_type graded at 0.05 weight (goal weight reduced 0.20→0.15)
  - confidence_primary calibration penalty
  - reasoning_scratchpad field (ungraded, aids chain-of-thought)

Single-step episodes. Reward strictly in (0.01, 0.99). Deterministic.
"""
from typing import Dict, List, Optional
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import AtmanAction, AtmanObservation, PhoneEvent, UIElement, MemoryEntry
except ImportError:
    from models import AtmanAction, AtmanObservation, PhoneEvent, UIElement, MemoryEntry


# ── Advice keywords ────────────────────────────────────────────────
_ADVICE_KEYWORDS: Dict[str, List[str]] = {
    "phishing":        ["phishing", "fake", "scam", "fraud", "suspicious", "avoid", "block", "ignore"],
    "malware":         ["malware", "virus", "apk", "install", "permission", "unsafe", "block", "deny"],
    "financial_fraud": ["otp", "fraud", "share", "bank", "block", "report", "transaction", "suspicious"],
    "spam":            ["spam", "scam", "fake", "ignore", "delete", "block", "prize"],
    "distraction":     ["distraction", "ignore", "dismiss", "focus", "later", "postpone"],
    "none":            ["safe", "normal", "ignore", "legitimate", "benign"],
}


# ── Task definition ────────────────────────────────────────────────

class _Task:
    def __init__(
        self,
        task_id: str,
        events: List[PhoneEvent],
        user_goal: str,
        user_profile_type: str,
        battery_level: int, charging: bool, network_type: str, do_not_disturb: bool,
        current_app: str, focus_mode: bool,
        current_time: str, in_meeting: bool, deadline_hint: str,
        app_switch_rate: int, time_stuck: int, repeated_actions: int,
        screen_name: str, visible_text: List[str], ui_elements: List[UIElement],
        message_sender: str, sender_reputation: str, message_contains_link: bool,
        initial_memory: List[MemoryEntry],
        # Grading oracles
        expected_priority_id: int,
        expected_threat_type: str,
        expected_threat_level: str,
        expected_goal_alignment: str,
        expected_action_category: str,
        expected_nav_target: Optional[int],
        expected_memory_keys: List[str],
        expected_retrieved_keys: List[str],
        expected_background_queue: List[int],
        expected_manipulation_type: str,      # [NEW v3]
    ):
        self.task_id = task_id
        self.events = events
        self.user_goal = user_goal
        self.user_profile_type = user_profile_type
        self.battery_level = battery_level
        self.charging = charging
        self.network_type = network_type
        self.do_not_disturb = do_not_disturb
        self.current_app = current_app
        self.focus_mode = focus_mode
        self.current_time = current_time
        self.in_meeting = in_meeting
        self.deadline_hint = deadline_hint
        self.app_switch_rate = app_switch_rate
        self.time_stuck = time_stuck
        self.repeated_actions = repeated_actions
        self.screen_name = screen_name
        self.visible_text = visible_text
        self.ui_elements = ui_elements
        self.message_sender = message_sender
        self.sender_reputation = sender_reputation
        self.message_contains_link = message_contains_link
        self.initial_memory = initial_memory
        self.expected_priority_id = expected_priority_id
        self.expected_threat_type = expected_threat_type
        self.expected_threat_level = expected_threat_level
        self.expected_goal_alignment = expected_goal_alignment
        self.expected_action_category = expected_action_category
        self.expected_nav_target = expected_nav_target
        self.expected_memory_keys = expected_memory_keys
        self.expected_retrieved_keys = expected_retrieved_keys
        self.expected_background_queue = expected_background_queue
        self.expected_manipulation_type = expected_manipulation_type


# ── Task catalogue ─────────────────────────────────────────────────

TASKS: Dict[str, _Task] = {

    "task_1_security_goal_alignment": _Task(
        task_id="task_1_security_goal_alignment",
        events=[
            PhoneEvent(id=1, source="Gmail",  text="Mom: When are you coming home?"),
            PhoneEvent(id=2, source="SMS",    text="BANK ALERT: Click http://hdfc-verify-now.xyz to unlock account."),
            PhoneEvent(id=3, source="Swiggy", text="Your order is 5 mins away!"),
        ],
        user_goal="Reply to mom's message",
        user_profile_type="casual",
        battery_level=72, charging=False, network_type="wifi", do_not_disturb=False,
        current_app="Gmail", focus_mode=False,
        current_time="18:30", in_meeting=False, deadline_hint="none",
        app_switch_rate=1, time_stuck=10, repeated_actions=0,
        screen_name="", visible_text=[], ui_elements=[],
        message_sender="Unknown SMS", sender_reputation="low", message_contains_link=True,
        initial_memory=[],
        expected_priority_id=2,
        expected_threat_type="phishing", expected_threat_level="critical",
        expected_goal_alignment="deviating",
        expected_action_category="warn",
        expected_nav_target=None,
        expected_memory_keys=[], expected_retrieved_keys=[],
        expected_background_queue=[1],
        expected_manipulation_type="fear_induction",     # "unlock account" = fear of losing access
    ),

    "task_2_navigation_stuck": _Task(
        task_id="task_2_navigation_stuck",
        events=[
            PhoneEvent(id=10, source="System", text="Payment failed. Please retry."),
        ],
        user_goal="Complete UPI payment to landlord",
        user_profile_type="productivity_focused",
        battery_level=45, charging=True, network_type="wifi", do_not_disturb=False,
        current_app="GPay", focus_mode=False,
        current_time="10:05", in_meeting=False, deadline_hint="Rent due today",
        app_switch_rate=2, time_stuck=140, repeated_actions=4,
        screen_name="GPay — Payment Failed",
        visible_text=["Payment failed", "Try again", "Change payment method", "Contact support"],
        ui_elements=[
            UIElement(id=101, type="button", text="Try again",             clickable=True),
            UIElement(id=102, type="button", text="Change payment method", clickable=True),
            UIElement(id=103, type="menu",   text="Contact support",       clickable=True),
            UIElement(id=104, type="button", text="Go back",               clickable=True),
        ],
        message_sender="", sender_reputation="", message_contains_link=False,
        initial_memory=[],
        expected_priority_id=10,
        expected_threat_type="none", expected_threat_level="none",
        expected_goal_alignment="aligned",
        expected_action_category="assist_navigation",
        expected_nav_target=102,
        expected_memory_keys=[], expected_retrieved_keys=[],
        expected_background_queue=[],
        expected_manipulation_type="none",
    ),

    "task_3_memory_store": _Task(
        task_id="task_3_memory_store",
        events=[
            PhoneEvent(id=20, source="SMS",      text="IRCTC: PNR 4812937650 confirmed. Train 12952, 14-Apr, Dep 06:20."),
            PhoneEvent(id=21, source="Gmail",    text="Newsletter: Weekend sale up to 70% off!"),
            PhoneEvent(id=22, source="WhatsApp", text="Friend: Running late, meet at 7 instead of 6?"),
        ],
        user_goal="Save travel details for the April 14 trip",
        user_profile_type="productivity_focused",
        battery_level=88, charging=False, network_type="mobile", do_not_disturb=False,
        current_app="Messages", focus_mode=False,
        current_time="09:15", in_meeting=False, deadline_hint="none",
        app_switch_rate=1, time_stuck=5, repeated_actions=0,
        screen_name="", visible_text=[], ui_elements=[],
        message_sender="", sender_reputation="", message_contains_link=False,
        initial_memory=[],
        expected_priority_id=20,
        expected_threat_type="none", expected_threat_level="none",
        expected_goal_alignment="aligned",
        expected_action_category="no_action",
        expected_nav_target=None,
        expected_memory_keys=["pnr", "train", "travel_date"],
        expected_retrieved_keys=[],
        expected_background_queue=[22],
        expected_manipulation_type="none",
    ),

    "task_4_phishing_truncated_link": _Task(
        task_id="task_4_phishing_truncated_link",
        events=[
            PhoneEvent(id=30, source="SMS",      text="SBI: Verify account. Click bit.ly/s9Xk2"),
            PhoneEvent(id=31, source="Calendar", text="Dentist appointment tomorrow 11 AM"),
            PhoneEvent(id=32, source="Spotify",  text="New playlist: Chill Vibes 2025"),
        ],
        user_goal="Check important bank notifications",
        user_profile_type="security_sensitive",
        battery_level=60, charging=False, network_type="wifi", do_not_disturb=False,
        current_app="Messages", focus_mode=False,
        current_time="14:20", in_meeting=False, deadline_hint="none",
        app_switch_rate=0, time_stuck=20, repeated_actions=0,
        screen_name="", visible_text=[], ui_elements=[],
        message_sender="Unknown short-code", sender_reputation="low", message_contains_link=True,
        initial_memory=[],
        expected_priority_id=30,
        expected_threat_type="phishing", expected_threat_level="critical",
        expected_goal_alignment="critical_conflict",
        expected_action_category="warn",
        expected_nav_target=None,
        expected_memory_keys=[], expected_retrieved_keys=[],
        expected_background_queue=[31],
        expected_manipulation_type="goal_hijacking",     # attacker mimics SBI to exploit user's own goal
    ),

    "task_5_focus_distraction": _Task(
        task_id="task_5_focus_distraction",
        events=[
            PhoneEvent(id=40, source="YouTube",   text="New video: Top 10 funniest moments 2025"),
            PhoneEvent(id=41, source="Instagram", text="50 people liked your photo."),
            PhoneEvent(id=42, source="Gmail",     text="Client: Feedback on proposal — please review ASAP."),
        ],
        user_goal="Finish project proposal draft before 5 PM deadline",
        user_profile_type="productivity_focused",
        battery_level=55, charging=True, network_type="wifi", do_not_disturb=True,
        current_app="Google Docs", focus_mode=True,
        current_time="16:10", in_meeting=False, deadline_hint="Deadline in 50 min",
        app_switch_rate=5, time_stuck=0, repeated_actions=0,
        screen_name="", visible_text=[], ui_elements=[],
        message_sender="", sender_reputation="", message_contains_link=False,
        initial_memory=[],
        expected_priority_id=42,
        expected_threat_type="distraction", expected_threat_level="medium",
        expected_goal_alignment="deviating",
        expected_action_category="redirect",
        expected_nav_target=None,
        expected_memory_keys=[], expected_retrieved_keys=[],
        expected_background_queue=[42],
        expected_manipulation_type="reward_lure",        # YT/IG offer dopamine reward to lure away
    ),

    "task_6_financial_fraud_memory": _Task(
        task_id="task_6_financial_fraud_memory",
        events=[
            PhoneEvent(id=50, source="System",    text="Battery at 8%. Connect charger."),
            PhoneEvent(id=51, source="Clipboard", text="upi://pay?pa=scammer@fakebank&am=24999", is_clipboard=True),
            PhoneEvent(id=52, source="SMS",       text="YONO SBI: OTP 739201 for Rs 24,999. Do NOT share."),
            PhoneEvent(id=53, source="WhatsApp",  text="Unknown: Your refund is processing. Share OTP to complete."),
        ],
        user_goal="Track refund from last month's failed transaction",
        user_profile_type="security_sensitive",
        battery_level=8, charging=False, network_type="mobile", do_not_disturb=False,
        current_app="WhatsApp", focus_mode=False,
        current_time="11:45", in_meeting=True, deadline_hint="none",
        app_switch_rate=3, time_stuck=30, repeated_actions=0,
        screen_name="", visible_text=[], ui_elements=[],
        message_sender="Unknown (+91-XXXXX)", sender_reputation="low", message_contains_link=False,
        initial_memory=[
            MemoryEntry(key="refund_ref",          value="REF-20240312-88821"),
            MemoryEntry(key="official_sbi_number", value="1800-11-2211"),
        ],
        expected_priority_id=52,
        expected_threat_type="financial_fraud", expected_threat_level="critical",
        expected_goal_alignment="critical_conflict",
        expected_action_category="warn",
        expected_nav_target=None,
        expected_memory_keys=[], expected_retrieved_keys=["refund_ref", "official_sbi_number"],
        expected_background_queue=[50],
        expected_manipulation_type="goal_hijacking",     # exploits user's real refund expectation
    ),

    "task_7_memory_domain_check": _Task(
        task_id="task_7_memory_domain_check",
        events=[
            PhoneEvent(id=60, source="SMS",   text="HDFC: OTP 481920 for login. Valid 10 mins."),
            PhoneEvent(id=61, source="SMS",   text="Unknown: Enter OTP at hdfc-secure-login.net"),
            PhoneEvent(id=62, source="Gmail", text="Team standup notes attached."),
        ],
        user_goal="Login to HDFC NetBanking to check statement",
        user_profile_type="security_sensitive",
        battery_level=90, charging=True, network_type="wifi", do_not_disturb=False,
        current_app="Chrome", focus_mode=False,
        current_time="15:00", in_meeting=False, deadline_hint="none",
        app_switch_rate=1, time_stuck=15, repeated_actions=0,
        screen_name="", visible_text=[], ui_elements=[],
        message_sender="Unknown SMS", sender_reputation="low", message_contains_link=True,
        initial_memory=[
            MemoryEntry(key="official_hdfc_domain", value="netbanking.hdfcbank.com"),
            MemoryEntry(key="last_login_device",    value="Chrome on Android — trusted"),
        ],
        expected_priority_id=61,
        expected_threat_type="phishing", expected_threat_level="critical",
        expected_goal_alignment="critical_conflict",
        expected_action_category="warn",
        expected_nav_target=None,
        expected_memory_keys=[], expected_retrieved_keys=["official_hdfc_domain"],
        expected_background_queue=[62],
        expected_manipulation_type="authority_impersonation",  # fake HDFC domain
    ),

    "task_8_malware_multicontext": _Task(
        task_id="task_8_malware_multicontext",
        events=[
            PhoneEvent(id=70, source="Chrome", text="Page loaded: free-movies-hd-apk.net/download"),
            PhoneEvent(id=71, source="System", text="Install 'Netflix_Premium_Unlocked.apk' from unknown source."),
            PhoneEvent(id=72, source="System", text="App requesting Accessibility permissions."),
            PhoneEvent(id=73, source="Gmail",  text="Team standup in 10 minutes."),
        ],
        user_goal="Watch Netflix before sleep",
        user_profile_type="casual",
        battery_level=65, charging=True, network_type="wifi", do_not_disturb=False,
        current_app="Chrome", focus_mode=False,
        current_time="22:30", in_meeting=False, deadline_hint="none",
        app_switch_rate=2, time_stuck=0, repeated_actions=0,
        screen_name="", visible_text=[], ui_elements=[],
        message_sender="", sender_reputation="", message_contains_link=False,
        initial_memory=[],
        expected_priority_id=71,
        expected_threat_type="malware", expected_threat_level="critical",
        expected_goal_alignment="deviating",
        expected_action_category="warn",
        expected_nav_target=None,
        expected_memory_keys=[], expected_retrieved_keys=[],
        expected_background_queue=[73],
        expected_manipulation_type="goal_hijacking",     # fake Netflix = user's own desire weaponised
    ),

    "task_9_ransomware_high_noise": _Task(
        task_id="task_9_ransomware_high_noise",
        events=[
            PhoneEvent(id=80, source="Calendar", text="Team lunch today at 1:00 PM — Olive Garden"),
            PhoneEvent(id=81, source="Swiggy",   text="Order delivered! Rate your experience."),
            PhoneEvent(id=82, source="System",   text="YOUR FILES HAVE BEEN ENCRYPTED. Send 0.5 BTC to 1FakeWallet39x. Timer: 23:47:12"),
            PhoneEvent(id=83, source="SMS",      text="Netflix: Your subscription has expired. Renew: netflix-payment-secure.xyz"),
        ],
        user_goal="Clear notification tray before meeting",
        user_profile_type="casual",
        battery_level=40, charging=False, network_type="mobile", do_not_disturb=False,
        current_app="Home screen", focus_mode=False,
        current_time="12:45", in_meeting=False, deadline_hint="Meeting in 15 min",
        app_switch_rate=3, time_stuck=0, repeated_actions=0,
        screen_name="", visible_text=[], ui_elements=[],
        message_sender="", sender_reputation="", message_contains_link=False,
        initial_memory=[],
        expected_priority_id=82,
        expected_threat_type="malware", expected_threat_level="critical",
        expected_goal_alignment="aligned",
        expected_action_category="warn",
        expected_nav_target=None,
        expected_memory_keys=[], expected_retrieved_keys=[],
        expected_background_queue=[80],
        expected_manipulation_type="urgency_pressure",   # countdown timer = artificial urgency
    ),

    "task_10_no_threat_baseline": _Task(
        task_id="task_10_no_threat_baseline",
        events=[
            PhoneEvent(id=90, source="Gmail",    text="Amazon: Your order #AZ-3829 has shipped. Arriving Thursday."),
            PhoneEvent(id=91, source="Calendar", text="Mom's birthday — tomorrow"),
            PhoneEvent(id=92, source="WhatsApp", text="Dad: Don't forget to eat dinner."),
        ],
        user_goal="Check today's reminders",
        user_profile_type="casual",
        battery_level=80, charging=False, network_type="wifi", do_not_disturb=False,
        current_app="Home screen", focus_mode=False,
        current_time="20:00", in_meeting=False, deadline_hint="none",
        app_switch_rate=1, time_stuck=5, repeated_actions=0,
        screen_name="", visible_text=[], ui_elements=[],
        message_sender="", sender_reputation="", message_contains_link=False,
        initial_memory=[],
        expected_priority_id=91,
        expected_threat_type="none", expected_threat_level="none",
        expected_goal_alignment="aligned",
        expected_action_category="no_action",
        expected_nav_target=None,
        expected_memory_keys=[], expected_retrieved_keys=[],
        expected_background_queue=[90, 92],
        expected_manipulation_type="none",
    ),

    "task_11_impersonation_deadline": _Task(
        task_id="task_11_impersonation_deadline",
        events=[
            PhoneEvent(id=100, source="Instagram", text="@cricket_fan liked your post."),
            PhoneEvent(id=101, source="WhatsApp",  text="Unknown (+91-XXXXX): Bro this is Rahul new number. Emergency send Rs 5000 on GPay will return tonight."),
            PhoneEvent(id=102, source="Gmail",     text="HR: Please submit your timesheet by 5 PM today."),
        ],
        user_goal="Wrap up work tasks before end of day",
        user_profile_type="productivity_focused",
        battery_level=50, charging=False, network_type="wifi", do_not_disturb=False,
        current_app="Gmail", focus_mode=False,
        current_time="16:30", in_meeting=False, deadline_hint="Deadline in 30 min",
        app_switch_rate=2, time_stuck=0, repeated_actions=0,
        screen_name="", visible_text=[], ui_elements=[],
        message_sender="Unknown (+91-XXXXX)", sender_reputation="low", message_contains_link=False,
        initial_memory=[],
        expected_priority_id=101,
        expected_threat_type="financial_fraud", expected_threat_level="high",
        expected_goal_alignment="deviating",
        expected_action_category="warn",
        expected_nav_target=None,
        expected_memory_keys=[], expected_retrieved_keys=[],
        expected_background_queue=[102],
        expected_manipulation_type="trust_exploitation",  # pretends to be known contact "Rahul"
    ),
}


# ── Grader ─────────────────────────────────────────────────────────

def _score_security(action: AtmanAction, task: _Task) -> float:
    """0.30: priority_id(0.16) + threat_type(0.09) + threat_level(±0.03) + advice_kw(0.02)"""
    score = 0.0
    if action.highest_priority_id == task.expected_priority_id:
        score += 0.16
    if action.threat_type == task.expected_threat_type:
        score += 0.09
    score += 0.03 if action.threat_level == task.expected_threat_level else -0.03
    keywords = _ADVICE_KEYWORDS.get(task.expected_threat_type, [])
    if any(kw in action.two_line_advice.lower() for kw in keywords):
        score += 0.02
    return max(0.0, score)


def _score_goal(action: AtmanAction, task: _Task) -> float:
    """0.15 (reduced from v2's 0.20 to make room for manipulation_type)."""
    if action.goal_alignment == task.expected_goal_alignment:
        return 0.15
    adjacent = {
        ("aligned",           "deviating"):          0.06,
        ("deviating",         "aligned"):             0.06,
        ("deviating",         "critical_conflict"):   0.04,
        ("critical_conflict", "deviating"):           0.04,
        ("aligned",           "critical_conflict"):   0.0,
        ("critical_conflict", "aligned"):             0.0,
    }
    return adjacent.get((task.expected_goal_alignment, action.goal_alignment), 0.0)


def _score_behavior(action: AtmanAction, task: _Task) -> float:
    """0.15: action_category match."""
    if action.action_category == task.expected_action_category:
        return 0.15
    close = {
        ("warn",              "prioritize"):          0.06,
        ("prioritize",        "warn"):                0.06,
        ("assist_navigation", "redirect"):            0.06,
        ("redirect",          "assist_navigation"):   0.06,
        ("no_action",         "prioritize"):          0.04,
    }
    return close.get((task.expected_action_category, action.action_category), 0.0)


def _score_navigation(action: AtmanAction, task: _Task) -> float:
    """0.10: correct UI element targeted."""
    if task.expected_nav_target is None:
        return 0.10 if action.target_element_id is None else 0.02
    return 0.10 if action.target_element_id == task.expected_nav_target else 0.0


def _score_memory(action: AtmanAction, task: _Task) -> float:
    """0.15: memory_store(0.08) + retrieval_refs(0.04) + background_queue(0.03)."""
    score = 0.0

    stored = {e.key.lower() for e in action.memory_store}
    if task.expected_memory_keys:
        expected = {k.lower() for k in task.expected_memory_keys}
        hits = len(stored & expected)
        fps = len(stored - expected)
        score += max(0.0, (hits / len(expected)) * 0.08 - fps * 0.02)
    else:
        score += 0.04 if not stored else 0.0

    if task.expected_retrieved_keys:
        mem_values = {e.value.lower() for e in task.initial_memory}
        advice_lower = action.two_line_advice.lower()
        referenced = sum(1 for v in mem_values if any(w in advice_lower for w in v.split()))
        score += min(0.04, (referenced / max(len(task.expected_retrieved_keys), 1)) * 0.04)
    else:
        score += 0.02

    expected_q = set(task.expected_background_queue)
    actual_q = set(action.background_queue)
    actual_q.discard(task.expected_priority_id)
    if expected_q:
        hits_q = len(actual_q & expected_q)
        fps_q = len(actual_q - expected_q)
        score += max(0.0, (hits_q / len(expected_q)) * 0.03 - fps_q * 0.01)
    else:
        score += 0.015 if not actual_q else 0.0

    return min(0.15, score)


def _score_manipulation(action: AtmanAction, task: _Task) -> float:
    """[NEW v3] 0.05: manipulation_type exact match."""
    return 0.05 if action.manipulation_type == task.expected_manipulation_type else 0.0


def _score_query_baseline() -> float:
    """0.10: full baseline awarded to valid terminal actions."""
    return 0.10


def _penalties(action: AtmanAction, task: _Task) -> float:
    """Hard penalties."""
    penalty = 0.0

    # Ignoring a critical threat
    if task.expected_threat_level == "critical" and action.action_category == "ignore":
        penalty += 0.50

    # Severity gap ≥ 3 levels
    order = ["none", "low", "medium", "high", "critical"]
    try:
        if abs(order.index(task.expected_threat_level) - order.index(action.threat_level)) >= 3:
            penalty += 0.10
    except ValueError:
        pass

    # Distraction promoted in focus mode
    if task.focus_mode and action.action_category == "prioritize" and action.threat_type == "distraction":
        penalty += 0.20

    # [NEW v3] Calibration penalty: high confidence on wrong priority_id
    if action.confidence_primary > 0.85 and action.highest_priority_id != task.expected_priority_id:
        penalty += 0.04

    return penalty


def _grade(action: AtmanAction, task: _Task) -> float:
    """
    v3 reward weights (sum = 1.00):
      security        0.30
      goal_alignment  0.15  (was 0.20 in v2)
      behavior        0.15
      navigation      0.10
      memory          0.15
      manipulation    0.05  (new in v3)
      query_baseline  0.10
    Clamped to (0.01, 0.99).
    """
    base = (
        _score_security(action, task)
        + _score_goal(action, task)
        + _score_behavior(action, task)
        + _score_navigation(action, task)
        + _score_memory(action, task)
        + _score_manipulation(action, task)
        + _score_query_baseline()
    )
    return max(0.01, min(0.99, base - _penalties(action, task)))


# ── Environment ────────────────────────────────────────────────────

class AtmanEnvironment(Environment):
    """ATMAN v3. Single-step, phase-2 compatible."""
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        super().__init__()
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task: Optional[_Task] = None
        self._done = False

    def _build_obs(self, done: bool, reward=None, feedback=None) -> AtmanObservation:
        t = self._task
        return AtmanObservation(
            step_number=self._state.step_count,
            total_steps=1,
            events=t.events,
            last_action_feedback=feedback,
            task_id=t.task_id,
            done=done,
            reward=reward,
            user_goal=t.user_goal,
            user_profile_type=t.user_profile_type,
            battery_level=t.battery_level,
            charging=t.charging,
            network_type=t.network_type,
            do_not_disturb=t.do_not_disturb,
            current_app=t.current_app,
            focus_mode=t.focus_mode,
            current_time=t.current_time,
            in_meeting=t.in_meeting,
            deadline_hint=t.deadline_hint,
            app_switch_rate=t.app_switch_rate,
            time_stuck=t.time_stuck,
            repeated_actions=t.repeated_actions,
            screen_name=t.screen_name,
            visible_text=t.visible_text,
            ui_elements=t.ui_elements,
            message_sender=t.message_sender,
            sender_reputation=t.sender_reputation,
            message_contains_link=t.message_contains_link,
            initial_memory=t.initial_memory,
        )

    def reset(self, seed=None, episode_id=None, task_id=None, task=None, **kwargs) -> AtmanObservation:
        chosen = task_id or task
        self._task = (
            TASKS.get(chosen, TASKS["task_1_security_goal_alignment"])
            if chosen else TASKS["task_1_security_goal_alignment"]
        )
        self._done = False
        self._state = State(episode_id=episode_id or str(uuid4()), step_count=0)
        return self._build_obs(done=False)

    def step(self, action: AtmanAction) -> AtmanObservation:  # type: ignore[override]
        if self._task is None or self._done:
            return AtmanObservation(
                step_number=1, total_steps=1, events=[],
                last_action_feedback="Call reset() first.",
                task_id=None, done=True, reward=0.05,
            )
        score = _grade(action, self._task)
        self._done = True
        self._state.step_count += 1
        return self._build_obs(done=True, reward=score, feedback=f"Score: {score:.2f}")

    @property
    def state(self) -> State:
        return self._state

    def close(self):
        pass
