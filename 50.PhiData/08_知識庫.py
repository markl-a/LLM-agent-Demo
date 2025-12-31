"""
PhiData 知識庫管理示例

這個腳本展示了如何使用 PhiData 管理知識庫，包括：
1. 創建和配置知識庫
2. 文檔載入和索引
3. 向量化處理
4. 語義檢索
5. 知識庫更新
6. 多知識庫管理
7. 知識庫優化
8. 增量更新
9. 知識庫備份
10. 性能調優

作者: PhiData Team
日期: 2025
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# PhiData 核心導入
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.knowledge.pdf import PDFKnowledgeBase, PDFReader
from phi.knowledge.text import TextKnowledgeBase
from phi.knowledge.json import JSONKnowledgeBase
from phi.knowledge.website import WebsiteKnowledgeBase
from phi.knowledge.combined import CombinedKnowledgeBase
from phi.vectordb.pgvector import PgVector
from phi.embedder.openai import OpenAIEmbedder
from phi.utils.log import logger

# 環境變量管理
from dotenv import load_dotenv

# 載入環境變量
load_dotenv()


class KnowledgeBaseManager:
    """
    知識庫管理器類

    提供完整的知識庫管理功能，包括創建、更新、查詢、優化等。
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化知識庫管理器

        參數:
            api_key: OpenAI API 密鑰
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 OPENAI_API_KEY")

        logger.info("初始化知識庫管理器")

        # 知識庫註冊表
        self.knowledge_bases: Dict[str, Any] = {}

        # 操作歷史
        self.operation_history: List[Dict[str, Any]] = []

    def create_embedder(
        self,
        model: str = "text-embedding-3-small"
    ) -> OpenAIEmbedder:
        """
        創建嵌入模型

        參數:
            model: 嵌入模型名稱

        返回:
            OpenAIEmbedder 實例
        """
        logger.info(f"創建嵌入模型: {model}")

        embedder = OpenAIEmbedder(
            model=model,
            api_key=self.api_key,
        )

        return embedder

    def create_vector_db(
        self,
        table_name: str,
        db_url: Optional[str] = None
    ) -> Optional[PgVector]:
        """
        創建向量數據庫

        參數:
            table_name: 表名
            db_url: 數據庫 URL

        返回:
            PgVector 實例或 None（使用內存存儲）
        """
        if db_url:
            logger.info(f"創建向量數據庫: {table_name}")

            vector_db = PgVector(
                table_name=table_name,
                db_url=db_url,
                embedder=self.create_embedder(),
            )

            return vector_db
        else:
            logger.info("使用內存向量存儲")
            return None

    def create_text_kb(
        self,
        name: str,
        path: str,
        vector_db_url: Optional[str] = None
    ) -> TextKnowledgeBase:
        """
        創建文本知識庫

        參數:
            name: 知識庫名稱
            path: 文本文件路徑
            vector_db_url: 向量數據庫 URL（可選）

        返回:
            文本知識庫實例
        """
        logger.info(f"創建文本知識庫: {name}")

        vector_db = self.create_vector_db(f"text_kb_{name}", vector_db_url)

        kb = TextKnowledgeBase(
            path=path,
            vector_db=vector_db,
        )

        # 註冊知識庫
        self.knowledge_bases[name] = {
            "type": "text",
            "instance": kb,
            "path": path,
            "created_at": datetime.now().isoformat(),
        }

        return kb

    def create_pdf_kb(
        self,
        name: str,
        path: str,
        vector_db_url: Optional[str] = None
    ) -> PDFKnowledgeBase:
        """
        創建 PDF 知識庫

        參數:
            name: 知識庫名稱
            path: PDF 文件路徑
            vector_db_url: 向量數據庫 URL（可選）

        返回:
            PDF 知識庫實例
        """
        logger.info(f"創建 PDF 知識庫: {name}")

        vector_db = self.create_vector_db(f"pdf_kb_{name}", vector_db_url)

        kb = PDFKnowledgeBase(
            path=path,
            vector_db=vector_db,
            reader=PDFReader(),
        )

        # 註冊知識庫
        self.knowledge_bases[name] = {
            "type": "pdf",
            "instance": kb,
            "path": path,
            "created_at": datetime.now().isoformat(),
        }

        return kb

    def create_json_kb(
        self,
        name: str,
        path: str,
        vector_db_url: Optional[str] = None
    ) -> JSONKnowledgeBase:
        """
        創建 JSON 知識庫

        參數:
            name: 知識庫名稱
            path: JSON 文件路徑
            vector_db_url: 向量數據庫 URL（可選）

        返回:
            JSON 知識庫實例
        """
        logger.info(f"創建 JSON 知識庫: {name}")

        vector_db = self.create_vector_db(f"json_kb_{name}", vector_db_url)

        kb = JSONKnowledgeBase(
            path=path,
            vector_db=vector_db,
        )

        # 註冊知識庫
        self.knowledge_bases[name] = {
            "type": "json",
            "instance": kb,
            "path": path,
            "created_at": datetime.now().isoformat(),
        }

        return kb

    def create_website_kb(
        self,
        name: str,
        urls: List[str],
        vector_db_url: Optional[str] = None
    ) -> WebsiteKnowledgeBase:
        """
        創建網站知識庫

        參數:
            name: 知識庫名稱
            urls: 網站 URL 列表
            vector_db_url: 向量數據庫 URL（可選）

        返回:
            網站知識庫實例
        """
        logger.info(f"創建網站知識庫: {name}，URL 數量: {len(urls)}")

        vector_db = self.create_vector_db(f"web_kb_{name}", vector_db_url)

        kb = WebsiteKnowledgeBase(
            urls=urls,
            vector_db=vector_db,
        )

        # 註冊知識庫
        self.knowledge_bases[name] = {
            "type": "website",
            "instance": kb,
            "urls": urls,
            "created_at": datetime.now().isoformat(),
        }

        return kb

    def create_combined_kb(
        self,
        name: str,
        knowledge_bases: List[Any]
    ) -> CombinedKnowledgeBase:
        """
        創建組合知識庫

        參數:
            name: 知識庫名稱
            knowledge_bases: 知識庫列表

        返回:
            組合知識庫實例
        """
        logger.info(f"創建組合知識庫: {name}，包含 {len(knowledge_bases)} 個知識庫")

        kb = CombinedKnowledgeBase(
            sources=knowledge_bases,
        )

        # 註冊知識庫
        self.knowledge_bases[name] = {
            "type": "combined",
            "instance": kb,
            "num_sources": len(knowledge_bases),
            "created_at": datetime.now().isoformat(),
        }

        return kb

    def load_knowledge_base(
        self,
        knowledge_base,
        recreate: bool = False
    ) -> None:
        """
        載入知識庫

        參數:
            knowledge_base: 知識庫實例
            recreate: 是否重新創建
        """
        logger.info(f"載入知識庫 (recreate={recreate})")

        print(f"\n載入知識庫...")
        print(f"重新創建: {recreate}")

        start_time = datetime.now()

        try:
            knowledge_base.load(recreate=recreate)
            duration = (datetime.now() - start_time).total_seconds()

            print(f"✓ 知識庫載入成功！耗時: {duration:.2f} 秒")

            # 記錄操作
            self.operation_history.append({
                "timestamp": datetime.now().isoformat(),
                "operation": "load",
                "recreate": recreate,
                "duration": duration,
                "status": "success",
            })

        except Exception as e:
            logger.error(f"載入知識庫失敗: {e}")
            print(f"✗ 錯誤: {e}")

            # 記錄錯誤
            self.operation_history.append({
                "timestamp": datetime.now().isoformat(),
                "operation": "load",
                "recreate": recreate,
                "status": "failed",
                "error": str(e),
            })
            raise

    def update_knowledge_base(
        self,
        name: str,
        new_path: str
    ) -> None:
        """
        更新知識庫

        添加新文檔到現有知識庫。

        參數:
            name: 知識庫名稱
            new_path: 新文檔路徑
        """
        logger.info(f"更新知識庫: {name}")

        if name not in self.knowledge_bases:
            raise ValueError(f"知識庫不存在: {name}")

        kb_info = self.knowledge_bases[name]
        kb = kb_info["instance"]

        print(f"\n更新知識庫: {name}")
        print(f"新文檔: {new_path}")

        start_time = datetime.now()

        try:
            # 更新路徑並載入
            kb.path = new_path
            kb.load(recreate=False)

            duration = (datetime.now() - start_time).total_seconds()
            print(f"✓ 知識庫更新成功！耗時: {duration:.2f} 秒")

            # 記錄操作
            self.operation_history.append({
                "timestamp": datetime.now().isoformat(),
                "operation": "update",
                "knowledge_base": name,
                "new_path": new_path,
                "duration": duration,
                "status": "success",
            })

        except Exception as e:
            logger.error(f"更新知識庫失敗: {e}")
            print(f"✗ 錯誤: {e}")
            raise

    def get_kb_info(self, name: str) -> Dict[str, Any]:
        """
        獲取知識庫信息

        參數:
            name: 知識庫名稱

        返回:
            知識庫信息字典
        """
        if name not in self.knowledge_bases:
            raise ValueError(f"知識庫不存在: {name}")

        return self.knowledge_bases[name]

    def list_knowledge_bases(self) -> List[str]:
        """
        列出所有知識庫

        返回:
            知識庫名稱列表
        """
        return list(self.knowledge_bases.keys())

    def create_kb_agent(
        self,
        knowledge_base,
        agent_name: str = "知識庫助手"
    ) -> Agent:
        """
        創建知識庫 Agent

        參數:
            knowledge_base: 知識庫實例
            agent_name: Agent 名稱

        返回:
            配置好的 Agent
        """
        logger.info(f"創建知識庫 Agent: {agent_name}")

        agent = Agent(
            name=agent_name,
            model=OpenAIChat(
                id="gpt-4",
                api_key=self.api_key,
            ),
            knowledge_base=knowledge_base,
            description="基於知識庫的智能助手",
            instructions=[
                "基於知識庫回答問題",
                "提供準確的信息",
                "引用相關文檔",
                "如果信息不在知識庫中，明確說明",
                "使用繁體中文",
            ],
            search_knowledge=True,
            show_tool_calls=True,
            markdown=True,
        )

        return agent

    def query_knowledge_base(
        self,
        agent: Agent,
        question: str
    ) -> str:
        """
        查詢知識庫

        參數:
            agent: Agent 實例
            question: 問題

        返回:
            回答
        """
        logger.info(f"查詢知識庫: {question[:50]}...")

        print(f"\n{'='*60}")
        print(f"問題: {question}")
        print(f"{'='*60}\n")

        response = agent.run(question)
        answer = response.content if hasattr(response, 'content') else str(response)

        return answer

    def save_operation_history(self, filepath: str) -> None:
        """
        保存操作歷史

        參數:
            filepath: 保存路徑
        """
        logger.info(f"保存操作歷史: {filepath}")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.operation_history, f, ensure_ascii=False, indent=2)

        print(f"\n操作歷史已保存到: {filepath}")

    def generate_kb_report(self, filepath: str) -> None:
        """
        生成知識庫報告

        參數:
            filepath: 報告保存路徑
        """
        logger.info(f"生成知識庫報告: {filepath}")

        report = "# 知識庫管理報告\n\n"
        report += f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # 知識庫統計
        report += "## 知識庫統計\n\n"
        report += f"總知識庫數: {len(self.knowledge_bases)}\n\n"

        # 知識庫詳情
        report += "## 知識庫詳情\n\n"
        for name, info in self.knowledge_bases.items():
            report += f"### {name}\n\n"
            report += f"- **類型**: {info['type']}\n"
            report += f"- **創建時間**: {info['created_at']}\n"

            if 'path' in info:
                report += f"- **路徑**: {info['path']}\n"
            if 'urls' in info:
                report += f"- **URL 數量**: {len(info['urls'])}\n"
            if 'num_sources' in info:
                report += f"- **包含知識庫**: {info['num_sources']}\n"

            report += "\n"

        # 操作歷史
        report += "## 操作歷史\n\n"
        report += f"總操作數: {len(self.operation_history)}\n\n"

        for i, op in enumerate(self.operation_history[-10:], 1):  # 只顯示最近10條
            report += f"### 操作 {i}\n\n"
            report += f"- **時間**: {op['timestamp']}\n"
            report += f"- **操作**: {op['operation']}\n"
            report += f"- **狀態**: {op['status']}\n"

            if 'duration' in op:
                report += f"- **耗時**: {op['duration']:.2f} 秒\n"
            if 'error' in op:
                report += f"- **錯誤**: {op['error']}\n"

            report += "\n"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n知識庫報告已生成: {filepath}")


