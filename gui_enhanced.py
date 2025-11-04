import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
from detection import detect_deadlock_and_cycle, build_wait_for_graph
from avoidance import is_safe_state, find_safe_sequence_with_process

BG = "#1a1a2e"
SECONDARY_BG = "#16213e"
ACCENT = "#0f3460"
ACCENT_LIGHT = "#16a085"
TEXT = "#eaeaea"
TEXT_DIM = "#a8a8a8"
DANGER = "#e74c3c"
SUCCESS = "#27ae60"
WARNING = "#f39c12"

class EnhancedRAGVisualizer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.node_positions = {}

    def draw_rag(self, processes, resources, allocation, request, highlight_nodes=None):
        self.canvas.delete("all")
        highlight_nodes = highlight_nodes or set()

        canvas_h = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 400
        canvas_w = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 700

        p_spacing = canvas_h / (len(processes) + 1)
        r_spacing = canvas_h / (len(resources) + 1)

        positions = {}
        for i, p in enumerate(processes):
            positions[p] = (100, (i + 1) * p_spacing)
        for j, r in enumerate(resources):
            positions[r] = (600, (j + 1) * r_spacing)

        self.node_positions = positions

        for i, p in enumerate(processes):
            for j, r in enumerate(resources):
                if allocation[i][j] > 0:
                    self._draw_edge(positions[r], positions[p], ACCENT_LIGHT, f"{allocation[i][j]}")
                if request[i][j] > 0:
                    self._draw_edge(positions[p], positions[r], WARNING, f"{request[i][j]}")

        for node, (x, y) in positions.items():
            color = DANGER if node in highlight_nodes else (ACCENT if node.startswith('P') else ACCENT_LIGHT)
            if node.startswith('P'):
                self._draw_process(x, y, node, color)
            else:
                self._draw_resource(x, y, node, color)

    def _draw_process(self, x, y, text, color):
        self.canvas.create_oval(x - 25, y - 25, x + 25, y + 25, fill=color, outline=TEXT, width=2)
        self.canvas.create_text(x, y, text=text, fill=TEXT, font=("Arial", 10, "bold"))

    def _draw_resource(self, x, y, text, color):
        self.canvas.create_rectangle(x - 20, y - 20, x + 20, y + 20, fill=color, outline=TEXT, width=2)
        self.canvas.create_text(x, y, text=text, fill=TEXT, font=("Arial", 10, "bold"))

    def _draw_edge(self, start, end, color, label=""):
        self.canvas.create_line(start[0], start[1], end[0], end[1], arrow=tk.LAST, fill=color, width=2.5)
        if label:
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            self.canvas.create_text(mid_x, mid_y - 8, text=label, fill=color, font=("Arial", 8, "bold"), bg=SECONDARY_BG)


class DeadlockDetectionTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.setup_ui()

    def setup_ui(self):
        container = ttk.Frame(self.frame)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        top_panel = ttk.LabelFrame(container, text="Configuration", padding=10)
        top_panel.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(top_panel, text="Processes:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.d_proc = ttk.Entry(top_panel, width=5)
        self.d_proc.grid(row=0, column=1, padx=5)

        ttk.Label(top_panel, text="Resources:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.d_res = ttk.Entry(top_panel, width=5)
        self.d_res.grid(row=0, column=3, padx=5)

        ttk.Label(top_panel, text="Available:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.d_avail = ttk.Entry(top_panel, width=15)
        self.d_avail.grid(row=0, column=5, padx=5)

        matrices_panel = ttk.LabelFrame(container, text="Input Matrices", padding=10)
        matrices_panel.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(matrices_panel, text="Allocation Matrix:").pack(anchor=tk.W)
        self.d_alloc = tk.Text(matrices_panel, height=4, width=50, bg=SECONDARY_BG, fg=TEXT)
        self.d_alloc.pack(pady=5)

        ttk.Label(matrices_panel, text="Request Matrix:").pack(anchor=tk.W)
        self.d_request = tk.Text(matrices_panel, height=4, width=50, bg=SECONDARY_BG, fg=TEXT)
        self.d_request.pack(pady=5)

        canvas_panel = ttk.LabelFrame(container, text="Wait-For Graph", padding=10)
        canvas_panel.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.canvas_detect = tk.Canvas(canvas_panel, bg=SECONDARY_BG, highlightthickness=0, height=300)
        self.canvas_detect.pack(fill=tk.BOTH, expand=True)
        self.detect_vis = EnhancedRAGVisualizer(self.canvas_detect)

        output_panel = ttk.LabelFrame(container, text="Analysis Results", padding=10)
        output_panel.pack(fill=tk.X, pady=(0, 10))
        self.d_output = scrolledtext.ScrolledText(output_panel, height=6, bg=SECONDARY_BG, fg=TEXT)
        self.d_output.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Analyze Deadlock", command=self.on_detection).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load Example", command=self.load_example).pack(side=tk.LEFT, padx=5)

    def parse_matrix(self, text):
        return [list(map(int, row.strip().split())) for row in text.strip().split("\n") if row.strip()]

    def parse_list(self, text):
        return list(map(int, text.strip().split()))

    def load_example(self):
        self.d_proc.delete(0, tk.END)
        self.d_proc.insert(0, "3")
        self.d_res.delete(0, tk.END)
        self.d_res.insert(0, "3")
        self.d_avail.delete(0, tk.END)
        self.d_avail.insert(0, "0 0 0")

        self.d_alloc.delete("1.0", tk.END)
        self.d_alloc.insert("1.0", "2 1 0\n0 2 1\n1 0 1")

        self.d_request.delete("1.0", tk.END)
        self.d_request.insert("1.0", "0 1 1\n1 0 1\n0 1 0")

    def on_detection(self):
        try:
            p = int(self.d_proc.get())
            r = int(self.d_res.get())
            processes = [f"P{i}" for i in range(p)]
            resources = [f"R{j}" for j in range(r)]

            allocation = self.parse_matrix(self.d_alloc.get("1.0", tk.END))
            request = self.parse_matrix(self.d_request.get("1.0", tk.END))
            available = self.parse_list(self.d_avail.get())

            is_deadlocked, deadlocked_procs, cycles = detect_deadlock_and_cycle(
                processes, resources, allocation, request, available
            )

            self.detect_vis.draw_rag(processes, resources, allocation, request,
                                    highlight_nodes=set(deadlocked_procs))

            self.d_output.delete("1.0", tk.END)
            output = f"Deadlock Status: {'DETECTED' if is_deadlocked else 'NOT DETECTED'}\n"
            output += f"Processes: {', '.join(processes)}\n"
            output += f"Resources: {', '.join(resources)}\n"
            output += f"Available: {available}\n\n"

            if is_deadlocked:
                output += f"Deadlocked Processes: {', '.join(deadlocked_procs)}\n"
                output += f"Number of cycles: {len(cycles)}\n\n"
                for idx, cycle in enumerate(cycles):
                    output += f"Cycle {idx + 1}: {' -> '.join(cycle)}\n"
            else:
                output += "System is in a safe state. No deadlock detected."

            self.d_output.insert("1.0", output)
            messagebox.showinfo("Analysis Complete",
                              f"Deadlock {'DETECTED' if is_deadlocked else 'NOT DETECTED'}")

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    def clear_fields(self):
        self.d_proc.delete(0, tk.END)
        self.d_res.delete(0, tk.END)
        self.d_avail.delete(0, tk.END)
        self.d_alloc.delete("1.0", tk.END)
        self.d_request.delete("1.0", tk.END)
        self.d_output.delete("1.0", tk.END)
        self.canvas_detect.delete("all")


class DeadlockAvoidanceTab:
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.setup_ui()

    def setup_ui(self):
        container = ttk.Frame(self.frame)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        config_panel = ttk.LabelFrame(container, text="Configuration", padding=10)
        config_panel.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(config_panel, text="Processes:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.a_proc = ttk.Entry(config_panel, width=5)
        self.a_proc.grid(row=0, column=1, padx=5)

        ttk.Label(config_panel, text="Resources:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.a_res = ttk.Entry(config_panel, width=5)
        self.a_res.grid(row=0, column=3, padx=5)

        ttk.Label(config_panel, text="Available:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.a_avail = ttk.Entry(config_panel, width=15)
        self.a_avail.grid(row=0, column=5, padx=5)

        matrices_panel = ttk.LabelFrame(container, text="Input Matrices", padding=10)
        matrices_panel.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(matrices_panel, text="Allocation Matrix:").pack(anchor=tk.W)
        self.a_alloc = tk.Text(matrices_panel, height=4, width=50, bg=SECONDARY_BG, fg=TEXT)
        self.a_alloc.pack(pady=5)

        ttk.Label(matrices_panel, text="Max Need Matrix:").pack(anchor=tk.W)
        self.a_max = tk.Text(matrices_panel, height=4, width=50, bg=SECONDARY_BG, fg=TEXT)
        self.a_max.pack(pady=5)

        output_panel = ttk.LabelFrame(container, text="Analysis Results", padding=10)
        output_panel.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.a_output = scrolledtext.ScrolledText(output_panel, height=8, bg=SECONDARY_BG, fg=TEXT)
        self.a_output.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Check Safe State", command=self.on_avoidance).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_fields).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load Example", command=self.load_example).pack(side=tk.LEFT, padx=5)

    def parse_matrix(self, text):
        return [list(map(int, row.strip().split())) for row in text.strip().split("\n") if row.strip()]

    def parse_list(self, text):
        return list(map(int, text.strip().split()))

    def load_example(self):
        self.a_proc.delete(0, tk.END)
        self.a_proc.insert(0, "3")
        self.a_res.delete(0, tk.END)
        self.a_res.insert(0, "3")
        self.a_avail.delete(0, tk.END)
        self.a_avail.insert(0, "10 5 7")

        self.a_alloc.delete("1.0", tk.END)
        self.a_alloc.insert("1.0", "0 1 0\n2 0 0\n3 0 2")

        self.a_max.delete("1.0", tk.END)
        self.a_max.insert("1.0", "7 5 3\n3 2 2\n9 0 2")

    def on_avoidance(self):
        try:
            p = int(self.a_proc.get())
            r = int(self.a_res.get())
            processes = [f"P{i}" for i in range(p)]
            resources = [f"R{j}" for j in range(r)]

            allocation = self.parse_matrix(self.a_alloc.get("1.0", tk.END))
            max_need = self.parse_matrix(self.a_max.get("1.0", tk.END))
            available = self.parse_list(self.a_avail.get())

            safe, seq, details = is_safe_state(processes, resources, available, allocation, max_need)

            self.a_output.delete("1.0", tk.END)
            output = f"Safety Status: {'SAFE STATE' if safe else 'UNSAFE STATE'}\n"
            output += f"Processes: {', '.join(processes)}\n"
            output += f"Resources: {', '.join(resources)}\n"
            output += f"Available: {available}\n\n"

            if safe:
                output += f"Safe Sequence: {' -> '.join(seq)}\n\n"
                output += f"Analysis Iterations: {len(details['iterations'])}\n"
                for idx, iter_info in enumerate(details['iterations']):
                    output += f"\nIteration {idx + 1}:\n"
                    for proc_info in iter_info['processes_checked']:
                        status = "✓ ALLOCATED" if proc_info['can_allocate'] else "✗ WAITING"
                        output += f"  {proc_info['process']}: {status}\n"
            else:
                output += f"Incomplete sequence: {', '.join(seq) if seq else 'None'}\n"
                output += "Some processes cannot be satisfied in any order.\n"

            self.a_output.insert("1.0", output)
            messagebox.showinfo("Analysis Complete",
                              f"State: {'SAFE' if safe else 'UNSAFE'}")

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    def clear_fields(self):
        self.a_proc.delete(0, tk.END)
        self.a_res.delete(0, tk.END)
        self.a_avail.delete(0, tk.END)
        self.a_alloc.delete("1.0", tk.END)
        self.a_max.delete("1.0", tk.END)
        self.a_output.delete("1.0", tk.END)


class EnhancedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Deadlock Detection & Avoidance System")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=ACCENT, foreground=TEXT, padding=[15, 8], font=("Arial", 10))
        style.map("TNotebook.Tab", background=[("selected", ACCENT_LIGHT)])
        style.configure("TFrame", background=BG)
        style.configure("TLabelFrame", background=BG, foreground=TEXT)
        style.configure("TLabelFrame.Label", background=BG, foreground=TEXT)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("TEntry", fieldbackground=SECONDARY_BG, foreground=TEXT)
        style.configure("TButton", background=ACCENT, foreground=TEXT)
        style.map("TButton", background=[("active", ACCENT_LIGHT)])

        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.detection_tab = DeadlockDetectionTab(notebook)
        self.avoidance_tab = DeadlockAvoidanceTab(notebook)

        notebook.add(self.detection_tab.frame, text="Deadlock Detection")
        notebook.add(self.avoidance_tab.frame, text="Deadlock Avoidance")


if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedApp(root)
    root.mainloop()
