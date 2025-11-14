# 🚀 LLM Agent Demo - 安裝指南

本指南將幫助您快速設置和運行 LLM Agent Demo 專案。

## 📋 系統需求

### 必需
- **Python**: 3.9 或更高版本（推薦 3.11）
- **pip**: 最新版本
- **Git**: 用於克隆專案

### 可選
- **Docker**: 如果使用容器化部署
- **CUDA**: 如果需要 GPU 加速（用於本地嵌入模型）

### 硬體建議
- **記憶體**: 至少 8GB RAM（推薦 16GB）
- **存儲**: 至少 5GB 可用空間
- **網絡**: 穩定的互聯網連接（用於 API 調用）

## 🛠️ 安裝方式

### 方式 1: 本地虛擬環境（推薦用於開發）

#### Step 1: 克隆專案

```bash
git clone https://github.com/yourusername/LLM-agent-Demo.git
cd LLM-agent-Demo
```

#### Step 2: 創建虛擬環境

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

#### Step 3: 升級 pip

```bash
pip install --upgrade pip
```

#### Step 4: 安裝依賴

```bash
pip install -r requirements.txt
```

這可能需要 5-10 分鐘，取決於您的網絡速度。

#### Step 5: 配置環境變數

```bash
# 複製範例文件
cp .env.example .env

# 編輯 .env 文件，添加你的 API Keys
# Linux/macOS:
nano .env
# 或使用你喜歡的編輯器

# Windows:
notepad .env
```

至少需要配置一個 LLM 提供商的 API Key：
- OpenAI: `OPENAI_API_KEY`
- Google Gemini: `GOOGLE_API_KEY`
- Anthropic Claude: `ANTHROPIC_API_KEY`
- Groq: `GROQ_API_KEY`

#### Step 6: 驗證安裝

```bash
# 測試 Python 導入
python -c "import langchain; import llama_index; print('安裝成功！')"
```

#### Step 7: 啟動 Jupyter Lab

```bash
jupyter lab
```

瀏覽器會自動打開 http://localhost:8888

---

### 方式 2: Docker 容器（推薦用於快速體驗）

#### Step 1: 安裝 Docker

