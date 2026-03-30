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

## Features & Core Algorithms

PawPal+ implements intelligent task scheduling through a 5-stage pipeline algorithm with multiple supporting algorithms.

### **Main Scheduling Pipeline** (Scheduler.generate_schedule)

The core algorithm orchestrates a multi-stage process:

1. **Task Filtering** — Extracts tasks relevant to the specific pet based on:
   - Task ownership (filters by pet_id)
   - Completion status (excludes already completed tasks)
   - Pet condition relevance (matches task target_condition to pet needs)
   - Condition thresholds (e.g., feed if hunger > 70, walk if tiredness > 70)

2. **Task Expansion** — Includes recurring task instances:
   - Extracts daily and weekly tasks for the current day
   - Handles one-time tasks as-is
   - Enables proper recurrence chain management

3. **Priority-Based Sorting** (Scheduler.sort_by_priority)
   - **Algorithm**: Multi-key sort with weighted priorities
   - **Primary Key**: Priority weight (high=3, medium=2, low=1) in descending order
   - **Secondary Key**: Duration in ascending order (shorter tasks first for better packing)
   - **Benefit**: Greedy bin packing optimization — high-priority tasks get scheduled first, and within same priority, shorter tasks fill gaps efficiently

4. **Time Slot Scheduling** (Scheduler.schedule_with_times)
   - **Algorithm**: Greedy bin-packing with time window preferences
   - Respects user time preferences: morning (6 AM–12 PM), afternoon (12 PM–5 PM), evening (5 PM–10 PM), anytime
   - Assigns earliest available time slot for each task
   - Marks tasks as "skipped" if they exceed available time
   - Validates against daily time bounds (0–1440 minutes)

5. **Conflict Resolution** (Scheduler.resolve_conflicts)
   - Detects overlapping task pairs using interval intersection
   - For each conflict, reschedules lower-priority task to start after higher-priority task ends
   - Non-destructive: modifies only task times, never removes tasks

### **Sorting & Display Algorithms**

- **Chronological Sorting** (Scheduler.sort_by_time) — Sorts tasks by scheduled_time in ascending order (earliest first) for human-readable schedule display. Unscheduled tasks placed at end.
- **Unscheduled Task Handling** — Gracefully positions tasks without times at end of list without crashing.

### **Conflict Detection Algorithms** (Non-Destructive)

- **Simultaneous Task Detection** (Scheduler.detect_simultaneous_tasks)
  - Groups tasks by start time (scheduled_time)
  - Identifies all tasks starting at same minute
  - **Severity Classification**:
    - CRITICAL: Multiple tasks for same pet (impossible to execute)
    - WARNING: Tasks for different pets (logically possible but unusual)
  - Returns structured warnings with task details, pet IDs, and formatted time strings
  - **Key Property**: Zero side effects — no task objects are modified

- **Full Overlap Detection** (Scheduler.detect_conflicts)
  - Algorithm: Pairwise interval intersection checking
  - For each task pair checks: NOT (task1_end ≤ task2_start OR task2_end ≤ task1_start)
  - Returns conflicting task pairs for manual review or resolution

### **Recurring Task Management Algorithms**

- **Recurrence Generation** (Task.create_next_occurrence)
  - Algorithm: Linked list chain using next_task_id
  - For daily tasks: advances task_date by 1 day
  - For weekly tasks: advances task_date by 7 days
  - Creates new task with: same properties, fresh state (progress=0, completed=False), incremented ID, date offset
  - Links current task to next via next_task_id field (enables task family tracking)

- **Automatic Next Task Creation** (Task.mark_complete)
  - On completion: returns new Task if frequency ∈ {daily, weekly}
  - For one-time tasks: returns None (no recurrence)
  - Maintains task lifecycle chain for long-term recurring work

### **Filtering & Query Algorithms**

