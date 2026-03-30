# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial design had 4 classes: Owner, Pet, Task, Calendar. 
- Owner: Holds a list of pet objects and coordinates with calendar
- Pet: Tracks condition attributes (hunger, tiredness, health status)
- Task: Represents work to be done with progress tracking and completion status
- Calendar: Data structure holding task list with basic CRUD operations (add, remove, clear, etc.)

**b. Design changes**


1. Scheduler Class — Extracted complex scheduling logic from Calendar into dedicated Scheduler class with:
   - `generate_schedule()` — Orchestrates full pipeline
   - `sort_by_priority()` and `sort_by_time()` — Multiple sorting strategies
   - `detect_simultaneous_tasks()` — Conflict detection with severity levels
   - `resolve_conflicts()` — Non-destructive conflict resolution

2. Task Class:
   - Added `pet_id` — Track which pet each task belongs to
   - Added `frequency` field — Support daily/weekly recurrence
   - Added `next_task_id` — Link recurrence chain for task lifecycle
   - Added `scheduled_time` — Store assigned time slot (minutes from midnight)
   - Added `time_window` — Support time preferences (morning/afternoon/evening)
   - Added `mark_complete()` → Returns next Task for recurring tasks
   - Added `create_next_occurrence()` — Auto-generate next day/week tasks

3. Calendar Class:
   - Added `pet_id` and `owner_id` — Optional context tracking
   - Extended filter methods — `filter_tasks_by_pet()`, `filter_tasks_by_status()`, `filter_tasks_by_pet_and_status()`
   - Delegates to Scheduler — No longer handles scheduling internally

The Scheduler class was added to separate responsibilities, so that calendars manage data, schedulers handle algorithms. This allows for:
- Testing complex scheduling in isolation (20 comprehensive tests)
- Extensibility for different scheduling algorithms
- Cleaner, more maintainable architecture


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers time availability per day, task priority levels (high/medium/low), task duration, time window preferences (morning/afternoon/evening), and pet condition thresholds. Priority ranking matters most, followed by time availability, then time window preferences. Time windows are preferences but don't block scheduling if time runs out.

**b. Tradeoffs**

The scheduler trades optimal time utilization for respecting user time window preferences. It may leave gaps before a preferred morning time window rather than fill them with lower-priority tasks scheduled earlier. This is reasonable because respecting how the user wants to structure their day matters more than packing every minute with tasks.

---

## 3. AI Collaboration (VS Code Copilot)

**a. How you used AI**

Copilot was most effective for generating boilerplate code like dataclass stubs and docstrings, which saved time on repetitive work. For testing, Copilot suggested useful test patterns that I refined into the 20 comprehensive tests. When designing complex algorithms like the priority sorting, Copilot's pseudocode suggestions helped clarify the approach. The refactoring suggestion to extract the Scheduler class from Calendar significantly improved the architecture.

The most helpful prompts were specific requests like asking for concrete test cases for daily task recurrence, algorithm pseudocode for detecting overlapping times, and architectural questions about whether scheduling logic belonged in Calendar or a separate class.

**b. Judgment and verification**

Copilot initially suggested I put all time window logic directly into schedule_with_times with nested conditionals. I rejected that approach and instead created a separate get_time_window_range method. This kept the code readable and testable. I verified the refactoring was correct by running the full test suite after each change—if all 20 tests passed, the change was safe.

Using separate chat sessions for different project phases helped a lot. Instead of one long conversation about design, implementation, and testing, I used distinct sessions for each phase. This prevented the conversation context from getting too large and reduced irrelevant suggestions from Copilot.

---

## 4. Testing and Verification

**a. What you tested**

I created 20 tests across 5 test classes. Three tests covered sorting correctness by verifying tasks are returned in chronological order and handling unscheduled tasks correctly. Five tests covered recurrence logic for daily and weekly tasks, ensuring they generate new occurrences with proper date linking and property inheritance. Five tests covered conflict detection, validating that simultaneous tasks for the same pet are flagged as critical and tasks for different pets are flagged as warnings. Two tests covered priority scheduling with high to low ordering and duration tiebreaking. Five tests covered time window preferences for morning, afternoon, evening, and anytime tasks.

These tests were important because they validate the core features the scheduler must guarantee to be useful.

**b. Confidence**

My confidence is very high. All 20 tests pass consistently. The system handles edge cases correctly including empty lists, unscheduled tasks, and the distinction between one-time and recurring tasks. Data integrity is maintained throughout task operations and the conflict detection approach is non-destructive, meaning it never modifies tasks.

If I had more time, I would test tasks that exceed available minutes to confirm they all get marked skipped, cascading conflicts with three or more simultaneous tasks, time window boundary conditions where a task starts exactly at a window edge, and pet condition extremes like 0 percent hunger or 100 percent tiredness.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the decision to separate scheduling logic into a dedicated Scheduler class. This choice made the system much better because it allowed me to test complex algorithms in isolation from the data models. It made the system easier to extend with new sorting strategies in the future. The responsibility boundaries became clear and the whole system stayed maintainable even as the feature set grew.

I'm also proud of the conflict detection design. By flagging conflicts by severity level without modifying any tasks, the system stays safe and doesn't lose information. Users get warnings but keep full control over what to do about them.

**b. What you would improve**

If I had another iteration, I would add more storage so tasks and pets survive between app sessions. Right now everything is in memory only. I would also let users manually reschedule conflicting tasks instead of having the system auto-resolve them, giving users more control. Optimizing across multiple pets simultaneously rather than one pet at a time would make the schedules better overall. And tracking task completion history over time would enable interesting insights about what actually gets done versus what was planned.

**c. Key takeaway**

The main lesson is that when working with AI, you have to stay in control as the architect. Copilot is fast and helpful but you need to question suggestions against your design goals. You need to verify ideas with tests instead of just accepting code completion. Use AI to speed up execution but not to replace your own decision-making.

The best approach I found was to sketch my architecture first, ask Copilot for help implementing it, then verify everything with tests. That way I kept control of the system's quality while still getting the benefit of AI's speed.