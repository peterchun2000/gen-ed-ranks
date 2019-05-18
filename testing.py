# This file is only used to test the concurrency thread implementation
import threading, time, random
from queue import Queue

jobs = Queue()
gens_list = {"DSHS", "DSHU", "DSNS", "DSNL", "DSSP", "DVCC", "DVUP", "SCIS"}
def run(q):
    while not q.empty():
        print("staring new thread")
        value = q.get()
        time.sleep(random.randint(1, 10))
        print(value)
        q.task_done()

for gen in gens_list:
    jobs.put(gen)

for i in range(3):
    worker = threading.Thread(target=run, args=(jobs,))
    worker.start()

print("waiting for queue to complete", jobs.qsize(), "tasks")
jobs.join()
print("all done")