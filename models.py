"""Data models for the ATMAN Environment v3.

Three additions over v2:
  1. reasoning_scratchpad  — ungraded chain-of-thought field (Action)
  2. confidence_primary / confidence_advice — split confidence for calibration grading
  3. manipulation_type — psychological attack vector classification (graded)

All new fields have defaults. Single-step episodes. Phase 2 compatible.
"""
from typing import List, Literal, Optional
from openenv.core.env_server.types import Action, Observation
from pydantic import BaseModel, Field


# ── Sub-models ─────────────────────────────────────────────────────

class PhoneEvent(BaseModel):
    id: int = Field(..., description="Unique event ID")
    source: str = Field(..., description="App or system source")
    text: str = Field(..., description="Notification content")
    is_clipboard: bool = Field(default=False)


class UIElement(BaseModel):
    id: int = Field(default=0)
    type: str = Field(default="button")
    text: str = Field(default="")
    clickable: bool = Field(default=True)


class MemoryEntry(BaseModel):
    key: str = Field(default="")
    value: str = Field(default="")


# ── Observation (unchanged from v2) ────────────────────────────────

class AtmanObservation(Observation):
    # Core
    step_number: int = Field(default=0)
    total_steps: int = Field(default=1)
    events: List[PhoneEvent] = Field(default_factory=list)
    last_action_feedback: Optional[str] = Field(default=None)
    task_id: Optional[str] = Field(default=None)

    # User context
    user_goal: str = Field(default="")
    user_profile_type: str = Field(default="casual")

    # Device context
    battery_level: int = Field(default=100)
    charging: bool = Field(default=False)
    network_type: str = Field(default="wifi")
    do_not_disturb: bool = Field(default=False)

    # App context
    current_app: str = Field(default="")
    focus_mode: bool = Field(default=False)

    # Temporal context
    current_time: str = Field(default="")
    in_meeting: bool = Field(default=False)
    deadline_hint: str = Field(default="none")

    # Behaviour signals
    app_switch_rate: int = Field(default=0)
    time_stuck: int = Field(default=0)
    repeated_actions: int = Field(default=0)

    # UI context
    screen_name: str = Field(default="")
    visible_text: List[str] = Field(default_factory=list)
    ui_elements: List[UIElement] = Field(default_factory=list)

    # Message context
    message_sender: str = Field(default="")
    sender_reputation: str = Field(default="")
    message_contains_link: bool = Field(default=False)

    # Memory
    initial_memory: List[MemoryEntry] = Field(default_factory=list)


# ── Action ─────────────────────────────────────────────────────────

class AtmanAction(Action):
    """
    Single-step action with three v3 additions:

    [NEW #1] reasoning_scratchpad
      Free-text field for chain-of-thought before committing to final answer.
      Never scored — exists purely to improve agent reasoning quality.
      Write threat links, credibility weights, what-if outcomes here.

    [NEW #2] confidence_primary / confidence_advice
      Replaces the single `confidence` float.
      Grader applies extra penalty for high-confidence wrong answers:
        confidence_primary > 0.85 AND wrong priority_id → −0.04
      This trains agents toward calibrated uncertainty.

    [NEW #3] manipulation_type
      Psychological attack vector beyond technical threat_type.
      Graded at 0.05 weight — rewards agents that detect HOW an attack
      manipulates the user, not just WHAT the threat is.
    """

    # ── Core security (required) ───────────────────────────────────
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

    # ── Goal + behaviour (required) ────────────────────────────────
    goal_alignment: Literal["aligned", "deviating", "critical_conflict"] = Field(
        default="aligned"
    )
    action_category: Literal[
        "warn", "prioritize", "assist_navigation",
        "redirect", "ignore", "no_action"
    ] = Field(default="warn")

    # ── Navigation (optional) ──────────────────────────────────────
    target_element_id: Optional[int] = Field(default=None)

    # ── Memory output (optional) ───────────────────────────────────
    memory_store: List[MemoryEntry] = Field(default_factory=list)

    # ── Background queue (from v3 IntelliNotify lineage) ──────────
    background_queue: List[int] = Field(
        default_factory=list,
        description="Event IDs deferred for background processing — not threats, not noise"
    )

    # ── [NEW #1] Shadow reasoning scratchpad ───────────────────────
    reasoning_scratchpad: str = Field(
        default="",
        description=(
            "Ungraded chain-of-thought. Write internal analysis here before "
            "committing to final fields. Suggested structure: "
            "(1) list each event's risk signal, "
            "(2) note source credibility, "
            "(3) identify threat links between events, "
            "(4) simulate user outcomes if threat is ignored."
        )
    )

    # ── [NEW #2] Split confidence (replaces single float) ─────────
    confidence_primary: float = Field(
        default=1.0, ge=0.0, le=1.0,
        description=(
            "Confidence in highest_priority_id selection (0–1). "
            "High confidence on wrong answer incurs extra penalty — "
            "calibrate honestly."
        )
    )
    confidence_advice: float = Field(
        default=1.0, ge=0.0, le=1.0,
        description="Confidence in two_line_advice quality (0–1)."
    )

    # ── [NEW #3] Manipulation type ─────────────────────────────────
    manipulation_type: Literal[
        "none",
        "urgency_pressure",      # artificial time pressure ("expires in 10 min")
        "authority_impersonation", # pretends to be bank/govt/employer
        "fear_induction",         # threatens negative outcome if ignored
        "reward_lure",            # promises prize/refund/benefit
        "trust_exploitation",     # exploits existing relationship (fake Rahul)
        "goal_hijacking",         # mirrors user's real goal to seem legitimate
    ] = Field(
        default="none",
        description=(
            "Psychological attack vector used by the threat. "
            "Captures HOW the attacker manipulates — not just WHAT the threat is. "
            "Score: 0.05 weight. Graded exactly."
        )
    )

    reason_code: str = Field(
        default="SECURITY",
        description="SECURITY | PRODUCTIVITY | SAFETY | NAVIGATION | MEMORY"
    )
