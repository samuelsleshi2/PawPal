import streamlit as st
from datetime import date, timedelta
from pawpal_system import Pet, Task, Calendar, Scheduler, Owner

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")

st.markdown(
    """
An intelligent pet care planning assistant that helps you schedule daily pet care tasks 
optimally based on priority, time constraints, and your pet's needs.
"""
)

with st.expander("About PawPal+", expanded=False):
    st.markdown(
        """
**PawPal+** helps you organize pet care tasks intelligently:

- **Smart Scheduling** — Organizes tasks by priority and fits them into your available time
- **Chronological Display** — Shows all tasks in time order for easy reading
- **Conflict Detection** — Alerts you to simultaneous tasks (critical for same pet, warnings for different pets)
- **Recurring Tasks** — Automatically manages daily and weekly recurring tasks
- **Time Preferences** — Respects morning/afternoon/evening task preferences
"""
    )

st.divider()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if "pets" not in st.session_state:
    st.session_state.pets = {}
if "calendar" not in st.session_state:
    st.session_state.calendar = Calendar()
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

# ============================================================================
# SIDEBAR: PET MANAGEMENT
# ============================================================================
with st.sidebar:
    st.header("🐾 Pet Management")
    
    pet_name_input = st.text_input("Pet name", placeholder="e.g., Mochi")
    col1, col2 = st.columns(2)
    with col1:
        species = st.selectbox("Species", ["dog", "cat", "rabbit", "hamster", "other"])
    with col2:
        pet_age = st.number_input("Age (years)", min_value=1, max_value=30, value=3)
    
    col1, col2 = st.columns(2)
    with col1:
        hunger = st.slider("Hunger level", 0, 100, 50)
    with col2:
        tiredness = st.slider("Tiredness level", 0, 100, 50)
    
    if st.button("➕ Add Pet", use_container_width=True):
        if pet_name_input:
            pet_id = len(st.session_state.pets) + 1
            new_pet = Pet(
                pet_id=pet_id,
                name=pet_name_input,
                species=species,
                age=pet_age,
                hunger_level=hunger,
                tiredness_level=tiredness
            )
            st.session_state.pets[pet_id] = new_pet
            st.success(f"✓ {pet_name_input} added!")
            st.rerun()
        else:
            st.error("Please enter a pet name")
    
    st.divider()
    
    if st.session_state.pets:
        st.subheader("Your Pets")
        for pet_id, pet in st.session_state.pets.items():
            with st.expander(f"🐾 {pet.name} ({pet.species})", expanded=False):
                st.write(f"**Age:** {pet.age} years")
                st.write(f"**Hunger:** {pet.hunger_level}%")
                st.write(f"**Tiredness:** {pet.tiredness_level}%")
                st.write(f"**Health:** {pet.health_status}")
                if st.button(f"Remove {pet.name}", key=f"remove_pet_{pet_id}", use_container_width=True):
                    del st.session_state.pets[pet_id]
                    st.rerun()

# ============================================================================
# MAIN: TASK MANAGEMENT
# ============================================================================
tab1, tab2, tab3 = st.tabs(["📋 Tasks", "📅 Schedule", "🔍 Analysis"])

