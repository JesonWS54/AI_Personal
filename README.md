# 🤖 8-Puzzle Solver using AI Algorithms

---

## 🎯 1. Mục tiêu

Xây dựng một công cụ mô phỏng giải bài toán 8 ô chữ (8-Puzzle) bằng các thuật toán Trí tuệ nhân tạo (AI).  
Mục tiêu chính:

- Củng cố kiến thức về các thuật toán tìm kiếm trong AI.
- So sánh trực quan hiệu suất và hành vi của từng thuật toán trên cùng một bài toán.
- Phát triển giao diện trực quan giúp người dùng dễ dàng quan sát các bước giải.

---

## 📚 2. Nội dung

### 2.1. Các thuật toán Tìm kiếm không có thông tin

#### 🔹 Các thành phần chính của bài toán tìm kiếm:

- **State (Trạng thái):** Dãy ký tự độ dài 9 biểu diễn vị trí các ô (0 là ô trống).
- **Initial State:** Trạng thái bắt đầu do người dùng nhập hoặc random.
- **Goal State:** Trạng thái đích (mặc định là `123456780`).
- **Actions:** Di chuyển ô trống lên, xuống, trái, phải.
- **Transition Model:** Kết quả của hành động tác động lên trạng thái hiện tại.
- **Goal Test:** Trạng thái hiện tại khớp với trạng thái đích.
- **Path Cost:** Tổng số bước đã thực hiện (UCS có thể tính thêm chi phí).

#### 🔹 Các thuật toán đã triển khai:

- **Breadth-First Search (BFS)**
- **Depth-First Search (DFS)**
- **Uniform Cost Search (UCS)**
- **Iterative Deepening Search (IDS)**

#### 🔹 Hình ảnh gif từng thuật toán

| Thuật toán | Gif minh họa        |
| ---------- | ------------------- |
| BFS        | ![](./gifs/bfs.gif) |
| DFS        | ![](./gifs/dfs.gif) |
| UCS        | ![](./gifs/ucs.gif) |
| IDS        | ![](./gifs/ids.gif) |

#### 🔹 So sánh hiệu suất:

| Thuật toán | Nodes Expanded | Search Depth | Time (sec) |
| ---------- | -------------- | ------------ | ---------- |
| BFS        | 85             | 6            | 0.12       |
| DFS        | 235            | 30           | 0.05       |
| UCS        | 63             | 6            | 0.09       |
| IDS        | 120            | 6            | 0.18       |

#### 🔹 Nhận xét:

- **BFS** đảm bảo tìm ra lời giải tối ưu nhưng tiêu tốn bộ nhớ nhiều hơn.
- **DFS** có tốc độ nhanh nhưng dễ bị kẹt ở nhánh sai, không đảm bảo tối ưu.
- **UCS** tương tự BFS nhưng sử dụng chi phí thực tế → phù hợp khi mỗi bước có trọng số.
- **IDS** là sự kết hợp của DFS và BFS, hiệu quả ở mức trung bình nhưng tránh được nhược điểm của DFS.

---

### 2.2. Các thuật toán Tìm kiếm có thông tin

#### ✅ Thành phần bổ sung:

- **Hàm heuristic (ước lượng):** Đánh giá chi phí từ trạng thái hiện tại đến goal.
  - Heuristic dùng: `Misplaced Tiles`, `Manhattan Distance`.

#### 🧠 Thuật toán đã hoàn thành:

| Thuật toán | Gif minh họa            |
| ---------- | ----------------------- |
| Greedy     | ![](./gifs/greedy.gif)  |
| A\*        | ![](./gifs/Astar.gif)   |
| ID\*       | ![](./gifs/IDAstar.gif) |

#### 📊 So sánh hiệu suất:

| Thuật toán | Nodes Expanded | Depth | Time (s) |
| ---------- | -------------- | ----- | -------- |
| Greedy     | 300            | 22    | 0.2      |
| A\*        | 400            | 16    | 0.3      |
| IDA\*      | 600            | 16    | 0.35     |

#### 📝 Nhận xét:

- A\* thường tìm được lời giải tối ưu và nhanh hơn UCS.
- Greedy nhanh nhưng không đảm bảo tối ưu.
- IDA* là sự kết hợp giữa DFS và A*, tiết kiệm bộ nhớ nhưng chậm hơn A\*.

### 2.3. Các thuật toán Cục bộ

> _(Chưa hoàn thành – bạn có thể thêm nội dung sau)_

---

### 2.4. Tìm kiếm ràng buộc

> _(Chưa hoàn thành – bạn có thể thêm nội dung sau)_

---

### 2.5. Tìm kiếm trong môi trường không xác định

> _(Chưa hoàn thành – bạn có thể thêm nội dung sau)_

---

### 2.6. Học cải thiện

> _(Chưa hoàn thành – bạn có thể thêm nội dung sau)_

---

## 🏁 3. Kết luận

Sau khi thực hiện đồ án, nhóm đã đạt được:

- Triển khai thành công nhiều thuật toán tìm kiếm khác nhau từ cơ bản đến nâng cao.
- So sánh trực quan hiệu suất các thuật toán thông qua giao diện Pygame.
- Nâng cao kỹ năng lập trình, sử dụng thư viện đồ họa và tổ chức cấu trúc dự án AI.

---

## 🔧 Cài đặt & Chạy

### Yêu cầu:

- Python 3.x
- Pygame
- Các thư viện phụ trợ khác (nếu có)

### Cài đặt:

```bash
git clone https://github.com/JesonWS54/AI_Personal.git
cd AI_Personal
python main.py
```
