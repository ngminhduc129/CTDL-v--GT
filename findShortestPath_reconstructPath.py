import MinHeap_Graph

def findShortestPath(graph, source, destination):    #source là đỉnh nguồn, destination là đỉnh đích
    #Khởi tạo
    distances = {node: float('inf') for node in graph.adjacency_list}   #Khởi tạo khoảng cách từ đỉnh nguồn đến tất cả các đỉnh là vô cực
    prev = {node: None for node in graph.adjacency_list}                #Lưu dấu vết đỉnh trước đó

    if source not in distances or destination not in distances:         #Kiểm tra xem có tồn tại trên bản đồ hay không
        return {"distance": float('inf'), "path": []}

    distances[source] = 0                                               #Khởi tạo khoảng cách = 0
    pq = MinHeap_Graph.MinHeap()
    pq.push(0, source)                                                  #Đưa vào hàng đợi, ưu tiên cao nhất

    #Vòng lặp chính
    while not pq.is_empty():
        current_distance, current_node = pq.pop()                       #Lấy điểm có khoảng cách ngắn nhất hiện tại

        #Dừng sớm nếu đã đến được đích
        if current_node == destination:
            break

        #Bỏ qua nếu tìm thấy một khoảng cách cũ trong hàng đợi lớn hơn khoảng cách hiện tại
        if current_distance > distances[current_node]:
            continue

        #Duyệt qua các điểm kề
        for neighbor in graph.getNeighbors(current_node):
            next_node = neighbor["node"]
            weight = neighbor["weight"]

            #Tính toán khoảng cách mới
            distance = current_distance + weight

            #Cập nhật nếu đường đi mới ngắn hơn
            if distance < distances[next_node]:
                distances[next_node] = distance
                prev[next_node] = current_node
                pq.push(distance, next_node)

    #Nếu không thể đi tới đích
    if distances[destination] == float('inf'):
        return {"distance": float('inf'), "path": []}

    return {
        "distance": distances[destination],
        "path": reconstructPath(prev, destination)
    }


def reconstructPath(prev, destination):            #Lưu vết đường đi
    path = []
    current = destination

    #Truy vết ngược từ đích về nguồn
    while current is not None:
        path.append(current)
        current = prev.get(current)

    #Đảo ngược mảng để có thứ tự từ nguồn -> đích
    path.reverse()
    return path

if __name__ == "__main__":
    graph = MinHeap_Graph.Graph()
    graph.addEdge("A", "B", 1)
    graph.addEdge("A", "C", 4)
    graph.addEdge("B", "C", 2)
    graph.addEdge("B", "D", 5)
    graph.addEdge("C", "D", 1)

    result = findShortestPath(graph, "A", "D")
    print(f"Shortest distance from A to D: {result['distance']}")
    print(f"Path from A to D: {' -> '.join(result['path'])}")