"""
Streamlit 圖表可視化示例

運行方式：streamlit run 03_圖表可視化.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="圖表可視化", page_icon="📈", layout="wide")

st.title("📈 Streamlit 圖表可視化")
st.markdown("---")

# 生成數據
@st.cache_data
def generate_data():
    dates = pd.date_range('2024-01-01', periods=30)
    return pd.DataFrame({
        '日期': dates,
        '銷售額': np.random.randint(1000, 5000, 30),
        '成本': np.random.randint(500, 2500, 30),
        '利潤': np.random.randint(300, 2000, 30)
    })

df = generate_data()

# Streamlit 內建圖表
st.header("1. Streamlit 內建圖表")

col1, col2 = st.columns(2)
with col1:
    st.subheader("折線圖")
    st.line_chart(df.set_index('日期')[['銷售額', '成本', '利潤']])

with col2:
    st.subheader("柱狀圖")
    st.bar_chart(df.set_index('日期')[['銷售額', '成本']])

# Plotly 圖表
st.header("2. Plotly 互動圖表")

col1, col2 = st.columns(2)

with col1:
    st.subheader("折線圖")
    fig = px.line(df, x='日期', y=['銷售額', '成本', '利潤'], 
                  title='趨勢分析')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("散點圖")
    fig = px.scatter(df, x='成本', y='銷售額', size='利潤',
                     title='成本 vs 銷售額')
    st.plotly_chart(fig, use_container_width=True)

# 更多 Plotly 圖表
st.header("3. 高級圖表")

tab1, tab2, tab3 = st.tabs(["餅圖", "箱型圖", "熱力圖"])

with tab1:
    category_data = pd.DataFrame({
        '類別': ['A', 'B', 'C', 'D'],
        '數值': [30, 25, 20, 25]
    })
    fig = px.pie(category_data, values='數值', names='類別', title='銷售佔比')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = px.box(df, y=['銷售額', '成本', '利潤'], title='數據分布')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    corr_data = df[['銷售額', '成本', '利潤']].corr()
    fig = px.imshow(corr_data, text_auto=True, title='相關性熱力圖')
    st.plotly_chart(fig, use_container_width=True)
