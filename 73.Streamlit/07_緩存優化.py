"""
Streamlit 緩存優化示例

運行方式：streamlit run 07_緩存優化.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(page_title="緩存優化", page_icon="⚡", layout="wide")

st.title("⚡ Streamlit 緩存優化")
st.markdown("---")

# 緩存數據
st.header("1. @st.cache_data - 緩存數據轉換")

@st.cache_data
def load_large_dataset(rows):
    """模擬加載大數據集"""
    time.sleep(2)  # 模擬耗時操作
    return pd.DataFrame({
        'A': np.random.randn(rows),
        'B': np.random.randn(rows),
        'C': np.random.randn(rows)
    })

col1, col2 = st.columns(2)

with col1:
    st.subheader("首次加載（慢）")
    start = time.time()
    df = load_large_dataset(1000)
    duration = time.time() - start
    st.write(f"⏱️ 加載時間：{duration:.2f} 秒")
    st.dataframe(df.head())

with col2:
    st.subheader("緩存加載（快）")
    start = time.time()
    df = load_large_dataset(1000)
    duration = time.time() - start
    st.write(f"⚡ 加載時間：{duration:.2f} 秒")
    st.dataframe(df.head())

# 緩存資源
st.header("2. @st.cache_resource - 緩存全局資源")

@st.cache_resource
def load_model():
    """模擬加載 ML 模型"""
    time.sleep(3)
    return {"model": "trained_model", "version": "1.0"}

if st.button("加載模型"):
    with st.spinner("加載中..."):
        model = load_model()
        st.success("✅ 模型已加載（所有用戶共享）")
        st.json(model)

# TTL 緩存
st.header("3. TTL（Time To Live）緩存")

@st.cache_data(ttl=10)  # 10 秒後過期
def get_current_time():
    return time.strftime("%H:%M:%S")

st.write(f"當前時間（10秒緩存）：{get_current_time()}")
st.caption("刷新頁面，時間只會每 10 秒更新一次")

# 緩存清除
st.header("4. 緩存管理")

col1, col2 = st.columns(2)

with col1:
    if st.button("清除所有緩存"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("✅ 緩存已清除")

with col2:
    if st.button("清除特定函數緩存"):
        load_large_dataset.clear()
        st.success("✅ 數據集緩存已清除")

# 性能對比
st.header("5. 性能對比")

def slow_function(n):
    time.sleep(1)
    return n * 2

@st.cache_data
def fast_function(n):
    time.sleep(1)
    return n * 2

col1, col2 = st.columns(2)

with col1:
    st.subheader("無緩存")
    if st.button("執行（慢）"):
        start = time.time()
        result = slow_function(10)
        duration = time.time() - start
        st.write(f"結果：{result}")
        st.write(f"耗時：{duration:.2f}秒")

with col2:
    st.subheader("有緩存")
    if st.button("執行（快）"):
        start = time.time()
        result = fast_function(10)
        duration = time.time() - start
        st.write(f"結果：{result}")
        st.write(f"耗時：{duration:.2f}秒")

st.markdown("---")
st.info("""
💡 **緩存最佳實踐**

- `@st.cache_data`：用於數據轉換、API 調用、數據庫查詢
- `@st.cache_resource`：用於 ML 模型、數據庫連接、全局資源
- 使用 `ttl` 參數控制緩存過期時間
- 使用 `show_spinner` 參數控制加載提示
""")
