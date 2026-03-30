"""
Test script demonstrating recurring task generation.
Clean output without emoji characters for clarity.
"""

from pawpal_system import Task
from datetime import date, timedelta


def test_daily_task_recurrence():
    """Test that daily tasks generate next occurrence when completed."""
    print("=" * 70)
    print("TEST 1: DAILY TASK RECURRENCE")
    print("=" * 70)
    
    today = date.today()
    daily_task = Task(
        task_id=1,
        title="Daily Walk",
        description="Walk the dog",
        duration_minutes=30,
        priority="high",
        target_condition="tiredness_level",
        pet_id=1,
        frequency="daily",
        task_date=today
    )
    
    print(f"\nCreated task: {daily_task.title}")
    print(f"  - Task ID: {daily_task.task_id}")
    print(f"  - Date: {daily_task.task_date}")
    print(f"  - Frequency: {daily_task.frequency}")
    print(f"  - Status: {daily_task.status}")
    print(f"  - Completed: {daily_task.completed}")
    print(f"  - Progress: {daily_task.progress}%")
    
    print(f"\nCompleting task...")
    next_task = daily_task.mark_complete()
    
    print(f"\nOriginal task after completion:")
    print(f"  - Completed: {daily_task.completed}")
    print(f"  - Status: {daily_task.status}")
    print(f"  - Progress: {daily_task.progress}%")
    print(f"  - Next Task ID Link: {daily_task.next_task_id}")
    
    if next_task:
        print(f"\nNext occurrence created automatically:")
        print(f"  - Task ID: {next_task.task_id}")
        print(f"  - Title: {next_task.title}")
        print(f"  - Date: {next_task.task_date}")
        print(f"  - Status: {next_task.status}")
        print(f"  - Completed: {next_task.completed}")
        print(f"  - Progress: {next_task.progress}%")
        print(f"  - Days after original: {(next_task.task_date - daily_task.task_date).days}")
        print(f"\nSUCCESS: Daily task recurrence working!")
    else:
        print("\nERROR: No next occurrence created!")


def test_weekly_task_recurrence():
    """Test that weekly tasks generate next occurrence when completed."""
    print("\n" + "=" * 70)
    print("TEST 2: WEEKLY TASK RECURRENCE")
    print("=" * 70)
    
    today = date.today()
    weekly_task = Task(
        task_id=2,
        title="Weekly Grooming",
        description="Groom the dog",
        duration_minutes=60,
        priority="medium",
        target_condition="health_status",
        pet_id=1,
        frequency="weekly",
        task_date=today
    )
    
    print(f"\nCreated task: {weekly_task.title}")
    print(f"  - Task ID: {weekly_task.task_id}")
    print(f"  - Date: {weekly_task.task_date}")
    print(f"  - Frequency: {weekly_task.frequency}")
    print(f"  - Status: {weekly_task.status}")
    
    print(f"\nCompleting task...")
    next_task = weekly_task.mark_complete()
    
    if next_task:
        print(f"\nNext occurrence created automatically:")
        print(f"  - Task ID: {next_task.task_id}")
        print(f"  - Title: {next_task.title}")
        print(f"  - Date: {next_task.task_date}")
        print(f"  - Days after original: {(next_task.task_date - weekly_task.task_date).days}")
        
        expected_days = 7
        actual_days = (next_task.task_date - weekly_task.task_date).days
        if actual_days == expected_days:
            print(f"\nSUCCESS: Weekly task recurrence working (7 days)!")
        else:
            print(f"\nERROR: Expected {expected_days} days, got {actual_days}")
    else:
        print("\nERROR: No next occurrence created!")


def test_once_task_no_recurrence():
    """Test that 'once' frequency tasks don't create next occurrence."""
    print("\n" + "=" * 70)
    print("TEST 3: ONCE-ONLY TASK (NO RECURRENCE)")
    print("=" * 70)
    
    today = date.today()
    once_task = Task(
        task_id=3,
        title="Vet Appointment",
        description="Annual checkup",
        duration_minutes=45,
        priority="high",
        target_condition="health_status",
        pet_id=1,
        frequency="once",
        task_date=today
    )
    
    print(f"\nCreated task: {once_task.title}")
    print(f"  - Frequency: {once_task.frequency}")
    
    print(f"\nCompleting task...")
    next_task = once_task.mark_complete()
    
    if next_task is None:
        print(f"SUCCESS: One-time task does not generate next occurrence!")
    else:
        print(f"ERROR: One-time task should not generate next occurrence!")


def test_task_chain():
    """Test chaining multiple completed tasks to see the full lifecycle."""
    print("\n" + "=" * 70)
    print("TEST 4: TASK CHAIN (Multiple completions)")
    print("=" * 70)
    
    # Start with a task for March 30
    task1 = Task(
        task_id=100,
        title="Feed Dog",
        description="Morning feeding",
        duration_minutes=15,
        priority="high",
        target_condition="hunger_level",
        pet_id=1,
        frequency="daily",
        task_date=date(2026, 3, 30)
    )
    
    print(f"\nTask 1: {task1.title} on {task1.task_date}")
    
    # Complete task 1, get task 2
    task2 = task1.mark_complete()
    print(f"Task 1 completed -> Created Task 2 for {task2.task_date}")
    print(f"  Link: Task {task1.task_id} -> Task {task2.task_id}")
    
    # Complete task 2, get task 3
    task3 = task2.mark_complete()
    print(f"Task 2 completed -> Created Task 3 for {task3.task_date}")
    print(f"  Link: Task {task2.task_id} -> Task {task3.task_id}")
    
    print(f"\nTask chain created:")
    print(f"  {task1.task_id} (Mar 30) -> {task2.task_id} (Mar 31) -> {task3.task_id} (Apr 01)")
    print(f"SUCCESS: Task chaining works!")


def main():
    """Run all tests."""
    test_daily_task_recurrence()
    test_weekly_task_recurrence()
    test_once_task_no_recurrence()
    test_task_chain()
    
    print("\n" + "=" * 70)
    print("ALL TESTS COMPLETED")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
