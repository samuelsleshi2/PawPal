# PawPal+ System Architecture - Final UML Diagram

## Overview

This is the final UML diagram for PawPal+, updated to reflect the complete implementation with all classes, attributes, methods, and relationships.

## Class Diagram (Mermaid)

```
classDiagram
    class Owner {
        -int owner_id
        -str name
        -str contact_info
        -List~Pet~ pets
        -Dict preferences
        +__init__(owner_id, name, contact_info, preferences)
        +add_pet(pet: Pet)
        +remove_pet(pet_id: int)
        +get_pets() List~Pet~
        +get_pet_by_id(pet_id: int) Pet
    }

    class Pet {
        -int pet_id
        -str name
        -str species
        -int hunger_level
        -int tiredness_level
        -str health_status
        -int age
        -List~Task~ tasks
        +get_condition() Dict
        +update_condition(condition: str, value: int)
        +needs_task(task_type: str) bool
    }

    class Task {
        -int task_id
        -str title
        -str description
        -int duration_minutes
        -str priority
        -str target_condition
        -int pet_id
        -str frequency
        -int progress
        -bool completed
        -str status
        -Optional~int~ scheduled_time
        -Optional~str~ time_window
        -date task_date
        -Optional~int~ next_task_id
        +get_progress() int
        +update_progress(amount: int)
        +mark_complete() Optional~Task~
        +set_scheduled_time(minutes_from_midnight: int)
        +set_status(new_status: str)
        +get_time_window_range() Tuple~int, int~
        +get_description() str
        +create_next_occurrence() Task
    }

    class Calendar {
        -List~Task~ tasks
        -date date
        -Optional~int~ pet_id
        -Optional~int~ owner_id
        +add_task(task: Task)
        +remove_task(task_id: int)
        +clear_tasks()
        +get_tasks() List~Task~
        +is_empty() bool
        +generate_schedule(pet: Pet, available_minutes: int) List~Task~
        +get_task_by_id(task_id: int) Optional~Task~
        +filter_tasks_by_pet(pet_id: int) List~Task~
        +filter_tasks_by_status(status: str) List~Task~
        +filter_tasks_by_completion(completed: bool) List~Task~
        +filter_tasks_by_pet_and_status(pet_id: int, status: str) List~Task~
        +get_tasks_for_date(target_date: date) List~Task~
    }

    class Scheduler {
        -Dict~str, int~ priority_weights
        +__init__(priority_weights: Optional~Dict~)
        +generate_schedule(pet: Pet, available_tasks: List~Task~, available_minutes: int) List~Task~
        +filter_tasks_for_pet(pet: Pet, tasks: List~Task~) List~Task~
        +expand_recurring_tasks(tasks: List~Task~) List~Task~
        +sort_by_priority(tasks: List~Task~) List~Task~
        +sort_by_time(tasks: List~Task~) List~Task~
        +schedule_with_times(tasks: List~Task~, available_minutes: int) List~Task~
        +detect_conflicts(tasks: List~Task~) List~Tuple~Task, Task~~
        +detect_simultaneous_tasks(tasks: List~Task~) List~Dict~
        +print_conflict_warnings(tasks: List~Task~) int
        +resolve_conflicts(tasks: List~Task~) List~Task~
        +fit_tasks_in_time(tasks: List~Task~, available_minutes: int) List~Task~
    }

    Owner "1" --> "*" Pet: owns
    Pet "1" --> "*" Task: has
    Calendar "1" --> "*" Task: contains
    Calendar "0..1" --> "1" Pet: manages
    Calendar "0..1" --> "1" Owner: belongs_to
    Scheduler "1" --> "*" Task: processes
```

## Detailed Class Descriptions

### **Owner**
**Responsibility:** Manages the collection of pets and their aggregate information.

**Key Attributes:**
- `owner_id`: Unique identifier
- `name`: Owner's full name
- `contact_info`: Phone/email for notifications
- `pets`: List of Pet objects
- `preferences`: Dictionary for owner scheduling preferences

**Key Methods:**
- `add_pet()` / `remove_pet()` — Pet collection management
- `get_pet_by_id()` — Quick pet lookup

---

### **Pet**
**Responsibility:** Represents an individual pet with health/condition tracking.

**Key Attributes:**
- `pet_id`: Unique identifier
- `name`, `species`, `age` — Basic pet info
- `hunger_level`, `tiredness_level` — Condition states (0-100)
- `health_status` — Current health state
- `tasks` — Associated task list

**Key Methods:**
- `get_condition()` — Returns current state summary
- `update_condition()` — Updates condition with bounds checking (0-100 clamping)
- `needs_task()` — Determines if pet needs specific task types based on condition thresholds

---

### **Task**
**Responsibility:** Represents a single pet care task with lifecycle tracking and recurrence support.

**Key Attributes:**
- `task_id`: Unique identifier
- `title`, `description` — Task details
- `duration_minutes`: How long the task takes
- `priority`: high/medium/low weighting
- `target_condition`: Condition this task affects (hunger_level, tiredness_level, health_status)
- `pet_id`: Which pet this task is for
- `frequency`: once/daily/weekly for recurrence
- `progress`, `completed`, `status` — Lifecycle tracking
- `scheduled_time`: Time slot in minutes from midnight (0-1440)
- `time_window`: Preference (morning/afternoon/evening/anytime)
- `task_date`: Date this task is scheduled for
- `next_task_id`: Link to next recurring occurrence

