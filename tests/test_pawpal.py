import pytest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path so pawpal_system can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Task, Scheduler
import uuid


@pytest.fixture
def sample_task():
    return Task(
        task_id=str(uuid.uuid4()),

        pet_id=str(uuid.uuid4()),
        task_type="Walking",
        due_time=datetime.now() + timedelta(hours=1),
        priority=1,
        completed=False,
    )


def test_task_complete(sample_task):
    """Test that calling task.complete() sets task.completed to True"""
    assert sample_task.completed is False
    sample_task.complete()
    assert sample_task.completed is True


def test_scheduler_add_task():
    """Test that adding a task to a scheduler increases the task count by 1"""
    scheduler = Scheduler(tasks=[])
    initial_count = len(scheduler.tasks)

    task = Task(
        task_id=str(uuid.uuid4()),
        pet_id=str(uuid.uuid4()),
        task_type="Feeding",
        due_time=datetime.now() + timedelta(hours=2),
        priority=2,
        completed=False,
    )

    scheduler.add_task(task)
    assert len(scheduler.tasks) == initial_count + 1


def test_detect_conflicts():
    scheduler = Scheduler(tasks=[])
    pet_id = str(uuid.uuid4())

    task1 = Task(
        task_id=str(uuid.uuid4()),
        pet_id=pet_id,
        task_type="Feeding",
        due_time=datetime.now(),
        priority=1,
        completed=False,
    )
    task2 = Task(
        task_id=str(uuid.uuid4()),
        pet_id=pet_id,  # same pet!
        task_type="Walking",
        due_time=datetime.now() + timedelta(minutes=15),  # only 15 mins apart
        priority=2,
        completed=False,
    )

    scheduler.add_task(task1)
    scheduler.add_task(task2)

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1  # should find one conflict pair


def test_no_conflicts():
    scheduler = Scheduler(tasks=[])
    pet_id = str(uuid.uuid4())

    task1 = Task(
        task_id=str(uuid.uuid4()),
        pet_id=pet_id,
        task_type="Feeding",
        due_time=datetime.now(),
        priority=1,
        completed=False,
    )
    task2 = Task(
        task_id=str(uuid.uuid4()),
        pet_id=pet_id,
        task_type="Walking",
        due_time=datetime.now() + timedelta(hours=2),  # 2 hours apart = no conflict
        priority=2,
        completed=False,
    )

    scheduler.add_task(task1)
    scheduler.add_task(task2)

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 0