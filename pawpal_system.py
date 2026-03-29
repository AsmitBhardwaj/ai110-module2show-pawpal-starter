from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Optional
from copy import copy
from uuid import uuid4
import json
import os

@dataclass
class Task:
    """
Represents a task associated with a pet, such as feeding, walking, or medication.

Attributes:
    task_id (str): Unique identifier for the task.
    pet_id (str): Identifier of the pet associated with the task.
    task_type (str): Type or description of the task.
    due_time (datetime): The scheduled time by which the task should be completed.
    priority (int): Priority level of the task (higher value indicates higher priority).
    completed (bool): Indicates whether the task has been completed.
    is_recurring (bool, optional): Whether the task is recurring. Defaults to False.
    frequency (Optional[str], optional): Frequency of recurrence if the task is recurring.

Methods:
    complete():
        Marks the task as completed and returns the next recurring task when applicable.

    reschedule(new_time):
        Reschedules the task to a new due time.

    is_overdue():
        Checks if the task is overdue (not completed and due_time is in the past).
"""
    task_id: str
    pet_id: str
    task_type: str
    due_time: datetime
    priority: int
    completed: bool
    is_recurring: bool = False
    frequency: Optional[str] = None

    def complete(self):
        """Mark task complete and return the next recurring task when applicable."""
        self.completed = True

        if not self.is_recurring:
            return None

        frequency_map = {
            "daily": timedelta(days=1),
            "weekly": timedelta(days=7),
            "every 6 hours": timedelta(hours=6),
            "twice per day": timedelta(hours=12),
            "once a month": timedelta(days=30),
        }

        shift = frequency_map.get((self.frequency or "").strip().lower())
        if shift is None:
            return None

        next_task = copy(self)  # new Task object with same attributes
        next_task.task_id = f"{self.task_id}-next-{uuid4().hex[:8]}"
        next_task.completed = False
        next_task.due_time = self.due_time + shift
        return next_task

    def reschedule(self, new_time):
        self.due_time = new_time

    def is_overdue(self):
        return (not self.completed) and (self.due_time < datetime.now())

@dataclass
class Pet:
    """
    Represents a pet in the PawPal system.

    Attributes:
        pet_id (str): Unique identifier for the pet.
        name (str): Name of the pet.
        owner_id (str): Unique identifier for the pet's owner.
        species (str): Species of the pet (e.g., dog, cat).
        breed (str): Breed of the pet.
        age (int): Age of the pet.

    Methods:
        get_info():
            Returns a dictionary representation of the pet's attributes.

        get_tasks(scheduler):
            Returns a list of tasks associated with this pet from the provided scheduler.
            Args:
                scheduler: An object containing a list of tasks, each with a pet_id attribute.
            Returns:
                List of tasks related to this pet.
    """
    pet_id: str
    name: str
    owner_id: str
    species: str
    breed: str
    age: int

    def get_info(self):
        return asdict(self)

    def get_tasks(self, scheduler):
        return [task for task in scheduler.tasks if task.pet_id == self.pet_id]

