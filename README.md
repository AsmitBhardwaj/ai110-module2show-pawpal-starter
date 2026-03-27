# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

PawPal+ includes intelligent scheduling algorithms:

- **Priority + Time Sorting** — tasks are ordered by due time and priority
- **Pet & Status Filtering** — view tasks for a specific pet or completion status
- **Recurring Tasks** — completed recurring tasks automatically reschedule 
  based on their frequency
- **Conflict Detection** — warns when two tasks for the same pet overlap within 30 minutes

### Testing PawPal+
- python -m pytest
-test_task_complete completing a task sets it to True
-test_scheduler_add_task adding a task increases count by 1
-test_planned_task sorting returns task ordered by due time then priority
-test_recurring_completion completing a daily recurring task creates a new task due 1 day later
-test_pets_with_no_task filtering by pets with no tasks
-tests_time_conflict two task for same pet at identical time flagged as conflic
-test_reccuring_no_frequency recurring task with no frequency = none
-test_filler_empty_scheduler filerting tasks on an empty list returns []
-test_detect_conflicts two task within 30 min is flagged as conflict
-test_no_conflict two task 2hrs apart gives no conflict

Confidence Level 4/5

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
