from processors import Processor, Workstation, Inspector, Component
from fel import TaskQueue, Task

if __name__ == '__main__':
    infinity = 9999999  # its over 9000 so its basically infinity

    task_queue = TaskQueue()
    W1 = Workstation(index=1, buffers={Component.C1: 0}, receiving={})
    W2 = Workstation(index=2, buffers={Component.C1: 0, Component.C2: 0},
                     receiving={})
    W3 = Workstation(index=3, buffers={Component.C1: 0, Component.C3: 0},
                     receiving={})

    I1 = Inspector(index=1, buffers={Component.C1: infinity},
                   receiving={Component.C1: [W1, W2, W3]})
    I2 = Inspector(index=2,
                   buffers={Component.C2: infinity, Component.C3: infinity},
                   receiving={Component.C2: [W2], Component.C3: [W3]})

    processors = [I1, I2, W1, W2, W3]


    def attempt_start_task(processor_curr: Processor):
        """
        helper method to try and create a task is possible
        :param processor_curr: either the workstation or inspector
        """
        if processor_curr.is_free() and processor_curr.has_components():
            task = Task(processor_curr, processor_curr.get_components())
            processor_curr.set_working()
            task_queue.add_task(task)


    time_blocked = [0, 0, 0, 0, 0]
    time_working = [0, 0, 0, 0, 0]
    time_idling = [0, 0, 0, 0, 0]

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
        time_passed = task_queue.attempt_complete_task()  # goto future task and finish it

        for i, processor in processors:
            if processor.is_free():
                time_idling[i] += time_passed
            elif processor.is_working():
                time_working[i] += time_passed
            elif processor.is_blocked():
                time_blocked[i] += time_passed
