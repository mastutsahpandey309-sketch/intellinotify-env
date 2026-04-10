"""
IntelliNotify OpenEnv Server — full OpenEnv HTTP contract implementation.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from .models import IntelliNotifyAction, IntelliNotifyObservation
from .environment import IntelliNotifyEnvironment
from .task_definitions import TASKS

app = FastAPI(title="IntelliNotify OpenEnv", version="1.0.0")

# Single shared env instance — preserves state between /reset and /step
_env = IntelliNotifyEnvironment()


# ── OpenEnv required endpoints ─────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/metadata")
def metadata():
    return _env.get_metadata()


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


@app.get("/state")
def state():
    return _env.state()


@app.post("/mcp")
async def mcp(request: Dict[str, Any] = {}):
    """Minimal JSON-RPC 2.0 stub required by OpenEnv validator."""
    return {
        "jsonrpc": "2.0",
        "result": {"tools": []},
        "id": request.get("id", 1),
    }


@app.get("/tasks")
def list_tasks():
    """Enumerate all tasks with grader metadata."""
    result = []
    for task_id, task in TASKS.items():
        result.append({
            "id": task_id,
            "name": task_id.replace("_", " ").title(),
            "difficulty": (
                "easy" if "easy" in task_id
                else "hard" if "hard" in task_id
                else "medium"
            ),
            "has_grader": True,
            "grader_type": "deterministic",
            "num_events": len(task.events),
        })
    return {"tasks": result}


# ── Environment control ────────────────────────────────────────────

class ResetRequest(BaseModel):
    task: Optional[str] = None
    task_id: Optional[str] = None   # accept both field names
    seed: Optional[int] = None
    episode_id: Optional[str] = None


@app.post("/reset")
def reset(req: Optional[ResetRequest] = None):
    task_id = None
    if req:
        task_id = req.task or req.task_id
    obs = _env.reset(task=task_id)
    return {
        "observation": {
            "step_number": obs.step_number,
            "total_steps": obs.total_steps,
            "events": [e.model_dump() for e in obs.events],
            "last_action_feedback": obs.last_action_feedback,
        },
        "reward": obs.reward,
        "done": obs.done,
        "info": {"task_id": _env._current_task_id},
    }


@app.post("/step")
def step(action: IntelliNotifyAction):
    obs = _env.step(action)
    return {
        "observation": {
            "step_number": obs.step_number,
            "total_steps": obs.total_steps,
            "events": [e.model_dump() for e in obs.events],
            "last_action_feedback": obs.last_action_feedback,
        },
        "reward": obs.reward,
        "done": obs.done,
        "info": {
            "feedback": obs.last_action_feedback,
            "task_id": _env._current_task_id,
        },
    }


# ── Entry point ────────────────────────────────────────────────────

def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
