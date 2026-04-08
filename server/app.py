from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import os

# These are now relative imports because they are in the same folder
from .models import IntelliNotifyAction, IntelliNotifyObservation, IntelliNotifyState
from .environment import IntelliNotifyEnv
from .task_definitions import TASKS

app = FastAPI(title="IntelliNotify OpenEnv Server")
env = IntelliNotifyEnv()

class ResetRequest(BaseModel):
    task: Optional[str] = None

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/reset", response_model=IntelliNotifyObservation)
def reset_environment(req: Optional[ResetRequest] = None):
    try:
        task_id = req.task if req and req.task else None
        return env.reset(task_id=task_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step")
def step_environment(action: IntelliNotifyAction):
    try:
        return env.step(action)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state", response_model=IntelliNotifyState)
def get_state():
    return env.state()

@app.get("/tasks")
def list_tasks():
    return {"tasks": list(TASKS.keys())}

def main():
    import uvicorn
    # This is the exact string the grader wants to call
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
