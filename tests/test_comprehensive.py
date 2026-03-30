"""
Comprehensive unit tests for PawPal+ system.
Tests 5 critical features: sorting, recurrence, conflict detection, priority scheduling, and time windows.
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Calendar, Scheduler, Owner


class TestSortingCorrectness:
    """Tests for chronological task sorting (REQUIRED TEST 1)."""
    
    def test_sort_tasks_by_time_chronological_order(self):
        """Verify tasks are returned in chronological order."""
        # Create tasks with different scheduled times
        task_morning = Task(
            task_id=1,
            title="Morning Walk",
            description="Walk in the morning",
            duration_minutes=30,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1,
            scheduled_time=360  # 6:00 AM
        )
        
        task_afternoon = Task(
            task_id=2,
            title="Afternoon Play",
            description="Play in the afternoon",
            duration_minutes=20,
            priority="medium",
            target_condition="tiredness_level",
            pet_id=1,
            scheduled_time=900  # 3:00 PM
        )
        
        task_evening = Task(
            task_id=3,
            title="Evening Meal",
            description="Feed in the evening",
            duration_minutes=15,
            priority="high",
            target_condition="hunger_level",
            pet_id=1,
            scheduled_time=1140  # 7:00 PM
        )
        
        task_early = Task(
            task_id=4,
            title="Early Breakfast",
            description="Early breakfast",
            duration_minutes=10,
            priority="high",
            target_condition="hunger_level",
            pet_id=1,
            scheduled_time=300  # 5:00 AM
        )
        
        unsorted_tasks = [task_afternoon, task_early, task_evening, task_morning]
        scheduler = Scheduler()
        
        # Sort tasks by time
        sorted_tasks = scheduler.sort_by_time(unsorted_tasks)
        
        # Verify chronological order
        assert sorted_tasks[0].task_id == 4, "First task should be task_id=4 (5:00 AM)"
        assert sorted_tasks[1].task_id == 1, "Second task should be task_id=1 (6:00 AM)"
        assert sorted_tasks[2].task_id == 2, "Third task should be task_id=2 (3:00 PM)"
        assert sorted_tasks[3].task_id == 3, "Fourth task should be task_id=3 (7:00 PM)"
        
        # Verify all tasks are present
        assert len(sorted_tasks) == 4, "All tasks should be in sorted list"
        
        # Verify times are in ascending order
        for i in range(len(sorted_tasks) - 1):
            assert sorted_tasks[i].scheduled_time <= sorted_tasks[i + 1].scheduled_time, \
                f"Time order violated: {sorted_tasks[i].scheduled_time} > {sorted_tasks[i + 1].scheduled_time}"
    
    def test_sort_by_time_handles_unscheduled_tasks(self):
        """Verify unscheduled tasks are placed at the end."""
        task_scheduled = Task(
            task_id=1,
            title="Scheduled",
            description="Has a time",
            duration_minutes=30,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1,
            scheduled_time=600
        )
        
        task_unscheduled = Task(
            task_id=2,
            title="Unscheduled",
            description="No time assigned",
            duration_minutes=20,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1,
            scheduled_time=None
        )
        
        tasks = [task_unscheduled, task_scheduled]
        scheduler = Scheduler()
        sorted_tasks = scheduler.sort_by_time(tasks)
        
        # Scheduled task should come first
        assert sorted_tasks[0].task_id == 1, "Scheduled task should come first"
        assert sorted_tasks[1].task_id == 2, "Unscheduled task should come last"
    
    def test_sort_by_time_empty_list(self):
        """Verify empty task list is handled correctly."""
        scheduler = Scheduler()
        sorted_tasks = scheduler.sort_by_time([])
        assert len(sorted_tasks) == 0, "Empty list should remain empty"


class TestRecurrenceLogic:
    """Tests for recurring task generation (REQUIRED TEST 2)."""
    
    def test_daily_task_creates_next_occurrence_on_completion(self):
        """Confirm that marking a daily task complete creates a new task for the following day."""
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
        
        # Verify initial state
        assert daily_task.completed is False, "Task should start incomplete"
        assert daily_task.progress == 0, "Task should start with 0% progress"
        assert daily_task.status == "pending", "Task should start as pending"
        assert daily_task.next_task_id is None, "Should have no next task link initially"
        
        # Mark complete
        next_task = daily_task.mark_complete()
        
        # Verify original task is marked complete
        assert daily_task.completed is True, "Original task should be marked completed"
        assert daily_task.progress == 100, "Original task should be at 100% progress"
        assert daily_task.status == "completed", "Original task should have completed status"
        
        # Verify next task is created
        assert next_task is not None, "Next task should be created for daily recurring task"
        assert next_task.task_date == today + timedelta(days=1), "Next task should be tomorrow"
        assert next_task.completed is False, "Next task should start incomplete"
        assert next_task.progress == 0, "Next task should start at 0% progress"
        assert next_task.status == "pending", "Next task should start as pending"
        assert next_task.title == daily_task.title, "Next task should have same title"
        assert daily_task.next_task_id == next_task.task_id, "Original task should link to next"
    
    def test_weekly_task_creates_next_occurrence_on_completion(self):
        """Confirm that marking a weekly task complete creates a new task for next week."""
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
        
        # Mark complete
        next_task = weekly_task.mark_complete()
        
        # Verify next task is created with 7-day gap
        assert next_task is not None, "Next task should be created for weekly recurring task"
        assert next_task.task_date == today + timedelta(weeks=1), "Next task should be one week later"
        assert (next_task.task_date - today).days == 7, "Should be exactly 7 days after original"
    
    def test_one_time_task_returns_none_on_completion(self):
        """Verify that one-time tasks do not create next occurrences."""
        one_time_task = Task(
            task_id=3,
            title="Vet Appointment",
            description="Annual checkup",
            duration_minutes=40,
            priority="high",
            target_condition="health_status",
            pet_id=1,
            frequency="once"
        )
        
        # Mark complete
        next_task = one_time_task.mark_complete()
        
        # Verify no next task created
        assert next_task is None, "One-time task should not create next occurrence"
        assert one_time_task.completed is True, "Task should be marked complete"
    
    def test_created_next_task_has_incremented_id(self):
        """Verify next recurring task has a unique incremented ID."""
        daily_task = Task(
            task_id=100,
            title="Daily Feed",
            description="Feed the pet",
            duration_minutes=15,
            priority="high",
            target_condition="hunger_level",
            pet_id=1,
            frequency="daily"
        )
        
        next_task = daily_task.mark_complete()
        
        # IDs should be different to avoid conflicts
        assert next_task.task_id != daily_task.task_id, "Next task should have different ID"
        assert next_task.task_id > daily_task.task_id, "Next task ID should be greater"
    
    def test_recurring_task_inherits_properties(self):
        """Verify next recurring task inherits all properties from original."""
        original = Task(
            task_id=5,
            title="Custom Task",
            description="A detailed description",
            duration_minutes=45,
            priority="medium",
            target_condition="tiredness_level",
            pet_id=2,
            frequency="daily",
            time_window="afternoon"
        )
        
        next_task = original.mark_complete()
        
        # Verify properties are inherited
        assert next_task.title == original.title, "Title should be inherited"
        assert next_task.description == original.description, "Description should be inherited"
        assert next_task.duration_minutes == original.duration_minutes, "Duration should be inherited"
        assert next_task.priority == original.priority, "Priority should be inherited"
        assert next_task.target_condition == original.target_condition, "Target condition should be inherited"
        assert next_task.pet_id == original.pet_id, "Pet ID should be inherited"
        assert next_task.frequency == original.frequency, "Frequency should be inherited"
        assert next_task.time_window == original.time_window, "Time window should be inherited"


class TestConflictDetection:
    """Tests for time conflict flagging (REQUIRED TEST 3)."""
    
    def test_detect_simultaneous_tasks_same_pet_critical(self):
        """Verify that the Scheduler flags duplicate times for same pet as CRITICAL."""
        # Create two tasks for the same pet at the same time
        breakfast = Task(
            task_id=1,
            title="Breakfast",
            description="Feed dog",
            duration_minutes=10,
            priority="high",
            target_condition="hunger_level",
            pet_id=1,
            scheduled_time=360  # 6:00 AM
        )
        
        morning_walk = Task(
            task_id=2,
            title="Morning Walk",
            description="Walk dog",
            duration_minutes=30,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1,
            scheduled_time=360  # SAME TIME
        )
        
        scheduler = Scheduler()
        tasks = [breakfast, morning_walk]
        
        # Detect conflicts
        warnings = scheduler.detect_simultaneous_tasks(tasks)
        
        # Verify conflict is detected
        assert len(warnings) == 1, "Should detect one conflict"
        assert warnings[0]['severity'] == 'critical', "Same pet conflict should be CRITICAL"
        assert warnings[0]['start_time'] == 360, "Conflict should be at 6:00 AM"
        assert len(warnings[0]['tasks']) == 2, "Should have 2 conflicting tasks"
        assert set(warnings[0]['task_ids']) == {1, 2}, "Should identify both task IDs"
    
    def test_detect_simultaneous_tasks_different_pets_warning(self):
        """Verify that the Scheduler flags duplicate times for different pets as WARNING."""
        # Create tasks for different pets at the same time
        dog_meal = Task(
            task_id=10,
            title="Dog Meal",
            description="Feed dog",
            duration_minutes=10,
            priority="high",
            target_condition="hunger_level",
            pet_id=1,
            scheduled_time=420  # 7:00 AM
        )
        
        cat_meal = Task(
            task_id=11,
            title="Cat Meal",
            description="Feed cat",
            duration_minutes=5,
            priority="high",
            target_condition="hunger_level",
            pet_id=2,
            scheduled_time=420  # SAME TIME, DIFFERENT PET
        )
        
        scheduler = Scheduler()
        tasks = [dog_meal, cat_meal]
        
        # Detect conflicts
        warnings = scheduler.detect_simultaneous_tasks(tasks)
        
        # Verify conflict is detected as warning
        assert len(warnings) == 1, "Should detect one conflict"
        assert warnings[0]['severity'] == 'warning', "Different pet conflict should be WARNING"
        assert set(warnings[0]['pet_ids']) == {1, 2}, "Should involve both pets"
    
    def test_detect_no_conflicts_when_times_differ(self):
        """Verify no conflicts are flagged when task times differ."""
        task1 = Task(
            task_id=1,
            title="Morning Task",
            description="Morning",
            duration_minutes=30,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1,
            scheduled_time=360
        )
        
        task2 = Task(
            task_id=2,
            title="Afternoon Task",
            description="Afternoon",
            duration_minutes=30,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1,
            scheduled_time=900
        )
        
        scheduler = Scheduler()
        warnings = scheduler.detect_simultaneous_tasks([task1, task2])
        
        assert len(warnings) == 0, "Should have no conflicts when times differ"
    
    def test_detect_conflicts_ignores_unscheduled_tasks(self):
        """Verify detection ignores tasks without scheduled times."""
        scheduled = Task(
            task_id=1,
            title="Scheduled",
            description="Has time",
            duration_minutes=30,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1,
            scheduled_time=360
        )
        
        unscheduled = Task(
            task_id=2,
            title="Unscheduled",
            description="No time",
            duration_minutes=30,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1,
            scheduled_time=None
        )
        
        scheduler = Scheduler()
        warnings = scheduler.detect_simultaneous_tasks([scheduled, unscheduled])
        
        assert len(warnings) == 0, "Unscheduled tasks should be ignored in conflict detection"
    
    def test_multiple_conflicts_detected(self):
        """Verify multiple simultaneous conflicts are all detected."""
        task1 = Task(task_id=1, title="Task 1", description="", duration_minutes=10, 
                    priority="high", target_condition="hunger_level", pet_id=1, scheduled_time=360)
        task2 = Task(task_id=2, title="Task 2", description="", duration_minutes=10,
                    priority="high", target_condition="hunger_level", pet_id=1, scheduled_time=360)
        task3 = Task(task_id=3, title="Task 3", description="", duration_minutes=10,
                    priority="high", target_condition="hunger_level", pet_id=1, scheduled_time=900)
        task4 = Task(task_id=4, title="Task 4", description="", duration_minutes=10,
                    priority="high", target_condition="hunger_level", pet_id=1, scheduled_time=900)
        
        scheduler = Scheduler()
        warnings = scheduler.detect_simultaneous_tasks([task1, task2, task3, task4])
        
        # Should detect 2 conflicts (one at 360, one at 900)
        assert len(warnings) == 2, "Should detect 2 separate conflicts"


class TestPriorityBasedScheduling:
    """Tests for priority-based task scheduling."""
    
    def test_sort_by_priority_high_to_low(self):
        """Verify tasks are sorted by priority from high to low."""
        high_priority = Task(
            task_id=1, title="High", description="", duration_minutes=30,
            priority="high", target_condition="tiredness_level", pet_id=1
        )
        low_priority = Task(
            task_id=2, title="Low", description="", duration_minutes=30,
            priority="low", target_condition="tiredness_level", pet_id=1
        )
        medium_priority = Task(
            task_id=3, title="Medium", description="", duration_minutes=30,
            priority="medium", target_condition="tiredness_level", pet_id=1
        )
        
        unsorted = [low_priority, high_priority, medium_priority]
        scheduler = Scheduler()
        sorted_tasks = scheduler.sort_by_priority(unsorted)
        
        # Verify priority order
        assert sorted_tasks[0].priority == "high", "High priority should be first"
        assert sorted_tasks[1].priority == "medium", "Medium priority should be second"
        assert sorted_tasks[2].priority == "low", "Low priority should be last"
    
    def test_sort_by_priority_then_duration(self):
        """Verify tasks with same priority are sorted by duration (short first)."""
        high1 = Task(
            task_id=1, title="High 60min", description="", duration_minutes=60,
            priority="high", target_condition="tiredness_level", pet_id=1
        )
        high2 = Task(
            task_id=2, title="High 30min", description="", duration_minutes=30,
            priority="high", target_condition="tiredness_level", pet_id=1
        )
        high3 = Task(
            task_id=3, title="High 45min", description="", duration_minutes=45,
            priority="high", target_condition="tiredness_level", pet_id=1
        )
        
        unsorted = [high1, high3, high2]
        scheduler = Scheduler()
        sorted_tasks = scheduler.sort_by_priority(unsorted)
        
        # Same priority, should sort by duration ascending
        assert sorted_tasks[0].duration_minutes == 30, "Shortest duration should be first"
        assert sorted_tasks[1].duration_minutes == 45, "Medium duration should be second"
        assert sorted_tasks[2].duration_minutes == 60, "Longest duration should be last"


class TestTimeWindowRespect:
    """Tests for time window preference respecting."""
    
    def test_schedule_respects_morning_time_window(self):
        """Verify morning tasks are scheduled in morning window (6 AM - 12 PM)."""
        morning_task = Task(
            task_id=1,
            title="Morning Task",
            description="Schedule in morning",
            duration_minutes=30,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1,
            time_window="morning"  # 360-720 minutes
        )
        
        scheduler = Scheduler()
        scheduled = scheduler.schedule_with_times([morning_task], available_minutes=480)
        
        # Verify task is scheduled in morning window
        assert scheduled[0].scheduled_time is not None, "Task should be scheduled"
        assert 360 <= scheduled[0].scheduled_time <= 720, "Task should be in morning window"
    
    def test_schedule_respects_afternoon_time_window(self):
        """Verify afternoon tasks are scheduled in afternoon window (12 PM - 5 PM)."""
        afternoon_task = Task(
            task_id=2,
            title="Afternoon Task",
            description="Schedule in afternoon",
            duration_minutes=30,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1,
            time_window="afternoon"  # 720-1020 minutes
        )
        
        # Provide full day of available time (1440 minutes = 24 hours)
        scheduler = Scheduler()
        scheduled = scheduler.schedule_with_times([afternoon_task], available_minutes=1440)
        
        # Verify task is scheduled in afternoon window
        assert scheduled[0].scheduled_time is not None, "Task should be scheduled"
        assert 720 <= scheduled[0].scheduled_time <= 1020, "Task should be in afternoon window (12 PM - 5 PM)"
    
    def test_schedule_respects_evening_time_window(self):
        """Verify evening tasks are scheduled in evening window (5 PM - 10 PM)."""
        evening_task = Task(
            task_id=3,
            title="Evening Task",
            description="Schedule in evening",
            duration_minutes=30,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1,
            time_window="evening"  # 1020-1320 minutes
        )
        
        # Extend available time to fit evening window
        scheduler = Scheduler()
        scheduled = scheduler.schedule_with_times([evening_task], available_minutes=1440)
        
        # Verify task is in evening window
        assert scheduled[0].scheduled_time is not None, "Task should be scheduled"
        assert 1020 <= scheduled[0].scheduled_time <= 1320, "Task should be in evening window"
    
    def test_get_time_window_range_returns_correct_bounds(self):
        """Verify time window methods return correct start/end times."""
        morning_task = Task(
            task_id=1, title="", description="", duration_minutes=10,
            priority="high", target_condition="tiredness_level", pet_id=1,
            time_window="morning"
        )
        
        start, end = morning_task.get_time_window_range()
        assert start == 360, "Morning start should be 6 AM (360 min)"
        assert end == 720, "Morning end should be 12 PM (720 min)"
    
    def test_anytime_task_not_constrained_by_window(self):
        """Verify anytime tasks can be scheduled flexibly."""
        anytime_task = Task(
            task_id=1,
            title="Flexible Task",
            description="Schedule anytime",
            duration_minutes=30,
            priority="high",
            target_condition="tiredness_level",
            pet_id=1,
            time_window="anytime"
        )
        
        scheduler = Scheduler()
        scheduled = scheduler.schedule_with_times([anytime_task], available_minutes=480)
        
        # Should be scheduled at the start (no window constraint)
        assert scheduled[0].scheduled_time == 0, "Anytime task should start at beginning"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
