# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial design had 4 classes: **Owner**, **Pet**, **Task**, **Calendar**. 
- **Owner**: Holds a list of pet objects and coordinates with calendar
- **Pet**: Tracks condition attributes (hunger, tiredness, health status)
- **Task**: Represents work to be done with progress tracking and completion status
- **Calendar**: Data structure holding task list with basic CRUD operations (add, remove, clear, etc.)
- **No inheritance** — All classes independent

**b. Design changes**

**Major additions during implementation:**

1. **Scheduler Class** (NEW) — Extracted complex scheduling logic from Calendar into dedicated Scheduler class with:
   - `generate_schedule()` — Orchestrates full pipeline
   - `sort_by_priority()` and `sort_by_time()` — Multiple sorting strategies
   - `detect_simultaneous_tasks()` — Conflict detection with severity levels
   - `resolve_conflicts()` — Non-destructive conflict resolution

2. **Task Class Enhancements**:
   - Added `pet_id` — Track which pet each task belongs to
   - Added `frequency` field — Support daily/weekly recurrence
   - Added `next_task_id` — Link recurrence chain for task lifecycle
   - Added `scheduled_time` — Store assigned time slot (minutes from midnight)
   - Added `time_window` — Support time preferences (morning/afternoon/evening)
   - Added `mark_complete()` → Returns next Task for recurring tasks
   - Added `create_next_occurrence()` — Auto-generate next day/week tasks

3. **Calendar Class Enhancements**:
   - Added `pet_id` and `owner_id` — Optional context tracking
   - Extended filter methods — `filter_tasks_by_pet()`, `filter_tasks_by_status()`, `filter_tasks_by_pet_and_status()`
   - Delegates to Scheduler — No longer handles scheduling internally

**Why:** The Scheduler class was added to separate concerns — calendars manage data, schedulers handle algorithms. This enables:
- Testing complex scheduling in isolation (20 comprehensive tests)
- Extensibility for different scheduling algorithms
- Cleaner, more maintainable architecture

See [UML_DIAGRAM.md](UML_DIAGRAM.md) for complete final architecture with all attributes and relationships.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
The scheduler trades optimal time utilization for respecting time window preferences. It is worth it because it respects user preferences.

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
