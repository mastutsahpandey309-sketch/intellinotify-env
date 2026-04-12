"""ATMAN Environment — context-aware mobile OS agent benchmark."""
from typing import Dict, List, Optional
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import (
        AtmanAction, AtmanObservation,
        PhoneEvent, DeviceContext, AppContext, TemporalContext,
        BehaviorSignals, UIElement, UIContext, MessageContext,
        HistoryContext, MemoryItem,
    )
except ImportError:
    from models import (
        AtmanAction, AtmanObservation,
        PhoneEvent, DeviceContext, AppContext, TemporalContext,
        BehaviorSignals, UIElement, UIContext, MessageContext,
        HistoryContext, MemoryItem,
    )


# ── Advice keywords (inherited from IntelliNotify) ─────────────────
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
        device_context: DeviceContext,
        app_context: AppContext,
        temporal_context: TemporalContext,
        behavior_signals: BehaviorSignals,
        history: HistoryContext,
        # optional rich context
        ui_context: Optional[UIContext],
        message_context: Optional[MessageContext],
        # initial memory agent can read from step 1
        initial_memory: List[MemoryItem],
        # expected outputs for grading
        expected_action_type: str,
        expected_goal_alignment: str,
        expected_navigation_target: Optional[int],  # UI element id
        expected_security_label: str,               # threat_type
        expected_security_level: str,               # threat_level
        expected_memory_keys: List[str],            # keys agent MUST store
        expected_retrieved_keys: List[str],         # keys agent MUST retrieve
        expected_background_queue: List[int],
        # multi-step support
        hidden_data: Dict[str, str],  # keyed by query_type
        requires_ask: bool,
        max_steps: int = 2,
    ):
        self.task_id = task_id
        self.events = events
        self.user_goal = user_goal
        self.user_profile_type = user_profile_type
        self.device_context = device_context
        self.app_context = app_context
        self.temporal_context = temporal_context
        self.behavior_signals = behavior_signals
        self.history = history
        self.ui_context = ui_context
        self.message_context = message_context
        self.initial_memory = initial_memory
        self.expected_action_type = expected_action_type
        self.expected_goal_alignment = expected_goal_alignment
        self.expected_navigation_target = expected_navigation_target
        self.expected_security_label = expected_security_label
        self.expected_security_level = expected_security_level
        self.expected_memory_keys = expected_memory_keys
        self.expected_retrieved_keys = expected_retrieved_keys
        self.expected_background_queue = expected_background_queue
        self.hidden_data = hidden_data
        self.requires_ask = requires_ask
        self.max_steps = max_steps


# ── Task catalogue ─────────────────────────────────────────────────