# ============================================================================
# TAB 1: TASK MANAGEMENT
# ============================================================================
with tab1:
    if not st.session_state.pets:
        st.info("👈 Add a pet first using the sidebar to start creating tasks!")
    else:
        st.subheader("Create a New Task")
        
        col1, col2 = st.columns(2)
        with col1:
            selected_pet_id = st.selectbox(
                "Assign to pet",
                options=list(st.session_state.pets.keys()),
                format_func=lambda x: st.session_state.pets[x].name
            )
        with col2:
            task_title = st.text_input("Task title", placeholder="e.g., Morning Walk")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            duration = st.number_input("Duration (min)", min_value=5, max_value=240, value=30)
        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        with col3:
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=1)
        
        col1, col2 = st.columns(2)
        with col1:
            target_condition = st.selectbox(
                "Target condition",
                ["tiredness_level", "hunger_level", "health_status"]
            )
        with col2:
            time_window = st.selectbox(
                "Time preference",
                ["anytime", "morning", "afternoon", "evening"],
                index=0
            )
        
        if st.button("➕ Add Task", use_container_width=True, type="primary"):
            if task_title:
                task_id = len(st.session_state.calendar.tasks) + 1
                new_task = Task(
                    task_id=task_id,
                    title=task_title,
                    description=f"{task_title} for {st.session_state.pets[selected_pet_id].name}",
                    duration_minutes=int(duration),
                    priority=priority,
                    target_condition=target_condition,
                    pet_id=selected_pet_id,
                    frequency=frequency,
                    time_window=time_window,
                    task_date=date.today()
                )
                st.session_state.calendar.add_task(new_task)
                st.success(f"✓ Task '{task_title}' added!")
                st.rerun()
            else:
                st.error("Please enter a task title")
        
        st.divider()
        st.subheader("📝 All Tasks")
        
        if st.session_state.calendar.tasks:
            # Create task display dataframe
            task_data = []
            for task in st.session_state.calendar.tasks:
                pet_name = st.session_state.pets[task.pet_id].name if task.pet_id in st.session_state.pets else "Unknown"
                task_data.append({
                    "ID": task.task_id,
                    "Title": task.title,
                    "Pet": pet_name,
                    "Duration": f"{task.duration_minutes} min",
                    "Priority": task.priority.upper(),
                    "Frequency": task.frequency,
                    "Window": task.time_window,
                    "Status": task.status
                })
            
            st.table(task_data)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear All Tasks", use_container_width=True):
                    st.session_state.calendar.clear_tasks()
                    st.rerun()
            with col2:
                filter_status = st.selectbox("Filter by status", ["all", "pending", "completed", "skipped"])
                if filter_status != "all":
                    filtered = st.session_state.calendar.filter_tasks_by_status(filter_status)
                    st.caption(f"Showing {len(filtered)} {filter_status} task(s)")
        else:
            st.info("No tasks yet. Create one above!")

# ============================================================================
# TAB 2: SCHEDULE GENERATION
# ============================================================================
with tab2:
    if not st.session_state.pets:
        st.info("👈 Add a pet first using the sidebar to generate a schedule!")
    elif not st.session_state.calendar.tasks:
        st.info("Please add tasks first (see Tasks tab)")
    else:
        st.subheader("🗓️ Generate Daily Schedule")
        
        col1, col2 = st.columns(2)
        with col1:
            selected_pet = st.selectbox(
                "Generate schedule for",
                options=list(st.session_state.pets.keys()),
                format_func=lambda x: st.session_state.pets[x].name
            )
        with col2:
            available_hours = st.number_input("Available time (hours)", min_value=1, max_value=24, value=8)
        
        available_minutes = available_hours * 60
        
        if st.button("📅 Generate Schedule", use_container_width=True, type="primary"):
            pet = st.session_state.pets[selected_pet]
            
            # Generate schedule using Scheduler
            scheduled_tasks = st.session_state.scheduler.generate_schedule(
                pet,
                st.session_state.calendar.tasks,
                available_minutes
            )
            
            if scheduled_tasks:
                # Sort tasks by time for display
                sorted_tasks = st.session_state.scheduler.sort_by_time(scheduled_tasks)
                
                st.success(f"✓ Schedule generated for {pet.name} ({available_hours} hours available)")
                
                # Detect conflicts
                warnings = st.session_state.scheduler.detect_simultaneous_tasks(sorted_tasks)
                
                if warnings:
                    st.divider()
                    st.subheader("⚠️ Schedule Conflicts Detected")
                    for warning in warnings:
                        if warning['severity'] == 'critical':
                            st.error(warning['warning'])
                        else:
                            st.warning(warning['warning'])
                
                st.divider()
                st.subheader("📋 Scheduled Tasks (Chronological Order)")
                
                # Prepare schedule table
                schedule_data = []
                for task in sorted_tasks:
                    if task.scheduled_time is not None:
                        hours = task.scheduled_time // 60
                        minutes = task.scheduled_time % 60
                        time_str = f"{hours:02d}:{minutes:02d}"
                        end_time_minutes = task.scheduled_time + task.duration_minutes
                        end_hours = end_time_minutes // 60
                        end_mins = end_time_minutes % 60
                        end_str = f"{end_hours:02d}:{end_mins:02d}"
                    else:
                        time_str = "—"
                        end_str = "—"
                    
                    pet_name = st.session_state.pets[task.pet_id].name if task.pet_id in st.session_state.pets else "Unknown"
                    
                    schedule_data.append({
                        "Time": time_str,
                        "Task": task.title,
                        "Pet": pet_name,
                        "Duration": f"{task.duration_minutes} min",
                        "Priority": task.priority.upper(),
                        "Status": task.status
                    })
                
                st.table(schedule_data)
                
                # Summary statistics
                st.divider()
                col1, col2, col3, col4 = st.columns(4)
                
                scheduled_count = sum(1 for t in sorted_tasks if t.scheduled_time is not None)
                skipped_count = sum(1 for t in sorted_tasks if t.status == "skipped")
                total_time = sum(t.duration_minutes for t in sorted_tasks if t.scheduled_time is not None)
                
                with col1:
                    st.metric("📅 Scheduled", scheduled_count)
                with col2:
                    st.metric("⏭️ Skipped", skipped_count)
                with col3:
                    st.metric("⏱️ Total Time", f"{total_time} min")
                with col4:
                    utilization = (total_time / available_minutes * 100) if available_minutes > 0 else 0
                    st.metric("📊 Utilization", f"{utilization:.1f}%")
            else:
                st.error("No tasks could be scheduled for this pet.")

