# gui_stage2.py
import tkinter as tk
from tkinter import messagebox
from detection import detect_deadlock_and_cycle
import math

# helpers to parse user input (same as before)
def parse_matrix(text):
    return [list(map(int, row.split())) for row in text.strip().split("\n") if row.strip()]

def parse_list(text):
    return list(map(int, text.strip().split()))

# drawing helpers
NODE_RADIUS = 25
RES_WIDTH = 40
RES_HEIGHT = 30
PADDING = 60

class RAGVisualizer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.node_positions = {}  # node_name -> (cx, cy)
        self.node_items = {}      # node_name -> canvas item id (oval/rect)
        self.label_items = {}     # node_name -> text id
        self.edge_items = []      # list of line ids

    def clear(self):
        self.canvas.delete("all")
        self.node_positions.clear()
        self.node_items.clear()
        self.label_items.clear()
        self.edge_items.clear()

    def layout_nodes(self, processes, resources):
        """Place process nodes vertically on left and resource nodes vertically on right."""
        w = int(self.canvas.cget("width"))
        h = int(self.canvas.cget("height"))
        left_x = PADDING + NODE_RADIUS
        right_x = w - PADDING - NODE_RADIUS
        # vertical spacing
        p_count = max(1, len(processes))
        r_count = max(1, len(resources))
        left_gap = max(1, (h - 2*PADDING) / (p_count))
        right_gap = max(1, (h - 2*PADDING) / (r_count))

        # processes (left)
        for i, p in enumerate(processes):
            cx = left_x
            cy = PADDING + left_gap/2 + i*left_gap
            self.node_positions[p] = (cx, cy)

        # resources (right)
        for j, r in enumerate(resources):
            cx = right_x
            cy = PADDING + right_gap/2 + j*right_gap
            self.node_positions[r] = (cx, cy)

    def draw_nodes(self, processes, resources, highlight_nodes=set()):
        # draw processes as circles
        for p in processes:
            cx, cy = self.node_positions[p]
            color = "red" if p in highlight_nodes else "white"
            outline = "black" if p not in highlight_nodes else "red"
            oid = self.canvas.create_oval(cx-NODE_RADIUS, cy-NODE_RADIUS, cx+NODE_RADIUS, cy+NODE_RADIUS,
                                          fill=color, outline=outline, width=2)
            tid = self.canvas.create_text(cx, cy, text=p)
            self.node_items[p] = oid
            self.label_items[p] = tid

        # draw resources as rectangles
        for r in resources:
            cx, cy = self.node_positions[r]
            color = "red" if r in highlight_nodes else "white"
            outline = "black" if r not in highlight_nodes else "red"
            oid = self.canvas.create_rectangle(cx-RES_WIDTH/2, cy-RES_HEIGHT/2, cx+RES_WIDTH/2, cy+RES_HEIGHT/2,
                                               fill=color, outline=outline, width=2)
            tid = self.canvas.create_text(cx, cy, text=r)
            self.node_items[r] = oid
            self.label_items[r] = tid

    def draw_edges(self, graph, highlight_nodes=set()):
        # graph: adjacency dict node -> [neighbors]
        # draw arrows from node to each neighbor
        for src, nbrs in graph.items():
            for dst in nbrs:
                x1, y1 = self.node_positions[src]
                x2, y2 = self.node_positions[dst]
                # compute line endpoints so they touch shapes nicely
                dx = x2 - x1
                dy = y2 - y1
                dist = math.hypot(dx, dy)
                if dist == 0:
                    continue
                # offset start/end by radius (approx)
                start_offset = NODE_RADIUS if src.startswith("P") else RES_WIDTH/2
                end_offset = NODE_RADIUS if dst.startswith("P") else RES_WIDTH/2
                sx = x1 + (dx/dist)*start_offset
                sy = y1 + (dy/dist)*start_offset
                ex = x2 - (dx/dist)*end_offset
                ey = y2 - (dy/dist)*end_offset

                color = "red" if (src in highlight_nodes and dst in highlight_nodes) else "black"
                line = self.canvas.create_line(sx, sy, ex, ey, arrow=tk.LAST, width=2, fill=color)
                self.edge_items.append(line)

    def draw_rag(self, processes, resources, allocation, request, cycle_nodes):
        self.clear()
        self.layout_nodes(processes, resources)
        highlight = set(cycle_nodes)
        # draw adjacency graph locally to feed to draw_edges
        graph = {}
        for p in processes:
            graph[p] = []
        for r in resources:
            graph[r] = []
        # allocation edges: resource -> process
        for i, p in enumerate(processes):
            for j, r in enumerate(resources):
                if allocation[i][j] > 0:
                    graph[r].append(p)
        # request edges: process -> resource
        for i, p in enumerate(processes):
            for j, r in enumerate(resources):
                if request[i][j] > 0:
                    graph[p].append(r)

        self.draw_nodes(processes, resources, highlight_nodes=highlight)
        self.draw_edges(graph, highlight_nodes=highlight)


