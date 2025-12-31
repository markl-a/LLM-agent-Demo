"""
Streamlit 表單輸入示例

運行方式：streamlit run 05_表單輸入.py
"""

import streamlit as st
from datetime import datetime, date, time

st.set_page_config(page_title="表單輸入", page_icon="📝", layout="wide")

st.title("📝 Streamlit 表單和輸入組件")
st.markdown("---")

# 表單示例
st.header("1. 基礎表單")

with st.form("basic_form"):
    st.subheader("用戶註冊表單")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("姓名")
        email = st.text_input("電子郵件")
        password = st.text_input("密碼", type="password")

    with col2:
        age = st.number_input("年齡", min_value=0, max_value=120, value=25)
        gender = st.radio("性別", ["男", "女", "其他"])
        country = st.selectbox("國家", ["台灣", "中國", "美國", "日本"])

    bio = st.text_area("自我介紹", height=100)
    agree = st.checkbox("我同意服務條款")

    submitted = st.form_submit_button("提交", type="primary")

    if submitted:
        if agree:
            st.success("✅ 表單提交成功！")
            st.json({
                "姓名": name,
                "郵箱": email,
                "年齡": age,
                "性別": gender,
                "國家": country,
                "簡介": bio
            })
        else:
            st.error("❌ 請同意服務條款")

# 文件上傳
st.header("2. 文件上傳")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("選擇文件", type=["txt", "csv", "json"])
    if uploaded_file:
        st.success(f"已上傳：{uploaded_file.name}")
        st.write(f"文件大小：{uploaded_file.size} bytes")

with col2:
    multiple_files = st.file_uploader("多文件上傳", accept_multiple_files=True)
    if multiple_files:
        st.write(f"已上傳 {len(multiple_files)} 個文件")
        for file in multiple_files:
            st.write(f"- {file.name}")

# 日期和時間
st.header("3. 日期和時間選擇器")

col1, col2, col3 = st.columns(3)

with col1:
    selected_date = st.date_input("選擇日期", value=date.today())
    st.write(f"選擇的日期：{selected_date}")

with col2:
    selected_time = st.time_input("選擇時間", value=time(9, 0))
    st.write(f"選擇的時間：{selected_time}")

with col3:
    color = st.color_picker("選擇顏色", "#00f900")
    st.write(f"選擇的顏色：{color}")

# 各類輸入組件
st.header("4. 更多輸入組件")

col1, col2 = st.columns(2)

with col1:
    slider_val = st.slider("滑塊", 0, 100, 50)
    range_val = st.slider("範圍選擇", 0, 100, (25, 75))
    select_slider = st.select_slider("選擇滑塊", 
        options=["差", "一般", "好", "很好", "優秀"])

with col2:
    multi_select = st.multiselect("多選", ["選項 A", "選項 B", "選項 C", "選項 D"])
    toggle = st.toggle("啟用功能")
    rating = st.feedback("thumbs")

st.markdown("---")
st.info("💡 所有輸入組件都支持實時更新和狀態保存")
