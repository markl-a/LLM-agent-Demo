# Streamlit 框架完整範例

## 框架簡介

Streamlit 是一個專為數據科學家和機器學習工程師設計的 Python 框架，讓你能夠在幾分鐘內將 Python 腳本轉換為互動式 Web 應用。Streamlit 專注於數據展示、可視化和分析工具的快速開發。

### 核心特點

#### 1. 極簡的 API 設計 🎯
- Pure Python，無需 HTML/CSS/JavaScript
- 從上到下執行的直觀邏輯
- 自動重新運行機制
- 即時預覽和調試

```python
import streamlit as st

st.title("我的第一個 Streamlit 應用")
name = st.text_input("你的名字")
st.write(f"你好，{name}！")
```

#### 2. 豐富的數據展示組件 📊
- **圖表**：line_chart、bar_chart、area_chart
- **表格**：dataframe、table、metric
- **地圖**：map、deck_gl
- **媒體**：image、audio、video

```python
import pandas as pd
import streamlit as st

# 展示 DataFrame
df = pd.DataFrame({
    '列1': [1, 2, 3, 4],
    '列2': [10, 20, 30, 40]
})
st.dataframe(df)

# 展示圖表
st.line_chart(df)
```

#### 3. 強大的緩存機制 ⚡
- `@st.cache_data` - 緩存數據
- `@st.cache_resource` - 緩存資源（模型、連接等）
- 智能緩存失效
- 大幅提升性能

```python
@st.cache_data
def load_data():
    # 只在首次調用時執行
    return pd.read_csv("large_file.csv")

df = load_data()  # 後續調用直接從緩存讀取
```

#### 4. 靈活的布局系統 📐
- **Columns**：多列布局
- **Tabs**：標籤頁
- **Sidebar**：側邊欄
- **Expander**：可展開區域
- **Container**：容器

```python
# 多列布局
col1, col2, col3 = st.columns(3)
with col1:
    st.header("列 1")
with col2:
    st.header("列 2")
with col3:
    st.header("列 3")

# 側邊欄
with st.sidebar:
    st.title("設置")
    option = st.selectbox("選擇", ["A", "B", "C"])
```

#### 5. 會話狀態管理 💾
- `st.session_state` - 跨重新運行保持數據
- 實現複雜的互動邏輯
- 購物車、表單、遊戲等應用

```python
# 初始化狀態
if 'count' not in st.session_state:
    st.session_state.count = 0

# 更新狀態
if st.button('增加'):
    st.session_state.count += 1

st.write(f'計數：{st.session_state.count}')
```

#### 6. 表單和用戶輸入 📝
- 20+ 種輸入組件
- 表單批量提交
- 文件上傳
- 數據編輯器

```python
with st.form("my_form"):
    name = st.text_input("姓名")
    age = st.slider("年齡", 0, 100, 25)
    submitted = st.form_submit_button("提交")

    if submitted:
        st.write(f"{name}，{age} 歲")
```

#### 7. 整合流行庫 🔗
- **數據科學**：Pandas、NumPy
- **可視化**：Plotly、Altair、Matplotlib、Seaborn
- **機器學習**：Scikit-learn、TensorFlow、PyTorch
- **LLM**：OpenAI、LangChain、LlamaIndex

```python
import plotly.express as px

fig = px.scatter(df, x='x', y='y')
st.plotly_chart(fig)
```

#### 8. 多頁面應用 📱
- 輕鬆創建多頁面應用
- 自動導航菜單
- 頁面間狀態共享

```
my_app/
├── streamlit_app.py  # 主頁
└── pages/
    ├── 1_📊_數據.py
    ├── 2_📈_圖表.py
    └── 3_⚙️_設置.py
```

## 安裝指南

### 基礎安裝
```bash
pip install streamlit
```

### 完整安裝
```bash
pip install streamlit pandas plotly openai
```

### 開發環境設置
```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 安裝依賴
pip install -r requirements.txt

# 設置環境變量
export OPENAI_API_KEY='your-key-here'
```

## 快速開始

### 第一個 Streamlit 應用

創建 `app.py`：

```python
import streamlit as st

st.title("🎈 我的第一個 Streamlit 應用")
st.write("Hello, World!")

name = st.text_input("你的名字是？")
if name:
    st.write(f"你好，{name}！👋")
```

運行應用：
```bash
streamlit run app.py
```

訪問 http://localhost:8501 查看應用。

### 數據可視化應用

```python
import streamlit as st
import pandas as pd
import numpy as np

st.title("📊 數據可視化示例")

# 生成數據
data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['A', 'B', 'C']
)

# 展示數據
st.dataframe(data)

# 繪製圖表
st.line_chart(data)
st.bar_chart(data)
```

### 機器學習應用

