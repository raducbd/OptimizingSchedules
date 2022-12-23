"""
Module that contains objects used as inputs for test scenarios.
"""
import pandas as pd
import pytest

from scheduler import Scheduler
from scheduler.manufacturing import Task, Job


@pytest.fixture(scope="module")
def task_example() -> Task:
    """Task example for testing purposes.

    Returns:
        Task: Mocked task example for testing.
    """
    return Task(id=99, machine=20, duration=21)


@pytest.fixture(scope="module")
def job_example() -> Job:
    """Job example for testing purposes.

    Returns:
        Job: Mocked job example for testing.
    """
    return Job(id=99, tasks=[Task(id=99, machine=20, duration=21) for _ in range(2)])


@pytest.fixture(scope="module")
def scheduler_example() -> Scheduler:
    """Scheduler example for testing purposes.

    Returns:
        Scheduler: Mocked scheduler example for testing.
    """
    return Scheduler(
        jobs=[
            Job(
                id=0,
                tasks=[
                    Task(id=0, machine=1, duration=2),
                    Task(id=1, machine=2, duration=2),
                    Task(id=2, machine=3, duration=2),
                ],
            ),
            Job(
                id=1,
                tasks=[
                    Task(id=0, machine=3, duration=2),
                    Task(id=1, machine=2, duration=2),
                    Task(id=2, machine=1, duration=2),
                ],
            ),
        ]
    )


@pytest.fixture(scope="module")
def results_example() -> pd.DataFrame:
    """Scheduler example for testing purposes.

    Returns:
        Scheduler: Mocked scheduler example for testing.
    """
    return pd.DataFrame(
        {
            "job_id": [0, 1, 0, 1, 1, 0],
            "id": [
                "job(0, 0)",
                "job(1, 2)",
                "job(0, 1)",
                "job(1, 1)",
                "job(1, 0)",
                "job(0, 2)",
            ],
            "machine": [
                "Machine #1",
                "Machine #1",
                "Machine #2",
                "Machine #2",
                "Machine #3",
                "Machine #3",
            ],
            "start": [0, 6, 2, 4, 0, 4],
            "end": [2, 8, 4, 6, 2, 6],
        }
    )
