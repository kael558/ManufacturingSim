from enum import Enum
import numpy as np





'''
processor
 - type
 - index
 - state (blocked, processing/inspecting)
 - buffer 
 - receivers
'''


class Type(Enum):
    Workstation = "W"
    Inspector = "I"
    Product = "P"


class State(Enum):
    Blocked = "B" #inspector waiting for receiver opening, workstation waiting for components

class Task:
    def __init__(self, processor, components):
        self.time = np.random.normal(loc=500 if processor.type else 100,
                                     scale=10 if processor.isWorkstation else 5)
        self.processor = processor
        self.components = components

class TaskQueue:
    def __init__(self):
        self.tasks = []

    def next_task(self):



class Processor:
    def __init__(self, index: int, buffers: dict, receivers: list):
        self.index = index
        self.buffers = buffers
        self.receivers = receivers
        self.blocked = False

    def is_blocked(self):
        return self.blocked

    def is_free(self):
        return not self.blocked

    def block(self):
        self.blocked = True

    def free(self):
        self.blocked = False

    def has_components(self):
        return all(buffer > 0 for buffer in self.buffers.values())


class Component(Enum):
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"

class Workstation(Processor):
    def __str__(self):
        return "Inspector " + str(self.index) + ":"

    def use_components(self):
        if self.index == 2:
            return [Component.C2 if np.random.random() < 0.5 else Component.C3]
        return Component.C1

class Inspector(Processor):
    def __str__(self):
        return "Inspector " + str(self.index) + ":"

    def use_components(self):
        lst = []
        for component in self.buffers.keys():
            self.buffers[component] -= 1
            lst.append(component)
        return lst

if __name__ == "__main__":
    infinity = 99999999
    taskQueue = TaskQueue()
    W1 = Workstation(1, {Component.C1: 0}, [0])
    W2 = Workstation(2, {Component.C1: 0, Component.C2: 0}, [0])
    W3 = Workstation(3, {Component.C1: 0, Component.C3: 0}, [0])

    I1 = Inspector(1, {Component.C1: infinity}, [W1, W2, W3])
    I2 = Inspector(2, {Component.C2: infinity, Component.C3: infinity}, [W2, W3])

    def attempt_start_task(taskQueue, processor):
        if processor.is_free() and processor.has_components():
            task = Task(processor, processor.use_components())
            processor.block()
            taskQueue.add_task(task)

    attempt_start_task(taskQueue, I1)
    attempt_start_task(taskQueue, I2)

    while True:

        for processor in processorList:
            if processor.is_blocked():
                processor.attempt_work()