- **Pet-Specific Filtering** (Calendar.filter_tasks_by_pet) — Single-pass filter by pet_id
- **Status Filtering** (Calendar.filter_tasks_by_status) — Single-pass filter by status field
- **Completion Filtering** (Calendar.filter_tasks_by_completion) — Single-pass filter by boolean completed flag
- **Combined Filtering** (Calendar.filter_tasks_by_pet_and_status) — Filters both dimensions simultaneously

### **Time Window Constraint Algorithm**

- **Window Mapping** (Task.get_time_window_range)
  - Morning: [360, 720] minutes (6 AM – 12 PM)
  - Afternoon: [720, 1020] minutes (12 PM – 5 PM)
  - Evening: [1020, 1320] minutes (5 PM – 10 PM)
  - Anytime: [0, 1440] minutes (full day)

- **Window Respecting Scheduler** — When scheduling task with time_window preference:
  - Jumps to window start time if current_time < window_start
  - Schedules task at earliest valid slot within window
  - Continues scheduling subsequent tasks after completion

### **Condition-Based Task Relevance Algorithm**

- **Pet Needs Assessment** (Pet.needs_task)
  - Task type mapping: tiredness_level → {walk, play, rest}, hunger_level → {feed}, health_status → {vet_visit, medication}
  - Threshold-based logic:
    - walk: needed if tiredness > 70
    - feed: needed if hunger > 70
    - play: needed if tiredness > 60
    - rest: needed if tiredness < 30 (inverse logic)
  - Enables condition-aware task filtering

## Smarter Scheduling Features

- **Smart Time-Based Sorting** — Tasks organized chronologically for clear, readable schedules
- **Flexible Filtering** — Query tasks by pet, status, completion, or combinations
- **Recurring Task Management** — Daily/weekly tasks auto-generate with proper date linking
- **Time Window Respect** — Tasks scheduled in morning/afternoon/evening preferences
- **Priority-Based Scheduling** — Optimized bin-packing with duration tiebreaking
- **Lightweight Conflict Detection** — Non-destructive flagging (critical/warning by pet count)
- **Efficient Greedy Algorithm** — Maximizes task fit within available time

## Getting started

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

### Running the App

Once setup is complete, start the Streamlit application:

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Demo

### PawPal+ User Interface

![PawPal+ Scheduling Interface](pawpal.png)

The application features a professional multi-tab interface:

- **📋 Tasks Tab** — Add/manage pets and tasks with detailed configuration
- **📅 Schedule Tab** — Generate optimized schedules with conflict detection and summary metrics
- **🔍 Analysis Tab** — View scheduling statistics, priority breakdown, and sorting demonstrations

**Key UI Features:**
- Sidebar pet management with real-time condition tracking
- Task creation with priority, frequency, and time window preferences
- Professional tables for task and schedule display
- Color-coded conflict warnings (errors for critical, warnings for non-critical)
- Live metrics showing task scheduling efficiency and utilization percentage

## Testing PawPal+

### Running Tests

Run the comprehensive test suite:

```bash
python -m pytest tests/test_comprehensive.py -v
```

### Test Coverage

The test suite includes **20 comprehensive unit tests** organized into 5 test classes, covering:

- **Sorting Correctness** (3 tests) — Verifies tasks are returned in chronological order by scheduled time
- **Recurrence Logic** (5 tests) — Confirms daily/weekly tasks generate next occurrences and maintain date linking
- **Conflict Detection** (5 tests) — Validates simultaneous task flagging (critical for same pet, warning for different pets)
- **Priority-Based Scheduling** (2 tests) — Tests high→medium→low priority ordering with duration tiebreaking
- **Time Window Respect** (5 tests) — Ensures tasks respect morning/afternoon/evening time preferences

**All 20 tests passing** ✓

### Confidence Level: ⭐⭐⭐⭐⭐

**5/5 Stars** — The comprehensive test suite validates all critical scheduling functionality, recurring task generation, conflict detection, and time preference handling. The system reliably handles edge cases, maintains data integrity across task lifecycle operations, and provides non-destructive conflict detection without crashes.
