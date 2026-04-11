"""
IntelliNotify OpenEnv Server — root-level app.py (matches SecureAI-Guard pattern).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any

from schema.models import IntelliNotifyAction, IntelliNotifyObservation
from tasks.registry import TASKS, get_task
from graders.security_grader import IntelliNotifyGrader, grade_action

app = FastAPI(title="IntelliNotify OpenEnv", version="1.0.0")

# Shared state — single episode at a time
_current_task_id = "task_1_easy_blatant_scam"
_current_task = None
_done = False
_step_count = 0
_episode_id = None

grader = IntelliNotifyGrader()


# ── Health & metadata ──────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/metadata")
def metadata():
    return {
        "name": "IntelliNotify",
        "description": (
            "A mobile OS notification security environment where an agent triages "
            "phone notifications to identify threats like phishing, financial fraud, and malware."
        ),
        "version": "0.1.0",
        "author": "IntelliNotify Team",
    }


@app.get("/schema")
def schema():
    return {
        "action": IntelliNotifyAction.model_json_schema(),
        "observation": IntelliNotifyObservation.model_json_schema(),
        "state": {
            "type": "object",
            "properties": {
                "episode_id": {"type": "string"},
                "step_count": {"type": "integer"},
                "current_task_id": {"type": "string"},
                "done": {"type": "boolean"},
            },
        },
    }


# ── Tasks & graders ────────────────────────────────────────────────

@app.get("/tasks")
def list_tasks():
    result = []
    for tid, task in TASKS.items():
        result.append({
            "id": tid,
            "name": task.name,
            "description": task.description,
            "difficulty": task.difficulty,
            "has_grader": True,
            "grader": "IntelliNotifyGrader",
            "grader_type": "deterministic",
            "score_range": [0.01, 0.99],
        })
    return {"tasks": result}


@app.post("/grade")
def grade_endpoint(body: Dict[str, Any]):
    """Direct grader endpoint — validator can call this per task."""
    task_id = body.get("task_id", _current_task_id)
    action_dict = body.get("action", {})
    result = grader.grade(action_dict, task_id)
    return {
        "task_id": task_id,
        "score": result.score,
        "reasoning": result.reasoning,
        "components": result.components,
    }


# ── Environment control ────────────────────────────────────────────

class ResetRequest(BaseModel):
    task_id: Optional[str] = None
    task: Optional[str] = None
    seed: Optional[int] = None
    episode_id: Optional[str] = None


@app.post("/reset")
def reset(req: Optional[ResetRequest] = None):
    global _current_task_id, _current_task, _done, _step_count, _episode_id
    import uuid

    chosen = None
    if req:
        chosen = req.task_id or req.task
    if chosen and chosen in TASKS:
        _current_task_id = chosen

    _current_task = get_task(_current_task_id)
    _done = False
    _step_count = 0
    _episode_id = (req.episode_id if req and req.episode_id else None) or str(uuid.uuid4())

    return {
        "observation": {
            "step_number": 1,
            "total_steps": 1,
            "events": [e.model_dump() for e in _current_task.events],
            "last_action_feedback": None,
        },
        "reward": None,
        "done": False,
        "info": {"task_id": _current_task_id, "episode_id": _episode_id},
        "state": {
            "episode_id": _episode_id,
            "step_count": _step_count,
            "current_task_id": _current_task_id,
            "done": _done,
        },
    }


@app.post("/step")
def step(action: IntelliNotifyAction):
    global _done, _step_count

    if _current_task is None or _done:
        return {
            "observation": {"step_number": 1, "total_steps": 1, "events": [],
                            "last_action_feedback": "Call /reset first."},
            "reward": 0.05,
            "done": True,
            "info": {"error": "Episode done. Call /reset."},
            "state": {"episode_id": _episode_id, "step_count": _step_count,
                      "current_task_id": _current_task_id, "done": True},
        }

    result = grade_action(
        action=action,
        expected_priority_id=_current_task.expected_id,
        expected_threat_level=_current_task.expected_level,
        expected_threat_type=_current_task.expected_type,
    )
    _done = True
    _step_count += 1

    return {
        "observation": {
            "step_number": 1,
            "total_steps": 1,
            "events": [],
            "last_action_feedback": result.reasoning,
        },
        "reward": result.score,
        "done": True,
        "info": {
            "feedback": result.reasoning,
            "components": result.components,
            "task_id": _current_task_id,
        },
        "state": {
            "episode_id": _episode_id,
            "step_count": _step_count,
            "current_task_id": _current_task_id,
            "done": _done,
        },
    }


@app.get("/state")
def state():
    return {
        "episode_id": _episode_id,
        "step_count": _step_count,
        "current_task_id": _current_task_id,
        "done": _done,
    }


@app.post("/mcp")
async def mcp(body: Dict[str, Any] = {}):
    return {"jsonrpc": "2.0", "result": {"tools": []}, "id": body.get("id", 1)}


# ── Entry point ────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