TASKS: Dict[str, _Task] = {

    # ── Task 1: Security + Goal alignment (easy, 1-step) ──────────
    "task_1_security_goal_alignment": _Task(
        task_id="task_1_security_goal_alignment",
        events=[
            PhoneEvent(id=1, source="Gmail",   text="Mom: When are you coming home?"),
            PhoneEvent(id=2, source="SMS",     text="BANK ALERT: Click http://hdfc-verify-now.xyz to unlock account."),
            PhoneEvent(id=3, source="Swiggy",  text="Your order is 5 mins away!"),
        ],
        user_goal="Reply to mom's message",
        user_profile_type="casual",
        device_context=DeviceContext(battery_level=72, charging=False, network_type="wifi", do_not_disturb=False),
        app_context=AppContext(current_app="Gmail", focus_mode=False),
        temporal_context=TemporalContext(current_time="18:30", in_meeting=False, deadline_hint="none"),
        behavior_signals=BehaviorSignals(app_switch_rate=1, time_stuck=10, repeated_actions=0),
        history=HistoryContext(recent_actions=["opened Gmail"], time_spent=30),
        ui_context=None,
        message_context=MessageContext(
            message_text="Click http://hdfc-verify-now.xyz to unlock account.",
            sender="Unknown SMS",
            sender_reputation="low",
            contains_link=True,
        ),
        initial_memory=[],
        expected_action_type="warn",
        expected_goal_alignment="aligned",
        expected_navigation_target=None,
        expected_security_label="phishing",
        expected_security_level="critical",
        expected_memory_keys=[],
        expected_retrieved_keys=[],
        expected_background_queue=[1],   # mom's message — defer, not discard
        hidden_data={},
        requires_ask=False,
        max_steps=1,
    ),

    # ── Task 2: Navigation assistance (stuck user, 1-step) ────────
    "task_2_navigation_stuck": _Task(
        task_id="task_2_navigation_stuck",
        events=[
            PhoneEvent(id=10, source="System", text="Payment failed. Please retry."),
        ],
        user_goal="Complete UPI payment to landlord",
        user_profile_type="productivity_focused",
        device_context=DeviceContext(battery_level=45, charging=True, network_type="wifi", do_not_disturb=False),
        app_context=AppContext(current_app="GPay", focus_mode=False),
        temporal_context=TemporalContext(current_time="10:05", in_meeting=False, deadline_hint="Rent due today"),
        behavior_signals=BehaviorSignals(app_switch_rate=2, time_stuck=140, repeated_actions=4),
        history=HistoryContext(recent_actions=["tap pay", "tap pay", "tap pay", "tap pay"], time_spent=210),
        ui_context=UIContext(
            screen_name="GPay — Payment Failed",
            visible_text=["Payment failed", "Try again", "Change payment method", "Contact support"],
            ui_elements=[
                UIElement(id=101, type="button", text="Try again",              clickable=True),
                UIElement(id=102, type="button", text="Change payment method",  clickable=True),
                UIElement(id=103, type="menu",   text="Contact support",        clickable=True),
                UIElement(id=104, type="button", text="Go back",                clickable=True),
            ],
        ),
        message_context=None,
        initial_memory=[],
        expected_action_type="assist_navigation",
        expected_goal_alignment="aligned",
        expected_navigation_target=102,   # Change payment method — correct fix for repeated failure
        expected_security_label="none",
        expected_security_level="none",
        expected_memory_keys=[],
        expected_retrieved_keys=[],
        expected_background_queue=[],
        hidden_data={
            "ui_details": "Button 101 (Try again) has failed 4 consecutive times. Button 102 allows switching to a different UPI-linked bank.",
        },
        requires_ask=False,
        max_steps=1,
    ),

    # ── Task 3: Memory store (important info, 2-step: store → final)
    "task_3_memory_store": _Task(
        task_id="task_3_memory_store",
        events=[
            PhoneEvent(id=20, source="SMS",   text="IRCTC: Your ticket PNR 4812937650 is confirmed. Train 12952, 14-Apr."),
            PhoneEvent(id=21, source="Gmail", text="Newsletter: Weekend sale up to 70% off!"),
            PhoneEvent(id=22, source="WhatsApp", text="Friend: Running late, meet at 7 instead of 6?"),
        ],
        user_goal="Save travel details for the trip on April 14",
        user_profile_type="productivity_focused",
        device_context=DeviceContext(battery_level=88, charging=False, network_type="mobile", do_not_disturb=False),
        app_context=AppContext(current_app="Messages", focus_mode=False),
        temporal_context=TemporalContext(current_time="09:15", in_meeting=False, deadline_hint="none"),
        behavior_signals=BehaviorSignals(app_switch_rate=1, time_stuck=5, repeated_actions=0),
        history=HistoryContext(recent_actions=["opened Messages"], time_spent=20),
        ui_context=None,
        message_context=None,
        initial_memory=[],
        expected_action_type="store",
        expected_goal_alignment="aligned",
        expected_navigation_target=None,
        expected_security_label="none",
        expected_security_level="none",
        expected_memory_keys=["pnr", "train", "travel_date"],   # any subset counts
        expected_retrieved_keys=[],
        expected_background_queue=[22],  # friend's rescheduling message — relevant
        hidden_data={},
        requires_ask=False,
        max_steps=2,
    ),

    # ── Task 4: Ask → final (truncated link, 2-step) ───────────────
    "task_4_ask_then_classify": _Task(
        task_id="task_4_ask_then_classify",
        events=[
            PhoneEvent(id=30, source="SMS",     text="SBI: Verify account. Click bit.ly/s9Xk2"),
            PhoneEvent(id=31, source="Calendar", text="Dentist appointment tomorrow 11 AM"),
            PhoneEvent(id=32, source="Spotify",  text="New playlist: Chill Vibes 2025"),
        ],
        user_goal="Check important bank notifications",
        user_profile_type="security_sensitive",
        device_context=DeviceContext(battery_level=60, charging=False, network_type="wifi", do_not_disturb=False),
        app_context=AppContext(current_app="Messages", focus_mode=False),
        temporal_context=TemporalContext(current_time="14:20", in_meeting=False, deadline_hint="none"),
        behavior_signals=BehaviorSignals(app_switch_rate=0, time_stuck=20, repeated_actions=0),
        history=HistoryContext(recent_actions=["opened SMS app"], time_spent=45),
        ui_context=None,
        message_context=MessageContext(
            message_text="Verify account. Click bit.ly/s9Xk2",
            sender="Unknown short-code",
            sender_reputation="low",
            contains_link=True,
        ),
        initial_memory=[],
        expected_action_type="final",
        expected_goal_alignment="aligned",
        expected_navigation_target=None,
        expected_security_label="phishing",
        expected_security_level="critical",
        expected_memory_keys=[],
        expected_retrieved_keys=[],
        expected_background_queue=[31],   # dentist appointment — relevant, defer
        hidden_data={
            "full_url": "http://sbi-account-verify-login.fraudsite.ru/reactivate?token=STEAL",
            "sender_details": "Sender: +91-SPOOFED-9988. Not registered with SBI TRAI DLT.",
        },
        requires_ask=True,
        max_steps=2,
    ),

    # ── Task 5: Focus mode — distraction penalty (1-step) ─────────
    "task_5_focus_distraction": _Task(
        task_id="task_5_focus_distraction",
        events=[
            PhoneEvent(id=40, source="YouTube",  text="New video: Top 10 funniest moments 2025"),
            PhoneEvent(id=41, source="Instagram", text="50 people liked your photo."),
            PhoneEvent(id=42, source="Gmail",     text="Client: Feedback on proposal — please review ASAP."),
        ],
        user_goal="Finish project proposal draft before 5 PM deadline",
        user_profile_type="productivity_focused",
        device_context=DeviceContext(battery_level=55, charging=True, network_type="wifi", do_not_disturb=True),
        app_context=AppContext(current_app="Google Docs", focus_mode=True),
        temporal_context=TemporalContext(current_time="16:10", in_meeting=False, deadline_hint="Deadline in 50 min"),
        behavior_signals=BehaviorSignals(app_switch_rate=5, time_stuck=0, repeated_actions=0),
        history=HistoryContext(recent_actions=["editing document", "switched to YouTube", "switched back"], time_spent=1800),
        ui_context=None,
        message_context=None,
        initial_memory=[],
        expected_action_type="prioritize",
        expected_goal_alignment="aligned",
        expected_navigation_target=None,
        expected_security_label="distraction",
        expected_security_level="medium",
        expected_memory_keys=[],
        expected_retrieved_keys=[],
        expected_background_queue=[42],   # client email is real but non-threatening — defer
        hidden_data={},
        requires_ask=False,
        max_steps=1,
    ),

    # ── Task 6: Financial fraud — multi-context (hard, 2-step) ─────
    "task_6_financial_fraud_complex": _Task(
        task_id="task_6_financial_fraud_complex",
        events=[
            PhoneEvent(id=50, source="System",    text="Battery at 8%. Connect charger."),
            PhoneEvent(id=51, source="Clipboard", text="upi://pay?pa=scammer@fakebank&am=24999", is_clipboard=True),
            PhoneEvent(id=52, source="SMS",       text="YONO SBI: OTP 739201 for Rs 24,999. Do NOT share."),
            PhoneEvent(id=53, source="WhatsApp",  text="Unknown: Your refund is processing. Share OTP to complete."),
        ],
        user_goal="Track refund from last month's failed transaction",
        user_profile_type="security_sensitive",
        device_context=DeviceContext(battery_level=8, charging=False, network_type="mobile", do_not_disturb=False),
        app_context=AppContext(current_app="WhatsApp", focus_mode=False),
        temporal_context=TemporalContext(current_time="11:45", in_meeting=True, deadline_hint="none"),
        behavior_signals=BehaviorSignals(app_switch_rate=3, time_stuck=30, repeated_actions=0),
        history=HistoryContext(recent_actions=["opened WhatsApp", "checked clipboard"], time_spent=90),
        ui_context=None,
        message_context=MessageContext(
            message_text="Your refund is processing. Share OTP to complete.",
            sender="Unknown (+91-XXXXX)",
            sender_reputation="low",
            contains_link=False,
        ),
        initial_memory=[
            MemoryItem(key="refund_ref", value="REF-20240312-88821"),  # legitimate refund ref agent already knows
        ],
        expected_action_type="warn",
        expected_goal_alignment="critical_conflict",   # user goal is being exploited as social engineering hook
        expected_navigation_target=None,
        expected_security_label="financial_fraud",
        expected_security_level="critical",
        expected_memory_keys=[],
        expected_retrieved_keys=["refund_ref"],         # agent should retrieve to verify legitimacy claim
        expected_background_queue=[50],                  # battery warning — real system event, defer
        hidden_data={
            "sender_details": "Sender not in contacts. Number recently registered. No association with any bank.",
            "full_message": "Hi, your refund REF-20240312-00000 is being processed. Share your OTP 739201 to verify identity and receive funds.",
        },
        requires_ask=True,
        max_steps=2,
    ),

    # ── Task 7: Retrieve memory → classify (2-step) ────────────────
    "task_7_memory_retrieve_and_act": _Task(
        task_id="task_7_memory_retrieve_and_act",
        events=[
            PhoneEvent(id=60, source="SMS",     text="HDFC: OTP 481920 for login. Valid 10 mins."),
            PhoneEvent(id=61, source="SMS",     text="Unknown: Enter OTP on hdfc-secure-login.net to complete verification."),
            PhoneEvent(id=62, source="Gmail",   text="Team: Notes from today's standup attached."),
        ],
        user_goal="Login to HDFC NetBanking to check statement",
        user_profile_type="security_sensitive",
        device_context=DeviceContext(battery_level=90, charging=True, network_type="wifi", do_not_disturb=False),
        app_context=AppContext(current_app="Chrome", focus_mode=False),
        temporal_context=TemporalContext(current_time="15:00", in_meeting=False, deadline_hint="none"),
        behavior_signals=BehaviorSignals(app_switch_rate=1, time_stuck=15, repeated_actions=0),
        history=HistoryContext(recent_actions=["opened Chrome", "navigated to HDFC"], time_spent=60),
        ui_context=None,
        message_context=MessageContext(
            message_text="Enter OTP on hdfc-secure-login.net to complete verification.",
            sender="Unknown SMS",
            sender_reputation="low",
            contains_link=True,
        ),
        initial_memory=[
            MemoryItem(key="official_hdfc_domain", value="netbanking.hdfcbank.com"),
            MemoryItem(key="last_login_device",     value="Chrome on Android — trusted"),
        ],
        expected_action_type="final",
        expected_goal_alignment="critical_conflict",   # OTP being requested by fake site = active attack on current goal
        expected_navigation_target=None,
        expected_security_label="phishing",
        expected_security_level="critical",
        expected_memory_keys=[],
        expected_retrieved_keys=["official_hdfc_domain"],   # compare stored domain vs message domain
        expected_background_queue=[62],                      # standup notes — relevant work
        hidden_data={
            "full_url": "http://hdfc-secure-login.net/otp?redirect=steal",
            "sender_details": "Sender spoofed SBI short-code. Not in TRAI DLT whitelist.",
        },
        requires_ask=True,
        max_steps=2,
    ),

    # ── Task 8: All-benign false-positive guard (1-step) ──────────
    "task_8_no_threat_baseline": _Task(
        task_id="task_8_no_threat_baseline",
        events=[
            PhoneEvent(id=70, source="Gmail",    text="Amazon: Your order #AZ-3829 has shipped. Arriving Thursday."),
            PhoneEvent(id=71, source="Calendar", text="Mom's birthday — tomorrow"),
            PhoneEvent(id=72, source="WhatsApp", text="Dad: Don't forget to eat dinner."),
        ],
        user_goal="Check today's reminders",
        user_profile_type="casual",
        device_context=DeviceContext(battery_level=80, charging=False, network_type="wifi", do_not_disturb=False),
        app_context=AppContext(current_app="Home screen", focus_mode=False),
        temporal_context=TemporalContext(current_time="20:00", in_meeting=False, deadline_hint="none"),
        behavior_signals=BehaviorSignals(app_switch_rate=1, time_stuck=5, repeated_actions=0),
        history=HistoryContext(recent_actions=["unlocked phone"], time_spent=10),
        ui_context=None,
        message_context=None,
        initial_memory=[],
        expected_action_type="final",
        expected_goal_alignment="aligned",
        expected_navigation_target=None,
        expected_security_label="none",
        expected_security_level="none",
        expected_memory_keys=[],
        expected_retrieved_keys=[],
        expected_background_queue=[70, 72],  # order tracking + dad's message — relevant
        hidden_data={},
        requires_ask=False,
        max_steps=1,
    ),
}


