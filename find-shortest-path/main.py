import heapq
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyBboxPatch
import matplotlib.patches as mpatches


def visualize_graph(graph, shortest_path=None, start=None, end=None, title="Graph Visualization", filename=None):
    """
    Vẽ đồ thị với matplotlib
    
    Input:
    - graph: Dictionary của đồ thị
    - shortest_path: List các đỉnh trong đường đi ngắn nhất (optional)
    - start: Đỉnh bắt đầu (optional)
    - end: Đỉnh kết thúc (optional)
    - title: Tiêu đề của đồ thị
    - filename: Tên file PNG để lưu (optional). Nếu không có, sẽ hiển thị trực tiếp
    """
    # Tạo đồ thị NetworkX
    G = nx.Graph()
    
    # Thêm các cạnh vào đồ thị
    for node, edges in graph.items():
        for neighbor, weight in edges:
            G.add_edge(node, neighbor, weight=weight)
    
    # Tạo figure và axis
    plt.figure(figsize=(14, 10))
    
    # Sử dụng Kamada-Kawai layout - tốt hơn cho việc thể hiện khoảng cách
    # Layout này cố gắng đặt các node theo tỷ lệ với khoảng cách thực tế
    pos = nx.kamada_kawai_layout(G, weight='weight', scale=3)
    
    # Lấy tất cả trọng số để tính toán độ dày cạnh
    edge_weights = [G[u][v]['weight'] for u, v in G.edges()]
    max_weight = max(edge_weights) if edge_weights else 1
    min_weight = min(edge_weights) if edge_weights else 1
    
    # Vẽ tất cả các cạnh với độ dày tỷ lệ nghịch với khoảng cách
    # (cạnh ngắn hơn sẽ dày hơn)
    for (u, v) in G.edges():
        weight = G[u][v]['weight']
        # Độ dày từ 1 đến 5, tỷ lệ nghịch với weight
        width = 5 - ((weight - min_weight) / (max_weight - min_weight)) * 4 if max_weight != min_weight else 3
        nx.draw_networkx_edges(G, pos, [(u, v)], edge_color='gray', width=width, alpha=0.6)
    
    # Vẽ nhãn trọng số của cạnh với font lớn hơn và background
    edge_labels = nx.get_edge_attributes(G, 'weight')
    # Format nhãn với đơn vị km
    formatted_labels = {k: f'{v}km' for k, v in edge_labels.items()}
    nx.draw_networkx_edge_labels(G, pos, formatted_labels, font_size=11, 
                                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    # Màu sắc cho các node
    node_colors = []
    for node in G.nodes():
        if node == start:
            node_colors.append('lightgreen')  # Màu xanh lá cho điểm bắt đầu
        elif node == end:
            node_colors.append('lightcoral')  # Màu đỏ nhạt cho điểm kết thúc
        elif shortest_path and node in shortest_path:
            node_colors.append('lightyellow')  # Màu vàng cho các node trên đường đi ngắn nhất
        else:
            node_colors.append('lightblue')  # Màu xanh dương cho các node khác
    
    # Vẽ các node với viền
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000, alpha=0.9,
                          edgecolors='black', linewidths=2)
    
    # Vẽ nhãn cho các node
    nx.draw_networkx_labels(G, pos, font_size=14, font_weight='bold')
    
    # Nếu có đường đi ngắn nhất, vẽ nó với màu đặc biệt
    if shortest_path and len(shortest_path) > 1:
        path_edges = [(shortest_path[i], shortest_path[i+1]) for i in range(len(shortest_path)-1)]
        # Vẽ đường đi ngắn nhất với độ dày lớn hơn
        for i in range(len(shortest_path)-1):
            u, v = shortest_path[i], shortest_path[i+1]
            nx.draw_networkx_edges(G, pos, [(u, v)], edge_color='red', width=6, alpha=0.8,
                                 style='solid', arrows=True, arrowsize=20, arrowstyle='->')
    
    # Thêm tiêu đề
    plt.title(title, fontsize=16, fontweight='bold')
    
    # Thêm chú giải
    legend_elements = [
        mpatches.Patch(color='lightgreen', label='Điểm bắt đầu'),
        mpatches.Patch(color='lightcoral', label='Điểm kết thúc'),
        mpatches.Patch(color='lightyellow', label='Trên đường đi ngắn nhất'),
        mpatches.Patch(color='lightblue', label='Các điểm khác'),
        mpatches.Patch(color='red', label='Đường đi ngắn nhất', linewidth=3),
        mpatches.Patch(color='gray', label='Độ dày cạnh tỷ lệ nghịch với khoảng cách', alpha=0.6)
    ]
    plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.2, 1))
    
    # Ẩn các trục
    plt.axis('off')
    plt.tight_layout()
    
    # Lưu vào file nếu có filename, nếu không thì hiển thị
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Đã lưu đồ thị vào file: {filename}")
        plt.close()
    else:
        plt.show()


