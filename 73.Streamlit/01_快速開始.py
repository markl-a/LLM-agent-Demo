"""
Streamlit 快速開始示例

本示例展示：
1. Streamlit 基本結構
2. 常用組件介紹
3. 文本和數據展示
4. Hello World 示例

運行方式：
    streamlit run 01_快速開始.py

訪問：
    http://localhost:8501
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime


# ==================== 頁面配置 ====================

st.set_page_config(
    page_title="Streamlit 快速開始",
    page_icon="🎈",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== 主標題 ====================

st.title("🎈 Streamlit 快速開始")
st.markdown("---")


# ==================== 文本展示 ====================

st.header("1. 文本展示")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("標題和文本")
    st.write("這是普通文本")
    st.caption("這是說明文字")
    st.code("print('Hello Streamlit')", language="python")

with col2:
    st.subheader("Markdown 支持")
    st.markdown("""
    - **粗體文本**
    - *斜體文本*
    - `代碼`
    - [連結](https://streamlit.io)
    """)

with col3:
    st.subheader("特殊文本")
    st.success("✅ 成功消息")
    st.info("ℹ️ 提示消息")
    st.warning("⚠️ 警告消息")
    st.error("❌ 錯誤消息")


# ==================== 數據展示 ====================

st.header("2. 數據展示")

# 創建示例數據
df = pd.DataFrame({
    '列A': np.random.randn(10),
    '列B': np.random.randn(10),
    '列C': np.random.randn(10)
})

col1, col2 = st.columns(2)

with col1:
    st.subheader("DataFrame")
    st.dataframe(df, use_container_width=True)

with col2:
    st.subheader("表格")
    st.table(df.head())


# ==================== 圖表展示 ====================

st.header("3. 基本圖表")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("折線圖")
    st.line_chart(df)

with col2:
    st.subheader("柱狀圖")
    st.bar_chart(df)

with col3:
    st.subheader("面積圖")
    st.area_chart(df)


# ==================== 用戶輸入 ====================

st.header("4. 用戶輸入")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("文本輸入")
    name = st.text_input("你的名字", "小明")
    st.write(f"你好，{name}！")

with col2:
    st.subheader("數字輸入")
    age = st.number_input("年齡", min_value=0, max_value=120, value=25)
    st.write(f"你 {age} 歲")

with col3:
    st.subheader("滑塊")
    value = st.slider("選擇值", 0, 100, 50)
    st.write(f"當前值：{value}")


# ==================== 選擇組件 ====================

st.header("5. 選擇組件")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("下拉選單")
    option = st.selectbox(
        "選擇一個選項",
        ["選項 1", "選項 2", "選項 3"]
    )
    st.write(f"你選擇了：{option}")

with col2:
    st.subheader("多選框")
    options = st.multiselect(
        "選擇多個",
        ["A", "B", "C", "D"],
        ["A", "C"]
    )
    st.write(f"已選擇：{options}")

with col3:
    st.subheader("單選按鈕")
    choice = st.radio(
        "選擇一個",
        ["紅色", "綠色", "藍色"]
    )
    st.write(f"你選擇了：{choice}")


# ==================== 按鈕和複選框 ====================

st.header("6. 按鈕和複選框")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("按鈕")
    if st.button("點我"):
        st.balloons()
        st.success("按鈕被點擊了！")

with col2:
    st.subheader("複選框")
    agree = st.checkbox("我同意")
    if agree:
        st.success("感謝你的同意！")

with col3:
    st.subheader("切換按鈕")
    on = st.toggle("啟用功能")
    if on:
        st.success("功能已啟用")


# ==================== 側邊欄 ====================

st.header("7. 側邊欄")

with st.sidebar:
    st.title("⚙️ 設置")
    st.write("這是側邊欄內容")

    sidebar_option = st.selectbox(
        "選擇模式",
        ["模式 A", "模式 B", "模式 C"]
    )

    st.markdown("---")

    st.subheader("關於")
    st.info("""
    這是一個 Streamlit 快速開始示例。

    展示了基本的組件和功能。
    """)


# ==================== 進度和狀態 ====================

st.header("8. 進度和狀態")

col1, col2 = st.columns(2)

with col1:
    st.subheader("進度條")
    progress_bar = st.progress(0)
    import time

    if st.button("開始進度"):
        for i in range(100):
            progress_bar.progress(i + 1)
            time.sleep(0.01)
        st.success("完成！")

with col2:
    st.subheader("指標卡")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("溫度", "70 °F", "1.2 °F")
    col_b.metric("風速", "9 mph", "-8%")
    col_c.metric("濕度", "86%", "4%")


# ==================== 容器和展開 ====================

st.header("9. 容器和展開")

# 展開器
with st.expander("點擊展開查看更多"):
    st.write("這裡是隱藏的內容")
    st.image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png", width=200)

# 容器
container = st.container()
container.write("這是容器中的內容")


# ==================== 幫助信息 ====================

st.markdown("---")
st.header("💡 使用提示")

st.info("""
**Streamlit 特點：**
- 純 Python 編寫
- 自動重新運行
- 簡潔的 API
- 強大的數據可視化

**運行命令：**
```bash
streamlit run 01_快速開始.py
```

**更多資源：**
- [官方文檔](https://docs.streamlit.io)
- [API 參考](https://docs.streamlit.io/library/api-reference)
- [社區論壇](https://discuss.streamlit.io)
""")


# ==================== 頁腳 ====================

st.markdown("---")
st.caption(f"最後更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("© 2024 Streamlit 快速開始示例")
