# LangChain Demos 環境設置指南

## 快速開始（5分鐘）

### 步驟 1: 克隆專案

```bash
git clone https://github.com/markl-a/LLM-agent-Demo.git
cd LLM-agent-Demo/1.LangchainDemos
```

### 步驟 2: 建立虛擬環境

#### 使用 venv（推薦）

```bash
# 創建虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

#### 使用 conda（替代方案）

```bash
# 創建虛擬環境
conda create -n langchain-demos python=3.10

# 啟動虛擬環境
conda activate langchain-demos
```

### 步驟 3: 安裝依賴

```bash
# 安裝所有依賴
pip install -r requirements.txt

# 或者分步驟安裝（針對特定需求）
# 基礎環境
pip install langchain langchain-community langchain-core
pip install langchain-openai chromadb sentence-transformers

# 如果遇到安裝問題，可以使用國內鏡像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步驟 4: 配置環境變數

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 文件，填入你的 API Keys
# Windows
notepad .env
# Linux/Mac
nano .env
# 或使用你喜歡的編輯器
```

**最少需要配置的 API Key：**
- `OPENAI_API_KEY`: 必需（用於運行大部分範例）
- `LANGCHAIN_API_KEY`: 強烈建議（用於追蹤和除錯）

### 步驟 5: 驗證安裝

```bash
# 運行驗證腳本
python verify_setup.py

# 或手動驗證
python -c "import langchain; from langchain_openai import ChatOpenAI; print('安裝成功!')"
```

### 步驟 6: 啟動 Jupyter Notebook

```bash
jupyter notebook
```

瀏覽器會自動打開，選擇任一 `.ipynb` 文件開始學習！

---

## 詳細設置說明

### 系統需求

- **Python**: 3.9 - 3.12（推薦 3.10）
- **記憶體**: 至少 8GB RAM（16GB 推薦）
- **磁碟空間**: 至少 5GB 可用空間
- **作業系統**: Windows 10/11, macOS, Linux

### 依賴說明

#### 核心依賴（必需）

```bash
pip install langchain langchain-community langchain-core
pip install langchain-openai
pip install chromadb sentence-transformers
pip install jupyter notebook
```

#### 進階功能依賴

```bash
# LangGraph（用於 Agent 開發）
pip install langgraph

# 多種 LLM 提供者支援
pip install langchain-anthropic  # Claude
pip install langchain-huggingface  # 開源模型

# 搜尋工具
pip install tavily-python

# SQL Agent
pip install sqlalchemy sqlite-utils
```

#### GPU 加速（選用）

如果有 NVIDIA GPU，可以安裝 GPU 版本以加速本地模型推理：

```bash
# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 使用 GPU 版本的 FAISS
pip uninstall faiss-cpu
pip install faiss-gpu
```

### API Keys 獲取指南

#### 1. OpenAI API Key（必需）

1. 訪問 https://platform.openai.com/signup
2. 註冊並登入帳號
3. 前往 https://platform.openai.com/api-keys
4. 點擊 "Create new secret key"
5. 複製 API Key（以 `sk-` 開頭）
6. 充值帳戶（建議先充值 $5-10 美元）

**注意事項：**
- 新用戶有 $5 的免費額度（有時間限制）
- 使用 GPT-4 會較貴，建議先用 GPT-3.5
- 設置使用限額以避免意外超支

#### 2. LangSmith API Key（強烈建議）

1. 訪問 https://smith.langchain.com/
2. 使用 GitHub/Google 登入
3. 前往 Settings → API Keys
4. 創建新的 API Key
5. 複製 Key（以 `ls__` 開頭）

**功能：**
- 追蹤每次 LLM 調用
- 視覺化工作流程
- 除錯和優化提示
- 免費版本已足夠學習使用

#### 3. HuggingFace Token（選用）

1. 訪問 https://huggingface.co/join
2. 註冊並登入
3. 前往 https://huggingface.co/settings/tokens
4. 創建 "Read" 權限的 Token
5. 複製 Token（以 `hf_` 開頭）

**用途：**
- 下載開源模型
- 使用 HuggingFace Inference API
- 訪問受限模型（如 Llama）

#### 4. Tavily API Key（建議）

1. 訪問 https://tavily.com/
2. 註冊免費帳號
3. 複製 API Key

**功能：**
- 用於 Agent 的網路搜尋
- 免費版本每月 1000 次搜尋

#### 5. Groq API Key（選用）

1. 訪問 https://console.groq.com/
2. 註冊並登入
3. 創建 API Key

**優勢：**
- 極快的推理速度
- 免費額度充足
- 支援 Llama3、Mixtral 等模型

### 驗證腳本

創建 `verify_setup.py` 文件來驗證安裝：

```python
#!/usr/bin/env python3
"""
LangChain Demos 環境驗證腳本
"""
import sys
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def check_python_version():
    """檢查 Python 版本"""
    print("檢查 Python 版本...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python 版本過舊: {version.major}.{version.minor}.{version.micro}")
        print("   請安裝 Python 3.9 或更高版本")
        return False

def check_package(package_name, import_name=None):
    """檢查套件是否已安裝"""
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} 未安裝")
        return False

