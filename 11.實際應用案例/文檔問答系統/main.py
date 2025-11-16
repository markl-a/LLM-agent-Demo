#!/usr/bin/env python3
"""
文檔問答系統 - 命令行版本

使用方法:
  python main.py --index data/           # 索引文檔
  python main.py --query "你的問題"       # 提問
  python main.py --interactive           # 互動模式
"""

import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

try:
    from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        StorageContext,
        load_index_from_storage,
    )
    from llama_index.core.node_parser import SentenceSplitter
    print("✓ 已導入 LlamaIndex")
except ImportError:
    print("警告: 未安裝 LlamaIndex，請運行: pip install llama-index")
    print("使用示例配置繼續...")


class DocumentQASystem:
    """文檔問答系統"""

    def __init__(self, persist_dir="./vectorstore"):
        """
        初始化問答系統

        Args:
            persist_dir: 向量數據庫持久化目錄
        """
        self.persist_dir = persist_dir
        self.index = None

        # 檢查 API Key
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
            print("警告: 未設置 OPENAI_API_KEY 或 GOOGLE_API_KEY")
            print("請在 .env 文件中設置")

    def index_documents(self, data_dir):
        """
        索引文檔目錄

        Args:
            data_dir: 文檔目錄路徑
        """
        print(f"\n📂 正在加載文檔: {data_dir}")

        try:
            # 加載文檔
            documents = SimpleDirectoryReader(
                data_dir,
                recursive=True
            ).load_data()

            print(f"✓ 已加載 {len(documents)} 個文檔")

            # 創建文本分割器
            text_splitter = SentenceSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )

            # 創建索引
            print("🔨 正在創建索引...")
            self.index = VectorStoreIndex.from_documents(
                documents,
                transformations=[text_splitter],
                show_progress=True
            )

            # 持久化索引
            print(f"💾 正在保存索引到: {self.persist_dir}")
            self.index.storage_context.persist(persist_dir=self.persist_dir)

            print("✓ 索引創建完成！")

        except Exception as e:
            print(f"❌ 索引失敗: {str(e)}")
            raise

    def load_index(self):
        """加載已存在的索引"""
        if not Path(self.persist_dir).exists():
            raise FileNotFoundError(
                f"索引目錄不存在: {self.persist_dir}\n"
                "請先使用 --index 命令創建索引"
            )

        print(f"📂 正在加載索引: {self.persist_dir}")
        storage_context = StorageContext.from_defaults(
            persist_dir=self.persist_dir
        )
        self.index = load_index_from_storage(storage_context)
        print("✓ 索引加載完成")

    def query(self, question, verbose=True):
        """
        查詢問題

        Args:
            question: 用戶問題
            verbose: 是否顯示詳細信息

        Returns:
            答案字符串
        """
        if self.index is None:
            self.load_index()

        if verbose:
            print(f"\n💬 問題: {question}")
            print("🤔 正在思考...")

        # 創建查詢引擎
        query_engine = self.index.as_query_engine(
            similarity_top_k=5,
            response_mode="compact"
        )

        # 執行查詢
        response = query_engine.query(question)

        if verbose:
            print(f"\n✅ 答案:")
            print(response.response)

            # 顯示來源
            if hasattr(response, 'source_nodes') and response.source_nodes:
                print(f"\n📚 來源文檔:")
                for i, node in enumerate(response.source_nodes[:3], 1):
                    file_name = node.node.metadata.get('file_name', '未知')
                    score = node.score
                    print(f"  {i}. {file_name} (相似度: {score:.2f})")

        return response.response

    def interactive_mode(self):
        """互動模式"""
        print("\n" + "="*60)
        print("文檔問答系統 - 互動模式")
        print("="*60)
        print("輸入 'exit' 或 'quit' 退出")
        print("輸入 'help' 查看幫助")
        print("="*60 + "\n")

        # 加載索引
        try:
            self.load_index()
        except FileNotFoundError as e:
            print(f"❌ {str(e)}")
            return

        while True:
            try:
                # 獲取用戶輸入
                question = input("\n💭 您的問題: ").strip()

                # 檢查退出命令
                if question.lower() in ['exit', 'quit', 'q']:
                    print("👋 再見！")
                    break

                # 幫助信息
                if question.lower() == 'help':
                    print("\n可用命令:")
                    print("  - 直接輸入問題進行查詢")
                    print("  - 'exit', 'quit', 'q': 退出")
                    print("  - 'help': 顯示此幫助")
                    continue

                # 跳過空輸入
                if not question:
                    continue

                # 執行查詢
                self.query(question, verbose=True)

            except KeyboardInterrupt:
                print("\n\n👋 再見！")
                break
            except Exception as e:
                print(f"❌ 錯誤: {str(e)}")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="文檔問答系統",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 索引文檔
  python main.py --index data/

  # 提問
  python main.py --query "公司的休假政策是什麼？"

  # 互動模式
  python main.py --interactive
        """
    )

    parser.add_argument(
        '--index',
        type=str,
        help='索引文檔目錄'
    )

    parser.add_argument(
        '--query',
        type=str,
        help='提出問題'
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='啟動互動模式'
    )

    parser.add_argument(
        '--persist-dir',
        type=str,
        default='./vectorstore',
        help='向量數據庫目錄（默認: ./vectorstore）'
    )

    args = parser.parse_args()

    # 創建問答系統
    qa_system = DocumentQASystem(persist_dir=args.persist_dir)

    # 執行命令
    if args.index:
        # 索引文檔
        qa_system.index_documents(args.index)

    elif args.query:
        # 回答問題
        qa_system.query(args.query)

    elif args.interactive:
        # 互動模式
        qa_system.interactive_mode()

    else:
        # 沒有指定命令，顯示幫助
        parser.print_help()


if __name__ == "__main__":
    main()
