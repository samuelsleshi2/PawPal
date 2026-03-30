"""
Test script demonstrating lightweight conflict detection.
Shows how the Scheduler detects simultaneous tasks and prints warnings 
without crashing or modifying tasks.
"""

from pawpal_system import Pet, Task, Calendar, Scheduler
from datetime import date


def test_same_pet_simultaneous_tasks():
    """Test detection of simultaneous tasks for the SAME PET."""
    print("=" * 70)
    print("TEST 1: SIMULTANEOUS TASKS FOR SAME PET (CRITICAL)")
    print("=" * 70)
    
    # Create a pet
    dog = Pet(
        pet_id=1,
        name="Mochi",
        species="dog",
        hunger_level=75,
        tiredness_level=80
    )
    
    # Create two tasks scheduled at the SAME time for the same pet
    breakfast = Task(
        task_id=1,
        title="Breakfast",
        description="Feed dog breakfast",
        duration_minutes=10,
        priority="high",
        target_condition="hunger_level",
        pet_id=1,
        scheduled_time=360  # 6:00 AM
    )
    
    morning_walk = Task(
        task_id=2,
        title="Morning Walk",
        description="Walk the dog",
        duration_minutes=30,
        priority="high",
        target_condition="tiredness_level",
        pet_id=1,
        scheduled_time=360  # SAME TIME: 6:00 AM
    )
    
    tasks = [breakfast, morning_walk]
    scheduler = Scheduler()
    
    print("\nCreated tasks:")
    print(f"  {breakfast.title}: {breakfast.scheduled_time:03d} minutes (6:00 AM)")
    print(f"  {morning_walk.title}: {morning_walk.scheduled_time:03d} minutes (6:00 AM)")
    
    print("\nChecking for simultaneous task conflicts...\n")
    warning_count = scheduler.print_conflict_warnings(tasks)
    
    print(f"\nResult: {warning_count} conflict(s) detected")
    print("Status: Task data NOT modified (lightweight detection only)")


def test_different_pets_simultaneous_tasks():
    """Test detection of simultaneous tasks for DIFFERENT PETS."""
    print("\n" + "=" * 70)
    print("TEST 2: SIMULTANEOUS TASKS FOR DIFFERENT PETS (WARNING)")
    print("=" * 70)
    
    # Create two pets
    dog = Pet(pet_id=1, name="Mochi", species="dog")
    cat = Pet(pet_id=2, name="Whiskers", species="cat")
    
    # Create tasks for different pets at the SAME time
    dog_meal = Task(
        task_id=10,
        title="Dog Meal",
        description="Feed the dog",
        duration_minutes=10,
        priority="high",
        target_condition="hunger_level",
        pet_id=1,
        scheduled_time=420  # 7:00 AM
    )
    
    cat_meal = Task(
        task_id=11,
        title="Cat Meal",
        description="Feed the cat",
        duration_minutes=5,
        priority="high",
        target_condition="hunger_level",
        pet_id=2,
        scheduled_time=420  # SAME TIME: 7:00 AM (different pet)
    )
    
    tasks = [dog_meal, cat_meal]
    scheduler = Scheduler()
    
    print("\nCreated tasks:")
    print(f"  {dog_meal.title} (Pet {dog_meal.pet_id}): {dog_meal.scheduled_time:03d} minutes (7:00 AM)")
    print(f"  {cat_meal.title} (Pet {cat_meal.pet_id}): {cat_meal.scheduled_time:03d} minutes (7:00 AM)")
    
    print("\nChecking for simultaneous task conflicts...\n")
    warning_count = scheduler.print_conflict_warnings(tasks)
    
    print(f"\nResult: {warning_count} conflict(s) detected")
    print("Severity: Lower (different pets, but simultaneous)")


def test_no_conflicts():
    """Test when tasks are at different times (no conflicts)."""
    print("\n" + "=" * 70)
    print("TEST 3: NO SIMULTANEOUS TASKS (NO CONFLICTS)")
    print("=" * 70)
    
    tasks = [
        Task(
            task_id=20,
            title="Breakfast",
            description="Feed dog",
            duration_minutes=10,
            priority="high",
            target_condition="hunger_level",
            pet_id=1,
            scheduled_time=360  # 6:00 AM
        ),
        Task(
            task_id=21,
            title="Morning Walk",
            description="Walk dog",
            duration_minutes=30,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1,
            scheduled_time=390  # 6:30 AM (different time)
        ),
        Task(
            task_id=22,
            title="Playtime",
            description="Play with dog",
            duration_minutes=20,
            priority="medium",
            target_condition="tiredness_level",
            pet_id=1,
            scheduled_time=420  # 7:00 AM (different time)
        )
    ]
    
    scheduler = Scheduler()
    
    print("\nCreated tasks:")
    for task in tasks:
        hours = task.scheduled_time // 60
        minutes = task.scheduled_time % 60
        print(f"  {task.title}: {hours:02d}:{minutes:02d}")
    
    print("\nChecking for simultaneous task conflicts...\n")
    warning_count = scheduler.print_conflict_warnings(tasks)
    
    if warning_count == 0:
        print("No conflicts detected - all tasks at different times!")
    else:
        print(f"Unexpected result: {warning_count} conflict(s) found")


def test_three_way_conflict():
    """Test detection of three tasks at the same time."""
    print("\n" + "=" * 70)
    print("TEST 4: THREE TASKS AT SAME TIME (MULTIPLE CONFLICTS)")
    print("=" * 70)
    
    tasks = [
        Task(
            task_id=30,
            title="Feed Dog",
            description="Breakfast",
            duration_minutes=10,
            priority="high",
            target_condition="hunger_level",
            pet_id=1,
            scheduled_time=480  # 8:00 AM
        ),
        Task(
            task_id=31,
            title="Feed Cat",
            description="Breakfast",
            duration_minutes=5,
            priority="high",
            target_condition="hunger_level",
            pet_id=2,
            scheduled_time=480  # SAME TIME: 8:00 AM
        ),
        Task(
            task_id=32,
            title="Owner's Meeting",
            description="Work call",
            duration_minutes=30,
            priority="high",
            target_condition="health_status",
            pet_id=1,
            scheduled_time=480  # SAME TIME: 8:00 AM
        )
    ]
    
    scheduler = Scheduler()
    
    print("\nCreated tasks at 8:00 AM:")
    for task in tasks:
        print(f"  {task.title} (Pet {task.pet_id})")
    
    print("\nChecking for simultaneous task conflicts...\n")
    warning_count = scheduler.print_conflict_warnings(tasks)
    
    print(f"\nResult: {warning_count} conflict(s) detected")
    
    # Show the warnings in detail
    warnings = scheduler.detect_simultaneous_tasks(tasks)
    for w in warnings:
        print(f"Severity: {w['severity'].upper()}")
        print(f"Involved task IDs: {w['task_ids']}")


def main():
    """Run all conflict detection tests."""
    test_same_pet_simultaneous_tasks()
    test_different_pets_simultaneous_tasks()
    test_no_conflicts()
    test_three_way_conflict()
    
    print("\n" + "=" * 70)
    print("ALL CONFLICT DETECTION TESTS COMPLETED")
    print("=" * 70)
    print("\nKey Takeaway:")
    print("  - Lightweight detection only checks start times (not durations)")
    print("  - Returns warnings without modifying tasks")
    print("  - Never crashes, always informational")
    print("  - Different severity levels (same pet = CRITICAL)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
