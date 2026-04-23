'''
This file managed the user interface of the application system,
Makes it organised into windows,
Produces a smooth and intuitive UX,
Makes the interface interactable
'''
import streamlit as st
# Python library used to build web apps
from task_manager import TaskManager
# Imports TaskManager class
from task import Task
# Imports Task class
import matplotlib.pyplot as plt
# Python library to create graphs and plots

manager = TaskManager()

st.set_page_config(page_title="Smart To-Do", layout="wide")

st.title("🧠 Smart Context-Aware To-Do List")

menu = st.sidebar.radio("Navigation", [
    "➕ Add Task",
    "📋 View Tasks",
    "🔥 Recommendations",
    "🔍 Search",
    "📊 Statistics"
])

# ---------- ADD TASK ----------
if menu == "➕ Add Task":
    st.header("Add New Task")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Task name")
        energy = st.slider("Energy (1-5)", 1, 5)
        priority = st.slider("Priority (1-5)", 1, 5)

    with col2:
        time_required = st.number_input("Time (minutes)", min_value=1)
        deadline = st.date_input("Deadline")
        location = st.selectbox("Location", ["home", "outside", "both"])

    if st.button("Add Task"):
        if not name.strip():
            st.error("Task must have a name")
        elif time_required <= 0:
            st.error("Time must be positive")
        else:
            task = Task(name, energy, priority, time_required, str(deadline), location)
            success, msg = manager.add_task(task)

            if success:
                st.success(msg)
            else:
                st.error(msg)

# ---------- VIEW TASKS ----------
elif menu == "📋 View Tasks":
    st.header("Your Tasks")

    if not manager.tasks:
        st.warning("You have no pending tasks! Enjoy your free time!")
    else:
        for i, task in enumerate(manager.tasks):
            with st.expander(f"{task.name} ({'Started' if task.started else 'Not Started'})"):

                # DISPLAY TASK
                st.markdown(f"""
                🔋 **Energy:** {task.energy}  
                ⭐ **Priority:** {task.priority}  
                ⏱ **Time Left:** {task.remaining_time} min  
                📅 **Deadline:** {task.deadline.date()}  
                📍 **Location:** {task.location}  
                📌 **Status:** {"Started" if task.started else "Not Started"}
                """)

                col1, col2 = st.columns(2)

                # START TASK
                with col1:
                    if not task.started:
                        remaining_time = st.number_input(
                            f"Remaining time for {task.name}",
                            min_value=1,
                            value=task.remaining_time,
                            key=f"remain_{i}"
                        )

                        if st.button(f"Start {task.name}", key=f"start_{i}"):
                            task.start_task(remaining_time)
                            manager.save_tasks()
                            st.success("Task started!")
                            st.rerun()

                # COMPLETE TASK
                with col2:
                    if st.button(f"Complete {task.name}", key=f"complete_{i}"):
                        manager.complete_task(task.name)
                        st.success("Task completed!")
                        st.rerun()

                # ---------- EDIT TASK ----------
                if st.checkbox(f"Edit {task.name}", key=f"edit_{i}"):

                    st.subheader("Edit Task")

                    new_energy = st.slider(
                        f"Energy for {task.name}",
                        1, 5,
                        value=task.energy,
                        key=f"energy_{i}"
                    )

                    new_priority = st.slider(
                        f"Priority for {task.name}",
                        1, 5,
                        value=task.priority,
                        key=f"priority_{i}"
                    )

                    new_time = st.number_input(
                        f"Time (minutes) for {task.name}",
                        min_value=1,
                        value=task.remaining_time,
                        key=f"time_{i}"
                    )

                    new_deadline = st.date_input(
                        f"Deadline for {task.name}",
                        value=task.deadline.date(),
                        key=f"deadline_{i}"
                    )

                    new_location = st.selectbox(
                        f"Location for {task.name}",
                        ["home", "outside", "both"],
                        index=["home", "outside", "both"].index(task.location),
                        key=f"location_{i}"
                    )

                    if st.button(f"Save changes for {task.name}", key=f"save_{i}"):

                        updated_task = Task(
                            task.name,
                            new_energy,
                            new_priority,
                            new_time,
                            str(new_deadline),
                            new_location
                        )

                        # preserve status + remaining time
                        updated_task.started = task.started
                        updated_task.remaining_time = new_time

                        manager.update_task(task.name, updated_task)

                        st.success("Task updated!")
                        st.rerun()

# ---------- RECOMMENDATIONS ----------
elif menu == "🔥 Recommendations":
    st.header("Smart Recommendations")

    # FILTER BY ENERGY, TIME AND LOCATION

    user_energy = st.slider("Your energy level", 1, 5)
    available_time = st.number_input("Available time (minutes)", min_value=1)
    user_location = st.selectbox(
        "Location?",
        ["home", "outside", "both"]
    )

    if st.button("Get Recommendation"):
        all_results = manager.get_recommendations(user_energy, available_time)

        # FILTER BY LOCATION
        filtered_results = []

        for task, score in all_results:
            if user_location == "home":
                if task.location in ["home", "both"]:
                    filtered_results.append((task, score))

            elif user_location == "outside":
                if task.location in ["outside", "both"]:
                    filtered_results.append((task, score))

            else:  # "both"
                filtered_results.append((task, score))

        if not filtered_results:
            st.error("No tasks available")
        else:
            best = filtered_results[0][0]

            st.success(f"🔥 Best Task: {best.name}")
            st.info(
                f"Time left: {best.remaining_time} min | "
                f"Energy: {best.energy} | "
                f"{'Started' if best.started else 'Not started'}"
            )

            st.subheader("Other Good Options")
            for task, score in filtered_results[1:4]:
                st.write(f"{task.name} | Time: {task.remaining_time} min | Score: {score}")

# ---------- SEARCH ----------
elif menu == "🔍 Search":
    st.header("Search Tasks")

    keyword = st.text_input("Search")

    if keyword:
        found = [t for t in manager.tasks if keyword.lower() in t.name.lower()]

        if not found:
            st.warning("No matching tasks")
        else:
            for task in found:
                st.markdown(f"""
                ### 📝 {task.name}

                🔋 **Energy:** {task.energy}  
                ⭐ **Priority:** {task.priority}  
                ⏱ **Time Left:** {task.remaining_time} min  
                📅 **Deadline:** {task.deadline.date()}  
                📍 **Location:** {task.location}  
                📌 **Status:** {"Started" if task.started else "Not Started"}

                ---
                """)

# ---------- STATISTICS ----------
elif menu == "📊 Statistics":
    st.header("Task Completion Insights")

    if not manager.completed_log:
        st.warning("No completed tasks yet")
    else:
        hours = [entry["completion_hour"] for entry in manager.completed_log]
        energies = [entry["energy"] for entry in manager.completed_log]

        fig1, ax1 = plt.subplots()
        ax1.hist(hours, bins=24)
        ax1.set_title("Tasks Completed by Hour")
        ax1.set_xlabel("Hour")
        ax1.set_ylabel("Tasks")
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots()
        ax2.scatter(energies, hours)
        ax2.set_title("Energy vs Completion Time")
        ax2.set_xlabel("Energy")
        ax2.set_ylabel("Hour")
        st.pyplot(fig2)