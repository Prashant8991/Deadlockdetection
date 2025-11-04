# avoidance.py
def is_safe_state(processes, resources, available, allocation, max_need):
    """
    Checks if the system is in a safe state using the Banker's Algorithm.
    """
    n = len(processes)
    m = len(resources)
    need = [[max_need[i][j] - allocation[i][j] for j in range(m)] for i in range(n)]
    work = available[:]
    finish = [False] * n
    safe_sequence = []

    while len(safe_sequence) < n:
        found_process_in_pass = False
        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                for k in range(m):
                    work[k] += allocation[i][k]
                safe_sequence.append(processes[i])
                finish[i] = True
                found_process_in_pass = True
        
        if not found_process_in_pass:
            return False, []

    return True, safe_sequence