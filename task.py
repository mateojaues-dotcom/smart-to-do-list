'''
This file essentially initialises the task class with its attributes,
implements data abstraction, to make understanding less complex,
manages data serialisation and deserialisation for storage and reloading
'''

from datetime import datetime

class Task:
# Task class represents a single task in the system

    def __init__(self, name, energy, priority, time_required, deadline, location):
    # initiates attributes of the Task class

        self.name = name
        self.energy = energy
        self.priority = priority
        self.time_required = time_required
        self.remaining_time = time_required
        self.deadline = datetime.strptime(deadline, "%Y-%m-%d") # deadline is converted into a datetime object
        self.location = location
        self.started = False

    def start_task(self, remaining_time):
    # updates started status to true
    # updates remaining time estimated to complete the task

        self.started = True
        self.remaining_time = remaining_time

    def to_dict(self):
    # converts objects into dictionaries for JSON storage and data serialisation

        return {
            "name": self.name,
            "energy": self.energy,
            "priority": self.priority,
            "time_required": self.time_required,
            "remaining_time": self.remaining_time,
            "deadline": self.deadline.strftime("%Y-%m-%d"),
            "location": self.location,
            "started": self.started
        }

    @staticmethod
    #static methods don't depend on a specific object or instance,
    #are reusable for all instances as it doesn't use self

    def from_dict(data):
    # reverses to_dict(self)
    # converts the dictionary back into an object for deserialisation
    # enables loading back tasks from JSON files

        task = Task(
            data["name"],
            data["energy"],
            data["priority"],
            data["time_required"],
            data["deadline"],
            data["location"]
        )
        task.remaining_time = data["remaining_time"]
        task.started = data["started"]
        return task