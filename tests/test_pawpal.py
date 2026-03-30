"""
Unit tests for PawPal+ system.
"""

import pytest
from pawpal_system import Task, Pet


class TestTaskCompletion:
    """Tests for task completion functionality."""
    
    def test_mark_complete_sets_completed_flag(self):
        """Verify that mark_complete() sets the completed flag to True."""
        task = Task(
            task_id=1,
            title="Morning Walk",
            description="Take dog for a walk",
            duration_minutes=30,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1
        )
        
        # Initially, task should not be completed
        assert task.completed is False, "New task should start as not completed"
        
        # Mark task as complete
        task.mark_complete()
        
        # Verify completed flag is now True
        assert task.completed is True, "Task should be marked as completed"
    
    def test_mark_complete_sets_progress_to_100(self):
        """Verify that mark_complete() sets progress to 100."""
        task = Task(
            task_id=2,
            title="Feeding",
            description="Feed the pet",
            duration_minutes=10,
            priority="high",
            target_condition="hunger_level",
            pet_id=1,
            progress=45  # Start at 45% progress
        )
        
        # Initially, progress should be 45
        assert task.progress == 45, "Task should start with progress of 45"
        
        # Mark task as complete
        task.mark_complete()
        
        # Verify progress is now 100
        assert task.progress == 100, "Task progress should be 100 after completion"
    
    def test_mark_complete_both_conditions(self):
        """Verify that mark_complete() sets both completed flag and progress to 100."""
        task = Task(
            task_id=3,
            title="Playtime",
            description="Play with pet",
            duration_minutes=20,
            priority="medium",
            target_condition="tiredness_level",
            pet_id=2,
            progress=0,
            completed=False
        )
        
        # Mark task as complete
        task.mark_complete()
        
        # Verify both conditions are met
        assert task.completed is True, "Completed flag should be True"
        assert task.progress == 100, "Progress should be 100"


class TestTaskAddition:
    """Tests for adding tasks to pets."""
    
    def test_add_task_to_pet_increases_count(self):
        """Verify that adding a task to a Pet increases the pet's task count."""
        pet = Pet(
            pet_id=1,
            name="Mochi",
            species="dog",
            hunger_level=50,
            tiredness_level=50
        )
        
        # Initially, pet should have no tasks
        assert len(pet.tasks) == 0, "New pet should have no tasks"
        
        # Create and add a task
        task = Task(
            task_id=1,
            title="Morning Walk",
            description="Take dog for a walk",
            duration_minutes=30,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1
        )
        pet.tasks.append(task)
        
        # Verify task count increased
        assert len(pet.tasks) == 1, "Pet should have 1 task after adding"
    
    def test_add_multiple_tasks_to_pet(self):
        """Verify that adding multiple tasks increases the count correctly."""
        pet = Pet(
            pet_id=2,
            name="Whiskers",
            species="cat",
            hunger_level=50,
            tiredness_level=50
        )
        
        # Add multiple tasks
        task1 = Task(
            task_id=1,
            title="Breakfast",
            description="Feed cat",
            duration_minutes=5,
            priority="high",
            target_condition="hunger_level",
            pet_id=2
        )
        task2 = Task(
            task_id=2,
            title="Playtime",
            description="Play with cat",
            duration_minutes=15,
            priority="medium",
            target_condition="tiredness_level",
            pet_id=2
        )
        task3 = Task(
            task_id=3,
            title="Grooming",
            description="Brush cat",
            duration_minutes=10,
            priority="low",
            target_condition="health_status",
            pet_id=2
        )
        
        # Initially empty
        assert len(pet.tasks) == 0, "New pet should start with no tasks"
        
        # Add tasks
        pet.tasks.extend([task1, task2, task3])
        
        # Verify count is 3
        assert len(pet.tasks) == 3, "Pet should have 3 tasks after adding 3"
    
    def test_task_contains_correct_data_after_addition(self):
        """Verify that task data is preserved after adding to pet."""
        pet = Pet(
            pet_id=1,
            name="Rex",
            species="dog",
            hunger_level=50,
            tiredness_level=50
        )
        
        task = Task(
            task_id=42,
            title="Evening Walk",
            description="Walk in the neighborhood",
            duration_minutes=45,
            priority="medium",
            target_condition="tiredness_level",
            pet_id=1
        )
        
        pet.tasks.append(task)
        
        # Verify data is intact
        assert len(pet.tasks) == 1, "Should have 1 task"
        added_task = pet.tasks[0]
        assert added_task.task_id == 42, "Task ID should be preserved"
        assert added_task.title == "Evening Walk", "Task title should be preserved"
        assert added_task.duration_minutes == 45, "Task duration should be preserved"
