"""ATMAN Environment Client."""
from typing import Dict
from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State
from .models import AtmanAction, AtmanObservation


class AtmanEnv(EnvClient[AtmanAction, AtmanObservation, State]):
    def _step_payload(self, action: AtmanAction) -> Dict:
        return action.model_dump(exclude={"metadata"})
