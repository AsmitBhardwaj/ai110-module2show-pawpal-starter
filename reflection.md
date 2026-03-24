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

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