# GUI main window
root = tk.Tk()
root.title("Deadlock Visualizer — RAG View")
root.geometry("900x700")

# Top input frame (reusing previous input design)
frame_top = tk.Frame(root)
frame_top.pack(padx=10, pady=8, anchor="w")

tk.Label(frame_top, text="Processes:").grid(row=0, column=0)
entry_processes = tk.Entry(frame_top, width=5)
entry_processes.grid(row=0, column=1, padx=6)

tk.Label(frame_top, text="Resources:").grid(row=0, column=2)
entry_resources = tk.Entry(frame_top, width=5)
entry_resources.grid(row=0, column=3, padx=6)

# matrices
frame_mid = tk.Frame(root)
frame_mid.pack(padx=10, pady=6)

tk.Label(frame_mid, text="Allocation matrix (rows=processes, cols=resources):").grid(row=0, column=0, sticky="w")
text_allocation = tk.Text(frame_mid, height=5, width=45)
text_allocation.grid(row=1, column=0, padx=6, pady=4)

tk.Label(frame_mid, text="Request matrix (for detection):").grid(row=2, column=0, sticky="w")
text_request = tk.Text(frame_mid, height=5, width=45)
text_request.grid(row=3, column=0, padx=6, pady=4)

# Canvas for graph
canvas = tk.Canvas(root, width=760, height=360, bg="white")
canvas.pack(padx=10, pady=10)

visualizer = RAGVisualizer(canvas)

def on_draw_rag():
    try:
        p = int(entry_processes.get())
        r = int(entry_resources.get())
        processes = [f"P{i+1}" for i in range(p)]
        resources = [f"R{j+1}" for j in range(r)]
        allocation = parse_matrix(text_allocation.get("1.0", tk.END))
        request = parse_matrix(text_request.get("1.0", tk.END))

        # basic validation
        if len(allocation) != p:
            raise ValueError("Allocation rows must equal number of processes")
        if any(len(row) != r for row in allocation):
            raise ValueError("Allocation cols must equal number of resources")
        if len(request) != p or any(len(row) != r for row in request):
            raise ValueError("Request matrix size mismatch")

        has_cycle, cycle_nodes = detect_deadlock_and_cycle(processes, resources, allocation, request)

        visualizer.draw_rag(processes, resources, allocation, request, cycle_nodes)

        if has_cycle:
            messagebox.showerror("Deadlock Detection", f"Deadlock detected!\nNodes in cycle: {', '.join(cycle_nodes)}")
        else:
            messagebox.showinfo("Deadlock Detection", "No deadlock detected.")
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")

# Buttons
frame_btns = tk.Frame(root)
frame_btns.pack(pady=6)
btn_draw = tk.Button(frame_btns, text="Draw RAG & Detect Deadlock", command=on_draw_rag, font=("Arial", 11))
btn_draw.grid(row=0, column=0, padx=8)

btn_quit = tk.Button(frame_btns, text="Exit", command=root.quit, font=("Arial", 11))
btn_quit.grid(row=0, column=1, padx=8)

# sample prefill for convenience
entry_processes.insert(0, "2")
entry_resources.insert(0, "2")
text_allocation.insert("1.0", "1 0\n0 1")
text_request.insert("1.0", "0 1\n1 0")

root.mainloop()
