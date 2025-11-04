# detection.py
def detect_deadlock_and_get_deadlocked_procs(processes, resources, available, allocation, request):
    """
    Detects deadlock for systems with multiple resource instances using the Banker's detection algorithm.
    
    Returns:
        (is_deadlocked: bool, deadlocked_processes: list[str])
    """
    n = len(processes)
    m = len(resources)
    work = available[:]
    finish = [False] * n

    # Main detection loop
    while True:
        found_process = False
        for i in range(n):
            if not finish[i] and all(request[i][j] <= work[j] for j in range(m)):
                for k in range(m):
                    work[k] += allocation[i][k]
                finish[i] = True
                found_process = True
        
        if not found_process:
            break

    is_deadlocked = not all(finish)
    deadlocked_processes = [processes[i] for i in range(n) if not finish[i]]
    
    return is_deadlocked, deadlocked_processes

def detect_deadlock_and_cycle(processes, resources, allocation, request, available):
    """ Main function called by the GUI to maintain a consistent interface name. """
    return detect_deadlock_and_get_deadlocked_procs(processes, resources, available, allocation, request)