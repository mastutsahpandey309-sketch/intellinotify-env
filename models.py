"""Data models for the ATMAN Environment."""
from typing import Dict, List, Literal, Optional
from openenv.core.env_server.types import Action, Observation
from pydantic import BaseModel, Field


# ── Context sub-models ─────────────────────────────────────────────

class DeviceContext(BaseModel):
    battery_level: int = Field(..., ge=0, le=100)
    charging: bool
    network_type: Literal["wifi", "mobile", "offline"]
    do_not_disturb: bool


class AppContext(BaseModel):
    current_app: str
    focus_mode: bool


class TemporalContext(BaseModel):
    current_time: str          # "HH:MM"
    in_meeting: bool
    deadline_hint: str         # e.g. "Deadline in 45 min" or "none"


class BehaviorSignals(BaseModel):
    app_switch_rate: int       # switches per minute (high → distraction/confusion)
    time_stuck: int            # seconds on same screen (high → navigation help needed)
    repeated_actions: int      # same action repeated (high → confusion)


class UIElement(BaseModel):
    id: int
    type: Literal["button", "menu", "input"]
    text: str
    clickable: bool


class UIContext(BaseModel):
    screen_name: str
    visible_text: List[str]
    ui_elements: List[UIElement]


class MessageContext(BaseModel):
    message_text: str
    sender: str
    sender_reputation: Literal["high", "medium", "low"]
    contains_link: bool


class HistoryContext(BaseModel):
    recent_actions: List[str]
    time_spent: int            # seconds in current session


class MemoryItem(BaseModel):
    key: str
    value: str


# ── Phone event (carried from IntelliNotify) ──────────────────────

class PhoneEvent(BaseModel):
    id: int
    source: str
    text: str
    is_clipboard: bool = False


# ── Observation ────────────────────────────────────────────────────

class AtmanObservation(Observation):
    """Full contextual observation presented to the agent each step."""
    step_number: int = Field(default=1)
    total_steps: int = Field(default=2)

    # Core events
    events: List[PhoneEvent] = Field(default_factory=list)

    # User context
    user_goal: str = ""
    user_profile_type: Literal[
        "security_sensitive", "productivity_focused", "casual"
    ] = "casual"

    # Device / app / temporal context
    device_context: Optional[DeviceContext] = None
    app_context: Optional[AppContext] = None
    temporal_context: Optional[TemporalContext] = None

    # Behavioural signals
    behavior_signals: Optional[BehaviorSignals] = None

    # UI & message context (task-specific)
    ui_context: Optional[UIContext] = None
    message_context: Optional[MessageContext] = None

    # Session history
    history: Optional[HistoryContext] = None

    # Agent's in-episode memory (grows as agent stores items)
    memory: List[MemoryItem] = Field(default_factory=list)

    # Populated by environment after an "ask" query
    extra_info: Optional[str] = None

    last_action_feedback: Optional[str] = None
    task_id: Optional[str] = None


# ── Action ─────────────────────────────────────────────────────────

class AtmanAction(Action):
    """
    Unified action space.

    Intermediate actions (step 1 only):
      ask      — query hidden task data once
      store    — commit a key/value pair to episode memory
      retrieve — signal use of an existing memory key

    Terminal action (always ends episode):
      final    — full threat + goal + navigation classification

    Other action types (also terminal):
      prioritize | ignore | warn | redirect | assist_navigation
    """

    action_type: Literal[
        "prioritize", "ignore", "redirect", "assist_navigation",
        "warn", "store", "retrieve", "ask", "final"
    ]

    # Navigation / event targeting
    target_id: Optional[int] = Field(
        default=None,
        description="Event ID or UI element ID being acted on"
    )

    # Security classification (required on final / warn / prioritize)
    threat_type: Literal[
        "none", "phishing", "malware", "distraction",
        "spam", "financial_fraud"
    ] = "none"
    threat_level: Literal[
        "none", "low", "medium", "high", "critical"
    ] = "none"

    # Goal alignment assessment
    goal_alignment: Literal[
        "aligned", "deviating", "critical_conflict"
    ] = "aligned"

    # Memory operation fields
    memory_key: Optional[str] = None
    memory_value: Optional[str] = None

    # Ask query type
    query_type: Optional[Literal[
        "full_url", "sender_details", "full_message", "ui_details"
    ]] = None

    # Meta
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reason_code: Literal[
        "SECURITY", "PRODUCTIVITY", "SAFETY", "NAVIGATION", "MEMORY"
    ] = "SECURITY"
    message: str = Field(
        default="",
        description="Human-readable rationale, max 150 chars"
    )

    # Deferred-but-relevant events (from IntelliNotify lineage)
    background_queue: List[int] = Field(
        default_factory=list,
        description="Event IDs deferred for background processing (not threats, not noise)"
    )
