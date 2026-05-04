# Dynamic Resource Allocator

A preemptive system resource monitor that forecasts CPU and memory load to dynamically allocate hardware resources and prevent bottlenecks.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

## Overview

Traditional resource monitors are reactive—they show high usage only after the system is already overloaded, which often results in UI freezes or stuttering. This project takes a predictive approach. By applying linear regression over a rolling time-series window using Pandas and NumPy, the backend forecasts CPU load a few seconds into the future. This allows the system to identify and handle resource-heavy processes before hardware limits are reached.

## Features

* **Predictive load forecasting:** Uses rolling memory buffers and polynomial regression to estimate near-future CPU load.
* **Metric normalization:** Adjusts system metrics based on physical and logical core counts to maintain a strict 0-100% scale.
* **Real-time dashboard:** A Streamlit-based UI that provides live Plotly charts for both actual and predicted system loads.
* **Process management:** Identify memory and CPU-heavy processes from the dashboard and terminate them directly via OS-level `psutil` commands.
* **Stress testing utility:** Includes a background multi-threaded CPU stress test to verify the predictive engine's responsiveness.

---

## Setup

**Prerequisites**
* Python 3.10 or higher
* Git

**Installation**
1. Clone the repository:
   ```bash
   git clone https://github.com/Arman-khan01/Dynamic-Resource_Allocator.git
   cd Dynamic-Resource_Allocator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

The application consists of two main components that need to run simultaneously: the backend engine and the user interface.

**1. Start the backend monitor**
Open a terminal in the project directory and start the engine:
```bash
python -m src.main
```
*(Leave this process running. It continuously monitors the system and logs telemetry data.)*

**2. Start the dashboard**
Open a separate terminal window in the same directory and launch the UI:
```bash
python -m streamlit run dashboard/app.py
```

The dashboard will automatically open in your default web browser at `http://localhost:8501`.
