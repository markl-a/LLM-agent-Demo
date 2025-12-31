"""
Streamlit 雲端部署指南

運行方式：streamlit run 10_雲端部署.py
"""

import streamlit as st

st.set_page_config(page_title="雲端部署", page_icon="☁️", layout="wide")

st.title("☁️ Streamlit 雲端部署指南")
st.markdown("---")

# Streamlit Cloud 部署
st.header("1. Streamlit Cloud（推薦）")

st.markdown("""
### 📋 步驟

1. **準備代碼**
   - 將代碼推送到 GitHub
   - 添加 `requirements.txt`

2. **連接 Streamlit Cloud**
   - 訪問 [share.streamlit.io](https://share.streamlit.io)
   - 使用 GitHub 登錄
   - 選擇倉庫和分支

3. **配置應用**
   - 選擇主文件（如 `app.py`）
   - 設置環境變量（Secrets）
   - 點擊部署

4. **完成！**
   - 自動部署並生成 URL
   - 每次 Git Push 自動更新

### ✅ 優點
- 完全免費（公開應用）
- 自動 HTTPS
- 持續集成/部署
- 簡單易用

### 📝 Secrets 管理
在 Streamlit Cloud 設置中添加：
```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "sk-..."
DATABASE_URL = "postgresql://..."
```

在代碼中使用：
```python
import streamlit as st
api_key = st.secrets["OPENAI_API_KEY"]
```
""")

# Docker 部署
st.header("2. Docker 部署")

st.markdown("""
### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 構建和運行

```bash
# 構建鏡像
docker build -t my-streamlit-app .

# 運行容器
docker run -p 8501:8501 my-streamlit-app
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  streamlit:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```
""")

# 其他平台
st.header("3. 其他雲平台")

tab1, tab2, tab3 = st.tabs(["Hugging Face", "Railway", "Render"])

with tab1:
    st.markdown("""
    ### Hugging Face Spaces

    1. 創建 Space，選擇 Streamlit SDK
    2. 上傳代碼和 `requirements.txt`
    3. 自動部署

    特點：
    - ✅ 免費 CPU
    - ✅ 可選 GPU
    - ✅ 社區展示
    """)

with tab2:
    st.markdown("""
    ### Railway

    1. 連接 GitHub 倉庫
    2. 添加環境變量
    3. 設置啟動命令：`streamlit run app.py`

    特點：
    - ✅ 自動 HTTPS
    - ✅ 簡單配置
    - 💰 $5/月 免費額度
    """)

with tab3:
    st.markdown("""
    ### Render

    1. 創建 Web Service
    2. 連接 GitHub
    3. Build Command: `pip install -r requirements.txt`
    4. Start Command: `streamlit run app.py --server.port $PORT`

    特點：
    - ✅ 750 小時/月免費
    - ✅ 自動 SSL
    """)

# 生產配置
st.header("4. 生產環境配置")

st.markdown("""
### .streamlit/config.toml

```toml
[server]
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### 性能優化

```python
import streamlit as st

# 使用緩存
@st.cache_data
def load_data():
    return expensive_operation()

# 限制數據大小
st.set_page_config(
    page_title="App",
    page_icon="🎈",
    layout="wide",
    initial_sidebar_state="collapsed"
)
```

### 安全最佳實踐

1. **不要硬編碼密鑰**
2. **使用 st.secrets 或環境變量**
3. **啟用 HTTPS**
4. **驗證用戶輸入**
5. **定期更新依賴**
""")

# 監控和日誌
st.header("5. 監控和日誌")

st.code("""
import logging
import streamlit as st

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 記錄事件
logger.info(f"User visited page: {st.session_state.get('page', 'home')}")
""", language="python")

st.markdown("---")
st.success("✅ 準備好部署你的 Streamlit 應用了！")
