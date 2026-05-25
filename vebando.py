import json

# 1. Đọc dữ liệu từ file map_data.json
with open('map_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 2. Tạo cấu trúc Danh sách kề
# Cấu trúc: { "ID_Nguồn": [ {"to": ID_Đích, "weight": Khoảng_cách}, ... ] }
adjacency_list = {}

# Khởi tạo danh sách trống cho tất cả các node
for node in data['nodes']:
    adjacency_list[node['id']] = []

# Đổ dữ liệu từ edges vào
for edge in data['edges']:
    u = edge['from']
    v = edge['to']
    w = edge['weight']
    
    # Thêm đường đi từ u đến v
    adjacency_list[u].append({"to": v, "weight": w})
    # Nếu là đường 2 chiều, bạn thêm dòng dưới đây:
    adjacency_list[v].append({"to": u, "weight": w})

# 3. Lưu ra file để dùng cho Dijkstra
with open('danh_sach_ke.json', 'w', encoding='utf-8') as f_out:
    json.dump(adjacency_list, f_out, indent=4, ensure_ascii=False)

print("=> Đã tạo xong file danh_sach_ke.json!")