import multiprocessing
import sys
import time

def burn_cpu():
    # Infinite loop to max out a core
    while True:
        pass 

if __name__ == '__main__':
    # Check if the dashboard sent a specific number of threads, otherwise default to 14
    if len(sys.argv) > 1:
        cores = int(sys.argv[1])
    else:
        cores = max(1, multiprocessing.cpu_count() - 2) 
        
    processes = []
    for _ in range(cores):
        p = multiprocessing.Process(target=burn_cpu)
        p.start()
        processes.append(p)
    
    try:
        # Keep the script alive silently in the background
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for p in processes:
            p.terminate()