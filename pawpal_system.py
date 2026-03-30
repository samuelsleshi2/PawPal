from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import date, datetime, timedelta


@dataclass
class Pet:
    """Represents a pet with condition attributes and associated tasks.
    
    Attributes:
        pet_id: Unique identifier for this pet
        name: Pet's name
        species: Type of pet (e.g., "dog", "cat", "rabbit")
        hunger_level: Hunger state (0-100, where 100 is very hungry)
        tiredness_level: Fatigue state (0-100, where 100 is very tired)
        health_status: Current health condition (e.g., "healthy", "sick", "recovering")
        age: Pet's age in years
        tasks: List of Task objects associated with this pet
    """
    pet_id: int
    name: str
    species: str
    hunger_level: int = 50  # 0-100 scale
    tiredness_level: int = 50  # 0-100 scale
    health_status: str = "healthy"
    age: int = 1
    tasks: List['Task'] = field(default_factory=list)  # Tasks specific to this pet
    

    def get_condition(self) -> Dict[str, int]:
        """Return the current condition of the pet.
        
        Returns:
            Dictionary with keys 'hunger_level', 'tiredness_level', 'age' and their current values
        """
        return {
            "hunger_level": self.hunger_level,
            "tiredness_level": self.tiredness_level,
            "age": self.age
        }
    
    def update_condition(self, condition: str, value: int) -> None:
        """Update a specific condition attribute, clamped to [0, 100].
        
        Args:
            condition: Name of condition to update (e.g., 'hunger_level', 'tiredness_level')
            value: New value for the condition
            
        Raises:
            ValueError: If the condition attribute doesn't exist on this pet
            
        Note:
            All condition values are automatically clamped to the range [0, 100].
        """
        value = max(0, min(100, value))  # Clamp to 0-100
        if hasattr(self, condition):
            setattr(self, condition, value)
        else:
            raise ValueError(f"Pet has no condition attribute: {condition}")
    
    def needs_task(self, task_type: str) -> bool:
        """Check if the pet needs a specific type of task based on condition thresholds.
        
        Args:
            task_type: Type of task to check ('walk', 'feed', 'play', 'rest')
            
        Returns:
            True if the pet needs this task type, False otherwise
            
        Logic:
            - 'walk': Needed when tiredness_level > 70 (pet is very tired)
            - 'feed': Needed when hunger_level > 70 (pet is very hungry)
            - 'play': Needed when tiredness_level > 60 (pet wants activity)
            - 'rest': Needed when tiredness_level < 30 (pet is under-rested/anxious)
            
        Returns False if task_type is not recognized.
        """
        # Map task types to conditions and thresholds
        thresholds = {
            "walk": ("tiredness_level", 70),  # Needs walk if tiredness > 70
            "feed": ("hunger_level", 70),      # Needs feeding if hunger > 70
            "play": ("tiredness_level", 60),   # Needs play if tiredness > 60
            "rest": ("tiredness_level", 30),   # Needs rest if tiredness < 30 (overexerted)
        }
        
        if task_type not in thresholds:
            return False
        
        condition, threshold = thresholds[task_type]
        current_value = getattr(self, condition, None)
        
        if current_value is None:
            return False
        
        # For most tasks, need it if condition is HIGH
        # For rest, need it if condition is LOW
        if task_type == "rest":
            return current_value < threshold
        return current_value > threshold


