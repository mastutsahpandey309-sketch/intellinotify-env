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

Mobile OS notification security benchmark. Agent triages phone events to identify threats **and** schedules relevant-but-deferred events for background processing.

## Tasks (11 total, easy → hard)

| ID | Task | Difficulty |
|----|------|------------|
| task_1_easy_blatant_scam | Obvious prize scam SMS | Easy |
| task_2_medium_productivity_vs_security | Phishing vs real work urgency | Medium |
| task_3_hard_multi_vector | Clipboard hijack + OTP + browser | Hard |
| task_4_medium_fake_bank_alert | Fake debit alert + OTP share | Medium |
| task_5_hard_malware_install | APK from unknown source + permissions | Hard |
| task_6_fake_2fa_prompt | Fake Google 2FA SMS | Medium |
| task_7_whatsapp_impersonation | Unknown number financial ask | Medium |
| task_8_fake_app_update | Fake Flash Player APK | Hard |
| task_9_none_all_benign | No threats — false-positive test | Medium |
| task_10_ransomware | File encryption ransom demand | Hard |
| task_11_distractor_overload | 5 events, high-noise distraction | Hard |

## Scoring (reward strictly in 0.01–0.99)

| Component | Weight | Notes |
|-----------|--------|-------|
| `highest_priority_id` | 0.40 | Exact match on correct event ID |
| `threat_type` | 0.25 | Exact match on threat category |
| `threat_level` | ±0.08 | +0.08 correct, −0.08 wrong |
| `two_line_advice` keyword | 0.07 | Any single threat-relevant keyword present |
| `background_queue` | 0–0.20 | Partial credit; penalises false positives |

### Background Queue
Agent must populate `background_queue` with IDs of events that are:
- **Relevant** (not noise/spam)
- **Not the primary threat**
- **Deferred** — safe to process later when idle

Grading: `(hits / expected) × 0.20 − 0.05 × false_positives`. Queuing the threat itself is penalised.
