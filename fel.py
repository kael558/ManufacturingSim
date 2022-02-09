from processors import Processor, Workstation
from numpy import random


class Task:
    def __init__(self, processor_curr: Processor, components: list):
        """
        Obj that wraps processor with time to process/inspect to components.
        :param processor_curr: either a workstation or an inspector
        :param components: the components that the processor works with
        """
        # TODO time to inspect/process should be taken from fitted distributions of data provided.
        self.time = random.normal(
            loc=500 if isinstance(processor_curr, Workstation) else 100,
            scale=10 if isinstance(processor_curr, Workstation) else 5)
        self.processor = processor_curr
        self.components = components

    def can_be_finished(self):
        """
        Check to see if product can actually go somewhere
        :return:
        """
        if isinstance(self.processor, Workstation):  # workstations can always finish
            return True
        component = self.components[0]  # inspectors only have 1 component

        workstations = self.processor.receiving[component]
        return not all(
            workstation.get_num_components(component) == 2 for workstation in
            workstations)

    def finish(self):
        """
        Finishes a Task by sending the product to the appropriate place
        :return:
        """
        if isinstance(self.processor, Workstation):
            # TODO That second item in the first f-string looks wrong maybe(?)
            print(
                f"Workstation {self.processor.index}: produced Product {self.processor.index}")
            self.processor.counter += 1
            print(
                f"It has produced {self.processor.counter} products thus far.")
        else:
            component = self.components[0]  # inspectors only have 1 component
            # getting the minimum number of components
            min_num_components = min(self.processor.receiving[component],
                                     key=lambda w: w.get_num_components(
                                         component)) \
                .get_num_components(component)

            # getting all the workstations with the minimum number of components
            workstations = list(filter(lambda w: w.get_num_components(
                component) == min_num_components,
                                       self.processor.receiving[component]))

            # choosing the workstation with the lowest index
            workstation = min(workstations, key=lambda w: w.index)

            # send the component there
            workstation.add_component(component)
            print(
                f"{self.processor.name()}: sent component {component.value} to {workstation.name()}")
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


class TaskQueue:
    def __init__(self):
        """
        tasks: a list of Task objects sorted by time remaining to complete the task
        blocked_tasks: a list of Task objects that are blocked from sending their product
        """
        self.tasks = []
        self.blocked_tasks = []

    def attempt_complete_task(self):
        """
        Attempts to complete the next task. It may be blocked, so it may be placed in a blockedTask list instead.
        """
        if len(self.tasks) == 0:
            return

        time_taken = self.tasks[0].time
        for task in self.tasks:
            task.time = max(task.time - time_taken,
                            0)  # update the time for all other tasks

        #  get the finished tasks
        finished_tasks, self.tasks = partition(self.tasks,
                                               lambda t: t.time == 0.0)

        #  finish or block the tasks
        for task in finished_tasks:
            if task.can_be_finished():
                task.finish()
            else:
                self.blocked_tasks.append(task)

    def attempt_blocked_tasks(self):
        """
        check to see if blocked tasks can be completed and finish them.
        :return: the processors that finished their task
        """
        finished_tasks, self.blocked_tasks = partition(self.blocked_tasks, lambda t: t.can_be_finished())
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
        :return: the str representation of the task_queue
        """
        return "\n--State of tasks--\n" + "\n".join(map(str, self.tasks)) + \
               ("\n--State of blocked tasks--\n" + "\n".join(
                   map(str, self.blocked_tasks)) if len(
                   self.blocked_tasks) > 0 else "")