def dijkstra(graph, start, end):
    """
    Tìm đường đi ngắn nhất từ start đến end bằng Dijkstra

    Input:
    - graph: Dictionary, mỗi key là một đỉnh,
             value là list các (đỉnh_kề, trọng_số)
    - start: Đỉnh bắt đầu
    - end: Đỉnh kết thúc

    Output:
    - Tuple (khoảng_cách, đường_đi)
    """

    # Khởi tạo khoảng cách
    distances = {node: float("inf") for node in graph}
    distances[start] = 0

    # Lưu đường đi
    previous = {node: None for node in graph}

    # Priority queue: (khoảng_cách, đỉnh)
    pq = [(0, start)]
    visited = set()

    while pq:
        current_dist, current = heapq.heappop(pq)

        # Nếu đã thăm thì bỏ qua
        if current in visited:
            continue

        visited.add(current)

        # Nếu đến đích thì dừng
        if current == end:
            break

        # Xét các đỉnh kề
        for neighbor, weight in graph[current]:
            if neighbor not in visited:
                # Tính khoảng cách mới
                new_dist = current_dist + weight

                # Nếu tìm được đường ngắn hơn
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current
                    heapq.heappush(pq, (new_dist, neighbor))

    # Tạo đường đi từ end về start
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()

    return distances[end], path


# Ví dụ sử dụng Dijkstra
def demo_dijkstra():
    print("\n\n=== DEMO DIJKSTRA - TÌM ĐƯỜNG NGẮN NHẤT ===\n")

    # Đồ thị biểu diễn bản đồ
    # Mỗi đỉnh kết nối với (đỉnh_kề, khoảng_cách)
    graph = {
        "Nhà": [("Chợ", 3), ("Công viên", 2)],
        "Chợ": [("Nhà", 3), ("Trường", 7), ("Bệnh viện", 2)],
        "Công viên": [("Nhà", 2), ("Trường", 5), ("Thư viện", 1)],
        "Trường": [("Chợ", 7), ("Công viên", 5), ("Bệnh viện", 3), ("Thư viện", 2)],
        "Bệnh viện": [("Chợ", 2), ("Trường", 3), ("Thư viện", 4)],
        "Thư viện": [("Công viên", 1), ("Bệnh viện", 4), ("Trường",2)],
    }

    print("Bản đồ thành phố:")
    print("- Nhà → Chợ: 3km")
    print("- Nhà → Công viên: 2km")
    print("- Chợ → Trường: 4km")
    print("- Chợ → Bệnh viện: 2km")
    print("- Công viên → Trường: 5km")
    print("- Công viên → Thư viện: 1km")
    print("- Trường → Bệnh viện: 3km")
    print("- Bệnh viện → Thư viện: 4km")
    
    # Hiển thị đồ thị ban đầu
    print("\nĐang lưu bản đồ...")
    visualize_graph(graph, title="Bản đồ thành phố - Tất cả các đường", filename="city_map.png")

    start = "Nhà"
    end = "Trường"

    print(f"\nTìm đường ngắn nhất từ {start} đến {end}...")
    distance, path = dijkstra(graph, start, end)

    if distance < float("inf"):
        print(f"\nĐường đi ngắn nhất: {' → '.join(path)}")
        print(f"Tổng khoảng cách: {distance}km")
        
        # Hiển thị đồ thị với đường đi ngắn nhất
        print("\nĐang lưu đường đi ngắn nhất...")
        visualize_graph(graph, shortest_path=path, start=start, end=end, 
                       title=f"Đường đi ngắn nhất từ {start} đến {end} ({distance}km)",
                       filename="shortest_path.png")
    else:
        print("\nKhông tìm thấy đường đi!")


# ============================================
# PHẦN 3: BÀI TẬP THỰC HÀNH
# ============================================


def practice_exercise():
    """
    Bài tập 2: Tìm đường đi trong thành phố
    """
    print("\n\n=== BÀI TẬP 2: ĐƯỜNG ĐI TRONG THÀNH PHỐ ===\n")

    print("Cho bản đồ với các địa điểm và khoảng cách:")
    print("- A → B: 4km")
    print("- A → C: 2km")
    print("- B → D: 5km")
    print("- C → D: 8km")
    print("- C → E: 10km")
    print("- D → E: 2km")
    print("- D → F: 6km")
    print("- E → F: 3km")

    print("\nHãy tìm đường ngắn nhất từ A đến F")
    print("Gợi ý: Tạo graph và dùng hàm dijkstra!")

    # TODO: Học sinh điền code vào đây
    # graph = {
    #     'A': [('B', 4), ('C', 2)],
    #     'B': [...],
    #     ...
    # }
    # distance, path = dijkstra(graph, 'A', 'F')


# ============================================
# CHƯƠNG TRÌNH CHÍNH
# ============================================

if __name__ == "__main__":
    demo_dijkstra()

    # Bài tập thực hành
    print("\n\n" + "=" * 50)
    print("BÀI TẬP THỰC HÀNH")
    print("=" * 50)

    practice_exercise()
