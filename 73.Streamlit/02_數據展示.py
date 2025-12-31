"""
Streamlit 數據展示示例

運行方式：streamlit run 02_數據展示.py
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="數據展示", page_icon="📊", layout="wide")

st.title("📊 Streamlit 數據展示")
st.markdown("---")

# 創建示例數據
@st.cache_data
def load_data():
    return pd.DataFrame({
        '日期': pd.date_range('2024-01-01', periods=100),
        '銷售額': np.random.randint(1000, 5000, 100),
        '訪客數': np.random.randint(500, 2000, 100),
        '轉化率': np.random.uniform(0.01, 0.05, 100),
        '產品': np.random.choice(['A', 'B', 'C'], 100)
    })

df = load_data()

# DataFrame 展示
st.header("1. DataFrame 互動表格")
st.dataframe(df, use_container_width=True, height=400)

# 靜態表格
st.header("2. 靜態表格")
st.table(df.head(10))

# 指標卡
st.header("3. 指標卡 (Metrics)")
col1, col2, col3, col4 = st.columns(4)
col1.metric("總銷售額", f"${df['銷售額'].sum():,.0f}", f"{df['銷售額'].mean():.0f}")
col2.metric("平均訪客", f"{df['訪客數'].mean():.0f}", "8.5%")
col3.metric("平均轉化率", f"{df['轉化率'].mean():.2%}", "2.1%")
col4.metric("總訂單數", len(df), "23")

# 數據編輯器
st.header("4. 可編輯數據表")
edited_df = st.data_editor(df.head(10), num_rows="dynamic")

if st.button("顯示編輯後的數據"):
    st.write(edited_df)

# 統計摘要
st.header("5. 統計摘要")
st.write(df.describe())
