from models import IntelliNotifyObservation, IntelliNotifyAction, IntelliNotifyState
from task_definitions import get_task, grade_action

class IntelliNotifyEnv:
    def __init__(self):
        self.current_task_id = "task_1_easy_blatant_scam" # Default
        self.task = None
        self.current_step_index = 0
        self.cumulative_reward = 0.0
        self.is_done = True
        self.last_feedback = None

    def reset(self, task_id: str = None) -> IntelliNotifyObservation:
        """Starts a new episode and returns the first observation."""
        if task_id:
            self.current_task_id = task_id
            
        self.task = get_task(self.current_task_id)
        self.current_step_index = 0
        self.cumulative_reward = 0.0
        self.is_done = False
        self.last_feedback = None
        
        return self._get_observation()

    def step(self, action: IntelliNotifyAction) -> dict:
        """Processes the agent's action, grades it, and advances the queue."""
        if self.is_done:
            return {
                "observation": self._get_observation(),
                "reward": 0.0,
                "done": True,
                "info": {"error": "Episode is already done. Please call /reset."}
            }

        # 1. Grade the action against the current step's ground truth
        current_step_def = self.task.steps[self.current_step_index]
        reward_obj = grade_action(
            action=action,
            expected_priority_id=current_step_def.expected_id,
            expected_threat_level=current_step_def.expected_level,
            expected_threat_type=current_step_def.expected_type
        )

        # 2. Update state
        step_reward = reward_obj.score
        self.cumulative_reward += step_reward
        self.last_feedback = reward_obj.reasoning
        
        self.current_step_index += 1
        
        # 3. Check if episode is finished
        if self.current_step_index >= len(self.task.steps):
            self.is_done = True
            
        # 4. Format the standard RL return payload
        return {
            "observation": self._get_observation() if not self.is_done else None,
            "reward": step_reward,
            "done": self.is_done,
            "info": {"feedback": self.last_feedback}
        }

    def state(self) -> IntelliNotifyState:
        """Returns the internal state of the environment for debugging/logging."""
        return IntelliNotifyState(
            current_step=self.current_step_index,
            max_steps=len(self.task.steps) if self.task else 0,
            cumulative_reward=self.cumulative_reward,
            is_done=self.is_done,
            current_task_id=self.current_task_id
        )

    def _get_observation(self) -> IntelliNotifyObservation:
        """Constructs the observation payload for the current step."""
        if self.is_done or not self.task:
            return IntelliNotifyObservation(
                step_number=self.current_step_index,
                total_steps=len(self.task.steps) if self.task else 0,
                events=[],
                last_action_feedback="Episode complete."
            )
            
        current_step_def = self.task.steps[self.current_step_index]
        return IntelliNotifyObservation(
            step_number=self.current_step_index + 1,
            total_steps=len(self.task.steps),
            events=current_step_def.events,
            last_action_feedback=self.last_feedback
        )
