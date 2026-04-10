"""IntelliNotify environment - no openenv dependency required."""
from uuid import uuid4
from typing import Optional, Any
# These imports rely on the functions existing in task_definitions.py
from .models import IntelliNotifyAction, IntelliNotifyObservation
from .task_definitions import get_task, grade_action, TASKS

class _State:
    def __init__(self, episode_id: str):
        self.episode_id = episode_id
        self.step_count = 0

class IntelliNotifyEnvironment:
    def __init__(self):
        self._state = _State(str(uuid4()))
        self._current_task_id = "task_1_easy_blatant_scam"
        self._task = None
        self._done = False

    def reset(self, task=None, task_id=None, seed=None, episode_id=None, **kwargs):
        chosen = task_id or task
        if chosen and chosen in TASKS:
            self._current_task_id = chosen
        self._task = get_task(self._current_task_id)
        self._done = False
        self._state = _State(episode_id or str(uuid4()))
        return IntelliNotifyObservation(
            step_number=1,
            total_steps=1,
            events=self._task.events,
            last_action_feedback=None,
            reward=None,
            done=False,
        )

    def step(self, action: IntelliNotifyAction):
        if self._task is None or self._done:
            return IntelliNotifyObservation(
                step_number=1, total_steps=1, events=[],
                last_action_feedback="Call /reset first.",
                reward=0.05, done=True,
            )
        reward_obj = grade_action(
            action=action,
            expected_priority_id=self._task.expected_id,
            expected_threat_level=self._task.expected_level,
            expected_threat_type=self._task.expected_type,
        )
        self._done = True
        self._state.step_count += 1
        return IntelliNotifyObservation(
            step_number=1, total_steps=1, events=[],
            last_action_feedback=reward_obj.reasoning,
            reward=reward_obj.score,
            done=True,
        )