# ── Grader ─────────────────────────────────────────────────────────

def _goal_alignment_score(action: AtmanAction, task: _Task) -> float:
    """0.30 — did agent correctly assess goal alignment?"""
    if action.goal_alignment == task.expected_goal_alignment:
        return 0.30
    # Partial: deviating vs aligned is less wrong than critical_conflict vs aligned
    diff = {
        ("aligned", "deviating"): 0.10,
        ("deviating", "aligned"): 0.10,
        ("critical_conflict", "aligned"): 0.0,
        ("aligned", "critical_conflict"): 0.0,
        ("critical_conflict", "deviating"): 0.05,
        ("deviating", "critical_conflict"): 0.05,
    }
    return diff.get((task.expected_goal_alignment, action.goal_alignment), 0.0)


def _behavior_score(action: AtmanAction, task: _Task) -> float:
    """0.15 — did agent choose the right action_type given behavioral signals?"""
    if action.action_type == task.expected_action_type:
        return 0.15
    # Close matches get partial
    close = {
        ("assist_navigation", "prioritize"): 0.05,
        ("warn", "prioritize"): 0.08,
        ("prioritize", "warn"): 0.08,
        ("final", "prioritize"): 0.05,
        ("final", "warn"): 0.05,
    }
    return close.get((task.expected_action_type, action.action_type), 0.0)


