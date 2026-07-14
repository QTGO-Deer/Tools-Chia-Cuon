import pandas as pd
import streamlit as st
import io

# Định nghĩa hàm xử lý thuật toán (Đã sửa để nhận dữ liệu DataFrame và return DataFrame kết quả)
def group_by_column_8_perfect(df_input, column_name='Chieu_Dai', target=4000, max_limit=4010):
    df = df_input.copy()
    
    # Lấy dữ liệu dưới dạng danh sách các cặp [index_gốc, giá_trị]
    data_list = [[idx, val] for idx, val in df[column_name].dropna().to_dict().items()]

    groups = {}
    group_sums = {}
    group_counter = 1

    # Thuật toán tìm tổ hợp tối ưu
    while data_list:
        best_combination_indices = []
        best_sum = 0
        best_score = float('inf')

        data_list.sort(key=lambda x: x[1], reverse=True)
        
        def find_best_combo(start_idx, curr_sum, curr_indices):
            nonlocal best_sum, best_combination_indices, best_score

            if curr_sum > max_limit:
                return

            if target <= curr_sum <= max_limit:
                score = curr_sum - target
            else:
                score = (target - curr_sum) + 100

            if score < best_score:
                best_score = score
                best_sum = curr_sum
                best_combination_indices = curr_indices.copy()

            if best_score == 0:
                return

            for i in range(start_idx, min(start_idx + 20, len(data_list))):
                find_best_combo(i + 1, curr_sum + data_list[i][1], curr_indices + [i])
                if best_score == 0:
                    return

        find_best_combo(0, 0, [])

        if not best_combination_indices:
            best_combination_indices = list(range(len(data_list)))
            best_sum = sum([data_list[i][1] for i in best_combination_indices])

        group_name = group_counter
        group_counter += 1

        for i in sorted(best_combination_indices, reverse=True):
            orig_idx, _ = data_list.pop(i)
            groups[orig_idx] = group_name
            group_sums[orig_idx] = best_sum

    # Tạo 2 cột mới ở cuối cùng file Excel kết quả
    df['Nhom'] = df.index.map(groups)
    df['Tong_Nhom'] = df.index.map(group_sums)
    return df

# --- GIAO DIỆN STREAMLIT ---

# 1. Tạo giao diện tiêu đề
st.title("✂️ Công cụ chia cuộn tự động")

# 2. Tạo các ô nhập thông số ở thanh bên trái (Sidebar)
st.sidebar.header("⚙️ Cấu hình thông số")
column_name = st.sidebar.text_input("Tên cột chiều dài cuộn", value="Chieu_Dai")
target = st.sidebar.number_input("Mục tiêu tối thiểu (Target)", value=3950, step=10)
max_limit = st.sidebar.number_input("Giới hạn tối đa (Max Limit)", value=4010, step=10)

# 3. Tạo khung kéo thả file Excel
uploaded_file = st.file_uploader("Kéo và thả file Excel (.xlsx) vào đây", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Bước A: Đọc file Excel người dùng tải lên thành DataFrame trước
        df_input = pd.read_excel(uploaded_file)
        
        st.success("Đã tải file thành công! Bản xem trước 10 dòng đầu:")
        st.dataframe(df_input.head(10))
        
        # Bước B: Nút bấm bắt đầu tính toán (Đã sửa lại thụt lề chuẩn)
        if st.button("🚀 Bắt đầu tối ưu hóa"):
            with st.spinner("Đang tính toán tổ hợp tối ưu..."):
                # Gọi hàm thuật toán truyền đúng DataFrame và các tham số vào
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