**Key Methods:**
- `mark_complete()` → Returns next Task if recurring, None otherwise
- `create_next_occurrence()` — Generates with +1 day (daily) or +7 days (weekly)
- `get_time_window_range()` — Returns (start, end) minutes for preference
- `set_scheduled_time()` — Validates and assigns time slot

---

### **Calendar**
**Responsibility:** Container and query interface for tasks; delegates scheduling to Scheduler.

**Key Attributes:**
- `tasks`: List of all Task objects
- `date`: Calendar date
- `pet_id`: Optional single-pet focus
- `owner_id`: Optional owner association

**Key Methods:**
- **CRUD:** `add_task()`, `remove_task()`, `clear_tasks()`, `get_task_by_id()`
- **Filtering:** `filter_tasks_by_pet()`, `filter_tasks_by_status()`, `filter_tasks_by_completion()`, `filter_tasks_by_pet_and_status()`
- **Scheduling:** `generate_schedule()` — Creates Scheduler and delegates

---

### **Scheduler** ⭐ (New in Final Implementation)
**Responsibility:** Core scheduling engine; implements all intelligent scheduling logic.

**Key Attributes:**
- `priority_weights`: Customizable priority scoring (high=3, medium=2, low=1)

**Key Methods:**

| Method | Purpose |
|--------|---------|
| `generate_schedule()` | Master orchestrator: filter → expand → sort → schedule → resolve |
| `filter_tasks_for_pet()` | Extract pet-specific, non-completed tasks relevant to pet's conditions |
| `expand_recurring_tasks()` | Include daily/weekly tasks for the current day |
| `sort_by_priority()` | Order by: priority weight (desc), then duration (asc) |
| `sort_by_time()` | Chronological ordering by `scheduled_time` (asc) for display |
| `schedule_with_times()` | Greedy bin-packing: assign time slots respecting time windows |
| `detect_conflicts()` | Find overlapping task pairs |
| `detect_simultaneous_tasks()` | **REQUIRED TEST 3:** Find tasks at same start time, flag severity |
| `print_conflict_warnings()` | Format and display warnings to console |
| `resolve_conflicts()` | Reschedule lower-priority tasks to avoid overlaps |
| `fit_tasks_in_time()` | Legacy: filter tasks that fit within available minutes |

---

## Key Design Changes from Initial to Final

| Aspect | Initial | Final |
|--------|---------|-------|
| **Classes** | 4 (Owner, Pet, Task, Calendar) | 5 (+ Scheduler) |
| **Task.pet_id** | Not tracked | Added: links task to pet |
| **Task.frequency** | Single use only | Added: once/daily/weekly |
| **Task.next_task_id** | N/A | Added: links recurrence chain |
| **Calendar.pet_id/owner_id** | N/A | Added: optional context |
| **Scheduling Logic** | Simple inside Calendar | **Moved to Scheduler class** |
| **Time Windows** | N/A | Added: morning/afternoon/evening/anytime |
| **Conflict Detection** | Implicit | **Explicit methods with severity levels** |
| **Sort Capabilities** | N/A | `sort_by_priority()` and `sort_by_time()` |

---

## Relationships Summary

```
┌─────────────────────────────────────────┐
│              Owner                       │
│  (manages multiple pets & preferences)   │
└─────────────────────────────────────────┘
                 │ owns "1..*"
                 ▼
┌─────────────────────────────────────────┐
│              Pet                         │
│ (condition states: hunger, tiredness)    │
└─────────────────────────────────────────┘
                 │ has "1..*"
                 ▼
┌─────────────────────────────────────────┐
│              Task                        │
│ (scheduled work with priority/frequency) │
│ (linked: next_task_id for recurrence)    │
└─────────────────────────────────────────┘
                 ▲
                 │ contains "0..*"
                 │
┌─────────────────────────────────────────┐
│             Calendar                     │
│ (holds + queries tasks)                  │
│ (delegates to Scheduler)                 │
└─────────────────────────────────────────┘
                 │ delegates
                 ▼
┌─────────────────────────────────────────┐
│            Scheduler                     │
│ (core algorithm: sort, schedule, detect) │
│ (respects priorities, time windows)      │
│ (flags conflicts with severity)          │
└─────────────────────────────────────────┘
```

---

## Critical Features Implemented

✅ **Sorting Correctness** — `sort_by_time()` orders chronologically  
✅ **Recurrence Logic** — `Task.mark_complete()` + `create_next_occurrence()` for daily/weekly  
✅ **Conflict Detection** — `detect_simultaneous_tasks()` with critical/warning levels  
✅ **Priority Scheduling** — `sort_by_priority()` with duration tiebreaking  
✅ **Time Windows** — `schedule_with_times()` respects morning/afternoon/evening  
✅ **Non-Destructive Conflicts** — Detection without modifying tasks  

---

## Summary

The final PawPal+ architecture features a well-separated, responsibility-driven design:

- **Domain Models:** `Owner`, `Pet`, `Task` represent the problem space
- **Data Container:** `Calendar` manages task collections and provides query interface
- **Algorithm Engine:** `Scheduler` encapsulates all complex scheduling logic
- **Integration:** Streamlit UI (`app.py`) orchestrates the system, visualizing results with professional components

This architecture supports testing (20 comprehensive tests passing), extensibility (new scheduling algorithms), and maintainability (clear separation of concerns).
