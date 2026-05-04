import argparse
import pandas as pd
import numpy as np
from collections import deque
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
# --- NEW PREDICTIVE LOGIC ---
# Create a memory buffer to store the last 10 CPU readings
cpu_history = deque(maxlen=10) 

def predict_future_cpu(current_cpu):
    # Add the current reading to our history
    cpu_history.append(current_cpu)
    
    # We need at least 5 data points to draw a trend line
    if len(cpu_history) < 5: 
        return current_cpu 

    # Create a quick DataFrame to calculate the trend
    df = pd.DataFrame({'time_step': range(len(cpu_history)), 'cpu': list(cpu_history)})
    
    # Calculate the slope of the CPU usage over time
    slope, intercept = np.polyfit(df['time_step'], df['cpu'], 1)
    
    # Predict what the CPU will be 3 steps (seconds) into the future
    # Predict what the CPU will be 3 steps (seconds) into the future
    future_step = len(cpu_history) + 3 
    predicted_cpu = (slope * future_step) + intercept
    
    # NEW: Clamp the prediction so it cannot go below 0 or above 100
    return max(0.0, min(100.0, predicted_cpu))
# ----------------------------


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
        
        # --- PREDICTION INJECTION ---
        actual_cpu = sample.cpu_percent
        predicted_cpu = predict_future_cpu(actual_cpu)
        
        # Override the sample's CPU with our predicted CPU 
        # so the engine acts on the future, not the past!
        sample.cpu_percent = predicted_cpu 
        # ----------------------------

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
            "predicted_cpu": predicted_cpu # Saving this for our dashboard later!
        }
        write_state(state_file, state_payload)

        # Updated print statement to show both actual and predicted CPU
        print(
            f"[{sample.timestamp}] Actual CPU={actual_cpu:.1f}% -> "
            f"Predicted CPU={predicted_cpu:.1f}% | "
            f"MEM={sample.memory_percent:.1f}% | {result_message}"
        )
        time.sleep(args.sample_interval)


if __name__ == "__main__":
    run()
