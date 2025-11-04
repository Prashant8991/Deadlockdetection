import tkinter as tk
from tkinter import messagebox
from detection import detect_deadlock
from avoidance import is_safe_state

def parse_matrix(text):
    """Convert multiline text into a 2D integer list"""
    return [list(map(int, row.split())) for row in text.strip().split("\n")]

def parse_list(text):
    """Convert space-separated numbers into a list"""
    return list(map(int, text.strip().split()))

def run_detection_gui():
    try:
        processes = [f"P{i+1}" for i in range(int(entry_processes.get()))]
        resources = [f"R{j+1}" for j in range(int(entry_resources.get()))]

        allocation = parse_matrix(text_allocation.get("1.0", tk.END))
        request = parse_matrix(text_request.get("1.0", tk.END))

        if detect_deadlock(processes, resources, allocation, request):
            messagebox.showerror("Deadlock Detection", "Deadlock detected!")
        else:
            messagebox.showinfo("Deadlock Detection", "No deadlock detected.")
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")

def run_avoidance_gui():
    try:
        processes = [f"P{i+1}" for i in range(int(entry_processes.get()))]
        resources = [f"R{j+1}" for j in range(int(entry_resources.get()))]

        allocation = parse_matrix(text_allocation.get("1.0", tk.END))
        max_need = parse_matrix(text_maxneed.get("1.0", tk.END))
        available = parse_list(entry_available.get())

        safe, sequence = is_safe_state(processes, resources, available, allocation, max_need)
        if safe:
            messagebox.showinfo("Deadlock Avoidance", f"Safe state!\nSequence: {' -> '.join(sequence)}")
        else:
            messagebox.showerror("Deadlock Avoidance", "System is NOT in a safe state!")
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")

# Main GUI window
root = tk.Tk()
root.title("Deadlock Detection & Avoidance Visualizer")
root.geometry("600x650")

# Number of processes/resources
frame_top = tk.Frame(root)
frame_top.pack(pady=5)

tk.Label(frame_top, text="Processes:").grid(row=0, column=0)
entry_processes = tk.Entry(frame_top, width=5)
entry_processes.grid(row=0, column=1, padx=5)

tk.Label(frame_top, text="Resources:").grid(row=0, column=2)
entry_resources = tk.Entry(frame_top, width=5)
entry_resources.grid(row=0, column=3, padx=5)

# Allocation matrix
tk.Label(root, text="Allocation Matrix (rows=processes, cols=resources):").pack()
text_allocation = tk.Text(root, height=5, width=50)
text_allocation.pack()

# Request matrix (for detection)
tk.Label(root, text="Request Matrix (Detection):").pack()
text_request = tk.Text(root, height=5, width=50)
text_request.pack()

# Max need matrix (for avoidance)
tk.Label(root, text="Max Need Matrix (Avoidance):").pack()
text_maxneed = tk.Text(root, height=5, width=50)
text_maxneed.pack()

# Available resources (for avoidance)
tk.Label(root, text="Available Resources (space-separated):").pack()
entry_available = tk.Entry(root, width=30)
entry_available.pack(pady=5)

# Buttons
btn_detection = tk.Button(root, text="Run Deadlock Detection", font=("Arial", 12), command=run_detection_gui)
btn_detection.pack(pady=10)

btn_avoidance = tk.Button(root, text="Run Deadlock Avoidance", font=("Arial", 12), command=run_avoidance_gui)
btn_avoidance.pack(pady=10)

btn_exit = tk.Button(root, text="Exit", font=("Arial", 12), command=root.quit)
btn_exit.pack(pady=20)

root.mainloop()