def check_packages():
    """檢查所有必需套件"""
    print("\n檢查必需套件...")

    packages = [
        ("langchain", "langchain"),
        ("langchain-community", "langchain_community"),
        ("langchain-core", "langchain_core"),
        ("langchain-openai", "langchain_openai"),
        ("chromadb", "chromadb"),
        ("sentence-transformers", "sentence_transformers"),
        ("jupyter", "jupyter"),
    ]

    results = []
    for package_name, import_name in packages:
        results.append(check_package(package_name, import_name))

    return all(results)

def check_env_vars():
    """檢查環境變數"""
    print("\n檢查環境變數...")

    required_vars = {
        "OPENAI_API_KEY": "OpenAI API Key（必需）",
    }

    optional_vars = {
        "LANGCHAIN_API_KEY": "LangSmith API Key（建議）",
        "TAVILY_API_KEY": "Tavily API Key（建議）",
        "HUGGINGFACE_TOKEN": "HuggingFace Token（選用）",
    }

    all_ok = True

    # 檢查必需變數
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value and value != f"your-{var.lower().replace('_', '-')}-here":
            print(f"✅ {desc}")
        else:
            print(f"❌ {desc} - 未設置或使用範本值")
            all_ok = False

    # 檢查選用變數
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value and value != f"your-{var.lower().replace('_', '-')}-here":
            print(f"✅ {desc}")
        else:
            print(f"⚠️  {desc} - 未設置")

    return all_ok

def test_openai_connection():
    """測試 OpenAI 連接"""
    print("\n測試 OpenAI 連接...")

    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=10)
        response = llm.invoke("Say 'Hello'")
        print(f"✅ OpenAI 連接成功")
        print(f"   測試回應: {response.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI 連接失敗: {str(e)}")
        return False

def main():
    """主函數"""
    print("=" * 60)
    print("LangChain Demos 環境驗證")
    print("=" * 60)

    results = []

    # 執行各項檢查
    results.append(check_python_version())
    results.append(check_packages())
    results.append(check_env_vars())

    # 如果基本檢查通過，測試 OpenAI 連接
    if all(results):
        results.append(test_openai_connection())

    # 總結
    print("\n" + "=" * 60)
    if all(results):
        print("🎉 所有檢查通過！環境配置完成。")
        print("\n下一步：")
        print("1. 執行: jupyter notebook")
        print("2. 開啟任一 .ipynb 文件開始學習")
    else:
        print("⚠️  部分檢查未通過，請根據上述提示進行修復。")
        print("\n常見問題：")
        print("- 套件未安裝: pip install -r requirements.txt")
        print("- API Key 未設置: 編輯 .env 文件")
        print("- API Key 無效: 檢查 Key 是否正確複製")
    print("=" * 60)

    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())
```

將上述內容保存為 `verify_setup.py`，然後運行：

```bash
python verify_setup.py
```

### 常見安裝問題

#### 問題 1: pip 安裝速度慢

**解決方案：使用國內鏡像**

```bash
# 臨時使用
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 問題 2: chromadb 安裝失敗

**解決方案：**

```bash
# 方案 1: 升級 pip
pip install --upgrade pip setuptools wheel

# 方案 2: 使用預編譯版本
pip install chromadb --no-build-isolation

# 方案 3: Windows 用戶安裝 Visual C++ Build Tools
# 下載: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

#### 問題 3: sentence-transformers 下載模型慢

**解決方案：使用鏡像**

```python
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

#### 問題 4: Jupyter Notebook 無法啟動

**解決方案：**

```bash
# 重新安裝 Jupyter
pip uninstall jupyter notebook
pip install jupyter notebook

# 或使用 JupyterLab（現代化界面）
pip install jupyterlab
jupyter lab
```

#### 問題 5: 'No module named xxx' 錯誤

**解決方案：確保使用正確的 Python 環境**

```bash
# 檢查當前 Python 路徑
which python  # Linux/Mac
where python  # Windows

# 檢查已安裝的套件
pip list | grep langchain

# 確保在虛擬環境中
# 如果不在，重新啟動虛擬環境
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

### 進階配置

#### 1. 配置 LangSmith 追蹤

在 `.env` 文件中：

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=my-project-name
```

在程式碼中：

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "my-project-name"
```

#### 2. 配置向量資料庫持久化

```python
from langchain_community.vectorstores import Chroma

# 持久化到磁碟
db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)
```

#### 3. 配置日誌

```python
import logging

# 設置 LangChain 日誌級別
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("langchain")
logger.setLevel(logging.DEBUG)
```

#### 4. 使用代理（Proxy）

如果需要通過代理訪問 API：

```bash
# 在 .env 中設置
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080
```

或在程式碼中：

```python
import os
os.environ["HTTP_PROXY"] = "http://proxy.example.com:8080"
os.environ["HTTPS_PROXY"] = "http://proxy.example.com:8080"
```

### 下一步

環境設置完成後，建議按照以下順序學習：

1. **閱讀 README.md** - 了解專案結構和學習路徑
2. **運行 0.簡單的RAG_範例.ipynb** - 快速入門
3. **探索其他範例** - 根據興趣選擇
4. **參考 BEST_PRACTICES.md** - 學習最佳實踐（即將創建）

### 獲取幫助

- 查看 [常見問題](README.md#常見問題)
- 提交 [Issue](https://github.com/markl-a/LLM-agent-Demo/issues)
- 參考 [LangChain 官方文檔](https://python.langchain.com/)

---

**祝學習愉快！**
