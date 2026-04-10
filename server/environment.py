from uuid import uuid4
from .task_definitions import get_task, grade_action, TASKS
# Note the relative import for models inside the server folder if needed, 
# but here we point to the root models
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import IntelliNotifyObservation

class IntelliNotifyEnvironment:
    def __init__(self):
        self._current_task_id = "task_1_easy_blatant_scam"
        self._task = None
        self._done = False
        self._step_count = 0

    def reset(self, task=None, **kwargs):
        if task in TASKS:
            self._current_task_id = task
        self._task = get_task(self._current_task_id)
        self._done = False
        self._step_count = 0
        return IntelliNotifyObservation(
            step_number=0,
            total_steps=5,
            events=self._task.events,
            last_action_feedback="Reset successful.",
            reward=0.0,
            done=False
        )

    def step(self, action):
        self._step_count += 1
        reward_obj = grade_action(
            action=action,
            expected_priority_id=self._task.expected_id,
            expected_threat_level=self._task.expected_level,
            expected_threat_type=self._task.expected_type,
        )
        self._done = True
        return IntelliNotifyObservation(
            step_number=self._step_count,
            total_steps=5,
            events=[],
            last_action_feedback=reward_obj.reasoning,
            reward=reward_obj.score,
            done=True
        )