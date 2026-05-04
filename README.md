# ⚡ Adaptive Resource Allocator

A sophisticated, data-driven Operating System monitor that preemptively forecasts system load and dynamically allocates hardware resources to prevent bottlenecks. 

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

## 🧠 Core Concept: Predictive vs. Reactive
Most resource monitors react *after* a system is already overloaded, which often leads to UI freezes and system stutter. This project implements a **Predictive Allocation Engine**. By utilizing Pandas and NumPy for linear regression over a rolling time-series window, the backend forecasts future CPU load and takes action *before* the hardware hits critical limits.

## ✨ Key Features
* **Predictive Forecasting Engine:** Uses rolling memory buffers and 1st-degree polynomial regression to forecast CPU load 3 seconds into the future.
* **Intelligent Normalization:** Automatically calculates physical/logical core counts to normalize system metrics to a strict, readable 0-100% scale (eliminating the "1500% CPU" anomaly).
* **Live Control Center UI:** A responsive Streamlit dashboard featuring real-time Plotly charts tracking both actual and predicted system loads.
* **Integrated Process Sniper:** Locate memory-hogging processes via the UI and terminate them directly from the browser using OS-level `psutil` commands.
* **Built-in Stress Testing:** Safely launch background, multi-threaded CPU stress tests directly from the dashboard to watch the predictive engine react in real-time.

---

## 🚀 Quick Start Guide

### Prerequisites
* Python 3.10+
* Git

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR-USERNAME/Adaptive-Resource-Allocator.git](https://github.com/YOUR-USERNAME/Adaptive-Resource-Allocator.git)
   cd Adaptive-Resource-Allocator