from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date


@dataclass
class Pet:
    """Represents a pet with condition attributes and associated tasks."""
    pet_id: int
    name: str
    species: str
    hunger_level: int = 50  # 0-100 scale
    tiredness_level: int = 50  # 0-100 scale
    health_status: str = "healthy"
    age: int = 1
    tasks: List['Task'] = field(default_factory=list)  # Tasks specific to this pet
    

    def get_condition(self) -> Dict[str, int]:
        """Return the current condition of the pet."""
        return {
            "hunger_level": self.hunger_level,
            "tiredness_level": self.tiredness_level,
            "age": self.age
        }
    
    def update_condition(self, condition: str, value: int) -> None:
        """Update a specific condition attribute (clamped 0-100)."""
        value = max(0, min(100, value))  # Clamp to 0-100
        if hasattr(self, condition):
            setattr(self, condition, value)
        else:
            raise ValueError(f"Pet has no condition attribute: {condition}")
    
    def needs_task(self, task_type: str) -> bool:
        """Check if the pet needs a specific type of task based on condition thresholds."""
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
    
    def get_progress(self) -> int:
        """Return the current progress of the task (0-100)."""
        return self.progress
    
    def update_progress(self, amount: int) -> None:
        """Update progress by a given amount (clamped 0-100)."""
        self.progress = max(0, min(100, self.progress + amount))
    
    def mark_complete(self) -> None:
        """Mark the task as completed and set progress to 100."""
        self.completed = True
        self.progress = 100
    
    def get_description(self) -> str:
        """Return the task description."""
        return self.description


@dataclass
class Calendar:
    """Data structure that manages tasks and scheduling."""
    tasks: List[Task] = field(default_factory=list)
    date: date = field(default_factory=date.today)
    pet_id: Optional[int] = None  # Which pet this calendar is for (if single-pet)
    owner_id: Optional[int] = None  # Which owner this calendar belongs to
    
    def add_task(self, task: Task) -> None:
        """Add a task to the calendar."""
        if task not in self.tasks:
            self.tasks.append(task)
    
    def remove_task(self, task_id: int) -> None:
        """Remove a task from the calendar by ID."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]
    
    def clear_tasks(self) -> None:
        """Clear all tasks from the calendar."""
        self.tasks.clear()
    
    def get_tasks(self) -> List[Task]:
        """Return all tasks in the calendar."""
        return self.tasks.copy()
    
    def is_empty(self) -> bool:
        """Check if the calendar has any tasks."""
        return len(self.tasks) == 0
    
    def generate_schedule(self, pet: Pet, available_minutes: int = 480) -> List[Task]:
        """Generate a schedule for the pet using the Scheduler."""
        scheduler = Scheduler()
        return scheduler.generate_schedule(pet, self.tasks, available_minutes)
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by its ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None


class Scheduler:
    """Handles complex scheduling logic for generating daily pet care plans."""
    
    def __init__(self, priority_weights: Optional[Dict[str, int]] = None):
        """Initialize scheduler with optional custom priority weights."""
        self.priority_weights = priority_weights or {"high": 3, "medium": 2, "low": 1}
    
    def generate_schedule(self, pet: Pet, available_tasks: List[Task], available_minutes: int = 480) -> List[Task]:
        """Generate a daily schedule by filtering, sorting, and packing tasks within time constraints."""
        # Step 1: Filter tasks relevant to this pet and its current condition
        relevant_tasks = self.filter_tasks_for_pet(pet, available_tasks)
        
        # Step 2: Sort by priority (high -> low) and duration (short -> long)
        sorted_tasks = self.sort_by_priority(relevant_tasks)
        
        # Step 3: Fit tasks within available time using greedy algorithm
        scheduled = self.fit_tasks_in_time(sorted_tasks, available_minutes)
        
        return scheduled
    
    def filter_tasks_for_pet(self, pet: Pet, tasks: List[Task]) -> List[Task]:
        """Filter tasks that are: (1) for this pet, (2) relevant to pet's condition."""
        filtered = []
        for task in tasks:
            # Must be for this pet
            if task.pet_id != pet.pet_id:
                continue
            
            # Must not already be completed
            if task.completed:
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
    
    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by: (1) priority weight (desc), (2) duration (asc) for flexibility."""
        def task_sort_key(task: Task):
            """Return sort key tuple for task priority and duration."""
            priority_weight = self.priority_weights.get(task.priority, 0)
            # Negative priority so higher priority comes first in sort
            # Duration ascending so shorter tasks come first (better packing)
            return (-priority_weight, task.duration_minutes)
        
        return sorted(tasks, key=task_sort_key)
    
    def fit_tasks_in_time(self, tasks: List[Task], available_minutes: int) -> List[Task]:
        """Fit as many high-priority tasks as possible within available time (greedy algorithm)."""
        scheduled = []
        total_time = 0
        
        for task in tasks:
            # If task fits, add it
            if total_time + task.duration_minutes <= available_minutes:
                scheduled.append(task)
                total_time += task.duration_minutes
        
        return scheduled


class Owner:
    """Represents a pet owner."""
    
    def __init__(self, owner_id: int, name: str, contact_info: str = "", preferences: Optional[Dict] = None):
        """Initialize an owner with ID, name, contact info, and preferences."""
        self.owner_id = owner_id
        self.name = name
        self.contact_info = contact_info
        self.pets: List[Pet] = []
        self.preferences = preferences or {}
    
    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's collection."""
        if not any(p.pet_id == pet.pet_id for p in self.pets):
            self.pets.append(pet)
    
    def remove_pet(self, pet_id: int) -> None:
        """Remove a pet by ID."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]
    
    def get_pets(self) -> List[Pet]:
        """Return all pets owned by this owner."""
        return self.pets.copy()
    
    def create_schedule(self, calendar: Calendar, scheduler: 'Scheduler', available_minutes: int = 480) -> None:
        """Generate and populate a schedule for all owner's pets in the calendar."""
        # Clear the calendar for a fresh schedule
        calendar.clear_tasks()
        
        # For each pet, generate a schedule and add to calendar
        for pet in self.pets:
            # Generate tasks for this pet
            scheduled_tasks = scheduler.generate_schedule(pet, pet.tasks, available_minutes)
            
            # Add scheduled tasks to the calendar
            for task in scheduled_tasks:
                calendar.add_task(task)
