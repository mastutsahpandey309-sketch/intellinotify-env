from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
import os

# The Path Hack: Look in the root for models.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import IntelliNotifyAction, IntelliNotifyObservation
from .environment import IntelliNotifyEnvironment
from .task_definitions import TASKS

app = FastAPI(title="IntelliNotify OpenEnv")
_env = IntelliNotifyEnvironment()

@app.get("/health")
def health(): return {"status": "healthy"}

@app.get("/tasks")
def list_tasks():
    # Phase 2 Fix: Return raw list
    return [
        {"id": k, "name": k.replace("_", " ").title(), "has_grader": True}
        for k in TASKS.keys()
    ]

class ResetRequest(BaseModel):
    task: Optional[str] = None
    task_id: Optional[str] = None

@app.post("/reset", response_model=IntelliNotifyObservation)
def reset(req: Optional[ResetRequest] = None):
    try:
        t_id = (req.task or req.task_id) if req else None
        return _env.reset(task=t_id)
    except Exception as e:
        print(f"CRASH IN RESET: {e}")
        raise e

@app.post("/step", response_model=IntelliNotifyObservation)
def step(action: IntelliNotifyAction):
    return _env.step(action)

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
