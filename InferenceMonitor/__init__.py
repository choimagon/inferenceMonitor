import psutil
import os
import time
import threading
import matplotlib.pyplot as plt
import csv 

class InferenceMonitor:
    def __init__(self, interval=0.5):
        self.interval = interval
        self.cpu_total_log = []
        self.cpu_percore_log = []
        self.memory_log = []
        self.time_log = []
        self.monitoring_flag = False
        self.start_time = 0
        self.thread = None

    def _monitor(self):
        process = psutil.Process(os.getpid())

        while self.monitoring_flag:
            cpu_total = psutil.cpu_percent(interval=None)
            cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
            mem = process.memory_info().rss / 1024 / 1024  # MB
            t = time.time() - self.start_time

            self.cpu_total_log.append(cpu_total)
            self.cpu_percore_log.append(cpu_per_core)
            self.memory_log.append(mem)
            self.time_log.append(t)

            time.sleep(self.interval)

    def start(self):
        self.start_time = time.time()
        self.monitoring_flag = True
        self.thread = threading.Thread(target=self._monitor)
        self.thread.start()

    def stop(self):
        self.monitoring_flag = False
        if self.thread is not None:
            self.thread.join()
        self.plot()
        self.save_csv()

    def save_csv(self, csv_path=None):
        timestamp = int(time.time())
        if csv_path is None:
            csv_path = f"resource_usage-{timestamp}.csv"

        with open(csv_path, mode='w', newline='') as f:
            writer = csv.writer(f)
            
            # 헤더 구성
            num_cores = len(self.cpu_percore_log[0]) if self.cpu_percore_log else 0
            headers = ["Time(s)", "Total_CPU(%)"] + [f"Core_{i}(%)" for i in range(num_cores)] + ["Memory(MB)"]
            writer.writerow(headers)

            # 데이터 쓰기
            for i in range(len(self.time_log)):
                row = [
                    round(self.time_log[i], 3),
                    round(self.cpu_total_log[i], 2)
                ]
                row += [round(core, 2) for core in self.cpu_percore_log[i]]
                row += [round(self.memory_log[i], 2)]
                writer.writerow(row)

    def plot(self, save_path="resource_usage.png"):
        plt.figure(figsize=(12, 6))
        # CPU 전체 사용률
        plt.subplot(3, 1, 1)
        plt.plot(self.time_log, self.cpu_total_log, label='Total CPU %')
        plt.ylabel("Total CPU (%)")
        plt.title("CPU & Memory Usage During Inference")
        plt.grid(True)
        plt.legend()

        # CPU 코어별 사용률
        plt.subplot(3, 1, 2)
        if self.cpu_percore_log:
            num_cores = len(self.cpu_percore_log[0])
            for core_idx in range(num_cores):
                core_usage = [entry[core_idx] for entry in self.cpu_percore_log]
                plt.plot(self.time_log, core_usage, label=f"Core {core_idx}")
            plt.ylabel("Per-Core CPU (%)")
            plt.legend(ncol=4, fontsize=8)
            plt.grid(True)

        # 메모리 사용량
        plt.subplot(3, 1, 3)
        plt.plot(self.time_log, self.memory_log, color="purple", label="Memory (MB)")
        plt.xlabel("Time (s)")
        plt.ylabel("Memory (MB)")
        plt.grid(True)
        plt.legend()

        plt.tight_layout()
        timestamp = int(time.time())
        plt.savefig(f"resource_usage-{timestamp}.png", dpi=600)
        # plt.show()
