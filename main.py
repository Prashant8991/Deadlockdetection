# main_app.py
import tkinter as tk
from tkinter import ttk, messagebox
import math

# Import the corrected backend logic
from detection import detect_deadlock_and_cycle
from avoidance import is_safe_state

# -------------------- Constants --------------------
BG_COLOR = "#2c3e50"
CANVAS_BG = "#34495e"
TEXT_COLOR = "#ecf0f1"
ACCENT_COLOR = "#3498db"
FONT_STYLE = ("Segoe UI", 10)
NODE_RADIUS = 20
HIGHLIGHT_COLOR = "#e74c3c"
ALLOCATION_COLOR = "#2ecc71"
REQUEST_COLOR = "#f39c12"

# -------------------- Utilities --------------------
def parse_matrix(text):
    return [list(map(int, row.strip().split())) for row in text.strip().split("\n") if row.strip()]

def parse_list(text):
    return list(map(int, text.strip().split()))

# -------------------- RAG Visualizer Class --------------------
class RAGVisualizer:
    def __init__(self, canvas):
        self.canvas = canvas

    def clear(self):
        self.canvas.delete("all")

    def draw_rag(self, processes, resources, allocation, request, highlight_nodes=None):
        self.clear()
        highlight_nodes = highlight_nodes or set()

        canvas_h = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 300
        canvas_w = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 700

        p_spacing = canvas_h / (len(processes) + 1)
        r_spacing = canvas_h / (len(resources) + 1)
        
        positions = {}
        # Layout Processes on the left
        for i, p in enumerate(processes):
            positions[p] = (canvas_w * 0.2, (i + 1) * p_spacing)
        # Layout Resources on the right
        for j, r in enumerate(resources):
            positions[r] = (canvas_w * 0.8, (j + 1) * r_spacing)

        # Draw Edges first
        for i, p in enumerate(processes):
            for j, r in enumerate(resources):
                # Allocation Edge: R -> P
                if allocation[i][j] > 0:
                    self._draw_edge(positions[r], positions[p], ALLOCATION_COLOR)
                # Request Edge: P -> R
                if request[i][j] > 0:
                    self._draw_edge(positions[p], positions[r], REQUEST_COLOR)
        
        # Draw Nodes on top of edges
        for node, (x, y) in positions.items():
            color = HIGHLIGHT_COLOR if node in highlight_nodes else ACCENT_COLOR
            self._draw_node(x, y, node, color)

    def _draw_node(self, x, y, text, color):
        if text.startswith('P'): # Processes are circles
            self.canvas.create_oval(x - NODE_RADIUS, y - NODE_RADIUS, x + NODE_RADIUS, y + NODE_RADIUS, fill=color, outline=TEXT_COLOR, width=2)
        else: # Resources are squares
            self.canvas.create_rectangle(x - NODE_RADIUS, y - NODE_RADIUS, x + NODE_RADIUS, y + NODE_RADIUS, fill=color, outline=TEXT_COLOR, width=2)
        self.canvas.create_text(x, y, text=text, fill=TEXT_COLOR, font=(FONT_STYLE[0], 9, "bold"))

    def _draw_edge(self, start, end, color):
        self.canvas.create_line(start[0], start[1], end[0], end[1], arrow=tk.LAST, fill=color, width=2)

