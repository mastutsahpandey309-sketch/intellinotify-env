---
title: ATMAN
emoji: 🧠
colorFrom: indigo
colorTo: cyan
sdk: docker
pinned: false
tags:
  - openenv
---

# ATMAN — Context-Aware Mobile OS Agent Benchmark

ATMAN extends IntelliNotify v3 with full device/user/temporal context,
goal alignment grading, memory store/retrieve, UI navigation, and
behavioural signal awareness — all in single-step episodes that are
fully compatible with the OpenEnv phase 2 validator.

## Tasks (11 total, easy → hard)

| ID | Task | Key Skill |
|----|------|-----------|
| task_1_security_goal_alignment | Phishing SMS while user has legit goal | Security + Goal |
| task_2_navigation_stuck | User looping on failed GPay screen | Navigation |
| task_3_memory_store | Save IRCTC PNR from SMS | Memory store |
| task_4_phishing_truncated_link | Short URL phishing, security_sensitive user | Threat + Goal conflict |
| task_5_focus_distraction | Distraction during deadline + client email | Focus + Priority |
| task_6_financial_fraud_memory | OTP + clipboard + memory cross-reference | Multi-context + Memory |
| task_7_memory_domain_check | Stored domain vs fake login site | Memory retrieval |
| task_8_malware_multicontext | Fake APK while user wants Netflix | Malware + Goal |
| task_9_ransomware_high_noise | Ransomware buried in 4 events | High-noise triage |
| task_10_no_threat_baseline | All-benign — false-positive guard | None-threat |
| task_11_impersonation_deadline | WhatsApp impersonation near deadline | Financial fraud |

## Reward Function (weights sum to 1.00)

```
reward = security(0.30) + goal_alignment(0.20) + action_category(0.15)
       + navigation(0.10) + memory(0.15) + query_baseline(0.10)
       − penalties
```

### Security (0.30)
- priority_id exact match: +0.16
- threat_type exact match: +0.09
- threat_level exact match: ±0.03
- advice keyword match: +0.02

### Goal Alignment (0.20)
- Exact: 0.20 | Adjacent miss: 0.05–0.08 | Severe miss: 0.00

### Behaviour / Action Category (0.15)
- Exact: 0.15 | Close match: 0.06 | Wrong: 0.00

### Navigation (0.10)
- Correct UI element targeted: 0.10
- No navigation needed + none given: 0.10

### Memory (0.15)
- memory_store: correct keys earn up to 0.08; false keys penalised −0.02 each
- Memory retrieval (advice references initial_memory values): up to 0.04
- background_queue: up to 0.03; false positives −0.01 each

### Penalties
| Violation | Penalty |
|-----------|---------|
| Ignore a critical-level threat | −0.50 |
| Severity gap ≥ 3 levels | −0.10 |
| Promote distraction in focus mode | −0.20 |
| Irrelevant memory_store entry | −0.02 per item |

All rewards clamped to (0.01, 0.99).

## Episode Flow (single-step, phase-2 compatible)

```
reset(task_id=...) → AtmanObservation
step(AtmanAction)  → AtmanObservation (done=True, reward=float)
```

## Action Schema

```json
{
  "highest_priority_id": 52,
  "threat_level": "critical",
  "threat_type": "financial_fraud",
  "two_line_advice": "OTP fraud — never share. Block sender immediately.",
  "goal_alignment": "critical_conflict",
  "action_category": "warn",
  "target_element_id": null,
  "memory_store": [],
  "background_queue": [50],
  "confidence": 0.97,
  "reason_code": "SECURITY"
}
```

## Observation Includes

| Field | Description |
|-------|-------------|
| events | Phone notifications (with clipboard flag) |
| user_goal | What the user is trying to accomplish |
| user_profile_type | security_sensitive / productivity_focused / casual |
| battery_level, charging, network_type, do_not_disturb | Device state |
| current_app, focus_mode | App context |
| current_time, in_meeting, deadline_hint | Temporal context |
| app_switch_rate, time_stuck, repeated_actions | Behaviour signals |
| screen_name, visible_text, ui_elements | UI context |
| message_sender, sender_reputation, message_contains_link | Message context |
| initial_memory | Pre-loaded key-value memory agent can reference |
