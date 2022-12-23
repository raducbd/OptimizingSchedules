"""
Module that contains objects used as inputs for test scenarios.
"""
import pytest

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
