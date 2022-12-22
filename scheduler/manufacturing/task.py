from typing import Optional
from dataclasses import dataclass
from ortools.sat.python import cp_model


@dataclass
class Task:
    """Class for identifying a task in a given job."""

    id: int
    machine: int
    duration: int
    start: Optional[cp_model.IntVar] = None
    end: Optional[cp_model.IntVar] = None
    interval: Optional[cp_model.IntervalVar] = None
