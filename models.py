"""Data models for the ATMAN Environment.

Structural rule: single-step episodes only (same as IntelliNotify v3).
All ATMAN features (goal alignment, memory, navigation, context) are
delivered as flat fields on Action and Observation — no multi-step,
no intermediate done=False returns that break the phase 2 validator.
"""
from typing import List, Literal, Optional
from openenv.core.env_server.types import Action, Observation
from pydantic import BaseModel, Field


# ── Sub-models (all fields have defaults — safe for serialization) ─

class PhoneEvent(BaseModel):
    id: int = Field(..., description="Unique event ID")
    source: str = Field(..., description="App or system source")
    text: str = Field(..., description="Notification content")
    is_clipboard: bool = Field(default=False)


class UIElement(BaseModel):
    id: int = Field(default=0)
    type: str = Field(default="button")       # button | menu | input
    text: str = Field(default="")
    clickable: bool = Field(default=True)


class MemoryEntry(BaseModel):
    """A single key-value item in the agent's memory."""
    key: str = Field(default="")
    value: str = Field(default="")


# ── Observation ────────────────────────────────────────────────────

class AtmanObservation(Observation):
    """
    Full contextual observation. Extends v3 with flat context fields.
    All new fields have defaults so the base schema is never broken.
    """

    # Core (same as v3)
    step_number: int = Field(default=0)
    total_steps: int = Field(default=1)
    events: List[PhoneEvent] = Field(default_factory=list)
    last_action_feedback: Optional[str] = Field(default=None)
    task_id: Optional[str] = Field(default=None)

    # ── User context ───────────────────────────────────────────────
    user_goal: str = Field(default="")
    user_profile_type: str = Field(default="casual")   # security_sensitive | productivity_focused | casual

    # ── Device context (flat) ──────────────────────────────────────
    battery_level: int = Field(default=100)
    charging: bool = Field(default=False)
    network_type: str = Field(default="wifi")          # wifi | mobile | offline
    do_not_disturb: bool = Field(default=False)

    # ── App context (flat) ─────────────────────────────────────────
    current_app: str = Field(default="")
    focus_mode: bool = Field(default=False)

    # ── Temporal context (flat) ────────────────────────────────────
    current_time: str = Field(default="")              # HH:MM
    in_meeting: bool = Field(default=False)
    deadline_hint: str = Field(default="none")

    # ── Behaviour signals (flat) ───────────────────────────────────
    app_switch_rate: int = Field(default=0)            # switches per minute
    time_stuck: int = Field(default=0)                 # seconds on same screen
    repeated_actions: int = Field(default=0)           # same tap repeated

    # ── UI context (flat) ──────────────────────────────────────────
    screen_name: str = Field(default="")
    visible_text: List[str] = Field(default_factory=list)
    ui_elements: List[UIElement] = Field(default_factory=list)

    # ── Message context (flat) ─────────────────────────────────────
    message_sender: str = Field(default="")
    sender_reputation: str = Field(default="")        # high | medium | low
    message_contains_link: bool = Field(default=False)

    # ── Memory the agent can read and build on ─────────────────────
    initial_memory: List[MemoryEntry] = Field(
        default_factory=list,
        description="Key-value pairs from prior context the agent should use"
    )


# ── Action ─────────────────────────────────────────────────────────

class AtmanAction(Action):
    """
    Single-step action. Covers all ATMAN dimensions in one response.

    Required (no default):
      highest_priority_id — primary threat/event to act on
      threat_level, threat_type, two_line_advice — security classification
      goal_alignment — agent's assessment of how events relate to user goal

    Optional (all have defaults):
      action_category — what kind of response this is
      target_element_id — UI element to navigate to (navigation tasks)
      memory_store — key/value pairs agent wants to save
      background_queue — relevant events deferred for background processing
      confidence, reason_code — meta fields
    """

    # ── Core security (required — same contract as v3) ─────────────
    highest_priority_id: int = Field(
        ...,
        description="ID of the most critical event requiring immediate attention"
    )
    threat_level: Literal["none", "low", "medium", "high", "critical"]
    threat_type: Literal[
        "none", "phishing", "malware", "distraction",
        "spam", "financial_fraud"
    ]
    two_line_advice: str = Field(
        ...,
        description="Actionable advice under 150 chars; must contain a threat-relevant keyword"
    )

    # ── Goal alignment (new — required for ATMAN) ──────────────────
    goal_alignment: Literal["aligned", "deviating", "critical_conflict"] = Field(
        default="aligned",
        description="How the top threat relates to the user's stated goal"
    )

    # ── Action category (new — optional with default) ──────────────
    action_category: Literal[
        "warn", "prioritize", "assist_navigation",
        "redirect", "ignore", "no_action"
    ] = Field(
        default="warn",
        description="What the agent is doing in response"
    )

    # ── Navigation (new — optional with default) ───────────────────
    target_element_id: Optional[int] = Field(
        default=None,
        description="UI element ID to navigate to (navigation tasks only)"
    )

    # ── Memory output (new — optional with default) ────────────────
    memory_store: List[MemoryEntry] = Field(
        default_factory=list,
        description=(
            "Key-value pairs the agent wants to save for future reference. "
            "Store task-relevant info only (e.g. PNR numbers, official domains). "
            "Graded: correct stores rewarded, irrelevant or missing penalised."
        )
    )

    # ── Background queue (from v3 — preserved exactly) ────────────
    background_queue: List[int] = Field(
        default_factory=list,
        description=(
            "IDs of lower-priority but relevant events to process later in background. "
            "Exclude the top threat and pure noise."
        )
    )

    # ── Meta (optional with defaults) ─────────────────────────────
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reason_code: str = Field(
        default="SECURITY",
        description="SECURITY | PRODUCTIVITY | SAFETY | NAVIGATION | MEMORY"
    )
