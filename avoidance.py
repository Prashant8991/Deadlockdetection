# avoidance.py

def is_safe_state(processes, resources, available, allocation, max_need):
    """
    Enhanced Banker's Algorithm with detailed analysis.

    Args:
        processes: List of process names
        resources: List of resource names
        available: Available resources vector
        allocation: Current allocation matrix
        max_need: Maximum need matrix

    Returns:
        (is_safe: bool, safe_sequence: list[str], details: dict)
    """
    n = len(processes)
    m = len(resources)

    need = [[max_need[i][j] - allocation[i][j] for j in range(m)] for i in range(n)]
    work = available[:]
    finish = [False] * n
    safe_sequence = []
    iteration_log = []

    iteration = 0
    while len(safe_sequence) < n:
        found_process_in_pass = False
        iteration += 1
        iteration_info = {"iteration": iteration, "processes_checked": []}

        for i in range(n):
            if not finish[i]:
                can_allocate = all(need[i][j] <= work[j] for j in range(m))
                iteration_info["processes_checked"].append({
                    "process": processes[i],
                    "need": need[i],
                    "work": work[:],
                    "can_allocate": can_allocate
                })

                if can_allocate:
                    for k in range(m):
                        work[k] += allocation[i][k]
                    safe_sequence.append(processes[i])
                    finish[i] = True
                    found_process_in_pass = True

        iteration_log.append(iteration_info)

        if not found_process_in_pass:
            return False, [], {"iterations": iteration_log, "incomplete_sequence": safe_sequence}

    details = {
        "iterations": iteration_log,
        "final_work": work,
        "all_processes_finished": all(finish)
    }

    return True, safe_sequence, details


def can_process_continue(process_idx, need, work, resources):
    """
    Check if a specific process can continue (all its needs can be satisfied).

    Args:
        process_idx: Index of the process
        need: Need matrix
        work: Current work vector
        resources: List of resource names

    Returns:
        (can_continue: bool, unsatisfied_resources: list[str])
    """
    unsatisfied = []
    for j, resource in enumerate(resources):
        if need[process_idx][j] > work[j]:
            unsatisfied.append((resource, need[process_idx][j], work[j]))

    return len(unsatisfied) == 0, unsatisfied


def find_safe_sequence_with_process(processes, resources, available, allocation, max_need, target_process):
    """
    Find if a specific process can be safely allocated resources.

    Returns:
        (is_achievable: bool, sequence_to_achieve: list[str])
    """
    n = len(processes)
    m = len(resources)

    if target_process not in processes:
        return False, []

    need = [[max_need[i][j] - allocation[i][j] for j in range(m)] for i in range(n)]
    work = available[:]
    finish = [False] * n
    safe_sequence = []

    target_idx = processes.index(target_process)
    target_achieved = False

    while len(safe_sequence) < n:
        found_process = False

        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                for k in range(m):
                    work[k] += allocation[i][k]
                safe_sequence.append(processes[i])
                finish[i] = True
                found_process = True

                if i == target_idx:
                    target_achieved = True
                break

        if not found_process:
            break

    return target_achieved, safe_sequence if target_achieved else []