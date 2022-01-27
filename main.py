from enum import Enum

import numpy as np


class Component(Enum):
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"


class Processor:
    def __init__(self, index: int, buffers: dict):
        """
        The superclass for machine-like thing that inspects/processes things
        :param index: the index of the processor (e.g. 1 for I1, 3 for W3)
        :param buffers: a dictionary where keys are components and values are the numbers of respective component
        """
        self.index = index
        self.buffers = buffers
        self.blocked = False

    def is_free(self):
        return not self.blocked

    def block(self):
        self.blocked = True

    def free(self):
        self.blocked = False

    def get_num_components(self, component):
        return self.buffers[component]

    def add_component(self, component):
        self.buffers[component] += 1

    def has_components(self):
        return all(buffer > 0 for buffer in self.buffers.values())

    def get_components(self):
        lst = []
        for component in self.buffers.keys():
            self.buffers[component] -= 1
            lst.append(component)
        return lst

    def __str__(self):
        pass

    def name(self):
        pass


class Workstation(Processor):
    counter = 0

    def __str__(self):
        state = "free" if self.is_free() else "processing or blocked"
        return f"Workstation {self.index} is {state}. Buffer: {self.buffers}"

    def name(self):
        return f"Workstation {self.index}"

    def is_full(self):
        return all(buffer == 2 for buffer in self.buffers.values())


class Inspector(Processor):
    def __str__(self):
        state = "free" if self.is_free() else "inspecting or blocked"
        return f"Inspector {self.index} is {state}."

    def name(self):
        return f"Inspector {self.index}"

    def get_components(self):
        if self.index == 2:
            return [Component.C2 if np.random.random() < 0.5 else Component.C3]
        return super().get_components()


def partition(lst, predicate):
    """
    helper method to separate lst into two lists based on predicate
    :param lst: the initial list
    :param predicate: the separation predicate
    :return: the two lists
    """
    lst1, lst2 = [], []
    for elem in lst:
        if predicate(elem):
            lst1.append(elem)
        else:
            lst2.append(elem)
    return lst1, lst2


class Task:
    def __init__(self, processor: Processor, components: list):
        """
        Obj that wraps processor with time to process/inspect to components.
        :param processor: either a workstation or an inspector
        :param components: the components that the processor works with
        """
        # TODO time to inspect/process should be taken from fitted gaussians from data provided.
        self.time = np.random.normal(loc=500 if isinstance(processor, Workstation) else 100,
                                     scale=10 if isinstance(processor, Workstation) else 5)
        self.processor = processor
        self.components = components

    def is_finishable(self):
        """
        Check to see if product can actually go somewhere
        :return:
        """
        if isinstance(self.processor, Workstation):
            return True
        component = self.components[0]  # inspectors only have 1 component
        workstations = routing[component]
        return not all(workstation.get_num_components(component) == 2 for workstation in workstations)

    def finish(self):
        """
        Finishes a Task by sending the product to the appropriate place
        :return:
        """
        if isinstance(self.processor, Workstation):
            # TODO That second item in the first f-string looks wrong maybe(?)
            print(f"Workstation {self.processor.index}: produced Product {self.processor.index}")
            self.processor.counter += 1
            print(f"It has produced {self.processor.counter} products thus far.")
        else:
            component = self.components[0]  # inspectors only have 1 component
            # getting the minimum number of components
            min_num_components = min(routing[component], key=lambda w: w.get_num_components(component)) \
                .get_num_components(component)

            # getting all the workstations with the minimum number of components
            workstations = list(filter(lambda w: w.get_num_components(component) == min_num_components,
                                       routing[component]))

            # choose a random workstation from that list
            workstation = np.random.choice(workstations)

            # send the component there
            workstation.add_component(component)
            print(f"{self.processor.name()}: sent component {component.value} to {workstation.name()}")
        self.processor.free()  # free the processor to be used again

    def __str__(self):
        """
        :return: the str representation of the task
        """
        if isinstance(self.processor, Workstation):
            return f"{self.processor.name()} needs {self.time} to process " + \
                   ",".join(map(str, self.components))
        return f"{self.processor.name()} needs {self.time} to inspect " + \
               ",".join(map(str, self.components))


class TaskQueue:
    def __init__(self):
        """
        tasks: a list of Task objects sorted by time remaining to complete the task
        blockedTasks: a list of Task objects that are blocked from sending their product
        """
        self.tasks = []
        self.blockedTasks = []

    def attempt_complete_task(self):
        """
        Attempts to complete the next task. It may be blocked, so it may be placed in a blockedTask list instead.
        """
        if len(self.tasks) == 0:
            return

        time_taken = self.tasks[0].time
        for task in self.tasks:
            task.time = max(task.time - time_taken, 0)  # update the time for all other tasks

        #  get the finished tasks
        finished_tasks, self.tasks = partition(self.tasks, lambda t: t.time == 0.0)

        #  finish or block the tasks
        for task in finished_tasks:
            if task.is_finishable():
                task.finish()
            else:
                self.blockedTasks.append(task)

    def attempt_blocked_tasks(self):
        """
        check to see if blocked tasks can be completed and finish them.
        :return: the processors that finished their task
        """
        finished_tasks, self.blockedTasks = partition(self.blockedTasks, lambda t: t.is_finishable())
        for task in finished_tasks:
            task.finish()
        return [task.processor for task in finished_tasks]

    def add_task(self, new_task: Task):
        """
        places a new task in the appropriate place in the task list
        :param new_task: the new task to be added
        """
        for i, _ in enumerate(self.tasks):  # cant be arsed to do binary search
            if new_task.time < self.tasks[i].time:
                self.tasks.insert(i, new_task)
                break
        else:
            self.tasks.append(new_task)

    def __str__(self):
        """
        :return: the str representation of the taskqueue
        """
        return "\n--State of tasks--\n" + "\n".join(map(str, self.tasks)) + \
               ("\n--State of blocked tasks--\n" + "\n".join(map(str, self.blockedTasks)) if len(
                   self.blockedTasks) > 0 else "")


global routing
if __name__ == '__main__':
    infinity = 9999999  # its over 9000 so its basically infinity

    task_queue = TaskQueue()
    W1 = Workstation(1, {Component.C1: 0})
    W2 = Workstation(2, {Component.C1: 0, Component.C2: 0})
    W3 = Workstation(3, {Component.C1: 0, Component.C3: 0})

    I1 = Inspector(1, {Component.C1: infinity})
    I2 = Inspector(2, {Component.C2: infinity, Component.C3: infinity})

    processors = [I1, I2, W1, W2, W3]

    # global variable routing for components to workstations
    routing = {Component.C1: [W1, W2, W3], Component.C2: [W2], Component.C3: [W3]}


    def attempt_start_task(processor_curr: Processor):
        """
        helper method to try and create a task is possible
        :param processor_curr: either the workstation or inspector
        """
        if processor_curr.is_free() and processor_curr.has_components():
            task = Task(processor_curr, processor_curr.get_components())
            processor_curr.block()
            task_queue.add_task(task)


    while True:
        # attempt to start tasks
        for processor in processors:
            attempt_start_task(processor)

        # this part ensures if a workstation finishes a product, a blocked inspector will send a component right away
        free_processors = task_queue.attempt_blocked_tasks()  # get the processors from finished tasks that were blocked
        for processor in free_processors:
            attempt_start_task(processor)

        print(task_queue)
        print("--State of processors--")
        print("\n".join(list(map(str, processors))))

        print("\n--Tasks Completed--")
        task_queue.attempt_complete_task()  # goto and finish the next task