def _security_score(action: AtmanAction, task: _Task) -> float:
    """0.20 — correct threat type + level, with keyword check on message."""
    score = 0.0
    if action.threat_type == task.expected_security_label:
        score += 0.12
    if action.threat_level == task.expected_security_level:
        score += 0.05
    else:
        score -= 0.05
    # Keyword check on message
    keywords = _ADVICE_KEYWORDS.get(task.expected_security_label, [])
    if any(kw in action.message.lower() for kw in keywords):
        score += 0.03
    return max(0.0, score)


def _navigation_score(action: AtmanAction, task: _Task) -> float:
    """0.10 — correct UI element targeted (or correctly absent)."""
    if task.expected_navigation_target is None:
        # No navigation needed — penalise if agent targeted something
        return 0.10 if action.target_id is None else 0.0
    if action.target_id == task.expected_navigation_target:
        return 0.10
    return 0.0


def _memory_score(
    action: AtmanAction,
    task: _Task,
    stored_keys: List[str],
    retrieved_keys: List[str],
) -> float:
    """
    0.15 — memory + background queue combined.
      store accuracy  : 0.08
      retrieve accuracy: 0.04
      background_queue: 0.03
    """
    score = 0.0

    # Store scoring
    if task.expected_memory_keys:
        expected_set = set(task.expected_memory_keys)
        stored_set = set(stored_keys)
        hits = len(stored_set & expected_set)
        fps = len(stored_set - expected_set)
        store_raw = (hits / len(expected_set)) * 0.08 - fps * 0.02
        score += max(0.0, store_raw)
    else:
        # Nothing should be stored — reward clean episode
        score += 0.04 if not stored_keys else 0.0

    # Retrieve scoring
    if task.expected_retrieved_keys:
        expected_r = set(task.expected_retrieved_keys)
        retrieved_r = set(retrieved_keys)
        hits_r = len(retrieved_r & expected_r)
        fps_r = len(retrieved_r - expected_r)
        ret_raw = (hits_r / len(expected_r)) * 0.04 - fps_r * 0.01
        score += max(0.0, ret_raw)
    else:
        score += 0.02 if not retrieved_keys else 0.0

    # Background queue (from final action)
    expected_q = set(task.expected_background_queue)
    actual_q = set(q for q in action.background_queue if q != task.expected_background_queue)
    # Simpler: just check overlap
    actual_q_clean = set(action.background_queue)
    if expected_q:
        hits_q = len(actual_q_clean & expected_q)
        fps_q = len(actual_q_clean - expected_q)
        q_raw = (hits_q / len(expected_q)) * 0.03 - fps_q * 0.01
        score += max(0.0, q_raw)
    else:
        score += 0.015 if not actual_q_clean else 0.0

    return min(0.15, score)