@dataclass
class Owner:
    """
Represents a pet owner in the PawPal system.

Attributes:
    owner_id (str): Unique identifier for the owner.
    name (str): Name of the owner.
    email (str): Email address of the owner.
    phone (str): Phone number of the owner.
    pets (list): List of pets owned by the owner.

Methods:
    add_pet(pet):
        Adds a pet to the owner's list of pets and sets the pet's owner_id.
        Args:
            pet: The pet object to add.

    remove_pet(pet_id):
        Removes a pet from the owner's list by pet_id.
        Args:
            pet_id: The unique identifier of the pet to remove.

    get_pets():
        Returns the list of pets owned by the owner.
        Returns:
            list: The owner's pets.
"""
    owner_id: str
    name: str
    email: str
    phone: str
    pets: list

    def add_pet(self, pet):
        pet.owner_id = self.owner_id
        self.pets.append(pet)

    def remove_pet(self, pet_id):
        self.pets = [pet for pet in self.pets if pet.pet_id != pet_id]

    def get_pets(self):
        return self.pets

    def save_to_json(self, scheduler, filepath):
        """Save owner + pets + scheduler tasks to a JSON file."""
        owner_data = asdict(self)

        # Custom conversion for datetime fields in tasks.
        tasks_data = []
        for task in scheduler.tasks:
            task_data = asdict(task)
            task_data["due_time"] = task.due_time.isoformat()
            tasks_data.append(task_data)

        payload = {
            "owner": owner_data,
            "tasks": tasks_data,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    @staticmethod
    def load_from_json(filepath):
        """Load owner + pets + tasks from JSON and return (Owner, Scheduler)."""
        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        owner_blob = data.get("owner", {})
        pets = [Pet(**pet_data) for pet_data in owner_blob.get("pets", [])]

        tasks = []
        for task_data in data.get("tasks", []):
            task_copy = dict(task_data)
            due_time_raw = task_copy.get("due_time")
            if due_time_raw is not None:
                task_copy["due_time"] = datetime.fromisoformat(due_time_raw)
            tasks.append(Task(**task_copy))

        owner = Owner(
            owner_id=owner_blob.get("owner_id", ""),
            name=owner_blob.get("name", ""),
            email=owner_blob.get("email", ""),
            phone=owner_blob.get("phone", ""),
            pets=pets,
        )
        scheduler = Scheduler(tasks=tasks)
        return owner, scheduler

@dataclass
class Scheduler:   
    """
    A scheduler for managing pet care tasks with conflict detection and prioritization.

    Attributes:
        tasks (list): A list of Task objects to be scheduled and managed.

    Methods:
        add_task(task): Adds a new task to the scheduler.
        remove_task(task_id): Removes a task from the scheduler by its ID.
        get_todays_tasks(): Retrieves all incomplete tasks scheduled for today, sorted by priority.
        sort_by_priority(): Returns all tasks sorted by priority level.
        detect_conflicts(): Identifies scheduling conflicts for the same pet within 30-minute intervals.
        get_planned_tasks(): Return all incomplete tasks sorted by (due_time, priority).
        filter_tasks(pet_id=None, completed=None): Filter tasks in one pass.
        find_next_available_slot(pet_id, duration_minutes=30): Suggest next conflict-free start time.
    """
    tasks: list

    def add_task(self, task):
        if task is None:
            return
        self.tasks.append(task)

    def remove_task(self, task_id):
        self.tasks = [task for task in self.tasks if task.task_id != task_id]

    def get_todays_tasks(self):
        today = datetime.now().date()
        todays = [
            task for task in self.tasks
            if (not task.completed) and (task.due_time.date() == today)
        ]
        return sorted(todays, key=lambda t: t.priority)

    def sort_by_priority(self):
        return sorted(self.tasks, key=lambda t: t.priority)

    def detect_conflicts(self):
        conflicts = []
        for i in range(len(self.tasks)):
            for j in range(i + 1, len(self.tasks)):
                t1, t2 = self.tasks[i], self.tasks[j]
                if t1.pet_id != t2.pet_id:
                    continue
                if abs(t1.due_time - t2.due_time) <= timedelta(minutes=30):
                    conflicts.append((t1, t2))
        return conflicts

    def get_planned_tasks(self):
        """Return incomplete tasks sorted by due_time and priority."""
        incomplete_tasks = [task for task in self.tasks if not task.completed]
        return sorted(incomplete_tasks, key=lambda task: (task.due_time, task.priority))

    def filter_tasks(self, pet_id=None, completed=None):
        """Filter tasks by optional pet_id and/or completed status in one pass."""
        filtered = []
        for task in self.tasks:
            if pet_id is not None and task.pet_id != pet_id:
                continue
            if completed is not None and task.completed != completed:
                continue
            filtered.append(task)
        return filtered

    def find_next_available_slot(self, pet_id, duration_minutes=30):
        """Find the next start time with no tasks within 30 minutes for the given pet."""
        now = datetime.now()
        window = timedelta(minutes=30)
        pet_tasks = [task for task in self.tasks if task.pet_id == pet_id]

        # Default behavior when there is no nearby conflict from now.
        if not any(abs(task.due_time - now) <= window for task in pet_tasks):
            return now + timedelta(hours=1)

        candidate = now
        while True:
            conflicts = [task for task in pet_tasks if abs(task.due_time - candidate) <= window]
            if not conflicts:
                return candidate

            latest_conflict = max(task.due_time for task in conflicts)
            candidate = latest_conflict + window + timedelta(seconds=1)

    @staticmethod
    def format_time_gap(delta: timedelta) -> str:
        """Convert a timedelta into a compact, human-readable gap string."""
        total_minutes = int(abs(delta).total_seconds() // 60)
        if total_minutes < 60:
            return f"{total_minutes} minute(s)"

        hours, minutes = divmod(total_minutes, 60)
        if minutes == 0:
            return f"{hours} hour(s)"
        return f"{hours}h {minutes}m"