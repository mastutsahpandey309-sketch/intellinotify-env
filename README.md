---
title: IntelliNotify
emoji: 🔔
colorFrom: red
colorTo: yellow
sdk: docker
pinned: false
---

# IntelliNotify — OpenEnv Security Environment

A mobile OS notification security benchmark where an AI agent acts as a context manager, triaging a real-time queue of phone events to identify threats (phishing, financial fraud, spam) amid benign distractions.

## Environment

**Endpoint:** `POST /reset` → `POST /step` (repeat) → done

**Observation:** A list of `PhoneEvent` objects (notifications, SMS, clipboard contents).

**Action (JSON):**
```json
{
  "highest_priority_id": 3,
  "threat_level": "high",
  "threat_type": "phishing",
  "two_line_advice": "Do not click the link. It is a scam."
}
```

## Scoring (per step, max 1.0)
| Component | Weight |
|---|---|
| Correct priority ID | +0.5 |
| Correct threat type | +0.3 |
| Correct threat level | +0.1 (−0.1 if wrong) |
| Valid advice (10–150 chars) | +0.1 |

## Tasks
| ID | Difficulty | Description |
|---|---|---|
| `task_1_easy_blatant_scam` | Easy | Obvious spam SMS mixed with normal notifications |
| `task_2_medium_productivity_vs_security` | Medium | Phishing link vs urgent work email |
| `task_3_hard_multi_vector` | Hard | Clipboard UPI fraud + OTP correlation attack |

## Running locally
```bash
pip install -e .
server  # starts on port 7860
```