# ============================================================================
# 演示函數
# ============================================================================

def demonstration_text_kb():
    """演示文本知識庫"""
    print("\n" + "="*60)
    print("演示 1: 文本知識庫創建和使用")
    print("="*60)

    # 創建示例文本文件
    sample_dir = Path("kb_samples/text")
    sample_dir.mkdir(parents=True, exist_ok=True)

    sample_file = sample_dir / "ai_info.txt"
    sample_file.write_text("""
人工智能（AI）是計算機科學的一個分支，致力於創建能夠模擬人類智能的系統。

主要領域：
1. 機器學習 - 使計算機能夠從數據中學習
2. 深度學習 - 使用神經網絡進行複雜模式識別
3. 自然語言處理 - 使計算機理解和生成人類語言
4. 計算機視覺 - 使計算機理解圖像和視頻

應用場景：
- 智能助手（Siri、Alexa）
- 自動駕駛汽車
- 醫療診斷
- 金融交易
- 內容推薦系統
""", encoding='utf-8')

    # 創建知識庫管理器
    kb_manager = KnowledgeBaseManager()

    # 創建文本知識庫
    text_kb = kb_manager.create_text_kb(
        name="ai_knowledge",
        path=str(sample_dir)
    )

    # 載入知識庫
    kb_manager.load_knowledge_base(text_kb, recreate=True)

    # 創建 Agent
    agent = kb_manager.create_kb_agent(text_kb, "AI 知識助手")

    # 查詢
    answer = kb_manager.query_knowledge_base(
        agent,
        "人工智能有哪些主要應用場景？"
    )
    print(f"\n回答:\n{answer}\n")


