"""
Streamlit 會話狀態示例

運行方式：streamlit run 06_會話狀態.py
"""

import streamlit as st

st.set_page_config(page_title="會話狀態", page_icon="💾", layout="wide")

st.title("💾 Streamlit 會話狀態管理")
st.markdown("---")

# 計數器示例
st.header("1. 簡單計數器")

if 'count' not in st.session_state:
    st.session_state.count = 0

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("➕ 增加"):
        st.session_state.count += 1

with col2:
    if st.button("➖ 減少"):
        st.session_state.count -= 1

with col3:
    if st.button("🔄 重置"):
        st.session_state.count = 0

with col4:
    st.metric("當前計數", st.session_state.count)

# 購物車示例
st.header("2. 購物車示例")

if 'cart' not in st.session_state:
    st.session_state.cart = []

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("商品列表")

    products = [
        {"name": "商品 A", "price": 100},
        {"name": "商品 B", "price": 200},
        {"name": "商品 C", "price": 300}
    ]

    for product in products:
        col_a, col_b, col_c = st.columns([2, 1, 1])
        col_a.write(f"**{product['name']}**")
        col_b.write(f"${product['price']}")
        if col_c.button("加入購物車", key=product['name']):
            st.session_state.cart.append(product)
            st.success(f"已添加 {product['name']}")

with col2:
    st.subheader("購物車")

    if st.session_state.cart:
        total = sum(item['price'] for item in st.session_state.cart)
        st.metric("總計", f"${total}")

        for i, item in enumerate(st.session_state.cart):
            col_a, col_b = st.columns([2, 1])
            col_a.write(item['name'])
            if col_b.button("刪除", key=f"remove_{i}"):
                st.session_state.cart.pop(i)
                st.rerun()

        if st.button("清空購物車"):
            st.session_state.cart = []
            st.rerun()
    else:
        st.info("購物車為空")

# 表單數據持久化
st.header("3. 表單數據持久化")

if 'form_data' not in st.session_state:
    st.session_state.form_data = {}

with st.form("persistent_form"):
    name = st.text_input("姓名", value=st.session_state.form_data.get('name', ''))
    email = st.text_input("郵箱", value=st.session_state.form_data.get('email', ''))

    if st.form_submit_button("保存"):
        st.session_state.form_data = {"name": name, "email": email}
        st.success("數據已保存！")

if st.session_state.form_data:
    st.write("已保存的數據：", st.session_state.form_data)

# 狀態調試
st.header("4. 會話狀態調試")

with st.expander("查看所有會話狀態"):
    st.json(dict(st.session_state))
