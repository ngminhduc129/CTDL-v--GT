class MinHeap:
    #Khởi tạo danh sách lưu trữ dữ liệu
    def __init__(self):
        self.heap = []

    def push(self, priority, item):
        # Thêm phần tử vào cuối và đẩy dần lên để duy trì tính chất min-heap
        self.heap.append((priority, item))
        self._bubble_up(len(self.heap) - 1)

    def pop(self):
        if self.is_empty():
            return None
        # Đổi chỗ phần tử đầu và là phần tử nhỏ nhất với phần tử cuối, sau đó lấy phần tử cuối ra
        self._swap(0, len(self.heap) - 1)
        min_item = self.heap.pop()
        # Chìm phần tử đầu mới xuống, khôi phục tính chất min-heap
        self._sink_down(0)
        return min_item

    #Kiểm tra xem hàng đợi có rỗng hay không
    def is_empty(self):
        return len(self.heap) == 0

    def _bubble_up(self, index):   #Đưa phần tử lên vị trí chính xác
        parent = (index - 1) // 2 #Tìm kiếm vị trí của nút cha
        if index > 0 and self.heap[index][0] < self.heap[parent][0]: #Kiểm tra vị trí đã thỏa mãn hay chưa
            self._swap(index, parent)  #Hoán đổi vị trí
            self._bubble_up(parent)    #Đệ quy tiếp túc tìm vị trí chính xác

    def _sink_down(self, index):  #Đưa phần tử xuống vị trí chính xác
        smallest = index          #Gán cho vị trí nhỏ nhất
        left = 2 * index + 1      #Vị trí của phần tử trái
        right = 2 * index + 2     #Vị trí của phần tử phải

        if left < len(self.heap) and self.heap[left][0] < self.heap[smallest][0]:  #So sánh với phần tử trái
            smallest = left
        if right < len(self.heap) and self.heap[right][0] < self.heap[smallest][0]: #So sánh với phần tử phải
            smallest = right

        if smallest != index:          #Kiểm tra vị trí
            self._swap(index, smallest)
            self._sink_down(smallest)  #Đệ quy tìm vị trí chính xác

    def _swap(self, i, j):   #Hoán đổi vị trí trong hàng đợi
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

class Graph:
    def __init__(self):    #Khởi tạo
        self.adjacency_list = {}

    def addNode(self, node):   #Thêm node vào
        if node not in self.adjacency_list:     #Kiểm tra xem node đấy đã tồn tại chưa
            self.adjacency_list[node] = []

    def addEdge(self, node1, node2, weight):    #Thêm đường đi giữa hai điểm
        self.addNode(node1)
        self.addNode(node2)
        # Đồ thị vô hướng
        self.adjacency_list[node1].append({"node": node2, "weight": weight})  #Thêm đường đi từ node1 đến node2
        self.adjacency_list[node2].append({"node": node1, "weight": weight})  #Thêm đường đi từ node2 đến node1

    def getNeighbors(self, node):
        return self.adjacency_list.get(node, [])  #Lấy danh sách các node kề
