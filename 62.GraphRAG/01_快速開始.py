"""
GraphRAG 快速開始示例

這個示例展示了如何快速開始使用 GraphRAG 框架：
1. 環境配置
2. 基本索引構建
3. 簡單查詢
4. 結果展示

Author: GraphRAG Team
Date: 2025-12-31
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd


def setup_environment():
    """
    設置 GraphRAG 環境

    配置必要的環境變量和 API 密鑰
    """
    try:
        # 加載環境變量
        load_dotenv()

        # 檢查必要的環境變量
        api_key = os.getenv("GRAPHRAG_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  警告：未找到 API 密鑰")
            print("請在 .env 文件中設置 GRAPHRAG_API_KEY 或 OPENAI_API_KEY")
            return False

        # 設置環境變量
        os.environ["OPENAI_API_KEY"] = api_key

        print("✅ 環境配置成功")
        print(f"   API Key: {api_key[:10]}...")
        return True

    except Exception as e:
        print(f"❌ 環境配置失敗: {e}")
        return False


def create_sample_documents(output_dir: str = "./data/input"):
    """
    創建示例文檔

    Args:
        output_dir: 輸出目錄路徑
    """
    try:
        # 創建目錄
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 示例文檔內容
        documents = {
            "doc1.txt": """
            人工智能的發展歷程

            人工智能（Artificial Intelligence, AI）是計算機科學的一個分支，由 John McCarthy 在 1956 年的達特茅斯會議上首次提出。
            早期的 AI 研究集中在符號推理和專家系統上。

            在 21 世紀，深度學習的興起徹底改變了 AI 領域。Geoffrey Hinton、Yoshua Bengio 和 Yann LeCun
            因其在深度學習方面的貢獻而被稱為"深度學習三巨頭"。

            2022 年，OpenAI 發布了 ChatGPT，標誌著大型語言模型時代的到來。隨後，Google 發布了 Bard，
            Anthropic 發布了 Claude，微軟整合了 GPT-4 到 Bing。
            """,

            "doc2.txt": """
            知識圖譜技術簡介

            知識圖譜（Knowledge Graph）是一種結構化的知識表示方法，由 Google 在 2012 年提出。
            它使用圖結構來存儲實體及其之間的關係。

            知識圖譜的核心組成包括：
            1. 實體（Entity）：如人物、地點、組織
            2. 關係（Relation）：實體之間的連接
            3. 屬性（Attribute）：實體的特徵

            主要應用包括語義搜索、問答系統、推薦系統等。DBpedia、Wikidata 和 YAGO 是著名的開放知識圖譜。
            """,

            "doc3.txt": """
            RAG 技術演進

            檢索增強生成（Retrieval-Augmented Generation, RAG）是結合檢索和生成的技術框架。
            Facebook AI Research（現 Meta AI）的 Patrick Lewis 等人在 2020 年提出了這一概念。

            傳統 RAG 使用向量數據庫進行語義檢索，然後將檢索結果與提示詞一起送入大型語言模型。

            Microsoft Research 在 2024 年提出 GraphRAG，通過構建知識圖譜來增強 RAG 系統，
            使其能夠回答需要全局理解的複雜問題。GraphRAG 使用社區檢測算法來識別主題和概念集群。
            """
        }

        # 寫入文檔
        for filename, content in documents.items():
            file_path = os.path.join(output_dir, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content.strip())

        print(f"✅ 創建了 {len(documents)} 個示例文檔")
        print(f"   目錄: {output_dir}")
        return True

    except Exception as e:
        print(f"❌ 創建示例文檔失敗: {e}")
        return False


def initialize_graphrag_project(root_dir: str = "./graphrag_quickstart"):
    """
    初始化 GraphRAG 項目

    Args:
        root_dir: 項目根目錄
    """
    try:
        import subprocess

        # 創建項目目錄
        Path(root_dir).mkdir(parents=True, exist_ok=True)

        print(f"📁 初始化 GraphRAG 項目: {root_dir}")

        # 運行 graphrag init 命令
        # 注意：這需要安裝 graphrag CLI
        result = subprocess.run(
            ["graphrag", "init", "--root", root_dir],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ 項目初始化成功")
            print(f"   配置文件: {root_dir}/settings.yaml")
            print(f"   輸入目錄: {root_dir}/input")
            return True
        else:
            print(f"⚠️  項目初始化命令執行失敗: {result.stderr}")
            print("   手動創建項目結構...")

            # 手動創建必要的目錄
            dirs = ["input", "output", "cache", "prompts"]
            for dir_name in dirs:
                Path(root_dir, dir_name).mkdir(exist_ok=True)

            print("✅ 手動創建項目結構成功")
            return True

    except FileNotFoundError:
        print("⚠️  未找到 graphrag CLI，手動創建項目結構...")
        try:
            # 創建基本目錄結構
            Path(root_dir).mkdir(parents=True, exist_ok=True)
            dirs = ["input", "output", "cache", "prompts"]
            for dir_name in dirs:
                Path(root_dir, dir_name).mkdir(exist_ok=True)

            print("✅ 手動創建項目結構成功")
            return True
        except Exception as e:
            print(f"❌ 創建項目結構失敗: {e}")
            return False
    except Exception as e:
        print(f"❌ 項目初始化失敗: {e}")
        return False


def build_index_programmatic(input_dir: str, output_dir: str):
    """
    使用程序化方式構建索引

    這是一個簡化的示例，展示索引構建的基本流程
    實際使用中建議使用 CLI 命令或完整的 Python API

    Args:
        input_dir: 輸入文檔目錄
        output_dir: 輸出索引目錄
    """
    try:
        print("📊 開始構建索引...")
        print("   注意：這是一個簡化的演示流程")
        print("   實際使用請運行: graphrag index --root <project_dir>")

        # 讀取文檔
        documents = []
        for file_path in Path(input_dir).glob("*.txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append({
                    "id": file_path.stem,
                    "text": content
                })

        print(f"✅ 讀取了 {len(documents)} 個文檔")

        # 在實際應用中，這裡會：
        # 1. 使用 LLM 提取實體和關係
        # 2. 構建知識圖譜
        # 3. 執行社區檢測
        # 4. 生成嵌入向量
        # 5. 保存索引

        print("💡 提示：完整的索引構建需要:")
        print("   1. 配置 settings.yaml")
        print("   2. 運行 'graphrag index --root <project_dir>'")
        print("   3. 等待處理完成（可能需要較長時間）")

        return True

    except Exception as e:
        print(f"❌ 構建索引失敗: {e}")
        return False


def simple_query_example():
    """
    簡單查詢示例

    展示如何使用 GraphRAG 進行查詢
    """
    try:
        print("\n🔍 查詢示例")
        print("=" * 60)

        # 示例查詢
        queries = [
            ("local", "誰是深度學習三巨頭？"),
            ("global", "這些文檔的主要主題是什麼？"),
            ("local", "知識圖譜是什麼時候提出的？"),
            ("global", "AI 領域有哪些重要的發展趨勢？")
        ]

        print("以下是查詢示例（需要已構建的索引）：\n")

        for method, query in queries:
            print(f"📌 查詢類型: {method.upper()}")
            print(f"   問題: {query}")
            print(f"   命令: graphrag query --method {method} \"{query}\"")
            print()

        print("💡 說明：")
        print("   • Local Search: 適合特定事實查詢（如人名、日期）")
        print("   • Global Search: 適合主題總結和趨勢分析")
        print()

        return True

    except Exception as e:
        print(f"❌ 查詢示例生成失敗: {e}")
        return False


def display_results_format():
    """
    展示結果格式
    """
    print("\n📊 GraphRAG 查詢結果格式")
    print("=" * 60)

    # Local Search 結果示例
    print("\n1️⃣  Local Search 結果示例:")
    print("""
    {
        "answer": "深度學習三巨頭是指 Geoffrey Hinton、Yoshua Bengio 和 Yann LeCun...",
        "entities": [
            {"name": "Geoffrey Hinton", "type": "Person", "description": "..."},
            {"name": "Yoshua Bengio", "type": "Person", "description": "..."},
            {"name": "Yann LeCun", "type": "Person", "description": "..."}
        ],
        "relationships": [
            {"source": "Geoffrey Hinton", "target": "Deep Learning", "type": "contributed_to"}
        ],
        "sources": ["doc1.txt"]
    }
    """)

    # Global Search 結果示例
    print("\n2️⃣  Global Search 結果示例:")
    print("""
    {
        "answer": "這些文檔主要涵蓋三個主題：1) 人工智能的發展歷程...",
        "communities": [
            {
                "id": 1,
                "title": "人工智能發展",
                "summary": "記錄了 AI 從符號推理到深度學習再到大型語言模型的演進...",
                "entities": ["John McCarthy", "Geoffrey Hinton", "OpenAI", "ChatGPT"]
            },
            {
                "id": 2,
                "title": "知識表示技術",
                "summary": "介紹知識圖譜的概念、組成和應用...",
                "entities": ["Knowledge Graph", "Google", "DBpedia"]
            }
        ],
        "confidence": 0.92
    }
    """)

    print("\n💡 結果包含的信息：")
    print("   • 自然語言答案")
    print("   • 相關實體和關係")
    print("   • 證據來源")
    print("   • 置信度評分")


def main():
    """
    主函數：演示 GraphRAG 快速開始流程
    """
    print("=" * 70)
    print("🚀 GraphRAG 快速開始示例".center(70))
    print("=" * 70)
    print()

    # 步驟 1: 環境配置
    print("步驟 1: 環境配置")
    print("-" * 70)
    if not setup_environment():
        print("\n⚠️  環境配置失敗，部分功能可能無法使用")
        print("提示：創建 .env 文件並添加:")
        print("GRAPHRAG_API_KEY=your_openai_api_key_here")
    print()

    # 步驟 2: 創建示例文檔
    print("步驟 2: 創建示例文檔")
    print("-" * 70)
    create_sample_documents("./data/input")
    print()

    # 步驟 3: 初始化項目
    print("步驟 3: 初始化 GraphRAG 項目")
    print("-" * 70)
    initialize_graphrag_project("./graphrag_quickstart")
    print()

    # 步驟 4: 構建索引（簡化示例）
    print("步驟 4: 構建索引")
    print("-" * 70)
    build_index_programmatic("./data/input", "./graphrag_quickstart/output")
    print()

    # 步驟 5: 查詢示例
    print("步驟 5: 查詢示例")
    print("-" * 70)
    simple_query_example()

    # 步驟 6: 結果格式
    display_results_format()

    # 總結
    print("\n" + "=" * 70)
    print("📚 後續步驟")
    print("=" * 70)
    print("""
    1. 將您的文檔放入 ./graphrag_quickstart/input 目錄
    2. 配置 ./graphrag_quickstart/settings.yaml（可選）
    3. 運行索引構建：
       graphrag index --root ./graphrag_quickstart
    4. 執行查詢：
       graphrag query --root ./graphrag_quickstart --method global "您的問題"
    5. 查看結果並優化配置

    💡 提示：
       • 索引構建可能需要較長時間和 API 調用費用
       • 從小數據集開始測試
       • 查看其他示例文件學習高級功能
    """)

    print("\n✅ 快速開始示例完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  程序被用戶中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 程序執行出錯: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
