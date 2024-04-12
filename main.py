import heapq
from math import inf
import random


class Job:
    def __init__(self, arrival_time, service_time, server_type):
        self.arrival_time = arrival_time
        self.service_time = service_time
        self.server_type = server_type
        self.finish_time = None
        self.start_time = None


class Server:
    def __init__(self, server_type, t_limit):
        self.server_type = server_type
        self.t_limit = t_limit
        self.is_busy = False
        self.current_job = None

    def assign_job(self, job, current_time):
        self.is_busy = True
        self.current_job = job
        if self.server_type == 0 and job.service_time > self.t_limit:
            job.finish_time = current_time + self.t_limit
        else:
            job.finish_time = current_time + job.service_time


class Event:
    def __init__(self, event_time, event_type, job):
        self.event_time = event_time
        self.event_type = event_type
        self.job = job

    def __lt__(self, other):
        return self.event_time < other.event_time


class GenerateVariable:
    def __init__(self):
        ## Simulation parameters
        self.lamb = 3.1
        self.a2l = 0.85
        self.a2u = 1.21
        # Service rate
        self.p0 = 0.74
        self.alpha0 = 0.5
        self.beta0 = 5.7
        self.eta0 = 1.9
        self.alpha1 = 2.7
        self.eta1 = 2.5
        # Simulation time
        self.time_end = 1000
        self.arrival_times = []
        self.service_times = []
        ## Accounting parameters
        # The cumulative response time
        self.response_time_cumulative = 0
        # Number of customers served at the end of the simulation
        self.num_customers_served = 0

    def generate_arrival_times(self):
        current_time = 0
        while current_time < self.time_end:
            exp_time = random.expovariate(self.lamb)
            uni_time = random.uniform(self.a2l, self.a2u)
            inter_arrival_time = exp_time * uni_time
            current_time += inter_arrival_time
            if current_time < self.time_end:
                self.arrival_times.append(current_time)
        return self.arrival_times

    def generate_service_time(self):
        for _ in range(len(self.arrival_times)):
            server_group = 0 if random.random() < self.p0 else 1
            if server_group == 0:
                service_time = self._generate_group0_service_time()
            else:
                service_time = self._generate_group1_service_time()
            self.service_times.append((server_group, service_time))
        return self.service_times

    def _generate_group0_service_time(self):
        while True:
            t = random.uniform(self.alpha0, self.beta0)
            probability_density = self.eta0 / ((self.alpha0 ** -self.eta0) - (self.beta0 ** -self.eta0)) * (
                    t ** (self.eta0 + 1))
            if random.random() < probability_density:
                return t

    def _generate_group1_service_time(self):
        while True:
            t = random.uniform(self.alpha1, 10)
            probability_density = self.eta1 / (self.alpha1 ** -self.eta1) * (t ** (self.eta1 - 1))
            if random.random() < probability_density / 10:
                return t


