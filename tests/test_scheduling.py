from functools import reduce
import pandas as pd
import pytest

from scheduler import Scheduler
from scheduler.manufacturing import Job, Task
from scheduler.utils.errors import ModelNotFitted


class TestScheduler(object):
    def test_SchedulerInstantiated(self, scheduler_example: Scheduler):
        # OUTPUT
        output = scheduler_example.__dict__

        # EXPECTED
        expected = {
            "_jobs": {
                0: Job(
                    id=0,
                    tasks=[
                        Task(id=0, name="0", machine=1, duration=2),
                        Task(id=1, name="1", machine=2, duration=2),
                        Task(id=2, name="2", machine=3, duration=2),
                    ],
                ),
                1: Job(
                    id=1,
                    tasks=[
                        Task(id=0, name="0", machine=3, duration=2),
                        Task(id=1, name="1", machine=2, duration=2),
                        Task(id=2, name="2", machine=1, duration=2),
                    ],
                ),
            },
            "_fitted": False,
        }

        # ASSERT
        assert output == expected

    def test_horizonCorrectOutput(self, scheduler_example: Scheduler):
        # OUTPUT
        output = scheduler_example.horizon

        # EXPECTED
        expected = 12

        # ASSERT
        assert output == expected

    def test_all_machinesCorrectOutput(self, scheduler_example: Scheduler):
        # OUTPUT
        output = scheduler_example.all_machines

        # EXPECTED
        expected = [1, 2, 3]

        # ASSERT
        assert output == expected

    def test_get_resultsRaisesModelNotFitted(self, scheduler_example: Scheduler):
        with pytest.raises(ModelNotFitted):
            _ = scheduler_example.get_results()

    def test_get_resultsCorrectOutput(
        self, scheduler_example: Scheduler, results_example: pd.DataFrame
    ):
        # OUTPUT
        output = scheduler_example.fit().get_results()

        # EXPECTED
        expected = results_example

        # ASSERT
        assert reduce(
            lambda a, b: a and b,
            [(expected[c] == output[c]).all() for c in output.columns],
        )
