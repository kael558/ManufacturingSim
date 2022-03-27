from numpy import random
from enum import Enum


class Component(Enum):
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"


class Processor:
    def __init__(self, index: int, buffers: dict, receiving: dict):
        """
        The superclass for machine-like thing that inspects/processes things
        :param index: the index of the processor (e.g. 1 for I1, 3 for W3)
        :param buffers: a dictionary where keys are components and values are the numbers of respective component
        """
        self.index = index
        self.buffers = buffers
        self.working = False
        self.blocked = False
        self.receiving = receiving

        # Quantities of interest
        self.time_blocked = 0.0
        self.time_working = 0.0
        self.time_idling = 0.0

    def update_time_qoi(self, time):
        if self.is_free():
            self.time_idling += time
        elif self.is_working():
            self.time_working += time
        else:
            self.time_blocked += time

    def is_working(self):
        return self.working

    def is_blocked(self):
        return self.blocked

    def is_free(self):
        return not self.blocked and not self.working

    def set_working(self):
        self.working = True
        self.blocked = False

    def set_blocked(self):
        self.blocked = True
        self.working = False

    def set_free(self):
        self.blocked = False
        self.working = False

    def has_components(self):
        return all(buffer > 0 for buffer in self.buffers.values())

    def get_components(self):
        lst = []
        for component in self.buffers.keys():
            self.buffers[component] -= 1
            lst.append(component)
        return lst

    def name(self):
        pass

    def __str__(self):
        pass


class Workstation(Processor):
    def __init__(self, index: int, buffers: dict, receiving: dict):
        super().__init__(index, buffers, receiving)
        self.counter = 0

        # Quantities of interest
        self.component_arrivals = buffers.copy()
        self.avg_buffer_occupancy = buffers.copy()

    def update_buffer_qoi(self, total_time, step_time):
        if total_time == 0:
            return

        for component in self.buffers.keys():
            self.avg_buffer_occupancy[component] = (self.avg_buffer_occupancy[component] * total_time +
                                                    self.buffers[component] * step_time) / \
                                                   (step_time + total_time)

    def is_full(self):
        return all(buffer == 2 for buffer in self.buffers.values())

    def name(self):
        return f"Workstation {self.index}"

    def get_num_components(self, component):
        return self.buffers[component]

    def add_component(self, component):
        self.component_arrivals[component] += 1
        self.buffers[component] += 1

    def get_count(self):
        return self.counter

    def __str__(self):
        state = "idle" if self.is_free() else "processing"
        return f"Workstation {self.index} is {state}. Buffer: {self.buffers}"


class Inspector(Processor):
    def get_components(self):
        if self.index == 2:  # if current inspector is I2
            return [Component.C2 if random.random() < 0.5 else Component.C3]
        return super().get_components()

    def name(self):
        return f"Inspector {self.index}"

    def __str__(self):
        state = "idle"
        if self.is_blocked():
            state = "blocked"
        elif self.is_working():
            state = "inspecting"
        return f"Inspector {self.index} is {state}."