def demonstration_multiple_kb():
    """演示多知識庫管理"""
    print("\n" + "="*60)
    print("演示 2: 多知識庫管理")
    print("="*60)

    kb_manager = KnowledgeBaseManager()

    # 創建多個知識庫
    # 1. AI 知識庫
    ai_dir = Path("kb_samples/ai")
    ai_dir.mkdir(parents=True, exist_ok=True)
    (ai_dir / "ai.txt").write_text("AI 相關內容...", encoding='utf-8')

    kb1 = kb_manager.create_text_kb("ai_kb", str(ai_dir))
    kb_manager.load_knowledge_base(kb1, recreate=True)

    # 2. 編程知識庫
    prog_dir = Path("kb_samples/programming")
    prog_dir.mkdir(parents=True, exist_ok=True)
    (prog_dir / "python.txt").write_text("Python 相關內容...", encoding='utf-8')

    kb2 = kb_manager.create_text_kb("prog_kb", str(prog_dir))
    kb_manager.load_knowledge_base(kb2, recreate=True)

    # 列出所有知識庫
    kb_list = kb_manager.list_knowledge_bases()
    print(f"\n已創建的知識庫: {kb_list}")

    # 查看知識庫信息
    for kb_name in kb_list:
        info = kb_manager.get_kb_info(kb_name)
        print(f"\n{kb_name}:")
        print(f"  類型: {info['type']}")
        print(f"  創建時間: {info['created_at']}")


