from scheduler.manufacturing import Task, Job


class TestJob(object):
    def test_JobInstantiated(self, job_example: Job, task_example: Task):
        # OUTPUT
        output = job_example.__dict__

        # EXPECTED
        expected = {"id": 99, "tasks": [task_example for _ in range(2)]}

        # ASSERT
        assert output == expected

    def test_horizonOutputCorrect(self, job_example: Job):
        # OUTPUT
        output = job_example.horizon

        # EXPECTED
        expected = 42

        # ASSERT
        assert output == expected

    def test_machinesOutputCorrect(self, job_example: Job):
        # OUTPUT
        output = job_example.machines

        # EXPECTED
        expected = [20]

        # ASSERT
        assert output == expected