# -------------------- Main App Class --------------------
class DeadlockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadlock Detection & Avoidance Visualizer")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("800x750")

        # --- Setup Tabs ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TNotebook.Tab", background=BG_COLOR, foreground=TEXT_COLOR, padding=[10, 5], font=FONT_STYLE)
        style.map("TNotebook.Tab", background=[("selected", ACCENT_COLOR)])
        
        tab_control = ttk.Notebook(root)
        self.tab_detect = ttk.Frame(tab_control, style="TFrame")
        self.tab_avoid = ttk.Frame(tab_control, style="TFrame")
        tab_control.add(self.tab_detect, text="Deadlock Detection")
        tab_control.add(self.tab_avoid, text="Deadlock Avoidance")
        tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        self.build_detection_tab()
        self.build_avoidance_tab()

    def build_detection_tab(self):
        frame = self.tab_detect
        # --- Input Frame ---
        input_frame = ttk.Frame(frame)
        input_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(input_frame, text="Processes:", foreground=TEXT_COLOR, background=BG_COLOR).grid(row=0, column=0, sticky='w')
        self.d_proc = ttk.Entry(input_frame, width=5)
        self.d_proc.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Resources:", foreground=TEXT_COLOR, background=BG_COLOR).grid(row=0, column=2, sticky='w')
        self.d_res = ttk.Entry(input_frame, width=5)
        self.d_res.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="Available Vector:", foreground=TEXT_COLOR, background=BG_COLOR).grid(row=1, column=0, sticky='w', pady=5)
        self.d_avail = ttk.Entry(input_frame, width=20)
        self.d_avail.grid(row=1, column=1, columnspan=3, sticky='w', padx=5, pady=5)

        # --- Matrices Frame ---
        matrices_frame = ttk.Frame(frame)
        matrices_frame.pack(padx=10, pady=5, fill='x')
        ttk.Label(matrices_frame, text="Allocation Matrix:", foreground=TEXT_COLOR, background=BG_COLOR).grid(row=0, column=0, sticky='w')
        self.d_alloc = tk.Text(matrices_frame, height=5, width=35, bg=CANVAS_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.d_alloc.grid(row=1, column=0, padx=5)

        ttk.Label(matrices_frame, text="Request Matrix:", foreground=TEXT_COLOR, background=BG_COLOR).grid(row=0, column=1, sticky='w', padx=10)
        self.d_request = tk.Text(matrices_frame, height=5, width=35, bg=CANVAS_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.d_request.grid(row=1, column=1, padx=10)
        
        # --- Canvas ---
        canvas = tk.Canvas(frame, bg=CANVAS_BG, highlightthickness=0)
        canvas.pack(padx=10, pady=10, fill='both', expand=True)
        self.rag_visualizer = RAGVisualizer(canvas)

        # --- Buttons ---
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(padx=10, pady=10)
        ttk.Button(btn_frame, text="Run Detection & Visualize RAG", command=self.on_detection).pack()

    def on_detection(self):
        try:
            p = int(self.d_proc.get())
            r = int(self.d_res.get())
            processes = [f"P{i}" for i in range(p)]
            resources = [f"R{j}" for j in range(r)]
            
            allocation = parse_matrix(self.d_alloc.get("1.0", tk.END))
            request = parse_matrix(self.d_request.get("1.0", tk.END))
            available = parse_list(self.d_avail.get())

            is_deadlocked, deadlocked_procs = detect_deadlock_and_cycle(processes, resources, allocation, request, available)
            
            self.rag_visualizer.draw_rag(processes, resources, allocation, request, highlight_nodes=set(deadlocked_procs))

            if is_deadlocked:
                messagebox.showerror("Deadlock Detected", f"System is in a deadlocked state!\nDeadlocked Processes: {', '.join(deadlocked_procs)}")
            else:
                messagebox.showinfo("No Deadlock", "System is NOT in a deadlocked state.")
        except Exception as e:
            messagebox.showerror("Input Error", f"An error occurred: {e}")

    def build_avoidance_tab(self):
        frame = self.tab_avoid
        input_frame = ttk.Frame(frame)
        input_frame.pack(padx=10, pady=10, fill='x')

        ttk.Label(input_frame, text="Processes:", foreground=TEXT_COLOR, background=BG_COLOR).grid(row=0, column=0, sticky='w')
        self.a_proc = ttk.Entry(input_frame, width=5)
        self.a_proc.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Resources:", foreground=TEXT_COLOR, background=BG_COLOR).grid(row=0, column=2, sticky='w')
        self.a_res = ttk.Entry(input_frame, width=5)
        self.a_res.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="Available Vector:", foreground=TEXT_COLOR, background=BG_COLOR).grid(row=1, column=0, sticky='w', pady=5)
        self.a_avail = ttk.Entry(input_frame, width=20)
        self.a_avail.grid(row=1, column=1, columnspan=3, sticky='w', padx=5, pady=5)
        
        matrices_frame = ttk.Frame(frame)
        matrices_frame.pack(padx=10, pady=5, fill='x', expand=True)
        ttk.Label(matrices_frame, text="Allocation Matrix:", foreground=TEXT_COLOR, background=BG_COLOR).grid(row=0, column=0, sticky='w')
        self.a_alloc = tk.Text(matrices_frame, height=8, width=40, bg=CANVAS_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.a_alloc.grid(row=1, column=0, padx=5)

        ttk.Label(matrices_frame, text="Max Need Matrix:", foreground=TEXT_COLOR, background=BG_COLOR).grid(row=0, column=1, sticky='w', padx=10)
        self.a_max = tk.Text(matrices_frame, height=8, width=40, bg=CANVAS_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.a_max.grid(row=1, column=1, padx=10)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(padx=10, pady=20)
        ttk.Button(btn_frame, text="Check for Safe State", command=self.on_avoidance).pack()

    def on_avoidance(self):
        try:
            p = int(self.a_proc.get())
            r = int(self.a_res.get())
            processes = [f"P{i}" for i in range(p)]
            resources = [f"R{j}" for j in range(r)]
            
            allocation = parse_matrix(self.a_alloc.get("1.0", tk.END))
            max_need = parse_matrix(self.a_max.get("1.0", tk.END))
            available = parse_list(self.a_avail.get())

            safe, seq = is_safe_state(processes, resources, available, allocation, max_need)

            if safe:
                messagebox.showinfo("Safe State", f"System is in a safe state.\nSafe sequence: {', '.join(seq)}")
            else:
                messagebox.showerror("Unsafe State", "System is NOT in a safe state!")
        except Exception as e:
            messagebox.showerror("Input Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DeadlockApp(root)
    root.mainloop()