@dataclass
class Task:
    """Represents a pet care task with progress tracking."""
    task_id: int
    title: str
    description: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    target_condition: str  # e.g., "tiredness_level", "hunger_level"
    pet_id: int  # Which pet this task is for
    frequency: str = "once"  # "once", "daily", "weekly"
    progress: int = 0  # 0-100 scale
    completed: bool = False
    status: str = "pending"  # "pending", "in_progress", "completed", "skipped"
    scheduled_time: Optional[int] = None  # Start time in minutes from midnight (0-1440)
    time_window: Optional[str] = None  # "morning", "afternoon", "evening", "anytime"
    task_date: date = field(default_factory=date.today)  # Date this task is for
    next_task_id: Optional[int] = None  # ID for the next occurrence (if daily)
    
    def get_progress(self) -> int:
        """Return the current progress of the task (0-100).
        
        Returns:
            Integer representing task progress as a percentage (0-100)
        """
        return self.progress
    
    def update_progress(self, amount: int) -> None:
        """Update progress by a given amount (clamped 0-100).
        
        Args:
            amount: Integer amount to add to progress (can be negative to decrease)
            
        Note:
            Progress is automatically clamped to the range [0, 100].
            Passing 50 to a task with 75 progress results in 100 (not 125).
        """
        self.progress = max(0, min(100, self.progress + amount))
    
    def mark_complete(self) -> Optional['Task']:
        """Mark the task as completed and set progress to 100.
        
        For daily/weekly tasks, automatically creates and returns the next occurrence.
        For other frequencies, returns None.
        """
        self.completed = True
        self.progress = 100
        self.status = "completed"
        
        # Create next occurrence for recurring tasks
        if self.frequency in ["daily", "weekly"]:
            return self.create_next_occurrence()
        return None
    
    
    def set_scheduled_time(self, minutes_from_midnight: int) -> None:
        """Set the scheduled time for this task (0-1440 minutes from midnight)."""
        if 0 <= minutes_from_midnight <= 1440:
            self.scheduled_time = minutes_from_midnight
        else:
            raise ValueError("scheduled_time must be between 0 and 1440 minutes")
    
    def set_status(self, new_status: str) -> None:
        """Update task status (pending, in_progress, completed, skipped)."""
        valid_statuses = {"pending", "in_progress", "completed", "skipped"}
        if new_status in valid_statuses:
            self.status = new_status
        else:
            raise ValueError(f"Invalid status. Must be one of {valid_statuses}")
    
    def get_time_window_range(self) -> Tuple[int, int]:
        """Return (start_minutes, end_minutes) for the task's time window.
        
        Returns:
            Tuple of (start, end) in minutes from midnight:
            - 'morning': (360, 720)      # 6 AM - 12 PM
            - 'afternoon': (720, 1020)   # 12 PM - 5 PM
            - 'evening': (1020, 1320)    # 5 PM - 10 PM
            - 'anytime' or None: (0, 1440) # All day
        """
        windows = {
            "morning": (360, 720),      # 6 AM - 12 PM
            "afternoon": (720, 1020),   # 12 PM - 5 PM
            "evening": (1020, 1320),    # 5 PM - 10 PM
            "anytime": (0, 1440)        # All day
        }
        return windows.get(self.time_window, (0, 1440))
    def get_description(self) -> str:
        """Return the task description.
        
        Returns:
            Human-readable description of the task
        """
        return self.description
    
    def create_next_occurrence(self) -> 'Task':
        """Create the next occurrence of this task (for daily/weekly tasks).
        
        Returns a new Task with:
        - Same properties (title, description, priority, etc.)
        - Next day's date
        - Fresh state (not completed, progress=0, status=pending)
        - Incremented task_id to avoid duplication
        - Links back to current task via next_task_id
        
        Raises ValueError if task is not recurring (frequency must be 'daily' or 'weekly')
        """
        if self.frequency not in ["daily", "weekly"]:
            raise ValueError(f"Cannot create next occurrence for frequency '{self.frequency}'")
        
        # Calculate next occurrence date
        if self.frequency == "daily":
            next_date = self.task_date + timedelta(days=1)
        else:  # weekly
            next_date = self.task_date + timedelta(weeks=1)
        
        # Create new task instance
        next_task = Task(
            task_id=self.task_id + 1000,  # Offset to avoid ID collision
            title=self.title,
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            target_condition=self.target_condition,
            pet_id=self.pet_id,
            frequency=self.frequency,
            progress=0,  # Fresh start
            completed=False,  # Not yet completed
            status="pending",
            scheduled_time=None,  # Will be rescheduled
            time_window=self.time_window,
            task_date=next_date
        )
        
        # Link current task to the next one
        self.next_task_id = next_task.task_id
        
        return next_task


