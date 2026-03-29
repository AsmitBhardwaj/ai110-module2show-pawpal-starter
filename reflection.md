# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

    My initial design consists of 
    -Owner : represents a pet owner. stores name, email, phone and responsible for adding and removing pets
    -Pet : represents the pet. store species, breed, age and daily activities. 
    -Task : represents the care actions like feeding, walk, vet appointment. Stores time and priority level for the task. can be marked complete, schedule etc.
    -Scheduler : holds all task and sort them by priority. also detects scheduling conflicts

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
After asking Copilot to review the skeleton, it flagged that Pet.owner_id 
and Task.pet_id were auto-generating UUIDs instead of being passed in, 
which would break the Owner↔Pet and Pet↔Task relationships. I fixed these 
to be required parameters. I also changed frequency to Optional[str] = None 
and added proper type hints to list fields.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

    The Scheduler should retrieve tasks by traversing the ownership chain:
    **Owner -> pets -> tasks**.  
    I would implement a method like `Scheduler.get_owner_tasks(owner)` that flattens
    all tasks from each pet into one list, then applies scheduling rules.

    Minimal pattern:
    - Iterate `owner.pets`
    - For each pet, append `pet.tasks` into a single list
    - Optionally filter completed tasks
    - Sort by priority first, then scheduled time

    Pseudocode:
    `all_tasks = [task for pet in owner.pets for task in pet.tasks]`

    This keeps relationships consistent and avoids duplicated task storage inside Scheduler.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My conflict detection checks if two tasks are within 30 minutes of each other 
using only their start times. It does not account for task duration — for example, 
a 1-hour vet appointment and a walk scheduled 20 minutes later would not actually 
overlap in reality if the appointment finishes first. A more accurate approach 
would store a duration for each task and check if time windows overlap, but this 
adds complexity. For now, the 30-minute window is a simple and readable approximation.

The detect_conflicts() method is also O(n²) — it compares every task against every 
other task. This is fine for a small number of tasks, but would slow down with 
hundreds of tasks. A faster approach would sort tasks by time first and only 
compare neighbors, making it O(n log n). It is reasonable because realistically a owner 
is not gonna have an insane number of pets. A typical pet owner has 2-5 pets with 10-20
tasks a day meaning at that scale O(n²) and O(n log n) perform virtually identically. We 
will not be experiencing any performance cost

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I used GitHub Copilot throughout the project in several ways:
- **Design brainstorming** — used Copilot Chat to generate the initial UML 
  class diagram and brainstorm attributes and methods for each class
- **Code generation** — used Inline Chat to generate the Python dataclass 
  skeleton and implement method bodies like detect_conflicts() and get_planned_tasks()
- **Code review** — used #file:pawpal_system.py to ask Copilot to review 
  the skeleton for missing relationships and type mismatches
- **Test generation** — used Copilot to draft pytest tests for edge cases 
  like empty schedulers, recurring tasks, and conflict detection
- **Streamlit wiring** — used Copilot to connect the backend classes to 
  the UI using st.session_state

- What kinds of prompts or questions were most helpful?

The most helpful prompts were ones that referenced specific files using 
#file: and gave clear context about what the classes were supposed to do.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

Copilot hallucinated a method called scheduler.format_time_gap() in app.py 
that never existed in pawpal_system.py. The app would have crashed immediately 
if I had accepted it without reviewing. I caught it by reading the generated 
code carefully and checking it against the actual methods in pawpal_system.py. 
I replaced it with a direct calculation using timedelta.total_seconds() instead.

- How did you evaluate or verify what the AI suggested?

Copilot also initially dropped task_type, is_recurring, and frequency from 
the Task dataclass when generating the skeleton. I caught this by comparing 
the output against our UML design and asked Copilot to restore the missing fields
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

I wrote 10 pytest tests covering the following behaviors:

- **Task completion** — verified that calling complete() sets completed=True
- **Scheduler task addition** — verified that add_task() increases task count
- **Planned task sorting** — verified get_planned_tasks() returns tasks ordered 
  by due_time then priority
- **Recurring task logic** — verified that completing a daily recurring task 
  creates a new task due exactly 1 day later with completed=False
- **Pet with no tasks** — verified filter_tasks() returns an empty list without 
  errors when a pet has no tasks assigned
- **Exact time conflicts** — verified two tasks for the same pet at identical 
  times are flagged as a conflict
- **Recurring task with no frequency** — verified complete() returns None when 
  is_recurring=True but frequency=None
- **Empty scheduler filtering** — verified filter_tasks() handles all argument 
  combinations on an empty scheduler without crashing
- **Conflict detection** — verified tasks within 30 minutes trigger a conflict
- **No false conflicts** — verified tasks 2 hours apart are not flagged

- Why were these tests important?

These tests were important because the scheduling and conflict logic are the 
core of PawPal+ — if they break silently, the app gives wrong output without 
any error message.

**b. Confidence**

- How confident are you that your scheduler works correctly?

I am 4/5 confident that the scheduler works correctly. All 10 tests pass and 
the Streamlit UI correctly displays sorted tasks, filtered views, and conflict 
warnings. 

- What edge cases would you test next if you had more time?


If I had more time I would test:
- Recurring tasks with every frequency type (weekly, every 6 hours, etc.)
- What happens when two pets have tasks at the same time (should not conflict)
- get_todays_tasks() when tasks span multiple days
- The Streamlit UI behavior when the same pet is added twice

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with the conflict detection and recurring task logic. 
The detect_conflicts() algorithm correctly identifies overlapping tasks for 
the same pet, and the recurring task system automatically generates the next 
occurrence when a task is completed — both features work seamlessly in the 
Streamlit UI. The test suite also came together well, with 10 passing tests 
covering both happy paths and edge cases.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had another iteration I would:
- Add a task duration field so conflict detection checks for actual time 
  window overlaps rather than just proximity of start times
- Add a way to mark tasks complete directly from the Streamlit UI instead 
  of only through code
- Store data persistently using a database or JSON file so tasks and pets 
  don't reset when the app restarts
- Add support for multiple owners instead of just one

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing I learned is that AI is a powerful assistant but 
not a replacement for understanding your own code. Copilot hallucinated a 
method that didn't exist and dropped fields from my dataclasses — both of 
which would have broken the app silently. The only reason I caught these 
mistakes was because I understood the design well enough to know something 
was wrong. AI works best when you use it to speed up work you already 
understand, not to replace the understanding itself.

## 6. Prompt Comparison

**Task:** Implement `reschedule_recurring_tasks()` for the Scheduler class

**Copilot (GPT-4.o):**
- Builds `frequency_map` inside the loop — inefficient, recreates 
  the dict on every iteration
- Uses a `while` loop to catch up multiple missed intervals — 
  smarter for long gaps (e.g. app was closed for a week)
- Uses `task_id + "-rescheduled"` instead of a new uuid — 
  could cause duplicate ID bugs if rescheduled twice
- Uses `self.tasks.extend()` instead of `add_task()` — 
  bypasses any future logic added to add_task()
- No return value — caller can't inspect what was generated

**Claude:**
- Builds `frequency_map` once outside the loop — more efficient
- Uses `uuid.uuid4()` for new task IDs — safer, no duplicates
- Calls `self.add_task()` instead of direct list extend — 
  more modular, respects the class interface
- Returns new tasks so the caller can inspect or log them
- Handles `None` frequency gracefully with early `continue`

**Conclusion:** Copilot's `while` loop for catching up missed 
intervals is actually a useful improvement. Claude's version is 
more modular and Pythonic overall, but combining both approaches 
would produce the best result.
