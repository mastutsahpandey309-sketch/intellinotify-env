from .models import IntelliNotifyObservation, IntelliNotifyAction, IntelliNotifyState
from .task_definitions import TASKS
import datetime

class IntelliNotifyEnv:
    def __init__(self):
        self.current_task_id = None
        self.start_time = None
        self.is_done = False
        self.current_step = 0
        self.max_steps = 10  # Providing a default total steps

    def reset(self, task_id: str = None) -> IntelliNotifyObservation:
        if task_id and task_id in TASKS:
            self.current_task_id = task_id
        else:
            self.current_task_id = list(TASKS.keys())[0]
        
        self.start_time = datetime.datetime.now()
        self.is_done = False
        self.current_step = 0
        
        # We must include ALL fields required by the IntelliNotifyObservation model
        return IntelliNotifyObservation(
            observation=f"Environment reset. Current task: {self.current_task_id}",
            available_actions=["scan_network", "check_logs", "quarantine_device"],
            done=False,
            step_number=self.current_step,
            total_steps=self.max_steps,
            events=[]  # Providing an empty list for 'events'
        )

    def step(self, action: IntelliNotifyAction) -> IntelliNotifyObservation:
        self.current_step += 1
        task = TASKS.get(self.current_task_id)
        
        # Simple evaluation logic
        is_correct = action.action_type in task.get("required_actions", [])
        
        if self.current_step >= self.max_steps:
            self.is_done = True

        return IntelliNotifyObservation(
            observation=f"Action '{action.action_type}' performed. Security status updated.",
            available_actions=["check_logs", "finalize_report"],
            done=True if is_correct else self.is_done,
            step_number=self.current_step,
            total_steps=self.max_steps,
            events=[]  # Providing an empty list for 'events'
        )

    def state(self) -> IntelliNotifyState:
        return IntelliNotifyState(
            task_id=self.current_task_id,
            status="active" if not self.is_done else "completed",
            steps_taken=self.current_step
        )
