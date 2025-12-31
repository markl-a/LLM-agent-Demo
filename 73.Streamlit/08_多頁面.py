"""
Streamlit 多頁面應用示例

運行方式：streamlit run 08_多頁面.py

注意：這是主頁面文件
創建 pages/ 目錄並添加其他頁面：
- pages/1_📊_數據分析.py
- pages/2_📈_圖表展示.py
- pages/3_⚙️_設置.py
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="多頁面應用",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 主頁內容
st.title("📱 Streamlit 多頁面應用")

st.markdown("""
## 歡迎使用多頁面應用！

這是一個展示 Streamlit 多頁面功能的示例。

### 📚 頁面導覽

請查看左側邊欄中的頁面列表：

1. **📊 數據分析** - 數據加載和基礎分析
2. **📈 圖表展示** - 各類數據可視化
3. **⚙️ 設置** - 應用配置和偏好設置

### 🚀 快速開始

多頁面應用的目錄結構：
```
my_app/
├── 08_多頁面.py          # 主頁面（你現在在這裡）
└── pages/
    ├── 1_📊_數據分析.py
    ├── 2_📈_圖表展示.py
    └── 3_⚙️_設置.py
```

### 💡 特點

- **自動導航**：Streamlit 自動生成側邊欄導航
- **狀態共享**：使用 `st.session_state` 在頁面間共享數據
- **文件命名**：頁面文件名決定顯示順序和圖標
- **靈活組織**：輕鬆管理大型應用

""")

# 初始化共享數據
if 'shared_data' not in st.session_state:
    st.session_state.shared_data = pd.DataFrame({
        'A': np.random.randn(100),
        'B': np.random.randn(100),
        'C': np.random.randn(100)
    })

# 顯示一些示例數據
st.header("📊 示例數據預覽")

st.dataframe(st.session_state.shared_data.head(10), use_container_width=True)

# 側邊欄
with st.sidebar:
    st.header("📱 導航")
    st.info("使用上方的頁面選擇器切換頁面")

    st.markdown("---")

    st.header("📊 數據統計")
    st.metric("數據行數", len(st.session_state.shared_data))
    st.metric("數據列數", len(st.session_state.shared_data.columns))

st.markdown("---")
st.caption("💡 提示：在側邊欄選擇其他頁面查看更多功能")
