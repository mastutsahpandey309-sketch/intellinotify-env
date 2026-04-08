from .models import IntelliNotifyObservation, IntelliNotifyAction, IntelliNotifyState
from .task_definitions import TASKS
import datetime

class IntelliNotifyEnv:
    def __init__(self):
        self.current_task_id = None
        self.start_time = None
        self.is_done = False

    def reset(self, task_id: str = None) -> IntelliNotifyObservation:
        if task_id and task_id in TASKS:
            self.current_task_id = task_id
        else:
            self.current_task_id = list(TASKS.keys())[0]
        
        self.start_time = datetime.datetime.now()
        self.is_done = False
        
        return IntelliNotifyObservation(
            observation=f"Environment reset. Current task: {self.current_task_id}",
            available_actions=["scan_network", "check_logs", "quarantine_device"],
            done=False
        )

    def step(self, action: IntelliNotifyAction) -> IntelliNotifyObservation:
        # Basic logic: In a real hackathon, you'd match the action to the task
        task = TASKS.get(self.current_task_id)
        
        # Simple evaluation logic
        is_correct = action.action_type in task.get("required_actions", [])
        
        return IntelliNotifyObservation(
            observation=f"Action '{action.action_type}' performed. Security status updated.",
            available_actions=["check_logs", "finalize_report"],
            done=True if is_correct else False
        )

    def state(self) -> IntelliNotifyState:
        return IntelliNotifyState(
            task_id=self.current_task_id,
            status="active" if not self.is_done else "completed",
            steps_taken=1
        )
