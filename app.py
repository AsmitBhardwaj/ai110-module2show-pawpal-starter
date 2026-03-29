import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import datetime, timedelta
import uuid
import os


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

PawPal+ is a smart pet care management system that helps owners keep their pets happy and healthy.
Track daily routines, schedule tasks, and get intelligent conflict detection — all in one place.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** helps pet owners manage daily care routines for their pets. 
Add your pets, schedule tasks like feedings, walks, medications, and vet appointments, 
and let the system prioritize and organize your day automatically.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
- **Add Pets** — register multiple pets under one owner
- **Schedule Tasks** — assign care tasks with priority levels and due times
- **Smart Sorting** — tasks automatically sorted by priority and time
- **Recurring Tasks** — tasks auto-reschedule on completion
- **Conflict Detection** — get warned when two tasks overlap for the same pet
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

DATA_FILE = "data.json"


def save_session_data():
    st.session_state.owner.save_to_json(st.session_state.scheduler, DATA_FILE)

# Persist Owner object across reruns
if "owner" not in st.session_state or "scheduler" not in st.session_state:
    if os.path.exists(DATA_FILE):
        loaded_data = Owner.load_from_json(DATA_FILE)
        if loaded_data is not None:
            st.session_state.owner, st.session_state.scheduler = loaded_data
        else:
            st.session_state.owner = Owner(
                owner_id=str(uuid.uuid4()),
                name=owner_name,
                email="",
                phone="",
                pets=[],
            )
            st.session_state.scheduler = Scheduler(tasks=[])
    else:
        st.session_state.owner = Owner(
            owner_id=str(uuid.uuid4()),
            name=owner_name,
            email="",
            phone="",
            pets=[],
        )
        st.session_state.scheduler = Scheduler(tasks=[])

st.session_state.owner.name = owner_name

st.caption(f"Current Owner ID: {st.session_state.owner.owner_id}")

st.divider()
st.subheader("Add a Pet")

with st.form("add_pet_form"):
    new_pet_name = st.text_input("Pet name", value=pet_name)
    new_species = st.selectbox("Pet species", ["dog", "cat", "other"], key="add_pet_species")
    new_breed = st.text_input("Breed", value="Mixed")
    new_age = st.number_input("Age", min_value=0, max_value=40, value=1)
    add_pet_submitted = st.form_submit_button("Add Pet")

    if add_pet_submitted:
        pet = Pet(
            pet_id=str(uuid.uuid4()),
            name=new_pet_name,
            owner_id=st.session_state.owner.owner_id,
            species=new_species,
            breed=new_breed,
            age=int(new_age),
        )
        st.session_state.owner.add_pet(pet)
        save_session_data()
        st.success(f"Added pet: {pet.name}")

if st.session_state.owner.pets:
    st.write("Current pets:")
    st.table([
        {
            "Name": p.name,
            "Species": p.species,
            "Breed": p.breed,
            "Age": p.age,
        }
        for p in st.session_state.owner.pets
    ])
else:
    st.info("No pets yet. Add one above.")

st.divider()
st.subheader("Schedule a Task")

if not st.session_state.owner.pets:
    st.warning("Add at least one pet before scheduling tasks.")
else:
    pet_options = {f"{p.name} ({p.species})": p for p in st.session_state.owner.pets}
    with st.form("schedule_task_form"):
        selected_label = st.selectbox("Select pet", list(pet_options.keys()))
        task_type = st.text_input("Task type", value="Morning walk")
        due_in_hours = st.number_input("Due in hours", min_value=0, max_value=72, value=1)
        priority_label = st.selectbox("Priority", ["high", "medium", "low"], index=0)
        is_recurring = st.checkbox("Recurring task?", value=False)
        frequency = st.text_input("Frequency (optional)", value="") if is_recurring else ""
        schedule_task_submitted = st.form_submit_button("Schedule Task")

        if schedule_task_submitted:
            priority_map = {"high": 1, "medium": 2, "low": 3}
            selected_pet = pet_options[selected_label]
            task = Task(
                task_id=str(uuid.uuid4()),
                pet_id=selected_pet.pet_id,
                task_type=task_type,
                due_time=datetime.now() + timedelta(hours=int(due_in_hours)),
                priority=priority_map[priority_label],
                completed=False,
                is_recurring=is_recurring,
                frequency=frequency or None,
            )
            st.session_state.scheduler.add_task(task)
            save_session_data()
            st.success(f"Scheduled task: {task.task_type} for {selected_pet.name}")

st.subheader("⚠️ Task Conflicts")

conflicts = st.session_state.scheduler.detect_conflicts()  # required call

if not conflicts:
    st.info("No scheduling conflicts detected.")
else:
    pets_by_id = {pet.pet_id: pet.name for pet in st.session_state.owner.pets}

    for t1, t2 in conflicts:
        pet_name = pets_by_id.get(t1.pet_id, "Unknown")
        diff = abs((t1.due_time - t2.due_time).total_seconds() / 60)
        st.warning(f"⚠️ {pet_name}: '{t1.task_type}' and '{t2.task_type}' are {diff:.0f} mins apart")


if st.session_state.scheduler.tasks:
    pet_lookup = {p.pet_id: p.name for p in st.session_state.owner.pets}
    st.write("Scheduled tasks (by priority):")
    st.table([
        {
            "Task": t.task_type,
            "Pet": pet_lookup.get(t.pet_id, "Unknown"),
            "Due": t.due_time,
            "Priority": t.priority,
            "Status": "Done" if t.completed else "Pending",
        }
        for t in st.session_state.scheduler.get_planned_tasks()
    ])
else:
    st.info("No tasks scheduled yet.")

st.divider()
st.subheader("🕐 Next Available Slot")
if st.session_state.owner.pets:
    slot_pet = st.selectbox("Find next slot for:", [p.name for p in st.session_state.owner.pets], key="slot_pet")
    selected = next(p for p in st.session_state.owner.pets if p.name == slot_pet)
    slot = st.session_state.scheduler.find_next_available_slot(selected.pet_id)
    st.success(f"Next available slot for {slot_pet}: {slot.strftime('%Y-%m-%d %H:%M')}")
