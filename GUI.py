import tkinter as tk
from tkinter import ttk, messagebox
import json
from loaddata import load_data
from MinHeap_Graph import Graph
from findShortestPath_reconstructPath import findShortestPath

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
        self.root.title("HUST Pathfinding System - Member 3.3")
        self.root.geometry("1200x800")
        
        # Load dữ liệu từ loaddata.py
        self.graph_dict, self.nodes_data = load_data("map_data.json")
        if not self.graph_dict:
            messagebox.showerror("Lỗi", "Không tìm thấy file map_data.json!")
            root.destroy()
            return

        # Khởi tạo Graph thuật toán
        self.hust_graph = Graph()
        for node in self.nodes_data:
            self.hust_graph.addNode(node['id'])
        
        with open('map_data.json', 'r', encoding='utf-8') as f:
            edges = json.load(f)['edges']
            for edge in edges:
                self.hust_graph.addEdge(edge['from'], edge['to'], edge['weight'])

        self.setup_ui()
        self.draw_map()

    def setup_ui(self):
        # Sidebar
        sidebar = tk.Frame(self.root, width=300, bg="#f5f5f5", padx=20, pady=20)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(sidebar, text="HỆ THỐNG TÌM ĐƯỜNG HUST", font=("Arial", 12, "bold"), bg="#f5f5f5").pack(pady=10)
        
        node_names = [n['name'] for n in self.nodes_data]
        
        tk.Label(sidebar, text="Điểm xuất phát:", bg="#f5f5f5").pack(anchor="w")
        self.start_cb = ttk.Combobox(sidebar, values=node_names, width=35)
        self.start_cb.pack(pady=5)

        tk.Label(sidebar, text="Điểm đến:", bg="#f5f5f5").pack(anchor="w")
        self.end_cb = ttk.Combobox(sidebar, values=node_names, width=35)
        self.end_cb.pack(pady=5)

        tk.Button(sidebar, text="TÌM ĐƯỜNG", bg="#e31b23", fg="white", font=("Arial", 10, "bold"), 
                  command=self.handle_search).pack(pady=20, fill=tk.X)

        self.res_label = tk.Label(sidebar, text="Kết quả sẽ hiển thị ở đây", bg="#f5f5f5", wraplength=250, justify="left", font=("Arial", 11))
        self.res_label.pack(pady=10)

        # Canvas vẽ bản đồ
        self.canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    def lat_lng_to_pixels(self, lat, lng):
        x = (lng - 105.841) * 130000 + 50
        y = (21.0080 - lat) * 125000 + 60
        return x, y

    def draw_orthogonal_line(self, x1, y1, x2, y2, color, width):
        """Hàm vẽ đường gấp khúc vuông góc thay vì đường chéo"""
        # Tính điểm giữa trục X để bẻ góc, giúp đường đi gọn gàng hơn
        mid_x = (x1 + x2) / 2
        
        # Vẽ 3 đoạn: Ngang -> Dọc -> Ngang
        self.canvas.create_line(x1, y1, mid_x, y1, fill=color, width=width)
        self.canvas.create_line(mid_x, y1, mid_x, y2, fill=color, width=width)
        self.canvas.create_line(mid_x, y2, x2, y2, fill=color, width=width)

    def draw_map(self, path=None):
        self.canvas.delete("all")
        node_lookup = {n['id']: n for n in self.nodes_data}
        
        # 1. Vẽ toàn bộ đường đi
        drawn_edges = set() # Tránh vẽ đè 2 lần cho đường 2 chiều
        for n_id, neighbors in self.graph_dict.items():
            n1 = node_lookup[n_id]
            x1, y1 = self.lat_lng_to_pixels(n1['lat'], n1['lng'])
            for neighbor_id, _ in neighbors:
                edge_tuple = tuple(sorted((n_id, neighbor_id)))
                if edge_tuple not in drawn_edges:
                    n2 = node_lookup[neighbor_id]
                    x2, y2 = self.lat_lng_to_pixels(n2['lat'], n2['lng'])
                    # Gọi hàm vẽ vuông góc
                    self.draw_orthogonal_line(x1, y1, x2, y2, color="#e0e0e0", width=2)
                    drawn_edges.add(edge_tuple)

        # 2. Vẽ đè đường đi ngắn nhất (màu đỏ đậm)
        if path:
            for i in range(len(path) - 1):
                p1 = node_lookup[path[i]]
                p2 = node_lookup[path[i+1]]
                lx1, ly1 = self.lat_lng_to_pixels(p1['lat'], p1['lng'])
                lx2, ly2 = self.lat_lng_to_pixels(p2['lat'], p2['lng'])
                # Gọi hàm vẽ vuông góc cho đường được highlight
                self.draw_orthogonal_line(lx1, ly1, lx2, ly2, color="#e31b23", width=5)

        # 3. Vẽ các nút (Tòa nhà) lên trên cùng để không bị đường kẻ đè lên
        for node in self.nodes_data:
            x, y = self.lat_lng_to_pixels(node['lat'], node['lng'])
            
            # --- ĐOẠN CODE MỚI THÊM VÀO ĐÂY ---
            # Kiểm tra nếu tên không chứa chữ "Nga tu" thì mới vẽ hình tròn và in chữ
            if "Nga tu" not in node['name']:
                color = "#e31b23" if path and node['id'] in path else "#2c3e50"
                size = 7 if path and node['id'] in path else 5
                
                self.canvas.create_oval(x-size, y-size, x+size, y+size, fill=color, outline="white", width=2)
                self.canvas.create_text(x, y+16, text=node['name'], 
                                        font=("Arial", 8, "bold" if path and node['id'] in path else "normal"), 
                                        fill="#333")
            # ----------------------------------
    def handle_search(self):
        s_name = self.start_cb.get()
        e_name = self.end_cb.get()
        
        if not s_name or not e_name:
            messagebox.showwarning("Ngoại lệ", "Vui lòng chọn đầy đủ địa điểm xuất phát và đích đến!")
            return

        try:
            s_id = next(n['id'] for n in self.nodes_data if n['name'] == s_name)
            e_id = next(n['id'] for n in self.nodes_data if n['name'] == e_name)
        except StopIteration:
            messagebox.showerror("Lỗi dữ liệu", "Tên địa điểm không khớp với cơ sở dữ liệu!")
            return

        # Chạy Dijkstra
        result = findShortestPath(self.hust_graph, s_id, e_id)

        if result['path']:
            self.draw_map(result['path']) # Vẽ lại bản đồ với đường màu đỏ
            msg = f"✓ Đã tìm thấy lộ trình!\n\nTổng khoảng cách:\n{result['distance']} mét"
            self.res_label.config(text=msg, fg="#27ae60")
            
            # Ghi file saveData
            saveData("history_search.txt", s_name, e_name, result)
        else:
            messagebox.showinfo("Thông báo", "Không có đường đi khả thi giữa 2 điểm này!")

if __name__ == "__main__":
    root = tk.Tk()
    app = HUST_Nav_App(root)
    root.mainloop()