```python
import streamlit as st
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

st.title("🌸 鳶尾花分類器")

# 加載數據
@st.cache_data
def load_data():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['species'] = iris.target
    return df, iris.target_names

df, target_names = load_data()

# 訓練模型
@st.cache_resource
def train_model():
    model = RandomForestClassifier()
    model.fit(df.iloc[:, :-1], df['species'])
    return model

model = train_model()

# 預測界面
st.sidebar.header("輸入特徵")
sepal_length = st.sidebar.slider("萼片長度", 4.0, 8.0, 5.0)
sepal_width = st.sidebar.slider("萼片寬度", 2.0, 4.5, 3.0)
petal_length = st.sidebar.slider("花瓣長度", 1.0, 7.0, 4.0)
petal_width = st.sidebar.slider("花瓣寬度", 0.1, 2.5, 1.0)

prediction = model.predict([[sepal_length, sepal_width, petal_length, petal_width]])
st.write(f"預測結果：{target_names[prediction[0]]}")
```

## 與其他框架對比

### Streamlit vs Gradio

| 特性 | Streamlit | Gradio |
|------|-----------|--------|
| **主要用途** | 數據應用/儀表板 | ML 模型演示 |
| **學習曲線** | 低 | 非常低 |
| **布局靈活性** | 高 | 中等 |
| **數據可視化** | 強大 | 基礎 |
| **狀態管理** | session_state | State 組件 |
| **適用場景** | BI工具、數據分析 | 快速 Demo |

**Gradio 優點：**
- 更簡單的 ML 模型包裝
- HuggingFace 深度整合
- 內建分享功能
- 極速開發

**Streamlit 優點：**
- 更靈活的布局
- 豐富的數據組件
- 強大的可視化
- 多頁面支持
- 更適合複雜應用

### Streamlit vs Dash (Plotly)

| 特性 | Streamlit | Dash |
|------|-----------|------|
| **代碼量** | 少 | 多 |
| **學習曲線** | 低 | 中高 |
| **定制性** | 中 | 高 |
| **性能** | 好 | 優秀 |
| **企業支持** | Streamlit Cloud | Plotly Enterprise |

**Dash 優點：**
- 更高的定制性
- 更好的生產性能
- 企業級支持
- React 組件

**Streamlit 優點：**
- 極簡的 API
- 快速原型開發
- 純 Python
- 更易上手

### 選擇建議

**選擇 Streamlit：**
- 數據分析儀表板
- BI 報表工具
- 內部數據工具
- 快速原型開發
- 教學演示
- 數據探索

**選擇 Gradio：**
- ML 模型快速演示
- HuggingFace 模型部署
- 簡單的 AI 應用
- 需要快速分享

**選擇 Dash：**
- 高性能生產應用
- 需要高度定制
- 企業級項目
- 複雜的回調邏輯

## 範例文件導覽

### 基礎篇

#### 01_快速開始.py
- Streamlit 基本結構
- 常用組件介紹
- 文本和數據展示
- Hello World 示例

#### 02_數據展示.py
- DataFrame 展示
- 表格組件
- Metrics 指標卡
- 數據編輯器

#### 03_圖表可視化.py
- 內建圖表（line、bar、area）
- Plotly 整合
- Altair 整合
- Matplotlib 整合

#### 04_聊天應用.py
- Chat 組件
- 對話歷史
- 流式輸出
- OpenAI 整合

### 進階篇

#### 05_表單輸入.py
- 表單組件
- 各類輸入控件
- 文件上傳
- 數據驗證

#### 06_會話狀態.py
- session_state 使用
- 狀態管理模式
- 購物車示例
- 計數器應用

#### 07_緩存優化.py
- cache_data 裝飾器
- cache_resource 裝飾器
- 緩存策略
- 性能優化

#### 08_多頁面.py
- 多頁面結構
- 頁面導航
- 狀態共享
- 頁面配置

### 高級篇

#### 09_Agent界面.py
- Agent 對話界面
- 工具調用展示
- 思考過程可視化
- LangChain 整合

#### 10_雲端部署.py
- Streamlit Cloud 部署
- Docker 容器化
- 環境配置
- 生產最佳實踐

## 核心概念

### 執行模型

Streamlit 採用「從上到下」的執行模型：

```python
import streamlit as st

# 每次互動都會重新執行整個腳本
st.title("計數器")

if 'count' not in st.session_state:
    st.session_state.count = 0

if st.button('增加'):
    st.session_state.count += 1  # 修改狀態

st.write(f'當前計數：{st.session_state.count}')
# 腳本重新運行，顯示新值
```

### 緩存系統

**緩存數據：**
```python
@st.cache_data  # 適用於數據轉換
def load_csv(file):
    return pd.read_csv(file)

df = load_csv("data.csv")  # 首次：執行函數
df = load_csv("data.csv")  # 後續：從緩存讀取
```

**緩存資源：**
```python
@st.cache_resource  # 適用於全局資源
def load_model():
    return  SomeMLModel()

model = load_model()  # 所有用戶共享同一個模型實例
```

