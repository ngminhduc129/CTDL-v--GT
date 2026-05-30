import tkinter as tk
from tkinter import ttk, messagebox
import json
import heapq
from loaddata import load_data
from MinHeap_Graph import Graph
from findShortestPath_reconstructPath import findShortestPath
from PIL import Image, ImageTk

def saveData(filename, start_node, end_node, result):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=== KẾT QUẢ TÌM ĐƯỜNG HUST ===\n")
            f.write(f"Điểm đi: {start_node}\n")
            f.write(f"Điểm đến: {end_node}\n")
            if result['path']:
                f.write(f"Lộ trình: {' -> '.join(map(str, result['path']))}\n")
                f.write(f"Tổng quãng đường: {result['distance']} mét\n")
            else:
                f.write("Trạng thái: Không tìm thấy đường đi.\n")
        return True
    except Exception as e:
        print(f"Lỗi khi lưu file: {e}")
        return False

class HUST_Nav_App:
    def __init__(self, root):
        self.root = root
        self.root.title("HUST Pathfinding System - Cinematic Edition")
        self.root.state('zoomed') # Mở to toàn màn hình
        
        # --- BẢNG MÀU CINEMATIC ---
        self.c_bg = "#0d1117"           
        self.c_panel = "#161b22"        
        self.c_text = "#c9d1d9"         
        self.c_text_hl = "#ffffff"      
        self.c_neon_red = "#ff304f"     
        self.c_neon_green = "#2ea043"   
        self.c_dim_line = "#30363d"     
        self.c_node_bg = "#1f2428"      
        self.c_explore_node = "#f1c40f" 
        self.c_explore_edge = "#d35400" 
        self.root.configure(bg=self.c_bg)

        self.current_path = None 
        self.is_animating = False

        self.graph_dict, self.nodes_data = load_data("map_data.json")
        if not self.graph_dict:
            messagebox.showerror("Lỗi", "Không tìm thấy file map_data.json!")
            root.destroy()
            return

        self.hust_graph = Graph()
        for node in self.nodes_data:
            self.hust_graph.addNode(node['id'])
        
        with open('map_data.json', 'r', encoding='utf-8') as f:
            edges = json.load(f)['edges']
            for edge in edges:
                self.hust_graph.addEdge(edge['from'], edge['to'], edge['weight'])

        # Lấy kích thước ảnh gốc để làm cơ sở tính tỷ lệ co giãn
        try:
            self.original_bg = Image.open("hust_map.png")
            self.orig_w, self.orig_h = self.original_bg.size
        except Exception as e:
            print(f"Không tìm thấy ảnh nền: {e}")
            self.orig_w, self.orig_h = 900, 750

        self.canvas_w = 0
        self.canvas_h = 0
        self.scale_ratio = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.setup_ui()
        
        # Sự kiện tự động co giãn bản đồ khi kích thước cửa sổ (Canvas) thay đổi
        self.canvas.bind("<Configure>", self.on_canvas_resize)

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground=self.c_panel, background=self.c_dim_line, foreground="white", borderwidth=0)

        sidebar = tk.Frame(self.root, width=320, bg=self.c_panel, padx=25, pady=25)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(sidebar, text="HỆ THỐNG TÌM ĐƯỜNG", font=("Segoe UI", 16, "bold"), bg=self.c_panel, fg=self.c_neon_red).pack(pady=(10, 0))
        tk.Label(sidebar, text="HUST CAMPUS", font=("Segoe UI", 12, "bold"), bg=self.c_panel, fg=self.c_text).pack(pady=(0, 20))
        
        node_names = [n['name'] for n in self.nodes_data]
        
        tk.Label(sidebar, text="📍 ĐIỂM XUẤT PHÁT", font=("Segoe UI", 9, "bold"), bg=self.c_panel, fg=self.c_text).pack(anchor="w")
        self.start_cb = ttk.Combobox(sidebar, values=node_names, width=35, font=("Segoe UI", 10))
        self.start_cb.pack(pady=(5, 15), ipady=4)

        tk.Label(sidebar, text="🏁 ĐIỂM ĐẾN", font=("Segoe UI", 9, "bold"), bg=self.c_panel, fg=self.c_text).pack(anchor="w")
        self.end_cb = ttk.Combobox(sidebar, values=node_names, width=35, font=("Segoe UI", 10))
        self.end_cb.pack(pady=(5, 25), ipady=4)

        self.btn_search = tk.Button(sidebar, text="TRỰC QUAN HÓA THUẬT TOÁN", bg=self.c_neon_red, fg=self.c_text_hl, 
                        font=("Segoe UI", 11, "bold"), borderwidth=0, cursor="hand2", 
                        activebackground="#d11a35", command=self.handle_search)
        self.btn_search.pack(pady=10, fill=tk.X, ipady=8)

        self.res_label = tk.Label(sidebar, text="\nChờ lệnh tìm kiếm...", bg=self.c_panel, fg=self.c_dim_line, wraplength=260, justify="left", font=("Segoe UI", 11))
        self.res_label.pack(pady=20, fill=tk.X)

        self.canvas = tk.Canvas(self.root, bg=self.c_bg, highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    def on_canvas_resize(self, event):
        """Tự động tính toán để phóng to ảnh vừa khít không gian trống mà không làm méo ảnh"""
        if self.is_animating or event.widget != self.canvas: 
            return
        if event.width == self.canvas_w and event.height == self.canvas_h: 
            return

        self.canvas_w = event.width
        self.canvas_h = event.height

        # Tính toán tỷ lệ duy trì khung hình (Aspect Ratio)
        ratio = min(self.canvas_w / self.orig_w, self.canvas_h / self.orig_h)
        self.scale_ratio = ratio
        new_w = int(self.orig_w * ratio)
        new_h = int(self.orig_h * ratio)

        # Căn giữa ảnh vào Canvas
        self.offset_x = (self.canvas_w - new_w) // 2
        self.offset_y = (self.canvas_h - new_h) // 2

        # Tạo ảnh mới theo tỷ lệ
        resized_img = self.original_bg.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized_img)
        
        self.canvas.delete("bg_image")
        self.canvas.create_image(self.offset_x, self.offset_y, image=self.bg_photo, anchor="nw", tags="bg_image")
        
        self.draw_map(self.current_path)

    def draw_orthogonal_line(self, x1, y1, x2, y2, color, width, tags, is_dashed=False):
        mid_x = (x1 + x2) / 2
        d = (2, 4) if is_dashed else ""
        self.canvas.create_line(x1, y1, mid_x, y1, fill=color, width=width, tags=tags, capstyle=tk.ROUND, dash=d)
        self.canvas.create_line(mid_x, y1, mid_x, y2, fill=color, width=width, tags=tags, capstyle=tk.ROUND, dash=d)
        self.canvas.create_line(mid_x, y2, x2, y2, fill=color, width=width, tags=tags, capstyle=tk.ROUND, dash=d)

    def draw_map(self, path=None):
        self.current_path = path
        self.canvas.delete("drawn_elements")
        node_lookup = {n['id']: n for n in self.nodes_data}
        
        # Hàm tính toán tọa độ ánh xạ hoàn hảo (Tuyệt đối không lệch)
        def get_coords(node):
            nx = node['x'] * self.scale_ratio + self.offset_x
            ny = node['y'] * self.scale_ratio + self.offset_y
            return nx, ny

        drawn_edges = set()
        for n_id, neighbors in self.graph_dict.items():
            n1 = node_lookup[n_id]
            x1, y1 = get_coords(n1)
            for neighbor_id, _ in neighbors:
                edge_tuple = tuple(sorted((n_id, neighbor_id)))
                if edge_tuple not in drawn_edges:
                    n2 = node_lookup[neighbor_id]
                    x2, y2 = get_coords(n2)
                    edge_tag = f"edge_{edge_tuple[0]}_{edge_tuple[1]}"
                    self.draw_orthogonal_line(x1, y1, x2, y2, color="#777777", width=1, tags=("drawn_elements", edge_tag), is_dashed=True)
                    drawn_edges.add(edge_tuple)

        if path:
            for i in range(len(path) - 1):
                p1, p2 = path[i], path[i+1]
                edge_tag = f"edge_{min(p1, p2)}_{max(p1, p2)}"
                self.canvas.itemconfig(edge_tag, fill=self.c_neon_red, width=5, dash="")

        for node in self.nodes_data:
            x, y = get_coords(node)
            if "Nga" not in node['name']:
                node_tag = f"node_{node['id']}"
                fill_col = self.c_neon_red if path and node['id'] in path else self.c_node_bg
                out_col = "#ffffff" if path and node['id'] in path else self.c_dim_line
                size = 7 if path and node['id'] in path else 4 
                
                self.canvas.create_oval(x-size, y-size, x+size, y+size, fill=fill_col, outline=out_col, width=1.5, tags=("drawn_elements", node_tag))
                
                if path and node['id'] in path:
                    self.canvas.create_text(x+1, y+17, text=node['name'], font=("Segoe UI", 9, "bold"), fill="#ffffff", tags=("drawn_elements", f"text_{node['id']}"))
                    self.canvas.create_text(x, y+16, text=node['name'], font=("Segoe UI", 9, "bold"), fill=self.c_bg, tags=("drawn_elements", f"text_{node['id']}"))
                else:
                    self.canvas.create_text(x+1, y+15, text=node['name'], font=("Segoe UI", 8), fill="#ffffff", tags=("drawn_elements", f"text_{node['id']}"))
                    self.canvas.create_text(x, y+14, text=node['name'], font=("Segoe UI", 8), fill="#555555", tags=("drawn_elements", f"text_{node['id']}"))

    def handle_search(self):
        if self.is_animating: return 

        s_name = self.start_cb.get()
        e_name = self.end_cb.get()
        if not s_name or not e_name:
            messagebox.showwarning("Nhắc nhở", "Vui lòng chọn đầy đủ địa điểm!")
            return
        
        s_id = next(n['id'] for n in self.nodes_data if n['name'] == s_name)
        e_id = next(n['id'] for n in self.nodes_data if n['name'] == e_name)
        
        self.final_result = findShortestPath(self.hust_graph, s_id, e_id)
        
        if self.final_result['path']:
            self.res_label.config(text="Đang quét không gian đồ thị...", fg=self.c_explore_node)
            self.btn_search.config(state="disabled", bg="#555555")
            self.is_animating = True
            
            self.draw_map(None)
            self.animate_dijkstra(s_id, e_id)
        else:
            self.res_label.config(text="❌ Không có đường đi khả thi!", fg=self.c_neon_red)

    def animate_dijkstra(self, start_id, end_id):
        distances = {n['id']: float('inf') for n in self.nodes_data}
        distances[start_id] = 0
        pq = [(0, start_id)]
        visited = set()

        def step():
            if not pq:
                self.finish_animation(start_id, end_id)
                return

            current_dist, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                self.root.after(100, step) 
                return
                
            visited.add(current_node)

            self.canvas.itemconfig(f"node_{current_node}", fill=self.c_explore_node, outline="#ffffff")
            self.canvas.itemconfig(f"text_{current_node}", font=("Segoe UI", 9, "bold"))

            if current_node == end_id:
                self.finish_animation(start_id, end_id)
                return

            for neighbor, weight in self.graph_dict[current_node]:
                if neighbor not in visited:
                    new_dist = current_dist + weight
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        heapq.heappush(pq, (new_dist, neighbor))
                        
                        edge_tag = f"edge_{min(current_node, neighbor)}_{max(current_node, neighbor)}"
                        self.canvas.itemconfig(edge_tag, fill=self.c_explore_edge, width=3, dash="")

            self.root.after(400, step) 

        step()

    def finish_animation(self, s_id, e_id):
        self.is_animating = False
        self.btn_search.config(state="normal", bg=self.c_neon_red)
        self.draw_map(self.final_result['path'])
        
        msg = f"✓ ĐÃ TÌM THẤY LỘ TRÌNH\n\nKhoảng cách tối ưu:\n{self.final_result['distance']} mét"
        self.res_label.config(text=msg, fg=self.c_neon_green, font=("Segoe UI", 12, "bold"))
        
        s_name = next(n['name'] for n in self.nodes_data if n['id'] == s_id)
        e_name = next(n['name'] for n in self.nodes_data if n['id'] == e_id)
        saveData("history_search.txt", s_name, e_name, self.final_result)

if __name__ == "__main__":
    root = tk.Tk()
    app = HUST_Nav_App(root)
    root.mainloop()