def _query_efficiency_score(asked: bool, task: _Task) -> float:
    """0.10 — was the ask action used appropriately?"""
    if task.requires_ask:
        return 0.10 if asked else 0.0
    else:
        return 0.10 if not asked else 0.0   # unnecessary query penalised here


def _penalties(action: AtmanAction, task: _Task) -> float:
    """Apply hard penalties after base score computed."""
    penalty = 0.0
    # Ignoring a critical threat
    if (task.expected_security_level == "critical"
            and action.action_type == "ignore"):
        penalty += 0.50
    # Severely wrong severity
    severity_order = ["none", "low", "medium", "high", "critical"]
    try:
        exp_idx = severity_order.index(task.expected_security_level)
        act_idx = severity_order.index(action.threat_level)
        if abs(exp_idx - act_idx) >= 3:
            penalty += 0.10
    except ValueError:
        pass
    # Promoting distraction while in focus mode
    focus = task.app_context.focus_mode if task.app_context else False
    if focus and action.action_type == "prioritize" and action.threat_type == "distraction":
        penalty += 0.20
    return penalty


def _grade(
    action: AtmanAction,
    task: _Task,
    asked: bool,
    stored_keys: List[str],
    retrieved_keys: List[str],
) -> float:
    """
    Final reward = weighted sum of component scores − penalties.
    Strictly clamped to (0.01, 0.99).
    """
    goal    = _goal_alignment_score(action, task)       # 0.30
    behav   = _behavior_score(action, task)             # 0.15
    sec     = _security_score(action, task)             # 0.20
    nav     = _navigation_score(action, task)           # 0.10
    mem     = _memory_score(action, task, stored_keys, retrieved_keys)  # 0.15
    query   = _query_efficiency_score(asked, task)      # 0.10

    base = goal + behav + sec + nav + mem + query
    pen  = _penalties(action, task)

    return max(0.01, min(0.99, base - pen))


