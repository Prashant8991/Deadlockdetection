# main_app.py (or gui.py)

import tkinter as tk
from tkinter import ttk, messagebox
# We assume these files will be provided next
from detection import detect_deadlock_and_cycle
from avoidance import is_safe_state

# -------------------- Colors & Fonts --------------------
BG = "#2c3e50"
CANVAS_BG = "#34495e"
ACCENT = "#3498db"
TEXT = "#ecf0f1"
FONT = ("Segoe UI", 10)

# Vibrant color palette for nodes
NODE_COLORS = [
    "#e74c3c", "#f1c40f", "#2ecc71", "#3498db", "#9b59b6",
    "#e67e22", "#1abc9c", "#95a5a6", "#bdc3c7", "#f39c12"
]
ALLOCATION_COLOR = "#27ae60" # Emerald green
REQUEST_COLOR = "#f39c12"   # Orange
HIGHLIGHT_COLOR = "#c0392b"  # Pomegranate red

# -------------------- Utilities --------------------
def parse_matrix(text):
    return [list(map(int, row.strip().split())) for row in text.strip().split("\n") if row.strip()]

def parse_list(text):
    return list(map(int, text.strip().split()))

# -------------------- RAG Visualizer --------------------
class RAGVisualizer:
    def __init__(self, canvas):
        self.canvas = canvas

    def draw_rag(self, processes, resources, allocation, request, highlight_nodes=None, finished=None):
        self.canvas.delete("all")
        highlight_nodes = highlight_nodes or set()
        finished = finished or set()

        # Dynamic positions based on canvas size and number of nodes
        canvas_height = self.canvas.winfo_height()
        if canvas_height <= 1: canvas_height = 300 # Default if not rendered yet
        
        p_spacing = canvas_height // (len(processes) + 1)
        r_spacing = canvas_height // (len(resources) + 1)

        positions = {}
        node_color_map = {}
        color_index = 0

        for i, p in enumerate(processes):
            positions[p] = (150, (i + 1) * p_spacing)
            node_color_map[p] = NODE_COLORS[color_index % len(NODE_COLORS)]
            color_index += 1
        for j, r in enumerate(resources):
            positions[r] = (450, (j + 1) * r_spacing) # Increased spacing between P and R columns
            node_color_map[r] = NODE_COLORS[color_index % len(NODE_COLORS)]
            color_index += 1

        # draw edges
        for i, p in enumerate(processes):
            for j, r in enumerate(resources):
                if allocation[i][j] > 0:
                    self._draw_edge(positions[r], positions[p], color=ALLOCATION_COLOR)
                if request[i][j] > 0:
                    self._draw_edge(positions[p], positions[r], color=REQUEST_COLOR)

        # draw nodes
        for node, (x, y) in positions.items():
            color = node_color_map[node]
            if node in highlight_nodes:
                color = HIGHLIGHT_COLOR
            if node in finished:
                color = ALLOCATION_COLOR
            self._draw_node(x, y, node, color)

    def _draw_node(self, x, y, text, color):
        self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=color, outline=TEXT, width=2)
        self.canvas.create_text(x, y, text=text, fill=TEXT, font=("Segoe UI", 9, "bold"))

    def _draw_edge(self, start, end, color):
        self.canvas.create_line(start[0], start[1], end[0], end[1], arrow=tk.LAST, fill=color, width=2, smooth=True)

