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


def test_get_planned_tasks_sorts_incomplete_by_due_time_then_priority():
    scheduler = Scheduler(tasks=[])
    pet_id = str(uuid.uuid4())
    base = datetime(2030, 1, 1, 9, 0, 0)

    # Same due_time, different priority -> lower priority number first
    t1 = Task(
        task_id="t1",
        pet_id=pet_id,
        task_type="Task 1",
        due_time=base + timedelta(hours=1),
        priority=2,
        completed=False,
    )
    t2 = Task(
        task_id="t2",
        pet_id=pet_id,
        task_type="Task 2",
        due_time=base + timedelta(hours=1),
        priority=1,
        completed=False,
    )
    # Earlier due_time but completed=True -> should be excluded
    t3 = Task(
        task_id="t3",
        pet_id=pet_id,
        task_type="Task 3",
        due_time=base,
        priority=1,
        completed=True,
    )
    # Latest due_time, incomplete
    t4 = Task(
        task_id="t4",
        pet_id=pet_id,
        task_type="Task 4",
        due_time=base + timedelta(hours=2),
        priority=1,
        completed=False,
    )

    scheduler.add_task(t1)
    scheduler.add_task(t2)
    scheduler.add_task(t3)
    scheduler.add_task(t4)

    planned = scheduler.get_planned_tasks()
    assert [t.task_id for t in planned] == ["t2", "t1", "t4"]
    assert all(not t.completed for t in planned)


def test_complete_recurring_daily_creates_next_day_task():
    due = datetime(2030, 1, 1, 8, 0, 0)
    task = Task(
        task_id="daily-task",
        pet_id=str(uuid.uuid4()),
        task_type="Medication",
        due_time=due,
        priority=1,
        completed=False,
        is_recurring=True,
        frequency="daily",
    )

    next_task = task.complete()

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_time == due + timedelta(days=1)
    assert next_task.pet_id == task.pet_id
    assert next_task.task_type == task.task_type
    assert next_task.task_id != task.task_id


def test_filter_by_pet_id_with_no_tasks_returns_empty_list():
    scheduler = Scheduler(tasks=[])
    existing_pet_id = str(uuid.uuid4())
    missing_pet_id = str(uuid.uuid4())

    scheduler.add_task(
        Task(
            task_id=str(uuid.uuid4()),
            pet_id=existing_pet_id,
            task_type="Feeding",
            due_time=datetime.now() + timedelta(hours=1),
            priority=1,
            completed=False,
        )
    )

    result = scheduler.filter_tasks(pet_id=missing_pet_id)
    assert result == []


def test_detect_conflicts_exact_same_time_same_pet():
    scheduler = Scheduler(tasks=[])
    pet_id = str(uuid.uuid4())
    due = datetime(2030, 1, 1, 10, 0, 0)

    t1 = Task(
        task_id="same-1",
        pet_id=pet_id,
        task_type="Walk",
        due_time=due,
        priority=1,
        completed=False,
    )
    t2 = Task(
        task_id="same-2",
        pet_id=pet_id,
        task_type="Feed",
        due_time=due,
        priority=2,
        completed=False,
    )

    scheduler.add_task(t1)
    scheduler.add_task(t2)

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    pair_ids = {conflicts[0][0].task_id, conflicts[0][1].task_id}
    assert pair_ids == {"same-1", "same-2"}


def test_complete_recurring_with_none_frequency_returns_none():
    task = Task(
        task_id="rec-none",
        pet_id=str(uuid.uuid4()),
        task_type="Supplements",
        due_time=datetime(2030, 1, 1, 7, 0, 0),
        priority=1,
        completed=False,
        is_recurring=True,
        frequency=None,
    )

    next_task = task.complete()

    assert task.completed is True
    assert next_task is None


def test_filter_tasks_empty_scheduler_all_argument_combinations():
    scheduler = Scheduler(tasks=[])
    any_pet_id = str(uuid.uuid4())

    assert scheduler.filter_tasks() == []
    assert scheduler.filter_tasks(pet_id=any_pet_id) == []
    assert scheduler.filter_tasks(completed=True) == []
    assert scheduler.filter_tasks(completed=False) == []
    assert scheduler.filter_tasks(pet_id=any_pet_id, completed=True) == []
    assert scheduler.filter_tasks(pet_id=any_pet_id, completed=False) == []