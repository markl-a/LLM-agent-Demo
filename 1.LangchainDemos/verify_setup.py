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
        module = __import__(import_name)
        # 嘗試獲取版本號
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {package_name} ({version})")
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

def check_optional_packages():
    """檢查選用套件"""
    print("\n檢查選用套件...")

    optional_packages = [
        ("langgraph", "langgraph"),
        ("langchain-anthropic", "langchain_anthropic"),
        ("langchain-huggingface", "langchain_huggingface"),
        ("tavily-python", "tavily"),
    ]

    for package_name, import_name in optional_packages:
        check_package(package_name, import_name)

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
        "ANTHROPIC_API_KEY": "Anthropic API Key（選用）",
        "GROQ_API_KEY": "Groq API Key（選用）",
    }

    all_ok = True

    # 檢查必需變數
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value and not value.startswith("your-") and not value.startswith("sk-your"):
            # 遮蔽大部分 Key 內容
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {desc}: {masked_value}")
        else:
            print(f"❌ {desc} - 未設置或使用範本值")
            all_ok = False

    # 檢查選用變數
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value and not value.startswith("your-") and not value.startswith("sk-your"):
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {desc}: {masked_value}")
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
        print("\n可能的原因：")
        print("- API Key 無效或未設置")
        print("- 網絡連接問題")
        print("- API 配額已用完")
        print("- 需要配置代理")
        return False

def test_embedding():
    """測試 Embedding 功能"""
    print("\n測試 Embedding 功能...")

    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode("Test sentence")
        print(f"✅ Embedding 功能正常 (向量維度: {len(embedding)})")
        return True
    except Exception as e:
        print(f"❌ Embedding 測試失敗: {str(e)}")
        return False

def test_vector_db():
    """測試向量資料庫"""
    print("\n測試向量資料庫...")

    try:
        from langchain_community.vectorstores import Chroma
        from langchain_community.embeddings import SentenceTransformerEmbeddings
        from langchain.schema import Document

        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        docs = [Document(page_content="Test document")]

        # 創建臨時向量資料庫
        db = Chroma.from_documents(docs, embeddings)
        results = db.similarity_search("Test", k=1)

        print(f"✅ 向量資料庫功能正常 (找到 {len(results)} 個結果)")
        return True
    except Exception as e:
        print(f"❌ 向量資料庫測試失敗: {str(e)}")
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

    # 檢查選用套件（不影響總體結果）
    check_optional_packages()

    results.append(check_env_vars())

    # 如果基本檢查通過，執行功能測試
    if all(results):
        print("\n" + "=" * 60)
        print("執行功能測試...")
        print("=" * 60)

        test_results = []
        test_results.append(test_embedding())
        test_results.append(test_vector_db())
        test_results.append(test_openai_connection())

        # 功能測試結果不影響整體結果，但會顯示警告
        if not all(test_results):
            print("\n⚠️  部分功能測試未通過，但基本環境已配置完成。")

    # 總結
    print("\n" + "=" * 60)
    if all(results):
        print("🎉 環境配置檢查通過！")
        print("\n下一步：")
        print("1. 執行: jupyter notebook")
        print("2. 開啟 '0.簡單的RAG_範例.ipynb' 開始學習")
        print("\n推薦學習路徑：")
        print("- 基礎入門: 0 → 1 → 2")
        print("- 核心技術: 3 → 4 → 6")
        print("- 進階應用: 5 → 9 → 7")
    else:
        print("⚠️  部分檢查未通過，請根據上述提示進行修復。")
        print("\n常見解決方案：")
        print("- 套件未安裝: pip install -r requirements.txt")
        print("- API Key 未設置: cp .env.example .env 並編輯")
        print("- Python 版本過舊: 升級到 Python 3.9+")
        print("\n詳細設置指南: 查看 SETUP_GUIDE.md")
    print("=" * 60)

    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())
