import streamlit as st
import pandas as pd
import json
import time
from pathlib import Path
import plotly.graph_objects as go
from collections import deque
import multiprocessing
import subprocess
import psutil

st.set_page_config(page_title="Adaptive Allocator", layout="wide", page_icon="⚙️")

# --- Initialize Session State for Historical Data ---
if "time_history" not in st.session_state:
    st.session_state.time_history = deque(maxlen=60) # Keep last 60 seconds
    st.session_state.cpu_history = deque(maxlen=60)
    st.session_state.pred_history = deque(maxlen=60)

# Paths
root = Path(__file__).resolve().parents[1]
state_file = root / "logs" / "state.json"

def load_state():
    if state_file.exists():
        try:
            with open(state_file) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None
    return None

# --- UI Layout ---
st.title("⚡ Dynamic Resource Allocator Control Center")

# Sidebar Controls
st.sidebar.header("🎛️ Settings & Controls")
st.sidebar.markdown("*(Note: Changing these currently requires backend restart)*")
st.sidebar.slider("CPU Danger Threshold", min_value=50, max_value=100, value=85)
st.sidebar.slider("Memory Danger Threshold", min_value=50, max_value=100, value=90)
st.sidebar.button("Force Refresh State")

# --- NEW UI CONTROLS ---
st.sidebar.markdown("---")
st.sidebar.header("🔥 Integrated Stress Test")
threads = st.sidebar.slider("CPU Threads to Burn", min_value=1, max_value=16, value=14)

# Create two columns for the buttons so they sit side-by-side
col_launch, col_stop = st.sidebar.columns(2)

with col_launch:
    if st.button("Launch", type="primary"):
        subprocess.Popen(["python", "stress.py", str(threads)])
        st.sidebar.success(f"Launched {threads} threads!")

with col_stop:
    if st.button("Stop All"):
        killed_count = 0
        # Iterate through all running computer processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline')
                # If the process is running our stress script, terminate it!
                if cmdline and 'stress.py' in ' '.join(cmdline):
                    proc.terminate()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if killed_count > 0:
            st.sidebar.success(f"Nuked {killed_count} stress processes!")
        else:
            st.sidebar.info("No stress tests running.")

st.sidebar.markdown("---")
st.sidebar.header("🔫 Process Sniper")
st.sidebar.markdown("*(Find the PID in the Top Resources table)*")
target_pid = st.sidebar.number_input("Enter PID to Kill", min_value=0, step=1, value=0)

if st.sidebar.button("Terminate Single Process"):
    if target_pid == 0:
        st.sidebar.error("Cannot kill System Idle Process!")
    else:
        try:
            # Tell the Operating System to forcefully kill the target process
            p = psutil.Process(target_pid)
            p.terminate()
            st.sidebar.success(f"Successfully terminated PID {target_pid}!")
        except psutil.NoSuchProcess:
            st.sidebar.error(f"PID {target_pid} no longer exists.")
        except psutil.AccessDenied:
            st.sidebar.error("Access Denied. Some system processes are protected.")
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
# -----------------------

state = load_state()

if not state:
    st.warning("No backend state found. Make sure 'python -m src.main' is running!")
    st.stop()

# --- Top Metric Row ---
system = state.get("system", {})
actual_cpu = round(system.get("cpu_percent", 0), 1)
predicted_cpu = state.get("predicted_cpu", actual_cpu)
memory = system.get("memory_percent", 0)
last_action = state.get("last_result", "No action")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Actual CPU", f"{actual_cpu}%")
col2.metric("Predicted CPU", f"{predicted_cpu:.1f}%", delta=f"{(predicted_cpu - actual_cpu):.1f}%")
col3.metric("Memory Usage", f"{memory}%")

# Color code the action status
status_color = "normal" if "No action" in last_action else "inverse"
col4.metric("Last Action", last_action, delta_color=status_color)

# --- Update History ---
timestamp = time.strftime("%H:%M:%S")
st.session_state.time_history.append(timestamp)
st.session_state.cpu_history.append(actual_cpu)
st.session_state.pred_history.append(predicted_cpu)

# --- Live Interactive Chart ---
st.subheader("📈 Live Predictive CPU Monitoring")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=list(st.session_state.time_history), 
    y=list(st.session_state.cpu_history),
    mode='lines+markers', name='Actual CPU', line=dict(color='#00b4d8', width=3)
))
fig.add_trace(go.Scatter(
    x=list(st.session_state.time_history), 
    y=list(st.session_state.pred_history),
    mode='lines', name='Predicted Future (3s)', line=dict(color='#ff9f1c', width=3, dash='dash')
))

# Add a horizontal line for the danger threshold
fig.add_hline(y=85, line_dash="dot", line_color="red", annotation_text="Danger Zone (85%)")

fig.update_layout(
    height=400, margin=dict(l=0, r=0, t=30, b=0),
    yaxis=dict(range=[0, 105], title="CPU %"),
    xaxis=dict(title="Time")
)
st.plotly_chart(fig, use_container_width=True)

# --- Interactive Process List ---
st.subheader("🔥 Top Resource Consumers")
processes = system.get("top_processes", [])

if processes:
    df = pd.DataFrame(processes)
    
    # Hide the useless System Idle Process (PID 0)
    df = df[df['pid'] != 0]
    
    # Normalize the CPU usage to a strict 0-100% scale
    cores = multiprocessing.cpu_count()
    df['cpu_percent'] = (df['cpu_percent'] / cores).round(1)

    # Reorder columns for readability
    df = df[['pid', 'name', 'cpu_percent', 'memory_percent']]
    
    st.dataframe(
        df,
        column_config={
            "cpu_percent": st.column_config.ProgressColumn("CPU %", format="%.1f%%", min_value=0, max_value=100),
            "memory_percent": st.column_config.ProgressColumn("Memory %", format="%.1f%%", min_value=0, max_value=100),
        },
        hide_index=True,
        use_container_width=True
    )

# --- Auto-Refresh Logic ---
# Streamlit will automatically rerun this script every 2 seconds
time.sleep(2)
st.rerun()