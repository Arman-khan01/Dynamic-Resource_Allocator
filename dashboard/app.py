import json
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / "logs" / "state.json"
ACTIONS_LOG = ROOT / "logs" / "actions.log"


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def load_recent_logs(limit: int = 15) -> list[str]:
    if not ACTIONS_LOG.exists():
        return []
    lines = ACTIONS_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
    return lines[-limit:]


st.set_page_config(page_title="Resource Allocator Dashboard", layout="wide")
st.title("Dynamic Resource Allocator Dashboard")
st.caption("Live view of CPU/RAM pressure, target process, and allocation actions.")

state = load_state()
system = state.get("system", {})
decision = state.get("decision", {})

col1, col2, col3 = st.columns(3)
col1.metric("CPU Usage (%)", f"{system.get('cpu_percent', 0):.1f}")
col2.metric("Memory Usage (%)", f"{system.get('memory_percent', 0):.1f}")
col3.metric("Last Action", state.get("last_result", "No data"))

st.subheader("Decision")
st.write(f"**Should Act:** {decision.get('should_act', False)}")
st.write(f"**Reason:** {decision.get('reason', 'No decision yet')}")

target = decision.get("target")
if target:
    st.write(
        "Target Process: "
        f"PID={target.get('pid')} | Name={target.get('name')} | "
        f"CPU={target.get('cpu_percent', 0):.1f}% | "
        f"MEM={target.get('memory_percent', 0):.1f}%"
    )
else:
    st.write("Target Process: None")

st.subheader("Top Processes")
top_processes = system.get("top_processes", [])
if top_processes:
    st.dataframe(top_processes, use_container_width=True)
else:
    st.info("No process samples yet. Start `src/main.py` first.")

st.subheader("Recent Actions Log")
recent_logs = load_recent_logs()
if recent_logs:
    st.code("\n".join(recent_logs))
else:
    st.info("No actions logged yet.")

st.button("Refresh", help="Streamlit can also auto-refresh from menu.")
