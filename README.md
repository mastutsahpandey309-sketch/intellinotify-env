---
title: IntelliNotify
emoji: 🔔
colorFrom: red
colorTo: yellow
sdk: docker
pinned: false
tags:
  - openenv
---

# IntelliNotify — OpenEnv Security Environment

A mobile OS notification security benchmark where an AI agent triages phone events to identify threats like phishing, financial fraud, and malware.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Returns `{"status": "healthy"}` |
| `/metadata` | GET | Environment name and description |
| `/schema` | GET | Action/observation JSON schemas |
| `/tasks` | GET | All 5 tasks with grader info |
| `/reset` | POST | Start episode, returns events |
| `/step` | POST | Grade action, returns reward ∈ (0.01, 0.99) |
| `/state` | GET | Current episode state |
| `/grade` | POST | Direct grader access |

## Action Space

```json
{
  "highest_priority_id": 3,
  "threat_level": "high",
  "threat_type": "spam",
  "two_line_advice": "Do not click. This is a scam."
}
```

## Scoring

| Component | Weight |
|---|---|
| Correct priority ID | +0.50 |
| Correct threat type | +0.30 |
| Correct threat level | +0.10 / -0.10 |
| Valid advice (10-150 chars) | +0.10 |

## Tasks

| ID | Difficulty |
|---|---|
| task_1_easy_blatant_scam | Easy |
| task_2_medium_productivity_vs_security | Medium |
| task_3_hard_multi_vector | Hard |
| task_4_medium_fake_bank_alert | Medium |
| task_5_hard_malware_install | Hard |

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```
