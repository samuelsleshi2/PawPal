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

## Smarter Scheduling Features

This version of PawPal+ includes intelligent scheduling enhancements:

- **Smart Time-Based Sorting** — Tasks are organized chronologically by scheduled time for clear, readable schedules
- **Flexible Filtering** — Filter tasks by pet, completion status, or both to focus on what matters
- **Recurring Task Management** — Daily and weekly tasks automatically generate next occurrences with proper date linking
- **Time Window Respect** — Tasks can specify preferred times (morning, afternoon, evening) and the scheduler respects these preferences
- **Priority-Based Scheduling** — Tasks are scheduled based on priority weight and duration for optimized packing
- **Lightweight Conflict Detection** — Non-destructive detection of simultaneous tasks (same pet = critical, different pets = warning) without crashing
- **Efficient Bin Packing** — Greedy scheduling algorithm maximizes task fit within available time bounds

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
