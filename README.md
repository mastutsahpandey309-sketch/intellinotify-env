---
title: ATMAN
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
tags:
  - openenv
---

# ATMAN — Context-Aware Mobile OS Agent Benchmark

ATMAN extends IntelliNotify with full device/user/temporal context, multi-step
interaction, memory store/retrieve, and goal-alignment grading.

## Tasks (8 total)

| ID | Task | Steps | Key Skill |
|----|------|-------|-----------|
| task_1_security_goal_alignment | Phishing SMS while user does legitimate task | 1 | Security + Goal |
| task_2_navigation_stuck | User looping on failed payment screen | 1 | Navigation |
| task_3_memory_store | Save travel PNR details from SMS | 2 | Memory store |
| task_4_ask_then_classify | Truncated link — query then classify | 2 | Ask → classify |
| task_5_focus_distraction | Distraction during deadline focus mode | 1 | Goal conflict |
| task_6_financial_fraud_complex | OTP + clipboard + in-meeting fraud | 2 | Multi-context |
| task_7_memory_retrieve_and_act | Use stored domain to catch phishing | 2 | Memory retrieve |
| task_8_no_threat_baseline | All-benign — false-positive guard | 1 | None-threat |

## Episode Flow

```
reset(task_id=...) → Observation
  ↓ (optional step 1)
step(ask | store | retrieve) → Updated Observation + extra_info
  ↓ (step 2 / only step)
step(final | warn | prioritize | ...) → Graded Observation + reward
```

Max 2 steps per episode. Only 1 intermediate action allowed.

## Reward Function

```
reward = goal_alignment  * 0.30
       + behavior        * 0.15
       + security        * 0.20
       + navigation      * 0.10
       + memory          * 0.15   (store + retrieve + background_queue)
       + query_efficiency* 0.10
       − penalties
```

### Penalties
| Violation | Penalty |
|-----------|---------|
| Ignore a critical-level threat | −0.50 |
| Severity off by 3+ levels | −0.10 |
| Unnecessary query (task didn't need ask) | −0.10 |
| Promote distraction while in focus mode | −0.20 |
| Wrong memory storage (irrelevant key) | −0.02 per item |

All rewards clamped to (0.01, 0.99).

## Action Space

```json
{
  "action_type": "prioritize|ignore|redirect|assist_navigation|warn|store|retrieve|ask|final",
  "target_id": null,
  "threat_type": "none|phishing|malware|distraction|spam|financial_fraud",
  "threat_level": "none|low|medium|high|critical",
  "goal_alignment": "aligned|deviating|critical_conflict",
  "memory_key": null,
  "memory_value": null,
  "query_type": "full_url|sender_details|full_message|ui_details",
  "confidence": 0.95,
  "reason_code": "SECURITY|PRODUCTIVITY|SAFETY|NAVIGATION|MEMORY",
  "message": "Do not share OTP — active financial fraud attempt.",
  "background_queue": [31, 62]
}
```

## Observation Includes

- `events` — phone notifications (with clipboard flag)
- `user_goal` — what user is trying to accomplish
- `user_profile_type` — security_sensitive | productivity_focused | casual
- `device_context` — battery, network, DND
- `app_context` — current app, focus mode
- `temporal_context` — time, meeting status, deadline
- `behavior_signals` — app_switch_rate, time_stuck, repeated_actions
- `ui_context` — screen name, visible text, tappable elements
- `message_context` — message text, sender reputation, link presence
- `memory` — agent's accumulated memory for this episode
- `extra_info` — populated after ask / retrieve actions
