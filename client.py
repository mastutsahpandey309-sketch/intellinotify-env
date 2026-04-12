"""IntelliNotify Environment Client."""
from typing import Dict
from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State
from .models import IntelliNotifyAction, IntelliNotifyObservation


class IntelliNotifyEnv(EnvClient[IntelliNotifyAction, IntelliNotifyObservation, State]):
    def _step_payload(self, action: IntelliNotifyAction) -> Dict:
        return action.model_dump(exclude={"metadata"})
