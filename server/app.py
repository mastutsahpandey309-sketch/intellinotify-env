"""
IntelliNotify OpenEnv Server.

Implements the full OpenEnv HTTP contract:
  GET  /health    → {"status": "healthy"}
  GET  /metadata  → name + description
  GET  /schema    → action / observation / state schemas
  GET  /state     → current internal state
  POST /mcp       → JSON-RPC 2.0 (required by validator)
  POST /reset     → start episode, return observation
  POST /step      → grade action, return reward + done
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Any, Dict

from .models import IntelliNotifyAction, IntelliNotifyObservation
from .environment import IntelliNotifyEnvironment

app = FastAPI(
    title="IntelliNotify OpenEnv",
    version="1.0.0",
)

# Single shared environment — state preserved between /reset and /step
_env = IntelliNotifyEnvironment()


# ── Required OpenEnv endpoints ─────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/metadata")
def metadata():
    meta = _env.get_metadata()
    return {
        "name": meta.name,
        "description": meta.description,
        "version": meta.version,
        "author": meta.author,
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
            }
        },
    }


@app.get("/state")
def state():
    s = _env.state
    return {
        "episode_id": s.episode_id,
        "step_count": s.step_count,
        "current_task_id": _env._current_task_id,
        "done": _env._done,
    }


@app.post("/mcp")
def mcp(body: Dict[str, Any] = {}):
    """Minimal JSON-RPC 2.0 endpoint required by OpenEnv validator."""
    return {
        "jsonrpc": "2.0",
        "result": {"tools": []},
        "id": body.get("id", 1),
    }


# ── Environment control endpoints ──────────────────────────────────

class ResetRequest(BaseModel):
    task: Optional[str] = None
    seed: Optional[int] = None
    episode_id: Optional[str] = None


@app.post("/reset")
def reset(req: Optional[ResetRequest] = None):
    task_id = req.task if req else None
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
    }


@app.get("/tasks")
def list_tasks():
    from .task_definitions import TASKS
    return {"tasks": list(TASKS.keys())}


# ── Entry point ────────────────────────────────────────────────────

def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
