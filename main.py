from processors import Processor, Workstation, Inspector, Component
from fel import TaskQueue, Task

if __name__ == '__main__':
    infinity = 9999999  # its over 9000 so its basically infinity
    count = 3  # how many products to produce before stopping the simulation
    total_time = 0.0

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


    def calculate_new_buffer_occupancy(prev_buff_occ, total_time, new_buff_occ, time_passed):
        """
        Helper method to calculate the new buffer occupancy given the previous buffer occupancy, total time,
        new buffer occupancy and time passed
        :param prev_buff_occ:
        :param total_time:
        :param new_buff_occ:
        :param time_passed:
        :return:
        """
        return (prev_buff_occ * total_time + new_buff_occ * time_passed) / (total_time + time_passed)


    def get_all_produced_count():
        """
        Helper method to determine the total number of products produced
        :return: The total amount of products all workstations have produced
        """
        # Yeah this isn't a great way to do this LOL
        return sum(processors[i].get_count() for i in range(2, 5))


    def attempt_start_task(processor_curr: Processor):
        """
        helper method to try and create a task is possible
        :param processor_curr: either the workstation or inspector
        """
        if processor_curr.is_free() and processor_curr.has_components():
            task = Task(processor_curr, processor_curr.get_components())
            processor_curr.set_working()
            task_queue.add_task(task)


    def print_simulation_data():
        """
        Helper method to display the quantities of interest for the simulation.
        """
        print("\n\n---SIMULATION RESULTS---")
        # Print out Product throughput
        for i in range(2, 5):
            print(f"-- W{i - 1} --")
            print(f"\tTotal products: {processors[i].get_count()}")
            print(f"\tThroughput: {processors[i].get_count() / total_time} products/sec")

        # Print out total throughput
        print(f"Overall Throughput: {get_all_produced_count() / total_time} products/sec\n")

        # Print out Inspector stats
        for i in range(0, 2):
            print(f"-- I{i + 1} --")
            print(f"\tTotal time blocked: {processors[i].time_blocked} seconds")
            print(f"\tProportion of time blocked: {100 * processors[i].time_blocked / total_time}%")

        # Print out Workstation stats
        for i in range(2, 5):
            print(f"-- W{i - 1} --")
            print(f"\tTotal time working: {processors[i].time_working}")
            print(f"\tProportion of time working: {100 * processors[i].time_working / total_time}%")

        # Print out Buffer stats
        for i in range(2, 5):
            for component in processors[i].buffers.keys():
                print(f"Average buffer occupancy for component {component}: {processors[i].avg_buffer_occupancy[component]}/2")
                print(f"Buffer arrival rate: {processors[i].component_arrivals[component]/total_time} {component}/s")


    time_passed = 0

    while count > get_all_produced_count():
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

        for i in range(2, 5):
            workstation = processors[i]
            workstation.update_buffer_qoi(total_time, time_passed)

        time_passed = task_queue.attempt_complete_task()  # goto future task and finish it

        # Compute simulation results
        total_time += time_passed
        for i, processor in enumerate(processors):
            processor.update_time_qoi(time_passed)

        if get_all_produced_count() == count:
            print("--Simulation complete--")
            break

    # End of simulation
    print_simulation_data()
