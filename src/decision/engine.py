from dataclasses import dataclass

from src.models.metrics import ProcessSample, SystemSample


@dataclass
class Decision:
    should_act: bool
    reason: str
    target: ProcessSample | None


class DecisionEngine:
    def __init__(
        self,
        cpu_threshold: float = 85.0,
        memory_threshold: float = 90.0,
        process_cpu_heavy_threshold: float = 10.0,
        process_memory_heavy_threshold: float = 10.0,
    ) -> None:
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.process_cpu_heavy_threshold = process_cpu_heavy_threshold
        self.process_memory_heavy_threshold = process_memory_heavy_threshold

    def evaluate(self, sample: SystemSample) -> Decision:
        overloaded = (
            sample.cpu_percent >= self.cpu_threshold
            or sample.memory_percent >= self.memory_threshold
        )
        if not overloaded:
            return Decision(should_act=False, reason="System healthy", target=None)

        for proc in sample.top_processes:
            if (
                proc.cpu_percent >= self.process_cpu_heavy_threshold
                or proc.memory_percent >= self.process_memory_heavy_threshold
            ):
                return Decision(
                    should_act=True,
                    reason=(
                        f"Overload detected: CPU {sample.cpu_percent:.1f}% / "
                        f"MEM {sample.memory_percent:.1f}%"
                    ),
                    target=proc,
                )

        return Decision(
            should_act=False,
            reason="Overload detected, but no suitable process target found",
            target=None,
        )
