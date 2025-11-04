# detection.py

def find_cycles_dfs(graph, processes):
    """
    Find all cycles in the Wait-For Graph using Depth First Search.

    Args:
        graph: Adjacency list representing wait-for relationships
        processes: List of process names

    Returns:
        List of cycles found (each cycle is a list of process names)
    """
    visited = set()
    rec_stack = set()
    cycles = []

    def dfs_visit(node, path):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs_visit(neighbor, path[:])
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        rec_stack.remove(node)

    for process in processes:
        if process not in visited:
            dfs_visit(process, [])

    return cycles


def build_wait_for_graph(processes, resources, allocation, request):
    """
    Build a Wait-For Graph from allocation and request matrices.

    In a WFG:
    - Nodes represent processes
    - Edge P_i -> P_j means P_i is waiting for a resource held by P_j

    Args:
        processes: List of process names
        resources: List of resource names
        allocation: Allocation matrix (processes x resources)
        request: Request matrix (processes x resources)

    Returns:
        Dictionary representing the graph and resource holdings
    """
    n = len(processes)
    m = len(resources)
    graph = {p: [] for p in processes}
    resource_holder = {}

    for j in range(m):
        for i in range(n):
            if allocation[i][j] > 0:
                resource_holder[resources[j]] = processes[i]

    for i in range(n):
        for j in range(m):
            if request[i][j] > 0:
                if resources[j] in resource_holder:
                    holder = resource_holder[resources[j]]
                    if holder != processes[i]:
                        if holder not in graph[processes[i]]:
                            graph[processes[i]].append(holder)

    return graph


def detect_deadlock_and_cycle(processes, resources, allocation, request, available=None):
    """
    Enhanced deadlock detection using Wait-For Graph cycle detection.

    Returns:
        (is_deadlocked: bool, deadlocked_processes: list[str], cycles: list[list[str]])
    """
    n = len(processes)
    m = len(resources)

    if available is None:
        available = [0] * m

    graph = build_wait_for_graph(processes, resources, allocation, request)
    cycles = find_cycles_dfs(graph, processes)

    if cycles:
        deadlocked_processes = list(set(process for cycle in cycles for process in cycle))
        return True, deadlocked_processes, cycles

    return False, [], []


def detect_deadlock_and_get_deadlocked_procs(processes, resources, available, allocation, request):
    """
    Detects deadlock using both cycle detection and Banker's algorithm.

    Returns:
        (is_deadlocked: bool, deadlocked_processes: list[str])
    """
    is_deadlocked, deadlocked_processes, _ = detect_deadlock_and_cycle(
        processes, resources, allocation, request, available
    )
    return is_deadlocked, deadlocked_processes