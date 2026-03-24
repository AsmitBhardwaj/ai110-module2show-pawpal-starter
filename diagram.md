classDiagram
    class Owner {
        +owner_id: String
        +name: String
        +email: String
        +phone: String
        +pets: List<Pet>
        +add_pet(pet: Pet)
        +remove_pet(pet_id: String)
        +get_pets(): List<Pet>
    }

    class Pet {
        +pet_id: String
        +name: String
        +species: String
        +breed: String
        +age: Integer
        +owner_id: String
        +get_info(): String
        +get_tasks(): List<Task>
    }

    class Task {
        +task_id: String
        +pet_id: String
        +task_type: String
        +due_time: DateTime
        +priority: Integer
        +is_recurring: Boolean
        +frequency: String
        +completed: Boolean
        +complete()
        +reschedule(new_time: DateTime)
        +is_overdue(): Boolean
    }

    class Scheduler {
        +tasks: List<Task>
        +add_task(task: Task)
        +remove_task(task_id: String)
        +get_todays_tasks(): List<Task>
        +sort_by_priority()
        +detect_conflicts(): List<Task>
    }

    Owner "1" -- "0..*" Pet : owns
    Pet "1" -- "0..*" Task : has
    Scheduler "1" -- "0..*" Task : manages