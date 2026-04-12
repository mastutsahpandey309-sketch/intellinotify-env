---
title: ATMAN
emoji: 🛡️
colorFrom: blue
colorTo: cyan
sdk: docker
pinned: false
tags:
  - openenv
---

# ATMAN — Context-Aware Mobile OS Agent Benchmark

ATMAN (Adaptive Threat Management & Notification) is an OpenEnv-compatible benchmark for evaluating AI agents that act as a mobile OS context manager. The agent observes phone events, user goals, device state, and memory, then classifies threats and selects appropriate actions.

## Tasks (8 total, easy → hard)

| ID | Description | Steps | Difficulty |
|----|-------------|-------|------------|
| task_1_security_goal_alignment | Phishing SMS alongside benign notifications — warn & align | 1 | Easy |
| task_2_navigation_stuck | Repeated UPI payment failure — guide user to correct button | 1 | Easy |
| task_3_memory_store | Travel PNR arrives — store key details before replying | 2 | Medium |
| task_4_ask_then_classify | Truncated bank link — query full URL then classify as phishing | 2 | Medium |
| task_5_focus_distraction | Focus mode active — distraction notification should be deprioritised | 1 | Medium |
| task_6_financial_fraud_complex | Suspicious refund request with UPI clipboard — query & classify | 2 | Hard |
| task_7_memory_retrieve_and_act | OTP SMS + stored device-lock context — retrieve memory, then classify | 2 | Hard |
| task_8_no_threat_baseline | All-benign notifications — false-positive guard, no action needed | 1 | Medium |

## Action Space

| `action_type` | When to use |
|---------------|-------------|
| `warn` | Threat detected, alert user |
| `prioritize` | Surface important (non-threat) event |
| `ignore` | Dismiss noise |
| `redirect` | Route to correct app/screen |
| `assist_navigation` | Guide stuck user to correct UI element |
| `store` | Commit a key/value pair to episode memory (intermediate) |
| `retrieve` | Read a memory key (intermediate) |
| `ask` | Query hidden task data once (intermediate) |
| `final` | Full terminal classification |

## Scoring (reward strictly in 0.01–0.99)

| Component | Max Weight | Notes |
|-----------|-----------|-------|
| Goal alignment | 0.30 | aligned / deviating / critical_conflict |
| Behaviour match | 0.15 | Correct action_type selection |
| Security classification | 0.20 | threat_type + threat_level accuracy |
| Navigation targeting | 0.10 | Correct target_id when navigating |
| Memory operations | 0.15 | Store / retrieve accuracy; penalises false positives |
| Query efficiency | 0.10 | Reward asking when required; penalise unnecessary asks |

All component scores are summed, penalties applied, then clamped to (0.01, 0.99).

### Penalties
- Ignoring a critical threat: -0.50
- Threat level off by 3 or more severity steps: -0.10
- Promoting distraction in focus mode: -0.20
