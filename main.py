"""
Main script demonstrating the PawPal+ scheduling system.
"""

from pawpal_system import Owner, Pet, Task, Calendar, Scheduler
from datetime import date


def main():
    """Demonstrate the PawPal+ system with sample data."""
    
    # Create an owner
    owner = Owner(owner_id=1, name="Jordan", contact_info="jordan@email.com")
    
    # Create two pets
    mochi = Pet(
        pet_id=1,
        name="Mochi",
        species="dog",
        hunger_level=75,
        tiredness_level=80,
        health_status="healthy",
        age=3
    )
    
    whiskers = Pet(
        pet_id=2,
        name="Whiskers",
        species="cat",
        hunger_level=75,
        tiredness_level=65,
        health_status="healthy",
        age=5
    )
    
    # Add pets to owner
    owner.add_pet(mochi)
    owner.add_pet(whiskers)
    
    # Create tasks IN RANDOM ORDER (not chronological)
    # This will demonstrate that sorting works correctly
    
    # Task 5: Afternoon Play (Added 5th, but scheduled for afternoon)
    whiskers_playtime = Task(
        task_id=5,
        title="Interactive Play",
        description="Play with Whiskers using toy mouse",
        duration_minutes=15,
        priority="medium",
        target_condition="tiredness_level",
        pet_id=2,
        frequency="daily",
        time_window="anytime"
    )
    
    # Task 1: Morning Walk (Added 1st, but first chronologically)
    mochi_walk = Task(
        task_id=1,
        title="Morning Walk",
        description="Take Mochi for a walk in the park",
        duration_minutes=30,
        priority="high",
        target_condition="tiredness_level",
        pet_id=1,
        frequency="daily",
        time_window="morning"
    )
    
    # Task 6: Evening Grooming (Added 6th, but latest chronologically)
    whiskers_grooming = Task(
        task_id=6,
        title="Brushing",
        description="Brush Whiskers' fur",
        duration_minutes=10,
        priority="low",
        target_condition="health_status",
        pet_id=2,
        frequency="weekly",
        time_window="evening"
    )
    
    # Task 2: Breakfast (Added 2nd, early morning)
    mochi_breakfast = Task(
        task_id=2,
        title="Breakfast",
        description="Feed Mochi breakfast kibble",
        duration_minutes=10,
        priority="high",
        target_condition="hunger_level",
        pet_id=1,
        frequency="daily",
        time_window="morning"
    )
    
    # Task 4: Cat Breakfast (Added 4th, early morning)
    whiskers_feed = Task(
        task_id=4,
        title="Cat Breakfast",
        description="Feed Whiskers cat food",
        duration_minutes=5,
        priority="high",
        target_condition="hunger_level",
        pet_id=2,
        frequency="daily",
        time_window="morning"
    )
    
    # Task 3: Play Session (Added 3rd, afternoon)
    mochi_play = Task(
        task_id=3,
        title="Play Session",
        description="Play fetch with Mochi",
        duration_minutes=25,
        priority="medium",
        target_condition="tiredness_level",
        pet_id=1,
        frequency="daily",
        time_window="afternoon"
    )
    
    # Add tasks to pets (in random order to test sorting)
    mochi.tasks.extend([mochi_walk, mochi_breakfast, mochi_play])
    whiskers.tasks.extend([whiskers_feed, whiskers_playtime, whiskers_grooming])
    
    # Create calendar and scheduler
    calendar = Calendar(date=date.today(), owner_id=1)
    scheduler = Scheduler()
    
    # Generate schedule for the day (480 minutes = 8 hours available)
    owner.create_schedule(calendar, scheduler, available_minutes=480)
    
    # ====== DEMO: UNSORTED TASK LIST ======
    print("\n" + "="*70)
    print("📋 ORIGINAL TASK LIST (UNSORTED - Added Out of Order)")
    print("="*70)
    
    unsorted_tasks = calendar.get_tasks()
    for idx, task in enumerate(unsorted_tasks, 1):
        print(f"{idx}. {task.title} (Task ID: {task.task_id}) - Status: {task.status}")
    
    # ====== DEMO: SORTED BY TIME ======
    print("\n" + "="*70)
    print("⏰ TASKS SORTED BY TIME")
    print("="*70)
    
    sorted_by_time = scheduler.sort_by_time(unsorted_tasks)
    for idx, task in enumerate(sorted_by_time, 1):
        if task.scheduled_time is not None:
            hours = task.scheduled_time // 60
            minutes = task.scheduled_time % 60
            end_time = task.scheduled_time + task.duration_minutes
            hours_end = end_time // 60
            minutes_end = end_time % 60
            time_str = f"{hours:02d}:{minutes:02d}-{hours_end:02d}:{minutes_end:02d}"
        else:
            time_str = "Not scheduled"
        
        print(f"{idx}. {time_str:15s} | {task.title:20s} | Duration: {task.duration_minutes} min")
    
    # ====== DEMO: FILTER BY COMPLETION STATUS ======
    print("\n" + "="*70)
    print("✅ FILTERING BY COMPLETION STATUS")
    print("="*70)
    
    # Mark some tasks as completed for demo
    if len(unsorted_tasks) > 0:
        unsorted_tasks[0].mark_complete()
    if len(unsorted_tasks) > 1:
        unsorted_tasks[1].mark_complete()
    
    completed_tasks = calendar.filter_tasks_by_completion(completed=True)
    incomplete_tasks = calendar.filter_tasks_by_completion(completed=False)
    
    print(f"\n✓ COMPLETED TASKS ({len(completed_tasks)}):")
    for task in completed_tasks:
        print(f"  ✔ {task.title} - Progress: {task.progress}%")
    
    print(f"\n⏳ INCOMPLETE TASKS ({len(incomplete_tasks)}):")
    for task in incomplete_tasks:
        print(f"  ⏳ {task.title} - Progress: {task.progress}%")
    
    # ====== DEMO: SORT COMPLETED TASKS BY TIME ======
    print("\n" + "="*70)
    print("⏰ COMPLETED TASKS SORTED BY TIME")
    print("="*70)
    
    completed_sorted = scheduler.sort_by_time(completed_tasks)
    if completed_sorted:
        for idx, task in enumerate(completed_sorted, 1):
            if task.scheduled_time is not None:
                hours = task.scheduled_time // 60
                minutes = task.scheduled_time % 60
                print(f"{idx}. {hours:02d}:{minutes:02d} - {task.title}")
            else:
                print(f"{idx}. No time - {task.title}")
    else:
        print("No completed tasks")
    
    # ====== DEMO: FILTER BY PET AND SORT ======
    print("\n" + "="*70)
    print("🐕 MOCHI'S TASKS (SORTED BY TIME)")
    print("="*70)
    
    mochi_tasks = calendar.filter_tasks_by_pet(mochi.pet_id)
    mochi_sorted = scheduler.sort_by_time(mochi_tasks)
    for idx, task in enumerate(mochi_sorted, 1):
        if task.scheduled_time is not None:
            hours = task.scheduled_time // 60
            minutes = task.scheduled_time % 60
            print(f"{idx}. {hours:02d}:{minutes:02d} - {task.title} ({task.status})")
        else:
            print(f"{idx}. -- - {task.title} ({task.status})")
    
    print("\n" + "="*70)
    print("🐱 WHISKERS'S TASKS (SORTED BY TIME)")
    print("="*70)
    
    whiskers_tasks = calendar.filter_tasks_by_pet(whiskers.pet_id)
    whiskers_sorted = scheduler.sort_by_time(whiskers_tasks)
    for idx, task in enumerate(whiskers_sorted, 1):
        if task.scheduled_time is not None:
            hours = task.scheduled_time // 60
            minutes = task.scheduled_time % 60
            print(f"{idx}. {hours:02d}:{minutes:02d} - {task.title} ({task.status})")
        else:
            print(f"{idx}. -- - {task.title} ({task.status})")
    
    # ====== DEMO: FILTER BY STATUS AND PET ======
    print("\n" + "="*70)
    print("📊 MOCHI'S PENDING TASKS")
    print("="*70)
    
    mochi_pending = calendar.filter_tasks_by_pet_and_status(mochi.pet_id, "pending")
    if mochi_pending:
        for task in mochi_pending:
            print(f"  • {task.title}")
    else:
        print("  No pending tasks for Mochi")
    
    # ====== SUMMARY TABLE ======
    print("\n" + "="*70)
    print("📈 TASK SUMMARY REPORT")
    print("="*70)
    print(f"\nTotal Tasks: {len(unsorted_tasks)}")
    print(f"  ✓ Completed: {len(completed_tasks)}")
    print(f"  ⏳ Incomplete: {len(incomplete_tasks)}")
    print(f"  🟡 Pending: {len(calendar.filter_tasks_by_status('pending'))}")
    print(f"  🟢 Skipped: {len(calendar.filter_tasks_by_status('skipped'))}")
    
    print(f"\nTasks per Pet:")
    print(f"  🐕 Mochi: {len(mochi_tasks)} tasks")
    print(f"  🐱 Whiskers: {len(whiskers_tasks)} tasks")
    
    # ====== DEMO: RECURRING TASK GENERATION ======
    print("\n" + "="*70)
    print("🔄 RECURRING TASK GENERATION DEMO")
    print("="*70)
    
    print("\n📝 Creating a new daily task for Mochi:")
    daily_breakfast = Task(
        task_id=100,
        title="Daily Breakfast",
        description="Feed Mochi breakfast",
        duration_minutes=10,
        priority="high",
        target_condition="hunger_level",
        pet_id=1,
        frequency="daily",
        task_date=date.today()
    )
    print(f"  ✓ Task created: {daily_breakfast.title}")
    print(f"    - Task ID: {daily_breakfast.task_id}")
    print(f"    - Date: {daily_breakfast.task_date.strftime('%A, %B %d')}")
    print(f"    - Frequency: {daily_breakfast.frequency}")
    print(f"    - Status: {daily_breakfast.status}")
    
    print("\n📋 Before completion:")
    print(f"  - Completed: {daily_breakfast.completed}")
    print(f"  - Progress: {daily_breakfast.progress}%")
    print(f"  - Next Task ID: {daily_breakfast.next_task_id}")
    
    print("\n✅ Marking the task as complete...")
    next_occurrence = daily_breakfast.mark_complete()
    
    print("\n📋 After completion:")
    print(f"  - Completed: {daily_breakfast.completed}")
    print(f"  - Progress: {daily_breakfast.progress}%")
    print(f"  - Status: {daily_breakfast.status}")
    print(f"  - Next Task ID: {daily_breakfast.next_task_id}")
    
    if next_occurrence:
        print("\n🎉 Next occurrence automatically created!")
        print(f"  - Task ID: {next_occurrence.task_id}")
        print(f"  - Title: {next_occurrence.title}")
        print(f"  - Date: {next_occurrence.task_date.strftime('%A, %B %d')}")
        print(f"  - Status: {next_occurrence.status}")
        print(f"  - Progress: {next_occurrence.progress}%")
        print(f"  - Completed: {next_occurrence.completed}")
        
        print("\n📊 Linking:")
        print(f"  Original Task {daily_breakfast.task_id} → Next Task {next_occurrence.task_id}")
    
    # Demonstrate weekly task
    print("\n" + "-"*70)
    print("\n📝 Creating a weekly task for Whiskers:")
    weekly_grooming = Task(
        task_id=200,
        title="Weekly Grooming",
        description="Groom Whiskers",
        duration_minutes=30,
        priority="medium",
        target_condition="health_status",
        pet_id=2,
        frequency="weekly",
        task_date=date.today()
    )
    print(f"  ✓ Task created: {weekly_grooming.title}")
    print(f"    - Task ID: {weekly_grooming.task_id}")
    print(f"    - Date: {weekly_grooming.task_date.strftime('%A, %B %d')}")
    print(f"    - Frequency: {weekly_grooming.frequency}")
    
    print("\n✅ Marking the task as complete...")
    next_weekly = weekly_grooming.mark_complete()
    
    if next_weekly:
        print("\n🎉 Next weekly occurrence created!")
        print(f"  - Task ID: {next_weekly.task_id}")
        print(f"  - Date: {next_weekly.task_date.strftime('%A, %B %d')}")
        print(f"  - Days in future: {(next_weekly.task_date - weekly_grooming.task_date).days}")
    else:
        print("\n⚠️ No next occurrence was created (None returned)")
    
    # ====== DEMO: LIGHTWEIGHT CONFLICT DETECTION ======
    print("\n" + "="*70)
    print("LIGHTWEIGHT SIMULTANEOUS TASK CONFLICT DETECTION")
    print("="*70)
    
    print("\n📝 Creating two tasks scheduled at the SAME TIME (6:00 AM):\n")
    
    # Create two tasks for Mochi at the same time
    conflict_task1 = Task(
        task_id=300,
        title="Morning Breakfast",
        description="Feed Mochi breakfast kibble",
        duration_minutes=10,
        priority="high",
        target_condition="hunger_level",
        pet_id=1,
        scheduled_time=360  # 6:00 AM
    )
    
    conflict_task2 = Task(
        task_id=301,
        title="Morning Routine",
        description="Groom and prepare Mochi",
        duration_minutes=20,
        priority="high",
        target_condition="health_status",
        pet_id=1,
        scheduled_time=360  # SAME TIME: 6:00 AM
    )
    
    print(f"  1. {conflict_task1.title}")
    print(f"     - Pet ID: {conflict_task1.pet_id} (Mochi the dog)")
    print(f"     - Scheduled: 06:00 AM")
    print(f"     - Duration: {conflict_task1.duration_minutes} min")
    
    print(f"\n  2. {conflict_task2.title}")
    print(f"     - Pet ID: {conflict_task2.pet_id} (Mochi the dog)")
    print(f"     - Scheduled: 06:00 AM (SAME TIME)")
    print(f"     - Duration: {conflict_task2.duration_minutes} min")
    
    # Run lightweight conflict detection
    conflict_tasks = [conflict_task1, conflict_task2]
    print(f"\n{'-'*70}")
    print("Running lightweight conflict detection (non-destructive)...\n")
    
    warning_count = scheduler.print_conflict_warnings(conflict_tasks)
    
    print(f"\n{'-'*70}")
    print(f"Detection Complete: {warning_count} conflict(s) identified")
    print("\nKey Features of Lightweight Detection:")
    print("  - Returns warnings without modifying tasks")
    print("  - Never crashes the program")
    print("  - Only checks start times (not durations)")
    print("  - Categorizes severity (CRITICAL for same pet)")
    print("  - Allows system to continue running normally")
    
    # Verify tasks are unchanged
    print(f"\nVerification:")
    print(f"  - Task 1 still scheduled at: {conflict_task1.scheduled_time} (unchanged)")
    print(f"  - Task 2 still scheduled at: {conflict_task2.scheduled_time} (unchanged)")
    print(f"  - Task 1 status: {conflict_task1.status} (unchanged)")
    print(f"  - Task 2 status: {conflict_task2.status} (unchanged)")
    
    print("\n" + "="*70)
    print("✅ All demonstrations complete! 🎉")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