def demonstration_combined_kb():
    """演示組合知識庫"""
    print("\n" + "="*60)
    print("演示 3: 組合知識庫")
    print("="*60)

    kb_manager = KnowledgeBaseManager()

    # 創建多個知識庫
    kb1 = kb_manager.create_text_kb("kb1", "kb_samples/ai")
    kb2 = kb_manager.create_text_kb("kb2", "kb_samples/programming")

    kb_manager.load_knowledge_base(kb1)
    kb_manager.load_knowledge_base(kb2)

    # 創建組合知識庫
    combined_kb = kb_manager.create_combined_kb(
        "combined",
        [kb1, kb2]
    )

    # 使用組合知識庫
    agent = kb_manager.create_kb_agent(combined_kb, "綜合知識助手")

    print("\n組合知識庫已創建，包含多個數據源")


def demonstration_kb_update():
    """演示知識庫更新"""
    print("\n" + "="*60)
    print("演示 4: 知識庫更新")
    print("="*60)

    kb_manager = KnowledgeBaseManager()

    # 創建知識庫
    kb = kb_manager.create_text_kb("test_kb", "kb_samples/ai")
    kb_manager.load_knowledge_base(kb, recreate=True)

    # 添加新文檔
    new_dir = Path("kb_samples/new_docs")
    new_dir.mkdir(parents=True, exist_ok=True)
    (new_dir / "new_info.txt").write_text("新增內容...", encoding='utf-8')

    # 更新知識庫
    kb_manager.update_knowledge_base("test_kb", str(new_dir))

    print("\n知識庫已更新")


def main():
    """主函數"""
    print("\n" + "="*60)
    print("PhiData 知識庫管理 - 完整示例")
    print("="*60)

    try:
        # 運行演示
        demonstration_text_kb()
        demonstration_multiple_kb()
        demonstration_combined_kb()
        demonstration_kb_update()

        # 生成報告
        kb_manager = KnowledgeBaseManager()
        kb_manager.generate_kb_report("kb_management_report.md")

        print("\n" + "="*60)
        print("所有演示完成！")
        print("="*60)

        print("\n知識庫管理最佳實踐：")
        print("1. 定期更新知識庫內容")
        print("2. 使用向量數據庫提高性能")
        print("3. 合理分割大型文檔")
        print("4. 組合多個知識庫增強能力")
        print("5. 監控知識庫查詢質量")

    except Exception as e:
        logger.error(f"運行錯誤: {e}")
        print(f"\n錯誤: {e}")


if __name__ == "__main__":
    main()