# -------------------- Main App --------------------
class DeadlockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadlock Detection & Avoidance Visualizer")
        self.root.configure(bg=BG)
        self.root.geometry("920x650") # Increased height slightly
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=ACCENT, foreground="white", padding=[10, 5], font=FONT)
        style.map("TNotebook.Tab", background=[("selected", BG)])
        style.configure("TFrame", background=BG)
        style.configure("TButton", background=ACCENT, foreground="white", font=FONT, borderwidth=0)
        style.map("TButton", background=[("active", ACCENT)])

        tab_control = ttk.Notebook(root)
        self.tab_detect = ttk.Frame(tab_control)
        self.tab_avoid = ttk.Frame(tab_control)

        tab_control.add(self.tab_detect, text="Deadlock Detection")
        tab_control.add(self.tab_avoid, text="Deadlock Avoidance")
        tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        self.build_detection_tab(self.tab_detect)
        self.build_avoidance_tab(self.tab_avoid)

    # -------------------- Detection Tab --------------------
    def build_detection_tab(self, frame):
        # ... (GUI building code remains the same)
        top = tk.Frame(frame, bg=BG)
        top.pack(anchor="nw", padx=12, pady=8)

        tk.Label(top, text="Processes:", bg=BG, fg=TEXT, font=FONT).grid(row=0, column=0, sticky="w")
        self.d_proc = tk.Entry(top, width=6, font=FONT)
        self.d_proc.grid(row=0, column=1, padx=6)
        tk.Label(top, text="Resources:", bg=BG, fg=TEXT, font=FONT).grid(row=0, column=2, sticky="w", padx=(12, 0))
        self.d_res = tk.Entry(top, width=6, font=FONT)
        self.d_res.grid(row=0, column=3, padx=6)

        mid = tk.Frame(frame, bg=BG)
        mid.pack(anchor="nw", padx=12, fill="x", expand=True)
        
        # Using PanedWindow for resizable text areas
        pane = tk.PanedWindow(mid, orient=tk.HORIZONTAL, bg=BG, sashwidth=5, sashrelief=tk.RAISED)
        pane.pack(fill="x", expand=True, pady=4)

        alloc_frame = tk.Frame(pane, bg=BG)
        tk.Label(alloc_frame, text="Allocation matrix:", bg=BG, fg=TEXT, font=FONT).pack(anchor="w")
        self.d_alloc = tk.Text(alloc_frame, height=5, font=FONT, bg=CANVAS_BG, fg=TEXT, insertbackground=TEXT)
        self.d_alloc.pack(fill="x", expand=True)
        pane.add(alloc_frame, stretch="always")

        req_frame = tk.Frame(pane, bg=BG)
        tk.Label(req_frame, text="Request matrix:", bg=BG, fg=TEXT, font=FONT).pack(anchor="w")
        self.d_request = tk.Text(req_frame, height=5, font=FONT, bg=CANVAS_BG, fg=TEXT, insertbackground=TEXT)
        self.d_request.pack(fill="x", expand=True)
        pane.add(req_frame, stretch="always")
        
        self.canvas_detect = tk.Canvas(frame, bg=CANVAS_BG, bd=0, highlightthickness=0)
        self.canvas_detect.pack(padx=12, pady=8, fill="both", expand=True)
        self.detect_vis = RAGVisualizer(self.canvas_detect)

        btn_frame = tk.Frame(frame, bg=BG)
        btn_frame.pack(padx=12, pady=6, anchor="w")
        tk.Button(btn_frame, text="Run Deadlock Detection", bg=ACCENT, fg="white", font=FONT, command=self.on_detection).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Clear", bg="#7f8c8d", fg="white", font=FONT, command=self.clear_detection_fields).pack(side="left", padx=6)

    def clear_detection_fields(self):
        self.d_proc.delete(0, tk.END)
        self.d_res.delete(0, tk.END)
        self.d_alloc.delete("1.0", tk.END)
        self.d_request.delete("1.0", tk.END)
        self.canvas_detect.delete("all")

    def on_detection(self):
        try:
            p = int(self.d_proc.get())
            r = int(self.d_res.get())
            # --- IMPROVEMENT: Use 0-based indexing ---
            processes = [f"P{i}" for i in range(p)]
            resources = [f"R{j}" for j in range(r)]
            
            allocation = parse_matrix(self.d_alloc.get("1.0", tk.END))
            request = parse_matrix(self.d_request.get("1.0", tk.END))

            # This function needs to be fixed in detection.py
            has_cycle, cycle_nodes = detect_deadlock_and_cycle(processes, resources, allocation, request)

            if has_cycle:
                self.detect_vis.draw_rag(processes, resources, allocation, request, highlight_nodes=set(cycle_nodes))
                # The root cause is that cycle_nodes is not a full cycle
                messagebox.showerror("Deadlock Detected", f"A deadlock cycle was found involving these nodes:\n{' -> '.join(cycle_nodes)}")
            else:
                self.detect_vis.draw_rag(processes, resources, allocation, request)
                messagebox.showinfo("No Deadlock", "System is not in a deadlocked state.")
        except Exception as e:
            messagebox.showerror("Input Error", f"An error occurred: {e}")

    # -------------------- Avoidance Tab --------------------
    def build_avoidance_tab(self, frame):
        # ... (GUI building code remains the same)
        top = tk.Frame(frame, bg=BG)
        top.pack(anchor="nw", padx=12, pady=8)

        tk.Label(top, text="Processes:", bg=BG, fg=TEXT, font=FONT).grid(row=0, column=0, sticky="w")
        self.a_proc = tk.Entry(top, width=6, font=FONT)
        self.a_proc.grid(row=0, column=1, padx=6)
        tk.Label(top, text="Resources:", bg=BG, fg=TEXT, font=FONT).grid(row=0, column=2, sticky="w", padx=(12,0))
        self.a_res = tk.Entry(top, width=6, font=FONT)
        self.a_res.grid(row=0, column=3, padx=6)

        mid = tk.Frame(frame, bg=BG)
        mid.pack(anchor="nw", padx=12, fill="x")

        pane = tk.PanedWindow(mid, orient=tk.HORIZONTAL, bg=BG, sashwidth=5, sashrelief=tk.RAISED)
        pane.pack(fill="x", expand=True, pady=4)
        
        alloc_frame = tk.Frame(pane, bg=BG)
        tk.Label(alloc_frame, text="Allocation matrix:", bg=BG, fg=TEXT, font=FONT).pack(anchor="w")
        self.a_alloc = tk.Text(alloc_frame, height=5, font=FONT, bg=CANVAS_BG, fg=TEXT, insertbackground=TEXT)
        self.a_alloc.pack(fill="x", expand=True)
        pane.add(alloc_frame, stretch="always")

        max_frame = tk.Frame(pane, bg=BG)
        tk.Label(max_frame, text="Max matrix:", bg=BG, fg=TEXT, font=FONT).pack(anchor="w")
        self.a_max = tk.Text(max_frame, height=5, font=FONT, bg=CANVAS_BG, fg=TEXT, insertbackground=TEXT)
        self.a_max.pack(fill="x", expand=True)
        pane.add(max_frame, stretch="always")

        avail_frame = tk.Frame(mid, bg=BG)
        avail_frame.pack(fill="x", expand=True, pady=4)
        tk.Label(avail_frame, text="Available vector:", bg=BG, fg=TEXT, font=FONT).pack(anchor="w")
        self.a_avail = tk.Entry(avail_frame, width=20, font=FONT, bg=CANVAS_BG, fg=TEXT, insertbackground=TEXT)
        self.a_avail.pack(anchor="w")
        
        # No canvas needed for avoidance as it's a state check, not a graph problem
        
        btn_frame = tk.Frame(frame, bg=BG)
        btn_frame.pack(padx=12, pady=6, anchor="w")
        tk.Button(btn_frame, text="Run Banker's Algorithm", bg=ACCENT, fg="white", font=FONT, command=self.on_avoidance).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Clear", bg="#7f8c8d", fg="white", font=FONT, command=self.clear_avoidance_fields).pack(side="left", padx=6)

    def clear_avoidance_fields(self):
        self.a_proc.delete(0, tk.END)
        self.a_res.delete(0, tk.END)
        self.a_alloc.delete("1.0", tk.END)
        self.a_max.delete(0, tk.END)
        self.a_avail.delete(0, tk.END)

    def on_avoidance(self):
        try:
            p = int(self.a_proc.get())
            r = int(self.a_res.get())
            # --- IMPROVEMENT: Use 0-based indexing ---
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

# -------------------- Run App --------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = DeadlockApp(root)
    root.mainloop()