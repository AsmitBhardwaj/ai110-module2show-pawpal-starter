from pawpal_system import Owner, Task, Pet, Scheduler
from datetime import datetime, timedelta
import uuid

owner = Owner(
    owner_id=str(uuid.uuid4()),
    name="Asmit Bhardwaj",
    email="asmitbhardwaj1@gmail.com",
    phone="223-342-3423",
    pets=[],
)

pet1 = Pet(
    pet_id=str(uuid.uuid4()),
    name="Dodo",
    owner_id=owner.owner_id,
    species="Identity Crisis",
    breed="Identity Crisis again",
    age=5,
)

pet2 = Pet(
    pet_id=str(uuid.uuid4()),
    name="Bambi",
    owner_id=owner.owner_id,
    species="German Cat",
    breed="Mischevious",
    age=5,
)

task1 = Task(
    task_id=str(uuid.uuid4()),
    pet_id=pet1.pet_id,
    task_type="Walking",
    due_time=datetime.now() + timedelta(hours=1),
    priority=2,
    completed=False,
    is_recurring=True,
    frequency="Every 6 hours",
)

task2 = Task(
    task_id=str(uuid.uuid4()),
    pet_id=pet2.pet_id,
    task_type="Food",
    due_time=datetime.now() + timedelta(hours=1),
    priority=1,
    completed=False,
    is_recurring=True,
    frequency="Twice per day",
)

task3 = Task(
    task_id=str(uuid.uuid4()),
    pet_id=pet1.pet_id,
    task_type="Visit to the vet",
    due_time=datetime.now() + timedelta(hours=1),
    priority=3,
    completed=False,
    is_recurring=True,
    frequency="Once a month",
)

scheduler = Scheduler(tasks=[])

scheduler.add_task(task1)
scheduler.add_task(task2)
scheduler.add_task(task3)

owner.add_pet(pet1)
owner.add_pet(pet2)

# Create pet lookup dict
pet_lookup = {p.pet_id: p.name for p in owner.pets}

# print the schedule
print("----------Today's Schedule----------")
for task in scheduler.get_todays_tasks():
    pet_name = pet_lookup.get(task.pet_id, "Unknown")
    status = "Done" if task.completed else "Pending"
    print(f"Priority : {task.priority} {task.task_type} Due : {task.due_time} - Pet : {pet_name} Status : {status}")


