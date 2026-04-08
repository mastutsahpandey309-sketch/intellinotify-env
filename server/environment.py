from uuid import uuid4
from typing import Optional, Any

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State, EnvironmentMetadata

from .models import IntelliNotifyAction, IntelliNotifyObservation
from .task_definitions import get_task, grade_action, TASKS


class IntelliNotifyEnvironment(Environment):
    """
    IntelliNotify: mobile OS notification security benchmark.

    Each episode is a SINGLE step:
      1. /reset (with task= param) → returns a set of phone events
      2. /step (with action)       → grades the action, returns reward, done=True
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        super().__init__()
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._current_task_id = "task_1_easy_blatant_scam"
        self._task = None
        self._done = False

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        task: Optional[str] = None,
        **kwargs: Any,
    ) -> IntelliNotifyObservation:
        if task and task in TASKS:
            self._current_task_id = task
        self._task = get_task(self._current_task_id)
        self._done = False
        self._state = State(episode_id=episode_id or str(uuid4()), step_count=0)

        return IntelliNotifyObservation(
            step_number=1,
            total_steps=1,
            events=self._task.events,
            last_action_feedback=None,
            reward=None,
            done=False,
        )

    def step(self, action: IntelliNotifyAction) -> IntelliNotifyObservation:  # type: ignore[override]
        if self._task is None or self._done:
            return IntelliNotifyObservation(
                step_number=1,
                total_steps=1,
                events=[],
                last_action_feedback="Episode already done. Call /reset first.",
                reward=0.05,
                done=True,
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
            step_number=1,
            total_steps=1,
            events=[],
            last_action_feedback=reward_obj.reasoning,
            reward=reward_obj.score,
            done=True,
        )

    @property
    def state(self) -> State:
        return self._state

    def get_metadata(self) -> EnvironmentMetadata:
        return EnvironmentMetadata(
            name="IntelliNotify",
            description=(
                "A mobile OS notification security environment where an agent "
                "triages phone notifications to identify threats like phishing, "
                "financial fraud, and malware."
            ),
            version="0.1.0",
            author="IntelliNotify Team",
        )

    def close(self):
        pass
