from typing import List
from dataclasses import dataclass

from scheduler.manufacturing.task import Task


@dataclass
class Job:
    """Class for identifying a job and its associated tasks.

    Args:
        id (int): Job unique identifier
        tasks (List[Task]): List of all tasks required for the job to run completely
    """

    id: int
    name: str
    tasks: List[Task]

    @property
    def horizon(self) -> int:
        """(int) Job's horizon. Conceptually, it is the maximum job duration if all Tasks run sequentially."""
        return sum(task.duration for task in self.tasks)

    @property
    def machines(self) -> List[int]:
        """(List[int]) All machines required for running job's tasks."""
        return list(set([task.machine for task in self.tasks]))
