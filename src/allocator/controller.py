import time
from dataclasses import dataclass

import psutil

from src.models.metrics import ProcessSample


@dataclass
class AllocationResult:
    success: bool
    message: str


class ResourceAllocator:
    def __init__(self, cooldown_seconds: int = 30, protected_processes: set[str] | None = None):
        self.cooldown_seconds = cooldown_seconds
        self.protected_processes = protected_processes or set()
        self.last_action_time_by_pid: dict[int, float] = {}

    def apply_priority_reduction(self, target: ProcessSample) -> AllocationResult:
        if target.name in self.protected_processes:
            return AllocationResult(False, f"Skipped protected process: {target.name}")

        now = time.time()
        previous_action = self.last_action_time_by_pid.get(target.pid)
        if previous_action and (now - previous_action) < self.cooldown_seconds:
            return AllocationResult(False, f"Cooldown active for PID {target.pid}")

        try:
            proc = psutil.Process(target.pid)
            self._set_lower_priority(proc)
            self.last_action_time_by_pid[target.pid] = now
            return AllocationResult(
                True,
                f"Lowered priority for PID {target.pid} ({target.name})",
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied) as error:
            return AllocationResult(False, f"Failed PID {target.pid}: {error}")

    @staticmethod
    def _set_lower_priority(process: psutil.Process) -> None:
        # Windows + Unix fallback in one place.
        if hasattr(psutil, "BELOW_NORMAL_PRIORITY_CLASS"):
            process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            return
        process.nice(10)
