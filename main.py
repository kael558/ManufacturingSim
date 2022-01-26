from enum import Enum
import numpy as np


class Inspector(Enum):
    I1 = "I1"
    I2 = "I2"


class Workstation(Enum):
    W1 = "W1"
    W2 = "W2"
    W3 = "W3"


class Component(Enum):
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"


class Product(Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


def partition(lst, predicate):
    lst1, lst2 = [], []
    for elem in lst:
        if predicate(elem):
            lst1.append(elem)
        else:
            lst2.append(elem)
    return lst1, lst2


class TaskQueue:
    def __init__(self):
        self.tasks = []
        self.blockedTasks = []

    def attempt_complete_task(self):
        if len(self.tasks) == 0:
            return

        time_taken = self.tasks[0].time
        for task in self.tasks:
            task.time = max(task.time - time_taken, 0)

        finished_tasks, self.tasks = partition(self.tasks, lambda t: t.time == 0.0)

        for task in finished_tasks:
            if task.is_finishable():
                task.finish()
            else:
                self.blockedTasks.append(task)

    def attempt_blocked_tasks(self):
        finished_tasks, self.blockedTasks = partition(self.blockedTasks, lambda t: t.is_finishable())
        for task in finished_tasks:
            task.finish()
        return len(finished_tasks) > 0

    def add_task(self, new_task):
        for i in range(len(self.tasks)):  # cant be arsed to do binary search
            if new_task.time < self.tasks[i].time:
                self.tasks.insert(i, new_task)
                break
        else:
            self.tasks.append(new_task)

    def __str__(self):
        return "\n--State of tasks--\n" + "\n".join(map(str, self.tasks)) + \
               ("\n--State of blocked tasks--\n" + "\n".join(map(str, self.blockedTasks)) if len(
                   self.blockedTasks) > 0 else "")


class Task:
    def __init__(self, processor, components):
        self.time = np.random.normal(loc=500 if processor.isWorkstation else 100,
                                     scale=10 if processor.isWorkstation else 5)
        self.processor = processor
        self.components = components

    def finish(self):
        if self.processor.isWorkstation:
            print(self.processor.name, ": produced product")
        else:
            if self.processor.name == Inspector.I1:
                min_component_workstation = min(self.processor.receivers.values(),
                                                key=lambda w: w.get_num_components(Component.C1))
                min_component_workstation.add_component(self.components[0])
                print(self.processor.name, ": sent component C1 to " + str(min_component_workstation))
            else:
                if self.components[0] == Component.C2:
                    self.processor.receivers[Workstation.W2].add_component(self.components[0])
                    print(self.processor.name, ": sent component C2 to " + str(Workstation.W2))
                else:
                    self.processor.receivers[Workstation.W3].add_component(self.components[0])
                    print(self.processor.name, ": sent component C3 to " + str(Workstation.W3))
        self.processor.free()

    def is_finishable(self):
        if self.processor.isWorkstation:
            return True

        if self.processor.name == Inspector.I1:
            return not all(receiver.is_full() for receiver in self.processor.receivers.values())

        if self.components[0] == Component.C2:
            return self.processor.receivers[Workstation.W2].get_num_components(self.components[0]) != 2

        return self.processor.receivers[Workstation.W3].get_num_components(self.components[0]) != 2

    def __str__(self):
        if self.processor.isWorkstation:
            return str(self.processor.name) + " needs " + str(self.time) + " to process " + \
                   ",".join(map(str, self.components))

        return str(self.processor.name) + " needs " + str(self.time) + " to complete " + \
               ",".join(map(str, self.components))


class Processor:
    def __init__(self, name, buffers, receivers):
        self.blocked = False
        self.name = name
        self.buffers = buffers
        self.isWorkstation = str(name).startswith("W")
        self.receivers = receivers

    def __str__(self):
        return str(self.name)

    def is_free(self):
        return not self.blocked

    def block(self):
        self.blocked = True

    def free(self):
        self.blocked = False

    def is_full(self):
        return all(buffer == 2 for buffer in self.buffers.values())

    def get_num_components(self, component):
        return self.buffers[component]

    def add_component(self, component):
        self.buffers[component] += 1

    def has_components(self):
        return all(buffer > 0 for buffer in self.buffers.values())

    def get_components(self):
        if self.name == Inspector.I2:
            return [Component.C2 if np.random.random() < 0.5 else Component.C3]

        lst = []
        for component in self.buffers.keys():
            self.buffers[component] -= 1
            lst.append(component)
        return lst

    def get_string_state(self):
        if self.isWorkstation:
            if self.is_free():
                return str(self.name) + " is blocked. Buffer: " + str(self.buffers)
            else:
                return str(self.name) + " is processing. Buffer: " + str(self.buffers)

        return str(self.name) + " is inspecting."


if __name__ == '__main__':
    infinity = 9999999

    taskqueue = TaskQueue()
    W1 = Processor(Workstation.W1, {Component.C1: 0}, {Product.P1: 0})
    W2 = Processor(Workstation.W2, {Component.C1: 0, Component.C2: 0}, {Product.P2: 0})
    W3 = Processor(Workstation.W3, {Component.C1: 0, Component.C3: 0}, {Product.P3: 0})

    I1 = Processor(Inspector.I1, {Component.C1: infinity}, {Workstation.W1: W1, Workstation.W2: W2, Workstation.W3: W3})
    I2 = Processor(Inspector.I2, {Component.C2: infinity, Component.C3: infinity},
                   {Workstation.W2: W2, Workstation.W3: W3})


    def attempt_start_task(processor):
        if processor.is_free() and processor.has_components():
            task = Task(processor, processor.get_components())
            processor.block()
            taskqueue.add_task(task)


    while True:
        print("\n--Tasks Completed--")
        taskqueue.attempt_complete_task()

        attempt_start_task(I1)
        attempt_start_task(I2)
        attempt_start_task(W1)
        attempt_start_task(W2)
        attempt_start_task(W3)
        if taskqueue.attempt_blocked_tasks():
            attempt_start_task(I1)
            attempt_start_task(I2)
            attempt_start_task(W1)
            attempt_start_task(W2)
            attempt_start_task(W3)

        print(taskqueue)
        print("--State of processors--")
        print(I1.get_string_state())
        print(I2.get_string_state())
        print(W1.get_string_state())
        print(W2.get_string_state())
        print(W3.get_string_state())
