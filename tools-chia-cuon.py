import pandas as pd

def group_by_column_8_perfect(input_file, output_file, column_name='Chieu_Dai', target=4000, max_limit=4010):
    # 1. Đọc file Excel
    df = pd.read_excel(input_file)

    # Lấy dữ liệu dưới dạng danh sách các cặp [index_gốc, giá_trị]
    data_list = [[idx, val] for idx, val in df[column_name].dropna().to_dict().items()]

    groups = {}
    group_sums = {}
    group_counter = 1

    # 2. Thuật toán tìm tổ hợp tối ưu tuyệt đối cho từng nhóm
    while data_list:
        best_combination_indices = []
        best_sum = 0
        best_score = float('inf') # Điểm phạt càng thấp càng tốt

        # Sắp xếp lại danh sách còn lại giảm dần trước mỗi lượt tìm kiếm để tối ưu hóa việc vét số
        data_list.sort(key=lambda x: x[1], reverse=True)

        # Thử tìm tổ hợp bằng thuật toán tham lam quay lui thông minh
        current_indices = []
        current_sum = 0

        # Hàm đệ quy tìm kiếm tổ hợp tốt nhất
        def find_best_combo(start_idx, curr_sum, curr_indices):
            nonlocal best_sum, best_combination_indices, best_score

            # Nếu tổng vượt quá giới hạn tối đa được thiết lập, dừng nhánh này
            if curr_sum > max_limit:
                return

            # Tính điểm phạt cho tổng hiện tại dựa trên biến target đã cấu hình
            if target <= curr_sum <= max_limit:
                score = curr_sum - target  # Ưu tiên các số lọt khoảng và sát target nhất
            else:
                score = (target - curr_sum) + 100 # Nếu dưới target thì phạt nặng hơn để ép tìm thêm số

            # Nếu tìm thấy tổ hợp có điểm phạt nhỏ hơn (tốt hơn tổ hợp cũ)
            if score < best_score:
                best_score = score
                best_sum = curr_sum
                best_combination_indices = curr_indices.copy()

            # Điều kiện dừng nếu đã đạt điểm phạt bằng 0 (tổng bằng đúng số target hoàn hảo)
            if best_score == 0:
                return

            # Duyệt qua các phần tử còn lại (Giới hạn nhánh duyệt sâu 20 phần tử để đảm bảo tốc độ)
            for i in range(start_idx, min(start_idx + 20, len(data_list))):
                idx_goc, val = data_list[i]
                find_best_combo(i + 1, curr_sum + val, curr_indices + [i])
                if best_score == 0:
                    return

        # Kích hoạt tìm kiếm tổ hợp tốt nhất cho nhóm này
        find_best_combo(0, 0, [])

        # Nếu không nhặt thêm được bất kỳ số nào (mảng trống hoặc toàn số cực lớn > max_limit)
        if not best_combination_indices:
            # Gom toàn bộ các phần tử còn lại vào nhóm cuối cùng
            best_combination_indices = list(range(len(data_list)))
            best_sum = sum([data_list[i][1] for i in best_combination_indices])

        # Đặt tên nhóm thuần túy: "Nhóm + số nguyên"
        group_name = group_counter
        group_counter += 1

        # Cập nhật kết quả và xóa các phần tử đã chọn ra khỏi data_list
        for i in sorted(best_combination_indices, reverse=True):
            orig_idx, _ = data_list.pop(i)
            groups[orig_idx] = group_name
            group_sums[orig_idx] = best_sum

    # 3. Tạo 2 cột mới ở cuối cùng file Excel kết quả
    df['Nhom'] = df.index.map(groups)
    df['Tong_Nhom'] = df.index.map(group_sums)

    # Xuất ra file Excel mới nguyên vẹn cấu trúc cũ
    df.to_excel(output_file, index=False)
    print(f" Xử lý thành công! Đã tối ưu dựa trên Mục tiêu: {target} và Giới hạn tối đa: {max_limit}")

# --- KÍCH HOẠT CHẠY CHƯƠNG TRÌNH ---
# Từ giờ bạn chỉ cần thay đổi số 4000 và 4010 ở đây để điều chỉnh cấu hình toàn bộ bài toán
import streamlit as st
import io

# 1. Tạo giao diện tiêu đề
st.title("✂️ Công cụ tối ưu chia cuộn tự động")

# 2. Tạo các ô nhập thông số ở thanh bên trái (Sidebar)
st.sidebar.header("⚙️ Cấu hình thông số")
column_name = st.sidebar.text_input("Tên cột chứa Chiều Dài", value="Chieu_Dai")
target = st.sidebar.number_input("Mục tiêu tối thiểu (Target)", value=4000, step=10)
max_limit = st.sidebar.number_input("Giới hạn tối đa (Max Limit)", value=4010, step=10)

# 3. Tạo khung kéo thả file Excel
uploaded_file = st.file_uploader("Kéo và thả file Excel (.xlsx) vào đây", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Đọc dữ liệu từ file người dùng upload
        df_input = pd.read_excel(uploaded_file)
        st.success("Đã tải file thành công! Bản xem trước 5 dòng đầu:")
        st.dataframe(df_input.head(5))
        
        # Nút bấm kích hoạt tính toán
        if st.button("🚀 Bắt đầu tối ưu hóa"):
            with st.spinner("Đang tính toán..."):
                # Gọi hàm thuật toán của bạn (hàm group_by_column_8_perfect đã viết ở trên)
                df_result = group_by_column_8_perfect(df_input, column_name, target, max_limit)
                
                # Tạo file Excel lưu vào bộ nhớ tạm để tải về
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_result.to_excel(writer, index=False)
                processed_data = output.getvalue()
                
                st.success("🎉 Đã tối ưu xong!")
                st.download_button(
                    label="📥 Tải file kết quả (.xlsx)",
                    data=processed_data,
                    file_name="ket_qua_chia_cuon.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    except Exception as e:
        st.error(f"Lỗi xử lý dữ liệu: {e}")