class SimulationManager:
    def __init__(self):
        self.current_time = 0
        self.current_event = Event(None, None, None)
        self.event_queue = []
        self.server_farms = []
        self.finished_jobs = []
        self.server_farm_queues = [[], []]
        self.T0 = 0
        self.T1 = 0
        self.n0 = 0
        self.n1 = 0
        self.response_time_cumulative = 0

    def process_next_event(self):
        if not self.event_queue:
            return False
        event = heapq.heappop(self.event_queue)
        self.current_event = event
        self.current_time = event.event_time
        if event.event_type == 'arrival':
            self.handle_arrival(event.job)
        elif event.event_type == 'departure':
            self.handle_departure(event.job)
        return True

    def handle_arrival(self, job):
        server_farm = self.server_farms[0] if job.server_type == 0 else self.server_farms[1]
        job.start_time = self.current_time
        for server in server_farm:
            if not server.is_busy:
                server.assign_job(job, self.current_time)
                heapq.heappush(self.event_queue, Event(job.finish_time, 'departure', job))
                break
        else:
            if job.server_type == 0:
                self.server_farm_queues[0].append(job)
            elif job.server_type == 1:
                self.server_farm_queues[1].append(job)

    def handle_departure(self, job):
        t_limit = None
        server_farm = self.server_farms[0] if job.server_type == 0 else self.server_farms[1]
        for server in server_farm:
            if server.current_job == job:
                server.is_busy = False
                server.current_job = None
                t_limit = server.t_limit
                break
        self.finished_jobs.append(job)
        if job.server_type == 0:
            self.T0 += job.finish_time - job.start_time
            self.n0 += 1
        elif job.server_type == 1:
            self.T1 += job.finish_time - job.start_time
            self.n1 += 1
        if job.server_type == 0 and self.server_farm_queues[0]:
            self.handle_arrival(self.server_farm_queues[0].pop(0))
        elif job.server_type == 1 and self.server_farm_queues[1]:
            self.handle_arrival(self.server_farm_queues[1].pop(0))
        if job.service_time > t_limit and job.server_type == 0:
            job.server_type = 1
            self.handle_arrival(job)

    def run(self):
        input_mode = input("please select mode: \n 1.trace mode \n 2.random mode")
        if input_mode == '1':
            print('---- run trace mode ----')
            t_limit = 3
            self.server_farms = [[Server(0, t_limit)], [Server(1, inf), Server(1, inf)]]
            jobs = [Job(2, 5, 1), Job(10, 4, 0), Job(11, 9, 0), Job(12, 2, 0), Job(14, 8, 1), Job(15, 5, 0),
                    Job(19, 3, 0), Job(20, 6, 1)]
            for job in jobs:
                heapq.heappush(self.event_queue, Event(job.arrival_time, 'arrival', job))
            while self.process_next_event():
                self.print()
                pass
        elif input_mode == '2':
            print('---- run random mode ----')
            generate_variable = GenerateVariable()
            arrival_times = generate_variable.generate_arrival_times()
            service_times = generate_variable.generate_service_time()
            # print(len(generate_variable.arrival_times))
            # print(len(generate_variable.service_times))
            # print(generate_variable.arrival_times)
            # print(generate_variable.service_times)
            t_limit = 3.3
            self.server_farms = [[Server(0, t_limit)], [Server(1, inf), Server(1, inf)]]
            jobs = []
            for index, arrival_time in enumerate(arrival_times):
                job = Job(arrival_time, service_times[index][1], service_times[index][0])
                jobs.append(job)
            for job in jobs:
                heapq.heappush(self.event_queue, Event(job.arrival_time, 'arrival', job))
            while self.process_next_event():
                self.print()
                pass
            w0 = 0.83
            w1 = 0.059
            self.response_time_cumulative = w0 * self.T0 / self.n0 + w1 * self.T1 / self.n1
            print("response_time_cumulative T:", self.response_time_cumulative)

    def print(self):
        print()
        print("MasterClock:", self.current_time, end="; ")
        print(self.current_event.event_type, end="; ")
        for index, server_farm in enumerate(self.server_farms):
            print(f"serverGroup:{index}", end=" ")
            for index_server, server in enumerate(self.server_farms[index]):
                print(f"server_index{index_server}", end="; ")
                if server.is_busy:
                    print("busy", end="; ")
                    print(f"({server.current_job.arrival_time},{server.current_job.finish_time})", end="; ")
                else:
                    print("Idle", end="; ")
        for index, server_farm_queue in enumerate(self.server_farm_queues):
            print(f"Queue {index}:", end=" ")
            if self.server_farm_queues[index]:
                for job in self.server_farm_queues[index]:
                    print(f"({job.arrival_time},{job.service_time})", end="; ")
            else:
                print("NULL", end=" ")


if __name__ == "__main__":
    simulation_manager = SimulationManager()
    simulation_manager.run()
