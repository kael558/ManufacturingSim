from processors import Processor, Workstation, Inspector, Component
from fel import TaskQueue, Task

if __name__ == '__main__':
    infinity = 9999999  # its over 9000 so its basically infinity

    task_queue = TaskQueue()
    W1 = Workstation(1, {Component.C1: 0})
    W2 = Workstation(2, {Component.C1: 0, Component.C2: 0})
    W3 = Workstation(3, {Component.C1: 0, Component.C3: 0})

    I1 = Inspector(1, {Component.C1: infinity}, {Component.C1: [W1, W2, W3]})
    I2 = Inspector(2, {Component.C2: infinity, Component.C3: infinity}, {Component.C2: [W2], Component.C3: [W3]})

    processors = [I1, I2, W1, W2, W3]


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
        task_queue.attempt_complete_task()  # goto future task and finish it
