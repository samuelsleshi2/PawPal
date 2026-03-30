from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date


@dataclass
class Pet:
    """Represents a pet with condition attributes."""
    pet_id: int
    name: str
    species: str
    hunger_level: int = 50  # 0-100 scale
    tiredness_level: int = 50  # 0-100 scale
    health_status: str = "healthy"
    age: int = 1
    
    def get_condition(self) -> Dict[str, int]:
        """Return the current condition of the pet."""
        pass
    
    def update_condition(self, condition: str, value: int) -> None:
        """Update a specific condition attribute."""
        pass
    
    def needs_task(self, task_type: str) -> bool:
        """Check if the pet needs a specific type of task."""
        pass


@dataclass
class Task:
    """Represents a pet care task with progress tracking."""
    task_id: int
    title: str
    description: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    target_condition: str  # e.g., "tiredness_level", "hunger_level"
    progress: int = 0  # 0-100 scale
    completed: bool = False
    
    def get_progress(self) -> int:
        """Return the current progress of the task."""
        pass
    
    def update_progress(self, amount: int) -> None:
        """Update progress by a given amount."""
        pass
    
    def mark_complete(self) -> None:
        """Mark the task as completed."""
        pass
    
    def get_description(self) -> str:
        """Return the task description."""
        pass


@dataclass
class Calendar:
    """Data structure that manages tasks and scheduling."""
    tasks: List[Task] = field(default_factory=list)
    date: date = field(default_factory=date.today)
    
    def add_task(self, task: Task) -> None:
        """Add a task to the calendar."""
        pass
    
    def remove_task(self, task_id: int) -> None:
        """Remove a task from the calendar by ID."""
        pass
    
    def clear_tasks(self) -> None:
        """Clear all tasks from the calendar."""
        pass
    
    def get_tasks(self) -> List[Task]:
        """Return all tasks in the calendar."""
        pass
    
    def is_empty(self) -> bool:
        """Check if the calendar has any tasks."""
        pass
    
    def generate_schedule(self, pet: Pet) -> List[Task]:
        """Generate an ordered schedule for the pet based on conditions and priorities."""
        pass
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by its ID."""
        pass


class Owner:
    """Represents a pet owner."""
    
    def __init__(self, name: str, contact_info: str = "", preferences: Optional[Dict] = None):
        self.name = name
        self.contact_info = contact_info
        self.pets: List[Pet] = []
        self.preferences = preferences or {}
    
    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's collection."""
        pass
    
    def remove_pet(self, pet_id: int) -> None:
        """Remove a pet by ID."""
        pass
    
    def get_pets(self) -> List[Pet]:
        """Return all pets owned by this owner."""
        pass
    
    def create_schedule(self, calendar: Calendar) -> None:
        """Create a schedule using the calendar for the owner's pets."""
        pass
