from typing import List
from dataclasses import dataclass

from scheduler.manufacturing.task import Task


@dataclass
class Job:
    """Class for identifying a job and its sassociated tasks."""

    id: int
    tasks: List[Task]

    @property
    def horizon(self) -> int:
        return sum(task.duration for task in self.tasks)

    @property
    def machines(self) -> List[int]:
        return list(set([task.machine for task in self.tasks]))
