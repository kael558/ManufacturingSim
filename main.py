from processors import Processor, Workstation, Inspector, Component
from fel import TaskQueue, Task

if __name__ == '__main__':
    infinity = 9999999  # its over 9000 so its basically infinity
    count = 600  # how many products to produce before stopping the simulation
    clock = 0.0

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


    def get_all_produced_count():
        """
        Helper method to determine the total number of products produced
        :return: The total amount of products all workstations have produced
        """
        # Yeah this isn't a great way to do this
        return sum(processors[i].get_count() for i in range(2, 5))


    def attempt_start_task(processor_curr: Processor):
        """
        helper method to try and create a task is possible
        :param processor_curr: either the workstation or inspector
        """
        if processor_curr.is_free() and processor_curr.has_components():
            task = Task(processor_curr, processor_curr.get_components())

            processor_curr.block()
            task_queue.add_task(task)


    def print_simulation_data():
        """
        Helper method to display the quantities of interest for the simulation.
        """
        # Print out Inspector stats
        for i in range(0, 2):
            print(f"I{i + 1}")
            #print(f"Proportion of Time Spent Blocked: {}seconds")

        # Print out Workstation stats
        for i in range(2, 5):
            print(f"W{i - 1}")
            #print(f"\tThroughput: {}products/sec")
            print(f"\tProducts Produced: {processors[i].get_count()}")
            print(
                f"\tProportion of Total Products Produced: {(processors[i].get_count() / count) * 100}%")
            #print(f"\tTime Busy: {}")
            #print(f"\tProportion of Time Spent Busy: {}")

        # Print out Buffer stats

        # Print out total throughput
        print(f"\nOverall Throughput: {get_all_produced_count() / clock}products/sec")


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
        clock = task_queue.attempt_complete_task(clock)  # goto future task and finish it

        if get_all_produced_count() == count:
            print("--Simulation complete--")
            break

    # End of simulation
    print(clock)
    print_simulation_data()