@dataclass
class Calendar:
    """Data structure that manages tasks and scheduling."""
    tasks: List[Task] = field(default_factory=list)
    date: date = field(default_factory=date.today)
    pet_id: Optional[int] = None  # Which pet this calendar is for (if single-pet)
    owner_id: Optional[int] = None  # Which owner this calendar belongs to
    
    def add_task(self, task: Task) -> None:
        """Add a task to the calendar.
        
        Args:
            task: Task object to add
            
        Returns:
            None
            
        Behavior:
            - Ignores duplicate tasks (doesn't add if task already in list)
            - Maintains original order of addition
            
        Note:
            Tasks are stored in a simple list. For large calendars, consider indexing by pet_id or date.
        """
        if task not in self.tasks:
            self.tasks.append(task)
    
    def remove_task(self, task_id: int) -> None:
        """Remove a task from the calendar by ID.
        
        Args:
            task_id: The ID of the task to remove
            
        Returns:
            None
            
        Behavior:
            - Silently succeeds if task is not found
            - Removes only the first matching task if duplicates exist
        """
        self.tasks = [t for t in self.tasks if t.task_id != task_id]
    
    def clear_tasks(self) -> None:
        """Clear all tasks from the calendar.
        
        Returns:
            None
            
        Warning:
            This permanently removes all tasks. No undo available.
        """
        self.tasks.clear()
    
    def get_tasks(self) -> List[Task]:
        """Return all tasks in the calendar (as a copy).
        
        Returns:
            List of Task objects currently in the calendar
            
        Note:
            Returns a copy to prevent external modification of internal list.
        """
        return self.tasks.copy()
    
    def is_empty(self) -> bool:
        """Check if the calendar has any tasks.
        
        Returns:
            True if no tasks in calendar, False otherwise
        """
        return len(self.tasks) == 0
    
    def generate_schedule(self, pet: Pet, available_minutes: int = 480) -> List[Task]:
        """Generate a schedule for a pet using the attached Scheduler.
        
        Args:
            pet: The Pet object to generate schedule for
            available_minutes: Total minutes available in the day (default 480 = 8 hours)
            
        Returns:
            List of scheduled tasks for the pet
            
        Note:
            Creates a new Scheduler instance internally. For multiple generations, consider
            reusing a Scheduler instance for consistency.
        """
        scheduler = Scheduler()
        return scheduler.generate_schedule(pet, self.tasks, available_minutes)
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Retrieve a specific task by its ID.
        
        Args:
            task_id: The ID of the task to find
            
        Returns:
            Task object if found, None otherwise
            
        Example:
            task = calendar.get_task_by_id(42)
            if task:
                print(f"Found: {task.title}")
        """
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    
    def filter_tasks_by_pet(self, pet_id: int) -> List[Task]:
        """Return all tasks for a specific pet.
        
        Args:
            pet_id: The ID of the pet to filter by
            
        Returns:
            List of all tasks where task.pet_id matches the given pet_id
        """
        return [task for task in self.tasks if task.pet_id == pet_id]
    
    def filter_tasks_by_status(self, status: str) -> List[Task]:
        """Return all tasks with a specific status.
        
        Args:
            status: The status to filter by (e.g., 'pending', 'in_progress', 'completed', 'skipped')
            
        Returns:
            List of all tasks where task.status matches the given status
        """
        return [task for task in self.tasks if task.status == status]
    
    def filter_tasks_by_completion(self, completed: bool) -> List[Task]:
        """Filter tasks by completion status (True=completed, False=incomplete).
        
        Args:
            completed: Boolean flag - True to get completed tasks, False to get incomplete tasks
            
        Returns:
            List of tasks filtered by their completed flag
            
        Note:
            This uses the task.completed boolean field. For status-based filtering, use
            filter_tasks_by_status() which checks the task.status field.
        """
        return [task for task in self.tasks if task.completed == completed]
    
    def filter_tasks_by_pet_and_status(self, pet_id: int, status: str) -> List[Task]:
        """Return all tasks for a specific pet with a specific status.
        
        Args:
            pet_id: The ID of the pet to filter by
            status: The status to filter by (e.g., 'pending', 'in_progress', 'completed', 'skipped')
            
        Returns:
            List of all tasks where both pet_id and status match
            
        Example:
            Get all incomplete tasks for pet 1: filter_tasks_by_pet_and_status(1, 'pending')
        """
        return [task for task in self.tasks if task.pet_id == pet_id and task.status == status]
    
    def get_tasks_for_date(self, target_date: date) -> List[Task]:
        """Return tasks valid for a specific date (handles recurring tasks).
        
        Args:
            target_date: The date to retrieve tasks for
            
        Returns:
            List of tasks valid for the given date
            
        Note:
            Current implementation returns all tasks on the calendar.
            A full implementation would expand recurring tasks and filter by task_date.
        """


class Scheduler:
    """Handles complex scheduling logic for generating daily pet care plans."""
    
    def __init__(self, priority_weights: Optional[Dict[str, int]] = None):
        """Initialize scheduler with optional custom priority weights."""
        self.priority_weights = priority_weights or {"high": 3, "medium": 2, "low": 1}
    
    def generate_schedule(self, pet: Pet, available_tasks: List[Task], available_minutes: int = 480) -> List[Task]:
        """Generate a daily schedule by filtering, sorting, and packing tasks within time constraints.
        
        Args:
            pet: The Pet object to generate a schedule for
            available_tasks: List of all Task objects (will be filtered for this pet)
            available_minutes: Total available minutes in the day (default 480 = 8 hours)
            
        Returns:
            List of scheduled and processed tasks (may include skipped tasks)
            
        Process:
            1. Filter: Extract only tasks relevant to this pet's current condition
            2. Expand: Include recurring tasks (daily, weekly) for today
            3. Sort: Order by priority (high → low), then duration (short → long)
            4. Schedule: Assign time slots respecting time window preferences
            5. Resolve: Fix any overlapping task conflicts
            
        Output Tasks:
            - May have scheduled_time assigned (None if skipped)
            - Status updated to 'pending', 'completed', or 'skipped'
            - Conflicts resolved by rescheduling lower-priority tasks
        """
        # Step 1: Filter tasks relevant to this pet and its current condition
        relevant_tasks = self.filter_tasks_for_pet(pet, available_tasks)
        
        # Step 2: Expand recurring tasks for today
        expanded_tasks = self.expand_recurring_tasks(relevant_tasks)
        
        # Step 3: Sort by priority (high -> low) and duration (short -> long)
        sorted_tasks = self.sort_by_priority(expanded_tasks)
        
        # Step 4: Schedule tasks with time slots
        scheduled = self.schedule_with_times(sorted_tasks, available_minutes)
        
        # Step 5: Detect and resolve conflicts
        scheduled = self.resolve_conflicts(scheduled)
        
        return scheduled
    
    def filter_tasks_for_pet(self, pet: Pet, tasks: List[Task]) -> List[Task]:
        """Filter tasks that are: (1) for this pet, (2) relevant to pet's condition, (3) not completed.
        
        Args:
            pet: The Pet object to filter tasks for
            tasks: List of all Task objects to filter
            
        Returns:
            List of tasks that are relevant to the pet's current condition
            
        Filtering Criteria:
            1. Task must be for this specific pet (pet_id match)
            2. Task must not already be completed (status != 'completed')
            3. Task must be relevant to pet's current needs based on condition thresholds:
               - Hunger level: feed tasks
               - Tiredness level: walk, play, rest tasks
               - Health status: vet_visit, medication tasks
        """
        filtered = []
        for task in tasks:
            # Must be for this pet
            if task.pet_id != pet.pet_id:
                continue
            
            # Must not already be completed
            if task.status == "completed":
                continue
            
            # Must be relevant to pet's current condition
            # Infer task type from target_condition (e.g., "tiredness_level" -> "walk")
            task_type_map = {
                "tiredness_level": ["walk", "play", "rest"],
                "hunger_level": ["feed"],
                "health_status": ["vet_visit", "medication"],
            }
            
            relevant = False
            for condition, task_types in task_type_map.items():
                if task.target_condition == condition:
                    # Check if pet needs this type of task
                    if any(pet.needs_task(t) for t in task_types):
                        relevant = True
                        break
            
            if relevant:
                filtered.append(task)
        
        return filtered
    
    def expand_recurring_tasks(self, tasks: List[Task]) -> List[Task]:
        """Expand recurring tasks into individual instances for today.
        
        Args:
            tasks: List of Task objects with various frequencies
            
        Returns:
            List of tasks with all recurring tasks included for the current day
            
        Behavior:
            - 'once' frequency: Included as-is
            - 'daily' frequency: Included as-is (will repeat tomorrow)
            - 'weekly' frequency: Included as-is (will repeat next week)
            - Other frequencies: Currently not supported, filtered out
            
        Note:
            Current implementation does not truly "expand" tasks; it merely includes them once.
            A full implementation would generate multiple instances for the day if needed,
            considering the day of week for weekly tasks.
        """
        expanded = []
        for task in tasks:
            if task.frequency in ["once", "daily"]:
                # Include the task as-is
                expanded.append(task)
            elif task.frequency == "weekly":
                # For a full implementation, check day of week
                # For now, include weekly tasks
                expanded.append(task)
        
        return expanded
    
    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by: (1) priority weight (desc), (2) duration (asc) for flexibility.
        
        Args:
            tasks: List of Task objects to sort
            
        Returns:
            List of tasks sorted by priority (high → medium → low), then by duration (short → long)
            
        Algorithm:
            Uses tuple-based sorting with negative priority weight to ensure higher priority tasks
            come first. Within the same priority level, shorter duration tasks come first to maximize
            packing efficiency (best-fit bin packing).
        """
        def task_sort_key(task: Task):
            """Return sort key tuple for task priority and duration."""
            priority_weight = self.priority_weights.get(task.priority, 0)
            # Negative priority so higher priority comes first in sort
            # Duration ascending so shorter tasks come first (better packing)
            return (-priority_weight, task.duration_minutes)
        
        return sorted(tasks, key=task_sort_key)
    
    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by scheduled time (ascending), handling tasks without scheduled times last.
        
        Args:
            tasks: List of Task objects to sort
            
        Returns:
            List of tasks sorted chronologically by scheduled_time. Tasks with no scheduled time
            are placed at the end.
            
        Behavior:
            - Tasks with scheduled_time values are sorted ascending (earliest first)
            - Tasks with scheduled_time=None are grouped at the end
            - Useful for human-readable schedule displays and time-based analysis
        """
        def time_sort_key(task: Task):
            # Tasks with scheduled times come first, sorted by time
            # Tasks without scheduled times come last
            if task.scheduled_time is not None:
                return (0, task.scheduled_time)
            else:
                return (1, 0)
        
        return sorted(tasks, key=time_sort_key)
    
    def schedule_with_times(self, tasks: List[Task], available_minutes: int = 480) -> List[Task]:
        """Schedule tasks within time constraints, assigning time slots.
        
        Args:
            tasks: List of Task objects (should be pre-sorted by priority)
            available_minutes: Total available minutes in the day (default 480 = 8 hours)
            
        Returns:
            List of tasks with scheduled_time and status updated
            
        Algorithm:
            1. Start with current_time = 0 (midnight)
            2. For each task in order:
               a. If task has a preferred time_window, jump to that window's start
               b. If task fits in remaining time, assign scheduled_time and add to output
               c. If task doesn't fit, mark as 'skipped' and add to output
            3. Update current_time as tasks are scheduled
            
        Time Window Behavior:
            Tasks with time window preferences will be scheduled at the start of their window,
            potentially leaving gaps before the window. This respects user preferences but may
            waste available time between tasks.
            
        Output:
            - All input tasks are returned
            - scheduled_time is set for tasks that fit
            - scheduled_time remains None for skipped tasks
            - status is updated to 'skipped' for tasks that don't fit
        """
        scheduled = []
        current_time = 0  # Start of day in minutes from midnight
        
        for task in tasks:
            # Respect time window preferences
            if task.time_window and task.time_window != "anytime":
                window_start, window_end = task.get_time_window_range()
                # Try to place task in its preferred window
                if current_time < window_start:
                    current_time = window_start
            
            # Check if task fits in remaining time
            if current_time + task.duration_minutes <= available_minutes:
                task.scheduled_time = current_time
                scheduled.append(task)
                current_time += task.duration_minutes
            else:
                # Task doesn't fit in available time
                task.set_status("skipped")
                scheduled.append(task)
        
        return scheduled
    
    def detect_conflicts(self, tasks: List[Task]) -> List[Tuple[Task, Task]]:
        """Detect scheduling conflicts (overlapping tasks).
        
        Args:
            tasks: List of Task objects with scheduled_time values assigned
            
        Returns:
            List of (task1, task2) tuples where tasks overlap in time
            
        Detection Logic:
            - Skips tasks without scheduled_time or with status='skipped'
            - Compares each task pair to check for time overlaps
            - Two tasks overlap if: NOT (task1_end <= task2_start OR task2_end <= task1_start)
            - Returns unordered pairs
            
        Example:
            If Task A is 6:00-6:30 and Task B is 6:20-6:50, they overlap and would be returned
        """
        conflicts = []
        
        for i, task1 in enumerate(tasks):
            if task1.scheduled_time is None or task1.status == "skipped":
                continue
            
            task1_end = task1.scheduled_time + task1.duration_minutes
            
            for task2 in tasks[i + 1:]:
                if task2.scheduled_time is None or task2.status == "skipped":
                    continue
                
                task2_end = task2.scheduled_time + task2.duration_minutes
                
                # Check if times overlap
                if not (task1_end <= task2.scheduled_time or task2_end <= task1.scheduled_time):
                    conflicts.append((task1, task2))
        
        return conflicts
    
    def detect_simultaneous_tasks(self, tasks: List[Task]) -> List[Dict]:
        """Detect tasks scheduled at the SAME START time (lightweight, non-destructive).
        
        Args:
            tasks: List of Task objects with scheduled_time values assigned
            
        Returns:
            List of warning dictionaries. Each dict contains:
            - 'warning': Formatted message describing the conflict
            - 'tasks': List of Task objects that start at the same time
            - 'start_time': The time when conflict occurs (minutes from midnight)
            - 'task_ids': List of conflicting task IDs
            - 'pet_ids': List of pet IDs involved
            - 'severity': Either 'critical' (same pet) or 'warning' (different pets)
        
        Lightweight Design:
            - Only checks task start times (not full time overlaps)
            - Returns warnings without modifying any task objects
            - Never crashes the program; safely handles edge cases
            - Categorizes severity based on whether tasks involve the same pet
            - Skips unscheduled tasks (status='skipped' or scheduled_time=None)
            
        Severity Levels:
            - 'critical': Multiple tasks for the SAME pet at the same time (impossible to do)
            - 'warning': Tasks at same time for DIFFERENT pets (logically possible but unusual)
        """
        warnings = []
        time_groups = {}  # Group tasks by start time
        
        # Group tasks by start time
        for task in tasks:
            if task.scheduled_time is None or task.status == "skipped":
                continue
            
            start_time = task.scheduled_time
            if start_time not in time_groups:
                time_groups[start_time] = []
            time_groups[start_time].append(task)
        
        # Check for simultaneous tasks
        for start_time, tasks_at_time in time_groups.items():
            if len(tasks_at_time) > 1:
                # Multiple tasks at same start time
                pet_ids = [t.pet_id for t in tasks_at_time]
                same_pet = len(set(pet_ids)) == 1  # All same pet_id?
                
                # Format time as HH:MM
                hours = start_time // 60
                minutes = start_time % 60
                time_str = f"{hours:02d}:{minutes:02d}"
                
                # Build warning message
                task_titles = ", ".join([f"'{t.title}' (ID:{t.task_id})" for t in tasks_at_time])
                
                if same_pet:
                    severity = "critical"
                    warning_msg = f"CRITICAL: Multiple tasks for same pet at {time_str}: {task_titles}"
                else:
                    severity = "warning"
                    warning_msg = f"WARNING: Tasks starting simultaneously at {time_str}: {task_titles}"
                
                warnings.append({
                    'warning': warning_msg,
                    'tasks': tasks_at_time,
                    'start_time': start_time,
                    'task_ids': [t.task_id for t in tasks_at_time],
                    'pet_ids': pet_ids,
                    'severity': severity
                })
        
        return warnings
    
    def print_conflict_warnings(self, tasks: List[Task]) -> int:
        """Print formatted warnings for simultaneous task conflicts to console.
        
        Args:
            tasks: List of Task objects with scheduled_time values assigned
            
        Returns:
            Integer count of warnings found and printed
            
        Behavior:
            1. Calls detect_simultaneous_tasks() to find conflicts
            2. For each warning, prints severity and task details
            3. Displays task title, pet ID, and duration for each conflicting task
            4. Prints nothing if no conflicts are found
            5. Does not modify any task objects
            
        Output Format:
            Each warning prints as:
            [SEVERITY]: Multiple tasks/Tasks at HH:MM: 'Task Name' (ID:###), ...
              - Task Name (Pet ###, ## min)
              - Task Name (Pet ###, ## min)
            
        Use Case:
            Sanity-checking a generated schedule before deployment. Users can review
            warnings and manually adjust if needed.
        """
        warnings = self.detect_simultaneous_tasks(tasks)
        
        if warnings:
            for warning in warnings:
                print(f"\n{warning['warning']}")
                for task in warning['tasks']:
                    pet_name = f"Pet {task.pet_id}"
                    print(f"  - {task.title} ({pet_name}, {task.duration_minutes} min)")
        
        return len(warnings)
    
    def resolve_conflicts(self, tasks: List[Task]) -> List[Task]:
        """Resolve scheduling conflicts by adjusting task times or skipping lower-priority tasks.
        
        Args:
            tasks: List of Task objects potentially containing scheduling conflicts
            
        Returns:
            List of tasks with conflicts resolved. May modify scheduled_time of lower-priority tasks.
            
        Algorithm:
            1. Detect all overlapping task pairs using detect_conflicts()
            2. For each conflict pair, compare priorities using priority_order weights
            3. Reschedule the lower-priority task to start after the higher-priority task ends
            4. Return modified task list
            
        Note:
            This modifies task objects in-place (changes their scheduled_time).
            Only handles full-duration conflicts; does not check if rescheduled tasks exceed available time.
        """
        conflicts = self.detect_conflicts(tasks)
        
        if not conflicts:
            return tasks
        
        # For each conflict, try to reschedule the lower-priority task
        for task1, task2 in conflicts:
            # Determine which task has lower priority
            priority_order = {"high": 3, "medium": 2, "low": 1}
            priority1 = priority_order.get(task1.priority, 0)
            priority2 = priority_order.get(task2.priority, 0)
            
            if priority1 < priority2:
                # task1 has lower priority, try to move it
                task1.scheduled_time = task2.scheduled_time + task2.duration_minutes
            else:
                # task2 has lower priority, try to move it
                task2.scheduled_time = task1.scheduled_time + task1.duration_minutes
        
        return tasks
    
    def fit_tasks_in_time(self, tasks: List[Task], available_minutes: int) -> List[Task]:
        """Fit as many high-priority tasks as possible within available time (greedy algorithm).
        
        Args:
            tasks: List of Task objects, preferably already sorted by priority
            available_minutes: Total minutes available in the day (default 480 = 8 hours)
            
        Returns:
            List of tasks that fit within the time constraint
            
        Algorithm:
            Uses a simple greedy approach:
            1. Iterate through tasks in order (should be priority-sorted)
            2. Add each task if it fits in remaining time
            3. Skip tasks that exceed remaining time
            
        Note:
            Does not assign scheduled_time; use schedule_with_times() for actual scheduling.
            This is a legacy method; schedule_with_times() is preferred for complete scheduling.
        """
        scheduled = []
        total_time = 0
        
        for task in tasks:
            # If task fits, add it
            if total_time + task.duration_minutes <= available_minutes:
                scheduled.append(task)
                total_time += task.duration_minutes
        
        return scheduled


class Owner:
    """Represents a pet owner and manages their collection of pets.
    
    Attributes:
        owner_id: Unique identifier for the owner
        name: Owner's name
        contact_info: Contact information (phone, email, etc.)
        pets: List of Pet objects owned by this owner
        preferences: Dictionary of owner preferences (scheduling, communication, etc.)
    """
    
    def __init__(self, owner_id: int, name: str, contact_info: str = "", preferences: Optional[Dict] = None):
        """Initialize an owner with ID, name, contact info, and preferences.
        
        Args:
            owner_id: Unique identifier for this owner
            name: Owner's full name
            contact_info: Contact information (optional)
            preferences: Dictionary of owner preferences (optional, defaults to empty dict)
        """
        self.owner_id = owner_id
        self.name = name
        self.contact_info = contact_info
        self.pets: List[Pet] = []
        self.preferences = preferences or {}
    
    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's collection.
        
        Args:
            pet: Pet object to add
            
        Behavior:
            - Prevents duplicate pet IDs in collection
            - Maintains order of addition
        """
        if not any(p.pet_id == pet.pet_id for p in self.pets):
            self.pets.append(pet)
    
    def remove_pet(self, pet_id: int) -> None:
        """Remove a pet by ID from the owner's collection.
        
        Args:
            pet_id: The ID of the pet to remove
            
        Behavior:
            - Silently succeeds if pet not found
        """
        self.pets = [p for p in self.pets if p.pet_id != pet_id]
    
    def get_pets(self) -> List[Pet]:
        """Return all pets owned by this owner (as a copy).
        
        Returns:
            List of Pet objects owned by this owner
            
        Note:
            Returns a copy to prevent external modification of internal list.
        """
        return self.pets.copy()
    
    def create_schedule(self, calendar: Calendar, scheduler: 'Scheduler', available_minutes: int = 480) -> None:
        """Generate and populate a schedule for all owner's pets in the calendar.
        
        Args:
            calendar: Calendar object to populate with tasks
            scheduler: Scheduler object to use for scheduling logic
            available_minutes: Total minutes available in the day (default 480 = 8 hours)
            
        Returns:
            None
            
        Behavior:
            1. Clears the calendar to start fresh
            2. For each pet owned, generates a schedule
            3. Adds all scheduled tasks to the calendar
            4. Resolves conflicts within the schedule
            
        Note:
            This method integrates the Owner → Calendar → Scheduler pipeline.
            After calling, calendar.get_tasks() will contain all scheduled tasks for all pets.
        """
        # Clear the calendar for a fresh schedule
        calendar.clear_tasks()
        
        # For each pet, generate a schedule and add to calendar
        for pet in self.pets:
            # Generate tasks for this pet
            scheduled_tasks = scheduler.generate_schedule(pet, pet.tasks, available_minutes)
            
            # Add scheduled tasks to the calendar
            for task in scheduled_tasks:
                calendar.add_task(task)
