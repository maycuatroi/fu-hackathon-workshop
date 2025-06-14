import heapq


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
        "Chợ": [("Nhà", 3), ("Trường", 4), ("Bệnh viện", 2)],
        "Công viên": [("Nhà", 2), ("Trường", 5), ("Thư viện", 1)],
        "Trường": [("Chợ", 4), ("Công viên", 5), ("Bệnh viện", 3)],
        "Bệnh viện": [("Chợ", 2), ("Trường", 3), ("Thư viện", 4)],
        "Thư viện": [("Công viên", 1), ("Bệnh viện", 4)],
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

    start = "Nhà"
    end = "Trường"

    print(f"\nTìm đường ngắn nhất từ {start} đến {end}...")
    distance, path = dijkstra(graph, start, end)

    if distance < float("inf"):
        print(f"\nĐường đi ngắn nhất: {' → '.join(path)}")
        print(f"Tổng khoảng cách: {distance}km")
    else:
        print("\nKhông tìm thấy đường đi!")


# ============================================
# PHẦN 3: BÀI TẬP THỰC HÀNH
# ============================================


def practice_exercise_1():
    """
    Bài tập 1: Tìm đường trong mê cung lớn hơn
    """
    print("\n\n=== BÀI TẬP 1: MÊ CUNG 7x7 ===\n")

    maze = [
        [0, 0, 1, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [1, 1, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0],
        [0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0],
    ]

    print("Hãy tìm đường từ (0,0) đến (6,6)")
    print("Gợi ý: Sử dụng hàm bfs_maze đã viết sẵn!")

    # TODO: Học sinh điền code vào đây
    # path = bfs_maze(maze, (0, 0), (6, 6))
    # if path:
    #     print(f"Tìm thấy đường đi với {len(path)} bước!")
    # else:
    #     print("Không có đường đi!")


def practice_exercise_2():
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

    practice_exercise_1()
    practice_exercise_2()

    print("\n\n💡 Lời khuyên:")
    print("- Hãy vẽ ra giấy để dễ hình dung!")
    print("- Thử với ví dụ nhỏ trước khi làm bài lớn")
    print("- Đừng ngại hỏi thầy cô khi gặp khó khăn!")
