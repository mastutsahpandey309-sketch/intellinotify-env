"""
IntelliNotify baseline inference script.
Reads API_BASE_URL, MODEL_NAME, HF_TOKEN from env vars.
Uses OpenAI client. Emits [START], [STEP], [END] logs.
"""
import asyncio
import os
import json
import textwrap
import httpx
from typing import List, Optional
from openai import OpenAI

# ── Config ─────────────────────────────────────────────────────────
API_KEY      = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or "no-key"
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME   = os.getenv("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860").rstrip("/")
TEMPERATURE  = 0.2
SUCCESS_THRESHOLD = 0.5

ALL_TASKS = [
    "task_1_easy_blatant_scam",
    "task_2_medium_productivity_vs_security",
    "task_3_hard_multi_vector",
    "task_4_medium_fake_bank_alert",
    "task_5_hard_malware_install",
]

SYSTEM_PROMPT = textwrap.dedent("""
    You are an AI Context Manager for a mobile operating system.
    Analyse the phone events and identify the single most critical security threat.
    Output ONLY valid JSON with this exact schema:
    {
        "highest_priority_id": <int>,
        "threat_level": <"none"|"low"|"medium"|"high"|"critical">,
        "threat_type": <"none"|"phishing"|"malware"|"distraction"|"spam"|"financial_fraud">,
        "two_line_advice": "<string under 150 chars>"
    }
""").strip()

# ── Loggers ────────────────────────────────────────────────────────
def log_start(task: str, model: str) -> None:
    print(f"[START] task={task} env=intellinotify model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    clean = action.replace("\n", " ").replace("\r", "")
    err   = error if error else "null"
    print(f"[STEP] step={step} action={clean} reward={reward:.2f} done={str(done).lower()} error={err}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    r_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={r_str}", flush=True)

# ── LLM call ───────────────────────────────────────────────────────
def get_action(client: OpenAI, obs: dict) -> dict:
    prompt = f"Phone events:\n{json.dumps(obs, indent=2)}\n\nProvide your JSON action."
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=TEMPERATURE,
        )
        text = (resp.choices[0].message.content or "").strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as exc:
        print(f"[DEBUG] LLM error: {exc}", flush=True)
        return {
            "highest_priority_id": -1,
            "threat_level": "none",
            "threat_type": "none",
            "two_line_advice": "Could not process. Please review manually.",
        }

# ── Single task run ────────────────────────────────────────────────
async def run_task(client: OpenAI, task_id: str) -> float:
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0

    log_start(task=task_id, model=MODEL_NAME)

    try:
        async with httpx.AsyncClient(timeout=30.0) as http:
            # Reset
            r = await http.post(f"{ENV_BASE_URL}/reset", json={"task_id": task_id})
            r.raise_for_status()
            obs = r.json().get("observation", r.json())

            for step in range(1, 3):          # single-step tasks — max 2 attempts
                action_dict = get_action(client, obs)
                action_str  = json.dumps(action_dict, separators=(",", ":"))

                s = await http.post(f"{ENV_BASE_URL}/step", json={"action": action_dict})
                data   = s.json()
                reward = float(data.get("reward") or 0.0)
                done   = data.get("done", True)
                error  = data.get("info", {}).get("error") if isinstance(data.get("info"), dict) else None
                obs    = data.get("observation", {})

                rewards.append(reward)
                steps_taken = step
                log_step(step=step, action=action_str, reward=reward, done=done, error=error)

                if done:
                    break

        score   = sum(rewards) / len(rewards) if rewards else 0.0
        score   = max(0.0, min(1.0, score))
        success = score >= SUCCESS_THRESHOLD

    except Exception as exc:
        print(f"[DEBUG] Task error: {exc}", flush=True)
        success = False

    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return score

# ── Main ───────────────────────────────────────────────────────────
async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    scores = []
    for task_id in ALL_TASKS:
        score = await run_task(client, task_id)
        scores.append(score)
        print(f"[SUMMARY] task={task_id} score={score:.3f}", flush=True)

    avg = sum(scores) / len(scores) if scores else 0.0
    print(f"[SUMMARY] overall_avg={avg:.3f} tasks={len(scores)}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
