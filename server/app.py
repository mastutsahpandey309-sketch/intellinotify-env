from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
import os

# Adds root to path so it can find models.py at the top level
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
    """
    CRITICAL: Returns a RAW LIST. 
    Phase 2 fails if this is {"tasks": [...]}.
    """
    result = []
    for t_id, t_obj in TASKS.items():
        result.append({
            "id": t_id,
            "name": t_id.replace("_", " ").title(),
            "description": "Security triage task for notification management.",
            "difficulty": "medium",
            "has_grader": True
        })
    return result

class ResetRequest(BaseModel):
    task: Optional[str] = None
    task_id: Optional[str] = None

@app.post("/reset", response_model=IntelliNotifyObservation)
def reset(req: Optional[ResetRequest] = None):
    t_id = (req.task or req.task_id) if req else None
    return _env.reset(task=t_id)

@app.post("/step", response_model=IntelliNotifyObservation)
def step(action: IntelliNotifyAction):
    return _env.step(action)

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()