- [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- [Docker for Linux](https://docs.docker.com/engine/install/)

#### Step 2: 克隆專案

```bash
git clone https://github.com/yourusername/LLM-agent-Demo.git
cd LLM-agent-Demo
```

#### Step 3: 配置環境變數

```bash
cp .env.example .env
# 編輯 .env 文件
```

#### Step 4: 啟動容器

```bash
docker-compose up -d
```

第一次運行會下載映像和構建容器，需要 10-20 分鐘。

#### Step 5: 訪問 Jupyter Lab

打開瀏覽器訪問: http://localhost:8888

#### 管理容器

```bash
# 查看日誌
docker-compose logs -f

# 停止容器
docker-compose down

# 重啟容器
docker-compose restart

# 進入容器
docker exec -it llm-agent-demo bash
```

---

### 方式 3: Conda 環境（推薦用於數據科學用戶）

#### Step 1: 安裝 Anaconda/Miniconda

下載並安裝: https://www.anaconda.com/download

#### Step 2: 創建 Conda 環境

```bash
conda create -n llm-agent python=3.11
conda activate llm-agent
```

#### Step 3: 克隆專案並安裝依賴

```bash
git clone https://github.com/yourusername/LLM-agent-Demo.git
cd LLM-agent-Demo
pip install -r requirements.txt
```

#### Step 4: 配置並啟動

```bash
cp .env.example .env
# 編輯 .env
jupyter lab
```

---

## 🔑 API Keys 獲取指南

### OpenAI

1. 訪問 https://platform.openai.com/api-keys
2. 登錄或註冊帳號
3. 點擊 "Create new secret key"
4. 複製 API Key 並保存到 `.env`

**費用**: Pay-as-you-go，GPT-4 約 $0.03/1K tokens

### Google Gemini

1. 訪問 https://makersuite.google.com/app/apikey
2. 登錄 Google 帳號
3. 點擊 "Get API key"
4. 複製並保存

**費用**: 有免費額度，超出後按使用計費

### Anthropic Claude

1. 訪問 https://console.anthropic.com/
2. 註冊帳號
3. 進入 API Keys 頁面
4. 創建並複製 API Key

**費用**: Pay-as-you-go，Claude 3.5 Sonnet 約 $0.003/1K tokens

### Groq

1. 訪問 https://console.groq.com/
2. 註冊帳號
3. 創建 API Key

**費用**: 目前提供免費額度

---

## 📦 可選組件安裝

### 向量數據庫

#### Chroma（本地，已包含在 requirements.txt）
```bash
# 無需額外安裝，已包含在依賴中
```

#### Pinecone（雲端）
```bash
pip install pinecone-client
```
配置:
```bash
PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=your_env
```

#### Qdrant（本地或雲端）
```bash
# 本地安裝
docker run -p 6333:6333 qdrant/qdrant

# Python 客戶端已包含在 requirements.txt
```

### GPU 加速（可選）

如果您有 NVIDIA GPU：

```bash
# 卸載 CPU 版本
pip uninstall faiss-cpu

# 安裝 GPU 版本
pip install faiss-gpu

# 安裝 CUDA 相關庫（如需要）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## ✅ 驗證安裝

### 測試基本功能

創建測試腳本 `test_installation.py`:

```python
#!/usr/bin/env python3
"""測試 LLM Agent Demo 安裝"""

import sys

def test_imports():
    """測試基本導入"""
    print("測試 Python 包導入...")

    try:
        import langchain
        print("✓ LangChain 導入成功")
    except ImportError as e:
        print(f"✗ LangChain 導入失敗: {e}")
        return False

    try:
        import llama_index
        print("✓ LlamaIndex 導入成功")
    except ImportError as e:
        print(f"✗ LlamaIndex 導入失敗: {e}")
        return False

    try:
        import chromadb
        print("✓ ChromaDB 導入成功")
    except ImportError as e:
        print(f"✗ ChromaDB 導入失敗: {e}")
        return False

    try:
        import autogen
        print("✓ AutoGen 導入成功")
    except ImportError as e:
        print(f"✗ AutoGen 導入失敗: {e}")
        return False

    try:
        import crewai
        print("✓ CrewAI 導入成功")
    except ImportError as e:
        print(f"✗ CrewAI 導入失敗: {e}")
        return False

    return True

def test_env():
    """測試環境變數"""
    import os
    from dotenv import load_dotenv

    print("\n測試環境變數...")
    load_dotenv()

    api_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
    }

    found = False
    for key, value in api_keys.items():
        if value and value != f'your_{key.lower().replace("_", "_")}_here':
            print(f"✓ {key} 已配置")
            found = True
        else:
            print(f"○ {key} 未配置（可選）")

    if not found:
        print("\n⚠️  警告: 未發現任何已配置的 API Key")
        print("請編輯 .env 文件並添加至少一個 LLM 提供商的 API Key")

    return True

def main():
    print("=" * 50)
    print("LLM Agent Demo - 安裝驗證")
    print("=" * 50)

    if not test_imports():
        print("\n❌ 導入測試失敗")
        sys.exit(1)

    test_env()

    print("\n" + "=" * 50)
    print("✅ 安裝驗證完成！")
    print("=" * 50)
    print("\n下一步:")
    print("1. 確保至少配置一個 LLM API Key")
    print("2. 運行: jupyter lab")
    print("3. 打開任意 .ipynb 文件開始學習")

if __name__ == '__main__':
    main()
```

運行測試:

```bash
python test_installation.py
```

---

## 🐛 常見問題

### 問題 1: pip install 失敗

**解決方案:**
```bash
# 升級 pip
pip install --upgrade pip setuptools wheel

# 清理緩存
pip cache purge

# 重試安裝
pip install -r requirements.txt
```

### 問題 2: 導入錯誤

**症狀:** `ModuleNotFoundError: No module named 'xxx'`

**解決方案:**
```bash
# 確認虛擬環境已激活
which python  # Linux/macOS
where python  # Windows

# 重新安裝特定包
pip install --upgrade --force-reinstall package_name
```

### 問題 3: Jupyter Lab 無法啟動

**解決方案:**
```bash
# 重新安裝 Jupyter
pip install --upgrade jupyter jupyterlab

# 清理配置
jupyter lab clean

# 重啟
jupyter lab
```

### 問題 4: Docker 構建失敗

**解決方案:**
```bash
# 清理舊容器和映像
docker-compose down
docker system prune -a

# 重新構建
docker-compose build --no-cache
docker-compose up -d
```

### 問題 5: API 調用失敗

**檢查清單:**
- [ ] API Key 是否正確配置在 `.env`
- [ ] API Key 是否有效（未過期）
- [ ] 帳號是否有足夠額度
- [ ] 網絡連接是否正常
- [ ] 是否在支持的地區（某些 API 有地區限制）

---

## 📞 獲取幫助

如果遇到問題:

1. **查看文檔**: 閱讀 [README.md](README.md)
2. **搜索 Issues**: https://github.com/yourusername/LLM-agent-Demo/issues
3. **提出問題**: 創建新的 Issue
4. **社區討論**: GitHub Discussions

---

## 🎉 安裝成功！

現在您可以:

1. 啟動 Jupyter Lab: `jupyter lab`
2. 瀏覽學習路徑: 查看 [README.md](README.md#學習路徑)
3. 運行範例: 打開任意 `.ipynb` 文件
4. 開始學習: 從 `1.LangchainDemos/0.簡單的RAG_範例.ipynb` 開始

祝學習愉快！🚀
