#!/usr/bin/env python3

from detection import detect_deadlock_and_cycle, build_wait_for_graph
from avoidance import is_safe_state

def test_detection_case_1():
    print("\n" + "="*60)
    print("TEST 1: Deadlock Detection - Circular Wait")
    print("="*60)

    processes = ['P0', 'P1', 'P2']
    resources = ['R0', 'R1']
    allocation = [
        [1, 0],
        [0, 1],
        [0, 0]
    ]
    request = [
        [0, 1],
        [1, 0],
        [1, 0]
    ]

    print("\nSystem Configuration:")
    print(f"Processes: {processes}")
    print(f"Resources: {resources}")
    print("\nAllocation Matrix (P x R):")
    for i, p in enumerate(processes):
        print(f"  {p}: {allocation[i]}")
    print("\nRequest Matrix (P x R):")
    for i, p in enumerate(processes):
        print(f"  {p}: {request[i]}")

    is_deadlocked, deadlocked, cycles = detect_deadlock_and_cycle(
        processes, resources, allocation, request
    )

    print(f"\nResult: {'DEADLOCK DETECTED' if is_deadlocked else 'NO DEADLOCK'}")
    if is_deadlocked:
        print(f"Deadlocked Processes: {deadlocked}")
        print(f"Cycles Found: {len(cycles)}")
        for idx, cycle in enumerate(cycles):
            print(f"  Cycle {idx + 1}: {' -> '.join(cycle)}")


def test_detection_case_2():
    print("\n" + "="*60)
    print("TEST 2: No Deadlock - Linear Dependencies")
    print("="*60)

    processes = ['P0', 'P1', 'P2']
    resources = ['R0', 'R1', 'R2']
    allocation = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ]
    request = [
        [0, 1, 0],
        [0, 0, 1],
        [0, 0, 0]
    ]

    print("\nSystem Configuration:")
    print(f"Processes: {processes}")
    print(f"Resources: {resources}")
    print("\nAllocation Matrix:")
    for i, p in enumerate(processes):
        print(f"  {p}: {allocation[i]}")
    print("\nRequest Matrix:")
    for i, p in enumerate(processes):
        print(f"  {p}: {request[i]}")

    is_deadlocked, deadlocked, cycles = detect_deadlock_and_cycle(
        processes, resources, allocation, request
    )

    print(f"\nResult: {'DEADLOCK DETECTED' if is_deadlocked else 'NO DEADLOCK'}")
    if not is_deadlocked:
        print("System is in a SAFE state - no circular dependencies")


def test_avoidance_case_1():
    print("\n" + "="*60)
    print("TEST 3: Banker's Algorithm - Safe State")
    print("="*60)

    processes = ['P0', 'P1', 'P2']
    resources = ['R0', 'R1', 'R2']
    available = [10, 5, 7]
    allocation = [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2]
    ]
    max_need = [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2]
    ]

    print("\nSystem Configuration:")
    print(f"Processes: {processes}")
    print(f"Resources: {resources}")
    print(f"Available: {available}")
    print("\nAllocation Matrix:")
    for i, p in enumerate(processes):
        print(f"  {p}: {allocation[i]}")
    print("\nMax Need Matrix:")
    for i, p in enumerate(processes):
        print(f"  {p}: {max_need[i]}")

    safe, seq, details = is_safe_state(
        processes, resources, available, allocation, max_need
    )

    print(f"\nResult: {'SAFE STATE' if safe else 'UNSAFE STATE'}")
    if safe:
        print(f"Safe Sequence: {' -> '.join(seq)}")
        print(f"\nExecution Trace (Iterations: {len(details['iterations'])}):")
        for iter_idx, iter_info in enumerate(details['iterations']):
            print(f"\n  Iteration {iter_idx + 1}:")
            for proc_info in iter_info['processes_checked']:
                status = "✓ ALLOCATED" if proc_info['can_allocate'] else "✗ BLOCKED"
                print(f"    {proc_info['process']}: {status}")
    else:
        print(f"Unsafe - Cannot complete sequence: {seq}")


def test_avoidance_case_2():
    print("\n" + "="*60)
    print("TEST 4: Banker's Algorithm - Unsafe State")
    print("="*60)

    processes = ['P0', 'P1', 'P2']
    resources = ['R0', 'R1']
    available = [1, 1]
    allocation = [
        [2, 2],
        [1, 1],
        [1, 0]
    ]
    max_need = [
        [4, 3],
        [2, 2],
        [2, 1]
    ]

    print("\nSystem Configuration:")
    print(f"Processes: {processes}")
    print(f"Resources: {resources}")
    print(f"Available: {available}")
    print("\nAllocation Matrix:")
    for i, p in enumerate(processes):
        print(f"  {p}: {allocation[i]}")
    print("\nMax Need Matrix:")
    for i, p in enumerate(processes):
        print(f"  {p}: {max_need[i]}")

    safe, seq, details = is_safe_state(
        processes, resources, available, allocation, max_need
    )

    print(f"\nResult: {'SAFE STATE' if safe else 'UNSAFE STATE'}")
    if not safe:
        print("System cannot guarantee a safe execution sequence")
        print(f"Attempted sequence: {seq if seq else 'None'}")


def test_complex_case():
    print("\n" + "="*60)
    print("TEST 5: Complex System - 4 Processes, 3 Resources")
    print("="*60)

    processes = ['P0', 'P1', 'P2', 'P3']
    resources = ['R0', 'R1', 'R2']
    allocation = [
        [1, 1, 0],
        [0, 1, 1],
        [1, 0, 1],
        [0, 0, 0]
    ]
    request = [
        [0, 0, 1],
        [1, 0, 0],
        [0, 1, 0],
        [1, 1, 1]
    ]

    print("\nSystem Configuration:")
    print(f"Processes: {processes}")
    print(f"Resources: {resources}")

    graph = build_wait_for_graph(processes, resources, allocation, request)
    print("\nWait-For Graph:")
    for process, waiting_for in graph.items():
        if waiting_for:
            print(f"  {process} → {waiting_for}")
        else:
            print(f"  {process} → (no waiting)")

    is_deadlocked, deadlocked, cycles = detect_deadlock_and_cycle(
        processes, resources, allocation, request
    )

    print(f"\nDeadlock Status: {'DETECTED' if is_deadlocked else 'NOT DETECTED'}")
    if is_deadlocked:
        print(f"Deadlocked Processes: {deadlocked}")


def main():
    print("\n" + "#"*60)
    print("# COMPREHENSIVE DEADLOCK ALGORITHM TEST SUITE")
    print("#"*60)

    try:
        test_detection_case_1()
        test_detection_case_2()
        test_avoidance_case_1()
        test_avoidance_case_2()
        test_complex_case()

        print("\n" + "#"*60)
        print("# ALL TESTS COMPLETED SUCCESSFULLY")
        print("#"*60 + "\n")

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