# ── Environment ────────────────────────────────────────────────────

class AtmanEnvironment(Environment):
    """
    ATMAN: Context-Aware Mobile OS Agent Benchmark.

    Tests goal alignment, threat detection, navigation assistance,
    smart memory use, and background queue scheduling — all graded
    deterministically against predefined task oracles.

    Episode flow:
      reset() → Observation
      step(intermediate_action) → Updated Observation   [optional, max 1]
      step(final_action) → Graded Observation with reward
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        super().__init__()
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task: Optional[_Task] = None
        self._done = False
        self._asked = False
        self._stored_keys: List[str] = []
        self._retrieved_keys: List[str] = []
        self._episode_memory: List[MemoryItem] = []

    # ── Observation builder ────────────────────────────────────────

    def _build_obs(
        self,
        step: int,
        feedback: Optional[str] = None,
        extra_info: Optional[str] = None,
        done: bool = False,
        reward: Optional[float] = None,
    ) -> AtmanObservation:
        t = self._task
        return AtmanObservation(
            step_number=step,
            total_steps=t.max_steps,
            events=t.events,
            user_goal=t.user_goal,
            user_profile_type=t.user_profile_type,
            device_context=t.device_context,
            app_context=t.app_context,
            temporal_context=t.temporal_context,
            behavior_signals=t.behavior_signals,
            ui_context=t.ui_context,
            message_context=t.message_context,
            history=t.history,
            memory=t.initial_memory + self._episode_memory,
            extra_info=extra_info,
            last_action_feedback=feedback,
            task_id=t.task_id,
            done=done,
            reward=reward,
        )

    # ── OpenEnv interface ──────────────────────────────────────────

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task_id: Optional[str] = None,
        task: Optional[str] = None,
        **kwargs,
    ) -> AtmanObservation:
        chosen = task_id or task
        self._task = (
            TASKS.get(chosen, TASKS["task_1_security_goal_alignment"])
            if chosen
            else TASKS["task_1_security_goal_alignment"]
        )
        self._done = False
        self._asked = False
        self._stored_keys = []
        self._retrieved_keys = []
        self._episode_memory = []
        self._state = State(episode_id=episode_id or str(uuid4()), step_count=0)

        return self._build_obs(step=1, done=False)

    def step(self, action: AtmanAction) -> AtmanObservation:  # type: ignore[override]
        if self._task is None or self._done:
            return AtmanObservation(
                step_number=1, total_steps=1, events=[],
                last_action_feedback="Call reset() first.",
                task_id=None, done=True, reward=0.05,
            )

        self._state.step_count += 1
        step = self._state.step_count

        # ── Intermediate: ask ──────────────────────────────────────
        if action.action_type == "ask" and step < self._task.max_steps:
            if self._asked:
                return self._build_obs(
                    step=step,
                    feedback="Only one query allowed per episode.",
                    done=False,
                )
            self._asked = True
            qt = action.query_type or "full_url"
            info = self._task.hidden_data.get(qt, "No data available for that query type.")
            return self._build_obs(
                step=step + 1,
                feedback=f"Query answered ({qt}).",
                extra_info=info,
                done=False,
            )

        # ── Intermediate: store ────────────────────────────────────
        if action.action_type == "store" and step < self._task.max_steps:
            if action.memory_key and action.memory_value:
                self._episode_memory.append(
                    MemoryItem(key=action.memory_key, value=action.memory_value)
                )
                self._stored_keys.append(action.memory_key)
                feedback = f"Stored '{action.memory_key}'."
            else:
                feedback = "store requires memory_key and memory_value."
            return self._build_obs(step=step + 1, feedback=feedback, done=False)

        # ── Intermediate: retrieve ─────────────────────────────────
        if action.action_type == "retrieve" and step < self._task.max_steps:
            if action.memory_key:
                self._retrieved_keys.append(action.memory_key)
                all_mem = {m.key: m.value for m in (self._task.initial_memory + self._episode_memory)}
                val = all_mem.get(action.memory_key, "Key not found in memory.")
                feedback = f"Retrieved '{action.memory_key}'."
                return self._build_obs(step=step + 1, feedback=feedback, extra_info=val, done=False)
            return self._build_obs(step=step + 1, feedback="retrieve requires memory_key.", done=False)

        # ── Terminal: grade ────────────────────────────────────────
        score = _grade(
            action=action,
            task=self._task,
            asked=self._asked,
            stored_keys=self._stored_keys,
            retrieved_keys=self._retrieved_keys,
        )
        self._done = True

        return self._build_obs(
            step=step,
            feedback=f"Score: {score:.2f}",
            done=True,
            reward=score,
        )

    @property
    def state(self) -> State:
        return self._state

    def close(self):
        pass
