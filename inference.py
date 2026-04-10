import asyncio
import os
import json
import textwrap
import httpx
from typing import List, Optional
from openai import OpenAI

# -------------------------------------------------------------------
# Configuration & Environment Variables
# -------------------------------------------------------------------
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860").rstrip("/")
TASK_NAME = os.getenv("TASK_NAME", "task_2_medium_productivity_vs_security")
BENCHMARK = "intellinotify"

MAX_STEPS = 5
TEMPERATURE = 0.2 # Low temp for structured JSON tasks
SUCCESS_SCORE_THRESHOLD = 0.5

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an AI Context Manager for a mobile operating system.
    You will be given a list of current phone events/notifications. 
    Your job is to identify the single most critical event (prioritizing security and fraud over productivity) and output a JSON response.
    
    You MUST output ONLY valid JSON matching this schema exactly:
    {
        "highest_priority_id": <int>,
        "threat_level": <"none"|"low"|"medium"|"high"|"critical">,
        "threat_type": <"none"|"phishing"|"malware"|"distraction"|"spam"|"financial_fraud">,
        "two_line_advice": "<string under 150 chars>"
    }
    """
).strip()

# -------------------------------------------------------------------
# Strict STDOUT Loggers
# -------------------------------------------------------------------
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    # Ensure action string has no newlines
    clean_action = action.replace('\n', ' ').replace('\r', '')
    print(
        f"[STEP] step={step} action={clean_action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

# -------------------------------------------------------------------
# LLM Interaction
# -------------------------------------------------------------------
def get_model_action(client: OpenAI, obs_data: dict) -> dict:
    user_prompt = f"Current Phone State:\n{json.dumps(obs_data, indent=2)}\n\nProvide your JSON action."
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            response_format={"type": "json_object"} if "gpt" in MODEL_NAME.lower() else None
        )
        text = (completion.choices[0].message.content or "").strip()
        
        # Attempt to parse JSON safely
        # Strip markdown code blocks if the model included them
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text.strip())
    except Exception as exc:
        print(f"[DEBUG] Model request failed or invalid JSON: {exc}", flush=True)
        # Fallback safe action to prevent crashing
        return {
            "highest_priority_id": -1,
            "threat_level": "none",
            "threat_type": "none",
            "two_line_advice": "Error processing context."
        }

# -------------------------------------------------------------------
# Main Loop
# -------------------------------------------------------------------
async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    rewards: List[float] = []
    steps_taken = 0
    success = False
    
    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
    
    try:
        async with httpx.AsyncClient() as http_client:
            # 1. Reset Environment
            reset_resp = await http_client.post(f"{ENV_BASE_URL}/reset", json={"task": TASK_NAME})
            reset_resp.raise_for_status()
            obs = reset_resp.json()
            
            for step in range(1, MAX_STEPS + 1):
                if not obs:
                    break
                    
                # 2. Get LLM Action
                action_dict = get_model_action(client, obs)
                action_str = json.dumps(action_dict, separators=(',', ':')) # Compact JSON, no newlines
                
                # 3. Step Environment
                step_resp = await http_client.post(f"{ENV_BASE_URL}/step", json=action_dict)
                step_data = step_resp.json()
                
                reward = step_data.get("reward", 0.0)
                done = step_data.get("done", True)
                error = step_data.get("info", {}).get("error", None)
                obs = step_data.get("observation", None)
                
                rewards.append(reward)
                steps_taken = step
                
                # 4. Log Step
                log_step(step=step, action=action_str, reward=reward, done=done, error=error)
                
                if done:
                    break
                    
        # Calculate final score (average of step rewards)
        score = sum(rewards) / len(rewards) if rewards else 0.0
        score = min(max(score, 0.0), 1.0)  # clamp to [0, 1]
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as e:
        print(f"[DEBUG] Execution error: {e}", flush=True)
        score = 0.0
        
    finally:
        # 5. Always log END
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    asyncio.run(main())