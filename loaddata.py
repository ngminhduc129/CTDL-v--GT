import json

def load_data(file_path="map_data.json"):
    """
    Hàm đọc dữ liệu từ file JSON và chuyển đổi thành cấu trúc đồ thị (Danh sách kề).
    Trả về: (graph, nodes_list)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 1. Lấy danh sách các nút (địa điểm) để làm UI
        nodes_list = data['nodes']
        
        # 2. Tạo Danh sách kề (Adjacency List) cho thuật toán Dijkstra
        graph = {}
        
        # Khởi tạo danh sách trống cho từng tòa nhà dựa trên ID
        for node in nodes_list:
            graph[node['id']] = []
            
        # 3. Đổ dữ liệu các con đường (edges) vào đồ thị
        for edge in data['edges']:
            u = edge['from']
            v = edge['to']
            w = edge['weight']
            
            # Thêm quan hệ lân cận (đường 2 chiều)
            # Mỗi điểm sẽ lưu danh sách các bộ (điểm_đến, khoảng_cách)
            graph[u].append((v, w))
            graph[v].append((u, w))
            
        print(f"--- Đã tải thành công {len(nodes_list)} địa điểm từ hệ thống ---")
        return graph, nodes_list
    
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file '{file_path}'. Hãy kiểm tra lại đường dẫn!")
        return None, None
    except json.JSONDecodeError:
        print("Lỗi: File JSON bị sai định dạng cú pháp!")
        return None, None
    

    # Gọi hàm để chạy thử
graph, nodes = load_data("./map_data.json")

# Nếu chạy thành công thì in thử ra để kiểm tra
if graph:
    print("--- ĐÃ TẢI DỮ LIỆU THÀNH CÔNG ---")
    print(f"Số lượng tòa nhà: {len(nodes)}")
    for node_id, neighbors in graph.items():
     print(f"Điểm {node_id} nối với: {neighbors}")