from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn

from schema.models import IntelliNotifyAction, IntelliNotifyObservation
from tasks.registry import TASKS, get_task
from graders.security_grader import grade_action

app = FastAPI(title="IntelliNotify OpenEnv")

class IntelliNotifyEnvironment:
    def __init__(self):
        self._current_task_id = "task_1_easy_blatant_scam"
        self._task = None
        self._done = False
        self._step_count = 0

    def reset(self, task=None):
        if task in TASKS:
            self._current_task_id = task
        self._task = get_task(self._current_task_id)
        self._done = False
        self._step_count = 0
        return IntelliNotifyObservation(
            step_number=0, total_steps=5, events=self._task.events,
            last_action_feedback="Reset successful.", reward=0.0, done=False
        )

    def step(self, action: IntelliNotifyAction):
        self._step_count += 1
        reward_obj = grade_action(
            action=action,
            expected_priority_id=self._task.expected_id,
            expected_threat_level=self._task.expected_level,
            expected_threat_type=self._task.expected_type,
        )
        self._done = True
        return IntelliNotifyObservation(
            step_number=self._step_count, total_steps=5, events=[],
            last_action_feedback=reward_obj.reasoning, reward=reward_obj.score, done=True
        )

_env = IntelliNotifyEnvironment()

@app.get("/health")
def health(): return {"status": "healthy"}

@app.get("/tasks")
def list_tasks():
    return [
        {"id": t_id, "name": t_id.replace("_", " ").title(), "description": "Security Task", "difficulty": "medium", "has_grader": True}
        for t_id in TASKS.keys()
    ]

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

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860)
