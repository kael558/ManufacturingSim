import numpy as np

from processors import Processor, Workstation, Inspector, Component
from fel import TaskQueue, Task

if __name__ == '__main__':
    def populate_process_times(n):
        exp = {
            1: 4.604416667,
            2: 11.0926066666667,
            3: 8.79558,
            Component.C1: 10.35791,
            Component.C2: 15.53690333,
            Component.C3: 20.63275667
        }
        np.random.seed(69)
        for p in exp:
            Task.process_times[p].clear()
            for _ in range(n):
                Task.process_times[p].append(np.random.exponential(exp[p]))

    def reset_all_produced_count():
        """
        Helper method to reset the total number of products produced
        """
        for processor in processors:
            processor.counter = 0

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
        print("\n-- Buffer Quantities of Interest --")
        for i in range(2, 5):
            print(f"-- {processors[i].name()} --")
            for component in processors[i].buffers.keys():
                print(f"\tAverage buffer occupancy for {component}: {processors[i].avg_buffer_occupancy[component]}/2")
                print(f"\tBuffer arrival rate: {processors[i].component_arrivals[component]/total_time} {component}/s")

    R0 = 1

    throughput_P1 = []
    throughput_P2 = []
    throughput_P3 = []

    for R in range(1, R0+1):
        time_passed = 0
        infinity = 9999999  # its over 9000 so its basically infinity
        count = 1000  # how many products to produce before stopping the simulation
        total_time = 0.0
        populate_process_times(count*2)

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

        flag = True
        while flag or get_all_produced_count() < count:
            if get_all_produced_count() >= count:
                flag = False
                reset_all_produced_count()

            # attempt to start tasks
            for processor in processors:
                attempt_start_task(processor)

            # this part ensures if a workstation finishes a product, a blocked inspector will send a component right away
            free_processors = task_queue.attempt_blocked_tasks()  # get the processors from finished tasks that were blocked
            for processor in free_processors:
                attempt_start_task(processor)

            #print(task_queue)
            #print("--State of processors--")
            #print("\n".join(list(map(str, processors))))

            #print("\n--Tasks Completed--")

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

        throughput_P1.append(W1.get_count())
        throughput_P2.append(W2.get_count())
        throughput_P3.append(W3.get_count())

    def calc_m_s(data):
        mean = sum(data)/len(data)
        deviations = [(x - mean) ** 2 for x in data]
        variance = sum(deviations)/len(data)
        return mean,variance
    print(calc_m_s(throughput_P1))
    print(calc_m_s(throughput_P2))
    print(calc_m_s(throughput_P3))