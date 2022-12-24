import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from scheduler import Scheduler
from scheduler.manufacturing import Task, Job

MACHINES = ["E-101", "T-301", "R-201"]
if "TASKS" not in st.session_state:
    st.session_state["TASKS"] = []
if "JOBS" not in st.session_state:
    st.session_state["JOBS"] = []

st.set_page_config(
    page_title="Scheduler", page_icon="🗓", layout="wide", initial_sidebar_state="auto"
)
st.title("Scheduler 🗓")


@st.cache
def load_data(scheduler: Scheduler) -> pd.DataFrame:
    """Function that returns final dataframe with results of the scheduler.

    Args:
        scheduler (Scheduler): Scheduler object with all the Jobs required for the workflow.

    Returns:
        pd.DataFrame: Dataframe containing Job/Task Id and corresponding start, end times.
    """
    return scheduler.fit().get_results()


# SIDEBAR DEFINITIONS
st.sidebar.title("Start datetime and Tasks")
### START DATETIME INPUT
start_date = st.sidebar.date_input(
    label="Start Date",
    value=datetime.now() + timedelta(hours=1),
    min_value=datetime.now() + timedelta(hours=1),
)
start_time = st.sidebar.time_input(
    label="Start Time",
    value=datetime.strptime(datetime.now().strftime("%H:00"), "%H:%M")
    + timedelta(hours=1),
)
start = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M:%S")

### FORM TO ADD TASKS
with st.sidebar:
    with st.sidebar.form("task_form"):
        st.write("Insert a task")
        task_name = st.text_input("Unique Name", value="Heating")
        machine = st.selectbox(label="Machine", options=MACHINES)
        duration = st.slider(
            label="Task Duration (h)", min_value=1, max_value=5, value=2
        )

        # Every form must have a submit button.
        submitted = st.form_submit_button("Add Task")
        if submitted:
            st.session_state["TASKS"].append(
                Task(
                    id=len(st.session_state["TASKS"]),
                    name=task_name,
                    machine=machine,
                    duration=int(duration),
                )
            )

# MAIN APP
### ADD JOBS
n_jobs = st.selectbox(label="Number of Jobs", options=np.arange(start=0, stop=6))

if n_jobs > 0:
    cols = st.columns(int(n_jobs))
    for i, col in enumerate(cols):
        with col:
            job_name = st.text_input("Unique Name", value="HDPE", key=f"name_{i}")
            job_tasks = st.multiselect(
                label="Tasks (Follow logical order)",
                options=st.session_state["TASKS"],
                key=f"tasks_{i}",
            )

    if st.button(label="Add Jobs"):
        for i in range(n_jobs):
            st.session_state["JOBS"].append(
                Job(
                    id=len(st.session_state["JOBS"]),
                    tasks=st.session_state[f"tasks_{i}"],
                )
            )
