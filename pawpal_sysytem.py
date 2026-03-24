from dataclasses import dataclass, field
from datetime import datetime
import uuid
from typing import Optional

@dataclass
class Owner:
    owner_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    email: str = ""
    phone: str = ""
    pets: list["Pet"] = field(default_factory=list)

    def add_pet(self, pet):
        pass

    def remove_pet(self, pet_id):
        pass

    def get_pets(self):
        pass

@dataclass
class Pet:
    owner_id: uuid.UUID
    pet_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    species: str = ""
    breed: str = ""
    age: int = 0

    def get_info(self):
        pass

    def get_tasks(self):
        pass

@dataclass
class Task:
    pet_id: uuid.UUID
    task_id: uuid.UUID = field(default_factory=uuid.uuid4)
    task_type: str = ""
    due_time: datetime = field(default_factory=datetime.now)
    priority: int = 1  # 1-5
    is_recurring: bool = False
    frequency: Optional[str] = None
    completed: bool = False

    def complete(self):
        pass

    def reschedule(self, new_time):
        pass

    def is_overdue(self):
        pass

@dataclass
class Scheduler:
    tasks: list["Task"] = field(default_factory=list)

    def add_task(self, task):
        pass

    def remove_task(self, task_id):
        pass

    def get_todays_tasks(self):
        pass

    def sort_by_priority(self):
        pass

    def detect_conflicts(self):
        pass
