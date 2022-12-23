__all__ = ["Scheduler"]

import collections
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List
from ortools.sat.python import cp_model

from manufacturing import Job, Task
from utils.logging import logger
from utils.errors import SolverUnsuccessful, ModelNotFitted


class Scheduler(object):
    """Scheduler object which takes several jobs and their corresponding tasks and restrictions and optimizes the schedule.

    Args:
        jobs (List[Job]): List of all jobs that need to be accomplished.
    """

    def __init__(self, jobs: List[Job]) -> None:
        """Constructor method of Scheduler object.
        Args:
            jobs (List[Job]): List of all jobs that need to be accomplished.
        """
        self._jobs = {i: job for i, job in enumerate(jobs)}
        self._fitted = False

    @property
    def jobs(self) -> Dict[int, Job]:
        """(Dict[int, Job]) Dictionary with Job ID and actual Job object for all jobs that were passed to object."""
        return self._jobs

    @property
    def all_machines(self) -> List[int]:
        """(List[int]) List of all machines used for the Jobs."""
        machines = set()
        for job in self._jobs.values():
            machines |= set(job.machines)
        return sorted(machines)

    @property
    def horizon(self) -> int:
        """(int) Horizon of all jobs. Conceptually, it is the maximum duration if all Tasks from all Jobs run sequentially."""
        return sum(job.horizon for job in self._jobs.values())

    def _get_model(self) -> cp_model.CpModel:
        """Method to handle model as singleton

        Returns:
            cp_model.CpModel: Optimization Model.
        """
        if not hasattr(self, "_model"):
            self._model = cp_model.CpModel()
        return self._model

    def _get_machine_to_intervals(self) -> Dict[int, List[int]]:
        """Method to handle list of machine intervals as singleton

        Returns:
            Dict[int, List[int]]: Dictionary with machine id as key and list of intervals as values
        """
        if not hasattr(self, "_machine_to_intervals"):
            self._machine_to_intervals = collections.defaultdict(list)
        return self._machine_to_intervals

    def _get_solver(self) -> cp_model.CpSolver:
        """Method to handle solver as singleton

        Returns:
            cp_model.CpSolver: Optimization Solver.
        """
        if not hasattr(self, "_solver"):
            self._solver = cp_model.CpSolver()
        return self._solver

    def _initialize(self) -> None:
        """Method to initialize all variables required for optimization."""
        for job_id, job in self._jobs.items():
            for i, task in enumerate(job.tasks):
                suffix = f"{job_id}_{task.id}"
                task.start = self._get_model().NewIntVar(
                    0, self.horizon, f"start_{suffix}"
                )
                task.end = self._get_model().NewIntVar(0, self.horizon, f"end_{suffix}")
                task.interval = self._get_model().NewIntervalVar(
                    task.start, task.duration, task.end, f"interval_{suffix}"
                )
                self._jobs[job_id].tasks[i] = task
                self._get_machine_to_intervals()[task.machine].append(task.interval)

    def _fetch_task(self, job_id: int, task_id: int) -> Task:
        """Method to help retrieve a task of a job.

        Args:
            job_id (int): Single identifier of Job.
            task_id (int): Single identifier of Task.

        Returns:
            Task: Task object of specified job_id and task_id
        """
        return self._jobs[job_id].tasks[task_id]

    def _add_no_overlap_constraint(self) -> None:
        """Method to add no overlap constraint (machine handles single task at a time)"""
        for machine in self.all_machines:
            self._get_model().AddNoOverlap(
                interval_vars=self._get_machine_to_intervals()[machine]
            )

    def _add_precedence_constraints(self) -> None:
        """Method to add precedence constraint (end of previous task >= start next task in a single machine)"""
        for job_id, job in self._jobs.items():
            for task_id in range(len(job.tasks) - 1):
                precedent_task = self._fetch_task(job_id=job_id, task_id=task_id)
                next_task = self._fetch_task(job_id=job_id, task_id=task_id + 1)
                self._get_model().Add(next_task.start >= precedent_task.end)

    def _define_objective(self) -> None:
        """Method to define optimization main goal - ie, minimizing total duration of all jobs."""
        objective_var = self._get_model().NewIntVar(0, self.horizon, "makespan")
        self._get_model().AddMaxEquality(
            target=objective_var,
            exprs=[
                self._fetch_task(job_id=job_id, task_id=len(job.tasks) - 1).end
                for job_id, job in self._jobs.items()
            ],
        )
        self._get_model().Minimize(objective_var)

    def fit(self) -> object:
        """Method that orchestrates full training process.
        - Model and variables initialization;
        - No Overlap constraints are added;
        - Precedence constraints are added;
        - Objective measure is defined;
        - Optimization process;
        - Tasks are updated with final variables.

        Raises:
            SolverUnsuccessful: In case optimization encounters a problem along the way.

        Returns:
            Scheduler (object): Self object is returned
        """
        logger.info(f"Initialing model and defining variables...")
        self._initialize()

        logger.info(f"Adding No Overlap Constraint...")
        self._add_no_overlap_constraint()
        logger.info(f"Adding Precedence Constraints...")
        self._add_precedence_constraints()

        logger.info(f"Defining optimization goal...")
        self._define_objective()

        logger.info(f"Starting optimization...")
        status = self._get_solver().Solve(model=self._get_model())

        self._fitted = (status == cp_model.OPTIMAL) or (status == cp_model.FEASIBLE)
        if not self._fitted:
            raise SolverUnsuccessful(
                f"Optimization not successful with status {status}"
            )

        logger.info(f"Solver conflicts: {self._get_solver().NumConflicts()}")
        logger.info(f"Solver branches: {self._get_solver().NumBranches()}")
        logger.info(f"Solver wall time: {self._get_solver().WallTime()}s")

        self._update_tasks()

        return self

    def _update_tasks(self) -> None:
        """Method to update all taksk with values obtained after optimization."""
        if not self._fitted:
            raise ModelNotFitted(f"Model not fitted yet.")

        for job_id, job in self._jobs.items():
            for task_id, task in enumerate(job.tasks):
                task.start = self._get_solver().Value(
                    self._fetch_task(job_id=job_id, task_id=task_id).start
                )
                task.end = self._get_solver().Value(
                    self._fetch_task(job_id=job_id, task_id=task_id).end
                )
                self._jobs[job_id].tasks[task_id] = task

    def get_results(self, plot_gannt: bool = False) -> pd.DataFrame:
        """Method that generates a dataframe with the results obtained for every single task.

        Args:
            plot_gannt (bool, optional): Whether or not Gannt Chart should be displayed. Defaults to False.

        Raises:
            ModelNotFitted: If object hasn't been fitted yet, it is not possible to generate results.

        Returns:
            pd.DataFrame: Fianl dataframe containing start and end times for each task, after optimization.
        """
        if not self._fitted:
            raise ModelNotFitted(f"Model not fitted yet.")

        results = pd.DataFrame()
        for job_id, job in self._jobs.items():
            task_df = pd.DataFrame([task.__dict for task in job.tasks])
            task_df["job_id"] = job_id
            task_df["id"] = task_df["id"].apply(lambda x: f"job({job_id}, {x})")
            task_df["machine"] = task_df["machine"].apply(lambda x: f"Machine #{x}")
            results = pd.concat([results, task_df], axis=0, ignore_index=True)

        results["start_num"] = results["start"] - results["start"].min()
        results["end_num"] = results["end"] - results["start"].min()
        results["start_to_end"] = results["end_num"] - results["start_num"]

        if plot_gannt:
            self._plot_gannt(results)

        return (
            results.loc[:, ["job_id", "id", "machine", "start", "end"]]
            .sort_values(by=["machine", "start"])
            .reset_index(drop=True)
        )

    def _plot_gannt(self, df: pd.DataFrame) -> None:
        """Method to plot Gannt CHart once results dataframe is generated - a type of bar chart that illustrates a project schedule."""
        _, ax = plt.subplots(1, 1, figsize=(16, 6))
        labels = []
        for job_id in df["job_id"].unique():
            df_ = df[df["job_id"] == job_id]
            labels += df_.id.values.tolist()
            ax.barh(
                df_.machine,
                df_.start_to_end,
                left=df_.start_num,
                label=f"Job #{job_id}",
            )

        rects = ax.patches

        for rect, label in zip(rects, labels):
            height = rect.get_y() + rect.get_height() / 2
            width = rect.get_x() + rect.get_width() / 2
            ax.text(width, height, label, ha="center", va="center")

        xticks = np.arange(0, df.end_num.max() + 1, 1)
        ax.set_xticks(xticks)
        plt.legend()
        plt.show()
