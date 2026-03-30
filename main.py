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
    
    # Create tasks for Mochi (dog)
    mochi_walk = Task(
        task_id=1,
        title="Morning Walk",
        description="Take Mochi for a walk in the park",
        duration_minutes=30,
        priority="high",
        target_condition="tiredness_level",
        pet_id=1,
        frequency="daily"
    )
    
    mochi_breakfast = Task(
        task_id=2,
        title="Breakfast",
        description="Feed Mochi breakfast kibble",
        duration_minutes=10,
        priority="high",
        target_condition="hunger_level",
        pet_id=1,
        frequency="daily"
    )
    
    mochi_play = Task(
        task_id=3,
        title="Play Session",
        description="Play fetch with Mochi",
        duration_minutes=25,
        priority="medium",
        target_condition="tiredness_level",
        pet_id=1,
        frequency="daily"
    )
    
    # Create tasks for Whiskers (cat)
    whiskers_feed = Task(
        task_id=4,
        title="Cat Breakfast",
        description="Feed Whiskers cat food",
        duration_minutes=5,
        priority="high",
        target_condition="hunger_level",
        pet_id=2,
        frequency="daily"
    )
    
    whiskers_playtime = Task(
        task_id=5,
        title="Interactive Play",
        description="Play with Whiskers using toy mouse",
        duration_minutes=15,
        priority="medium",
        target_condition="tiredness_level",
        pet_id=2,
        frequency="daily"
    )
    
    whiskers_grooming = Task(
        task_id=6,
        title="Brushing",
        description="Brush Whiskers' fur",
        duration_minutes=10,
        priority="low",
        target_condition="health_status",
        pet_id=2,
        frequency="weekly"
    )
    
    # Add tasks to pets
    mochi.tasks.extend([mochi_walk, mochi_breakfast, mochi_play])
    whiskers.tasks.extend([whiskers_feed, whiskers_playtime, whiskers_grooming])
    
    # Create calendar and scheduler
    calendar = Calendar(date=date.today(), owner_id=1)
    scheduler = Scheduler()
    
    # Generate schedule for the day (480 minutes = 8 hours available)
    owner.create_schedule(calendar, scheduler, available_minutes=480)
    
    # Print today's schedule
    print("\n" + "="*60)
    print(f"🐾 PawPal+ DAILY SCHEDULE - {date.today().strftime('%A, %B %d, %Y')}")
    print("="*60)
    print(f"Owner: {owner.name}")
    print(f"Available Time: 480 minutes (8 hours)\n")
    
    scheduled_tasks = calendar.get_tasks()
    
    if not scheduled_tasks:
        print("✓ No urgent tasks needed today!")
    else:
        cumulative_time = 0
        for idx, task in enumerate(scheduled_tasks, 1):
            pet_name = next((p.name for p in owner.pets if p.pet_id == task.pet_id), "Unknown")
            time_start = f"{cumulative_time:3d} min"
            time_end = f"{cumulative_time + task.duration_minutes:3d} min"
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
            
            print(f"{idx}. [{time_start} → {time_end}] {priority_emoji} {task.title}")
            print(f"   Pet: {pet_name} ({pet_name.lower()})")
            print(f"   Duration: {task.duration_minutes} minutes")
            print(f"   Target: {task.target_condition}")
            print(f"   Description: {task.description}")
            print()
            
            cumulative_time += task.duration_minutes
    
    # Print pet condition summary
    print("="*60)
    print("🐾 PET STATUS")
    print("="*60)
    
    for pet in owner.pets:
        condition = pet.get_condition()
        print(f"\n{pet.name} ({pet.species.capitalize()}):")
        print(f"  Age: {pet.age} years")
        print(f"  Hunger Level: {condition['hunger_level']}/100")
        print(f"  Tiredness Level: {condition['tiredness_level']}/100")
        print(f"  Health Status: {pet.health_status}")
        print(f"  Available Tasks: {len(pet.tasks)}")
    
    print("\n" + "="*60)
    print("Schedule generated successfully! 🎉")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
