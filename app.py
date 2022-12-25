from typing import List, Optional
import streamlit as st
import time
from datetime import datetime, timedelta
from copy import copy
import pandas as pd
import numpy as np
import plotly.express as px

from scheduler import Scheduler
from scheduler.manufacturing import Task, Job
from scheduler.utils.errors import SolverUnsuccessful

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
def load_scheduler(jobs: List[Job]) -> Scheduler:
    """Function that returns our main Scheduler object.

    Args:
        jobs (List[Job]): List of all jobs input by the user

    Returns:
        Scheduler: Scheduler main object for generating final output.
    """
    return Scheduler(jobs)


@st.cache
def load_data(scheduler: Scheduler, start_date: Optional[datetime] = None) -> pd.DataFrame:
    """Function that returns final dataframe with results of the scheduler.

    Args:
        scheduler (Scheduler): Scheduler object with all the Jobs required for the workflow.
        start_date (datetime, optional): In case there is a start date, in order to build a proper schedule. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Job/Task Id and corresponding start, end times.
    """
    return scheduler.fit().get_results(start_date=start_date)

@st.cache
def convert_df(df: pd.DataFrame) -> None:
    """Function that caches conversion of pandas.DataFrame to CSV file, in order to prevent computation on every rerun.

    Args:
        df (pd.DataFrame): Pandas DataFrame
    """
    return df.to_csv().encode('utf-8')


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

    if st.button(label="Optimize Schedule"):
        for i in range(n_jobs):
            st.session_state["JOBS"].append(
                Job(
                    id=len(st.session_state["JOBS"]),
                    name=st.session_state[f"name_{i}"],
                    tasks=list(map(copy, st.session_state[f"tasks_{i}"])),
                )
            )

        scheduler = load_scheduler(st.session_state["JOBS"])
        try:
            results = load_data(scheduler, start_date=start)

            my_bar = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.1)
                my_bar.progress(percent_complete + 1)

            with st.container():
                st.write("OPTIMIZATION FINAL RESULTS")
                fig = px.timeline(results, x_start="Planned Start", x_end="Planned End", y="Process", color="Machine")
                fig.update_yaxes(autorange="reversed")
                st.plotly_chart(fig, theme="streamlit", use_container_width=True)
                
                st.dataframe(results)
                csv = convert_df(results)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name='results.csv',
                    mime='text/csv',
                )

        except SolverUnsuccessful:
            st.error("Optimization failed! Please start again...")
            st.session_state["TASKS"] = []
            st.session_state["JOBS"] = []
            n_jobs = 0

        else:
            st.info("Please contact gfluz94@gmail.com for any further explanations or adjustments! 😃")
