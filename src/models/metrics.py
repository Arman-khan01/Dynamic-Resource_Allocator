from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass
class ProcessSample:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SystemSample:
    timestamp: str
    cpu_percent: float
    memory_percent: float
    top_processes: list[ProcessSample]

    @classmethod
    def now(
        cls, cpu_percent: float, memory_percent: float, top_processes: list[ProcessSample]
    ) -> "SystemSample":
        return cls(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            top_processes=top_processes,
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["top_processes"] = [proc.to_dict() for proc in self.top_processes]
        return payload
