'''
This file is the core of the system application.
It manages different task objects,
Handles task storage, adding and updating
Computes recommendations based on parameters

Key concepts and tools used:
- JSON file handling
- Lists and iteration
- Scoring and sorting algorithms
- Error handling (try/except) mechanisms
- Time logging
- Weighted scoring
'''

import json
# Library used to store, transfer and load data to and from a server
# Stores tasks permanently and maintains data between sessions
from task import Task
# imports the created Task class
from datetime import datetime
# Library used for real time

class TaskManager:
# For JSON file storage

    def __init__(self, file="data.json", log_file="completed.json"):
    # initiates file paths and loads all tasks

        self.file = file
        self.log_file = log_file
        self.tasks = self.load_tasks()
        self.completed_log = self.load_completed()

    def load_tasks(self):
    # loads, reads and converts JSON file

        try:
            with open(self.file, "r") as f:
                data = json.load(f)
                return [Task.from_dict(t) for t in data]
        except:
            return []

    def save_tasks(self):
    # converts and writes task to JSON

        with open(self.file, "w") as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=4)

    def load_completed(self):
    # loads, reads and converts JSON file
        try:
            with open(self.log_file, "r") as f:
                return json.load(f)
        except:
            return []

    def save_completed(self):
        # converts and writes completed task to JSON

        with open(self.log_file, "w") as f:
            json.dump(self.completed_log, f, indent=4)

    def add_task(self, task):
    # checks for valid input (error handling)
    # Adds new task and saves data

        if any(t.name == task.name for t in self.tasks):
            return False, "Task with this name already exists"

        if task.deadline < datetime.now():
            return False, "Deadline cannot be in the past"

        self.tasks.append(task)
        self.save_tasks()
        return True, "Task added successfully!"

    def update_task(self, original_name, updated_task):
    # Replaces an existing task by the edited version of itself

        for i, task in enumerate(self.tasks):
            if task.name == original_name:
                self.tasks[i] = updated_task
                self.save_tasks()
                return True
        return False

    def complete_task(self, name):
    # Removes the tasks from the to-do list
    # Logs completion time of the task to use for statistics

        for task in self.tasks:
            if task.name == name:
                self.tasks.remove(task)
                self.completed_log.append({
                    "completion_hour": datetime.now().hour,
                    "energy": task.energy
                })
                self.save_tasks()
                self.save_completed()
                return

    def get_recommendations(self, user_energy, available_time):
    # Assigns a score to each task using a formula based on their parameters
    # Sorts them in descending order
        results = []

        for task in self.tasks:
            score = 0

            # DEADLINE (most important)
            days_left = (task.deadline - datetime.now()).days

            if days_left <= 0:
                deadline_score = 50  # overdue → VERY urgent
            else:
                deadline_score = max(0, 40 - days_left * 2)

            # PRIORITY
            priority_score = task.priority * 10

            # TIME FIT
            if task.remaining_time <= available_time:
                time_score = 15
            else:
                time_score = -10

            # ENERGY (least important)
            energy_diff = abs(task.energy - user_energy)
            energy_score = max(0, 10 - energy_diff * 2)

            # FINAL SCORE (weighted sum)
            score = (
                    deadline_score +
                    priority_score +
                    time_score +
                    energy_score
            )

            # Encourages finishing started tasks over starting new ones
            if task.started:
                score += 5

            results.append((task, score))

        results.sort(key=lambda x: x[1], reverse=True)
        # Ranking algorithm
        return results