# ============================================================================
# TAB 3: ANALYSIS & INSIGHTS
# ============================================================================
with tab3:
    st.subheader("📊 System Analysis")
    
    if st.session_state.pets and st.session_state.calendar.tasks:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🐾 Pets", len(st.session_state.pets))
        with col2:
            st.metric("📋 Total Tasks", len(st.session_state.calendar.tasks))
        with col3:
            total_time = sum(t.duration_minutes for t in st.session_state.calendar.tasks)
            st.metric("⏱️ Total Time", f"{total_time} min")
        
        st.divider()
        
        st.subheader("📈 Task Breakdown by Priority")
        priority_counts = {"high": 0, "medium": 0, "low": 0}
        for task in st.session_state.calendar.tasks:
            priority_counts[task.priority] += 1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔴 High Priority", priority_counts["high"])
        with col2:
            st.metric("🟡 Medium Priority", priority_counts["medium"])
        with col3:
            st.metric("🟢 Low Priority", priority_counts["low"])
        
        st.divider()
        
        st.subheader("🔄 Task Frequency Distribution")
        freq_counts = {"once": 0, "daily": 0, "weekly": 0}
        for task in st.session_state.calendar.tasks:
            if task.frequency in freq_counts:
                freq_counts[task.frequency] += 1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Once", freq_counts["once"])
        with col2:
            st.metric("Daily", freq_counts["daily"])
        with col3:
            st.metric("Weekly", freq_counts["weekly"])
        
        st.divider()
        
        st.subheader("🎯 Sorting Demonstration")
        if st.session_state.calendar.tasks:
            # Assign some sample times for demonstration
            demo_tasks = st.session_state.calendar.tasks.copy()
            for i, task in enumerate(demo_tasks):
                if task.scheduled_time is None:
                    task.scheduled_time = (360 + i * 100) % 1440  # Distribute across day
            
            st.caption("Tasks sorted by scheduled time (chronological order):")
            sorted_demo = st.session_state.scheduler.sort_by_time(demo_tasks)
            
            demo_data = []
            for task in sorted_demo:
                if task.scheduled_time is not None:
                    hours = task.scheduled_time // 60
                    minutes = task.scheduled_time % 60
                    time_str = f"{hours:02d}:{minutes:02d}"
                else:
                    time_str = "Unscheduled"
                
                pet_name = st.session_state.pets[task.pet_id].name if task.pet_id in st.session_state.pets else "Unknown"
                demo_data.append({
                    "Time": time_str,
                    "Task": task.title,
                    "Pet": pet_name,
                    "Duration": f"{task.duration_minutes} min"
                })
            
            st.table(demo_data)
        
    else:
        st.info("Add pets and tasks to see analysis.")

st.divider()
st.caption("🐾 PawPal+ — Intelligent pet care scheduling | v1.0")
