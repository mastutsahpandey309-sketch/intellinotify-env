from uuid import uuid4
from typing import Optional, Any

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State, EnvironmentMetadata

from .models import IntelliNotifyAction, IntelliNotifyObservation
from .task_definitions import get_task, grade_action


class IntelliNotifyEnvironment(Environment):
    """IntelliNotify: mobile OS notification security environment."""

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        super().__init__()
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current_task_id = "task_1_easy_blatant_scam"
        self.task = None
        self.current_step_index = 0
        self.last_feedback = None

    def reset(self, seed=None, episode_id=None, task=None, **kwargs):
        if task:
            self.current_task_id = task
        self.task = get_task(self.current_task_id)
        self.current_step_index = 0
        self.last_feedback = None
        self._state = State(episode_id=episode_id or str(uuid4()), step_count=0)
        return self._obs(reward=None, done=False)

    def step(self, action: IntelliNotifyAction):
        if self.task is None or self.current_step_index >= len(self.task.steps):
            return self._obs(reward=0.01, done=True)

        step_def = self.task.steps[self.current_step_index]
        reward_obj = grade_action(
            action=action,
            expected_priority_id=step_def.expected_id,
            expected_threat_level=step_def.expected_level,
            expected_threat_type=step_def.expected_type,
        )
        self.last_feedback = reward_obj.reasoning
        self.current_step_index += 1
        self._state.step_count += 1
        done = self.current_step_index >= len(self.task.steps)
        return self._obs(reward=reward_obj.score, done=done)

    @property
    def state(self):
        return self._state

    def get_metadata(self):
        return EnvironmentMetadata(
            name="IntelliNotify",
            description="A mobile OS notification security environment where an agent triages phone events to identify threats like phishing, financial fraud, and malware.",
            version="0.1.0",
            author="IntelliNotify Team",
        )

    def _obs(self, reward, done):
        if done or self.task is None:
            return IntelliNotifyObservation(
                step_number=self.current_step_index,
                total_steps=len(self.task.steps) if self.task else 0,
                events=[],
                last_action_feedback=self.last_feedback or "Episode complete.",
                reward=reward,
                done=done,
            )
        step_def = self.task.steps[self.current_step_index]
        return IntelliNotifyObservation(
            step_number=self.current_step_index + 1,
            total_steps=len(self.task.steps),
            events=step_def.events,
            last_action_feedback=self.last_feedback,
            reward=reward,
            done=done,
        )

    def close(self):
        pass
