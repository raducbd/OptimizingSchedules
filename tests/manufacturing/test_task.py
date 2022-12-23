from scheduler.manufacturing import Task


class TestTask(object):
    def test_TaskInstantiated(self, task_example: Task):
        # OUTPUT
        output = task_example.__dict__

        # EXPECTED
        expected = {
            "id": 99,
            "machine": 20,
            "duration": 21,
            "start": None,
            "end": None,
            "interval": None,
        }

        # ASSERT
        assert output == expected
