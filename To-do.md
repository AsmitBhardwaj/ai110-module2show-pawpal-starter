## Issues in main.py to fix

- Task list should be sorted by both priority and time.  
  **Plan:** Build `get_planned_tasks()` to support sorting by time/priority preference.

- There is no way to filter tasks by pet.  
  **Plan:** Add a task filtering method.

- Recurring tasks should duplicate automatically when completed.  
  **Plan:** Add recurring-task rollover logic (target completion path O(1)).

- Conflicts should be shown to the user.  
  **Plan:** Surface detected conflicts in the UI.

  # Stuff to verify in PawPal_System.py
  

