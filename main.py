import multiprocessing
from typing import List
from fastapi import FastAPI, Path

# Initialize FastAPI app
app = FastAPI()

# Queue for sharing results across processes
process_results = multiprocessing.Queue()

def myfunc(i, queue):
    results = []
    for j in range(0, i):
        result = f'output from myfunc is :{j}'
        results.append(result)
    queue.put(results)

@app.get("/start_processes/{count}", response_model=List[str])
def start_processes(count: int = Path(..., title="Number of processes to start", ge=1, le=9)):
    # Reset queue
    while not process_results.empty():
        process_results.get()

    # Start processes
    processes = []
    for i in range(count):
        process = multiprocessing.Process(target=myfunc, args=(i, process_results))
        processes.append(process)
        process.start()

    # Join processes
    for process in processes:
        process.join()

    # Collect results
    results = []
    while not process_results.empty():
        results.extend(process_results.get())

    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
