import psutil

from src.models.metrics import ProcessSample, SystemSample


class MetricsCollector:
    def __init__(self, top_process_limit: int = 10) -> None:
        self.top_process_limit = top_process_limit
        self._prime_cpu_counters()

    def _prime_cpu_counters(self) -> None:
        psutil.cpu_percent(interval=None)
        for proc in psutil.process_iter():
            try:
                proc.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def collect(self) -> SystemSample:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        return SystemSample.now(
            cpu_percent=cpu,
            memory_percent=memory,
            top_processes=self._get_top_processes(),
        )

    def _get_top_processes(self) -> list[ProcessSample]:
        samples: list[ProcessSample] = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = proc.info
                samples.append(
                    ProcessSample(
                        pid=info["pid"],
                        name=info.get("name", "unknown"),
                        cpu_percent=float(info.get("cpu_percent") or 0.0),
                        memory_percent=float(info.get("memory_percent") or 0.0),
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        samples.sort(key=lambda p: (p.cpu_percent, p.memory_percent), reverse=True)
        return samples[: self.top_process_limit]