### 布局 API

**列布局：**
```python
col1, col2, col3 = st.columns([1, 2, 1])  # 比例分配
col1.write("左")
col2.write("中")
col3.write("右")
```

**標籤頁：**
```python
tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])
with tab1:
    st.write("內容 1")
with tab2:
    st.write("內容 2")
```

**側邊欄：**
```python
with st.sidebar:
    st.title("側邊欄")
    option = st.selectbox("選擇", ["A", "B", "C"])
```

### 表單處理

```python
with st.form(key='my_form'):
    text_input = st.text_input('姓名')
    number_input = st.number_input('年齡')
    submit_button = st.form_submit_button('提交')

    if submit_button:
        st.success(f'提交成功：{text_input}, {number_input}')
```

## 最佳實踐

### 1. 使用緩存提升性能

```python
# 好：緩存昂貴操作
@st.cache_data
def expensive_computation(param):
    time.sleep(5)  # 模擬耗時操作
    return result

# 壞：每次都重新計算
def expensive_computation(param):
    time.sleep(5)
    return result
```

### 2. 合理組織代碼

```python
# 好：函數化
@st.cache_data
def load_data():
    return pd.read_csv("data.csv")

def main():
    st.title("我的應用")
    data = load_data()
    st.dataframe(data)

if __name__ == "__main__":
    main()

# 壞：所有代碼混在一起
```

### 3. 狀態管理模式

```python
# 初始化狀態
def init_state():
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.data = []
        st.session_state.counter = 0

init_state()
```

### 4. 錯誤處理

```python
try:
    data = load_data()
    st.success("數據加載成功！")
except Exception as e:
    st.error(f"錯誤：{str(e)}")
```

### 5. 進度提示

```python
with st.spinner('處理中...'):
    result = long_running_function()

# 或使用進度條
progress = st.progress(0)
for i in range(100):
    progress.progress(i + 1)
```

## 常見問題

### Q: 為什麼我的應用一直重新運行？

**A:** Streamlit 的設計理念就是在任何互動時重新運行腳本。使用 `st.session_state` 和緩存來優化性能。

### Q: 如何在頁面間共享數據？

**A:** 使用 `st.session_state`：

```python
# 頁面 1
st.session_state['shared_data'] = data

# 頁面 2
data = st.session_state.get('shared_data')
```

### Q: 如何部署 Streamlit 應用？

**A:** 多種方式：

1. **Streamlit Cloud**（推薦）：
   - 免費
   - 直接連接 GitHub
   - 自動部署

2. **Docker**：
```dockerfile
FROM python:3.10
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD streamlit run app.py --server.port 8501
```

3. **傳統服務器**：
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### Q: 如何自定義樣式？

**A:** 使用配置文件或直接設置：

```python
# 設置頁面配置
st.set_page_config(
    page_title="我的應用",
    page_icon="🎈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義 CSS
st.markdown("""
<style>
.stButton>button {
    background-color: #4CAF50;
    color: white;
}
</style>
""", unsafe_allow_html=True)
```

## 參考資源

### 官方文檔
- [Streamlit 官方文檔](https://docs.streamlit.io/)
- [API 參考](https://docs.streamlit.io/library/api-reference)
- [GitHub 倉庫](https://github.com/streamlit/streamlit)

### 社區資源
- [Streamlit 社區論壇](https://discuss.streamlit.io/)
- [示例畫廊](https://streamlit.io/gallery)
- [Streamlit Components](https://streamlit.io/components)

### 相關工具
- [Streamlit Cloud](https://streamlit.io/cloud) - 部署平台
- [Streamlit Components](https://streamlit.io/components) - 第三方組件
- [awesome-streamlit](https://github.com/MarcSkovMadsen/awesome-streamlit) - 資源集合

## 生態系統

### 熱門應用案例
- 數據分析儀表板
- 機器學習模型展示
- BI 報表工具
- 股票分析工具
- COVID-19 追蹤器
- 客戶流失預測

### 第三方組件
- streamlit-aggrid: 高級表格
- streamlit-echarts: ECharts 圖表
- streamlit-pandas-profiling: 數據分析報告
- streamlit-option-menu: 菜單組件

### 整合案例
- Streamlit + LangChain
- Streamlit + HuggingFace
- Streamlit + OpenAI
- Streamlit + Plotly Dash
- Streamlit + SQLite

## 貢獻指南

歡迎貢獻新的範例或改進現有代碼！

1. Fork 本倉庫
2. 創建功能分支
3. 編寫清晰的註釋
4. 測試代碼
5. 提交 Pull Request

## 授權

本範例集採用 MIT 授權，可自由使用和修改。

## 更新日誌

- **2024-12**: 創建初始範例集
- 包含 10 個完整範例
- 涵蓋所有核心功能
- 繁體中文註釋

---

**開始探索** → 從 `01_快速開始.py` 開始你的 Streamlit 之旅！
