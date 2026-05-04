# Adaptive Resource Allocator

A simple system monitor I built to explore how an OS could predict resource usage instead of just reacting to it.

## Idea

Most system monitors only show what’s already happening.
I wanted to try predicting CPU usage a few seconds ahead and see if that could help avoid sudden slowdowns.

## How it works

* Collects CPU usage continuously using `psutil`
* Stores recent values in a rolling buffer
* Applies basic linear regression using NumPy/Pandas
* Predicts CPU load around 3 seconds into the future
* Displays both actual and predicted values in a live dashboard

It’s a simple approach, but it gives a rough estimate of what’s coming next.

## Features

* Live dashboard (Streamlit)
  Shows real-time CPU usage along with predicted values

* Prediction system
  Uses linear regression instead of heavy ML models

* CPU normalization
  Converts multi-core usage into a clear 0–100% scale

* Process viewer and killer
  Lets you identify and stop heavy processes

* Stress testing tool
  Simulate CPU load and observe how the prediction reacts

## Running the project

```bash
git clone https://github.com/YOUR-USERNAME/Adaptive-Resource-Allocator.git
cd Adaptive-Resource-Allocator
pip install -r requirements.txt
python run_gui.py
```

(Optional) Run the stress test in another terminal:

```bash
python stress_test.py
```

## Tech used

* Python
* Pandas
* NumPy
* Streamlit
* psutil

## Notes

* This is an experimental project, not a production tool
* Prediction is basic, so it won’t handle sudden spikes well
* Built mainly to understand system behavior and resource handling

## Future improvements

* Try more advanced prediction methods
* Add memory and disk monitoring
* Automate responses instead of manual process termination

---

Built as a learning project to experiment with real-time system data and prediction.
