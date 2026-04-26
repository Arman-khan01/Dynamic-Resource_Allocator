import argparse
import time
from pathlib import Path

from src.allocator.controller import ResourceAllocator
from src.decision.engine import DecisionEngine
from src.monitor.collector import MetricsCollector
from src.utils.logger import build_logger, write_state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dynamic resource allocator starter app")
    parser.add_argument("--cpu-threshold", type=float, default=85.0)
    parser.add_argument("--memory-threshold", type=float, default=90.0)
    parser.add_argument("--sample-interval", type=int, default=2)
    parser.add_argument("--top-limit", type=int, default=10)
    parser.add_argument("--cooldown", type=int, default=30)
    return parser.parse_args()


def run() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    state_file = root / "logs" / "state.json"
    logger = build_logger(root / "logs" / "actions.log")

    collector = MetricsCollector(top_process_limit=args.top_limit)
    engine = DecisionEngine(
        cpu_threshold=args.cpu_threshold,
        memory_threshold=args.memory_threshold,
    )
    allocator = ResourceAllocator(
        cooldown_seconds=args.cooldown,
        protected_processes={"System", "Registry", "smss.exe", "csrss.exe", "wininit.exe"},
    )

    print("Dynamic resource allocator started. Press Ctrl+C to stop.")
    while True:
        sample = collector.collect()
        decision = engine.evaluate(sample)
        result_message = "No action"

        if decision.should_act and decision.target:
            result = allocator.apply_priority_reduction(decision.target)
            result_message = result.message
            logger.info("%s | reason=%s", result.message, decision.reason)
        else:
            logger.info("No action | reason=%s", decision.reason)

        state_payload = {
            "system": sample.to_dict(),
            "decision": {
                "should_act": decision.should_act,
                "reason": decision.reason,
                "target": decision.target.to_dict() if decision.target else None,
            },
            "last_result": result_message,
        }
        write_state(state_file, state_payload)

        print(
            f"[{sample.timestamp}] CPU={sample.cpu_percent:.1f}% "
            f"MEM={sample.memory_percent:.1f}% | {result_message}"
        )
        time.sleep(args.sample_interval)


if __name__ == "__main__":
    run()
