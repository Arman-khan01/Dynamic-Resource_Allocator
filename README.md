# Dynamic Resource Allocator

A beginner-friendly project that monitors system load and lowers process priority when CPU or memory pressure is high.

## Features

- Real-time system monitoring (CPU and memory)
- Top process tracking
- Rule-based decision engine
- Priority reduction with cooldown and protected-process rules
- Streamlit dashboard for presentation

## Setup

1. Create virtual environment:
   - `python -m venv .venv`
2. Activate it:
   - PowerShell: `.venv\Scripts\Activate.ps1`
3. Install dependencies:
   - `pip install -r requirements.txt`

## Run Backend Monitor

From project root:

- `python -m src.main`

Optional thresholds:

- `python -m src.main --cpu-threshold 80 --memory-threshold 85 --sample-interval 2`

## Run Dashboard

In a second terminal:

- `streamlit run dashboard/app.py`

## Notes

- On Windows, lowering some process priorities may require Administrator privileges.
- Current allocation strategy is rule-based and intentionally simple for learning.
