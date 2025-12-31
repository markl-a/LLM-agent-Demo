"""
GraphRAG 企業應用示例

這個示例展示了企業級部署方案：
1. 生產環境配置
2. 性能優化策略
3. 監控和日誌
4. 安全性考慮
5. 擴展性設計

Author: GraphRAG Team
Date: 2025-12-31
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from dotenv import load_dotenv


@dataclass
class GraphRAGConfig:
    """GraphRAG 配置"""
    # LLM 配置
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.0
    llm_max_tokens: int = 4000

    # 嵌入配置
    embedding_model: str = "text-embedding-3-small"
    embedding_batch_size: int = 16

    # 分塊配置
    chunk_size: int = 1200
    chunk_overlap: int = 100

    # 實體提取配置
    entity_max_gleanings: int = 1
    entity_types: List[str] = None

    # 社區檢測配置
    community_algorithm: str = "leiden"
    community_max_size: int = 10

    # 搜索配置
    local_search_top_k: int = 10
    global_search_top_k: int = 20
    max_hops: int = 2

    # 性能配置
    enable_cache: bool = True
    cache_ttl: int = 3600  # 秒
    max_workers: int = 4
    rate_limit_per_minute: int = 60

    # 安全配置
    enable_auth: bool = True
    max_query_length: int = 500
    allowed_file_types: List[str] = None

    def __post_init__(self):
        if self.entity_types is None:
            self.entity_types = ["PERSON", "ORGANIZATION", "LOCATION", "EVENT"]
        if self.allowed_file_types is None:
            self.allowed_file_types = [".txt", ".md", ".pdf", ".docx"]


class EnterpriseLogger:
    """企業級日誌系統"""

    def __init__(self, log_dir: str = "./logs"):
        """
        初始化日誌系統

        Args:
            log_dir: 日誌目錄
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 設置日誌
        self.logger = logging.getLogger("GraphRAG")
        self.logger.setLevel(logging.INFO)

        # 文件處理器
        log_file = self.log_dir / f"graphrag_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加處理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log_query(self, query: str, result: Dict[str, Any], duration: float):
        """
        記錄查詢日誌

        Args:
            query: 查詢文本
            result: 查詢結果
            duration: 執行時間（秒）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "duration": duration,
            "confidence": result.get("confidence", 0),
            "strategy": result.get("strategy", "unknown")
        }

        self.logger.info(f"Query: {json.dumps(log_entry, ensure_ascii=False)}")

    def log_error(self, error: Exception, context: str = ""):
        """
        記錄錯誤日誌

        Args:
            error: 異常對象
            context: 上下文信息
        """
        self.logger.error(f"Error in {context}: {str(error)}", exc_info=True)

    def log_performance(self, metrics: Dict[str, Any]):
        """
        記錄性能指標

        Args:
            metrics: 性能指標字典
        """
        self.logger.info(f"Performance: {json.dumps(metrics, ensure_ascii=False)}")


class CacheManager:
    """緩存管理器"""

    def __init__(self, cache_dir: str = "./cache", ttl: int = 3600):
        """
        初始化緩存管理器

        Args:
            cache_dir: 緩存目錄
            ttl: 緩存過期時間（秒）
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """
        獲取緩存

        Args:
            key: 緩存鍵

        Returns:
            緩存值，如果不存在或過期則返回 None
        """
        cache_file = self.cache_dir / f"{self._hash_key(key)}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 檢查是否過期
            timestamp = cache_data.get("timestamp", 0)
            if time.time() - timestamp > self.ttl:
                cache_file.unlink()  # 刪除過期緩存
                return None

            return cache_data.get("value")

        except Exception as e:
            print(f"⚠️  讀取緩存失敗: {e}")
            return None

    def set(self, key: str, value: Any):
        """
        設置緩存

        Args:
            key: 緩存鍵
            value: 緩存值
        """
        cache_file = self.cache_dir / f"{self._hash_key(key)}.json"

        cache_data = {
            "timestamp": time.time(),
            "value": value
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  寫入緩存失敗: {e}")

    def clear(self):
        """清空所有緩存"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()

    @staticmethod
    def _hash_key(key: str) -> str:
        """生成緩存鍵的哈希值"""
        import hashlib
        return hashlib.md5(key.encode()).hexdigest()


class SecurityValidator:
    """安全驗證器"""

    def __init__(self, config: GraphRAGConfig):
        """
        初始化安全驗證器

        Args:
            config: 配置對象
        """
        self.config = config

    def validate_query(self, query: str) -> Tuple[bool, str]:
        """
        驗證查詢是否安全

        Args:
            query: 查詢文本

        Returns:
            (是否有效, 錯誤消息)
        """
        # 長度檢查
        if len(query) > self.config.max_query_length:
            return False, f"查詢長度超過限制 ({self.config.max_query_length} 字符)"

        # 內容檢查（防止注入攻擊）
        dangerous_patterns = [
            "DROP TABLE", "DELETE FROM", "INSERT INTO",
            "<script>", "javascript:", "eval("
        ]

        query_upper = query.upper()
        for pattern in dangerous_patterns:
            if pattern in query_upper:
                return False, f"查詢包含危險內容: {pattern}"

        return True, ""

    def validate_file(self, file_path: str) -> Tuple[bool, str]:
        """
        驗證文件是否允許上傳

        Args:
            file_path: 文件路徑

        Returns:
            (是否有效, 錯誤消息)
        """
        file_ext = Path(file_path).suffix.lower()

        if file_ext not in self.config.allowed_file_types:
            return False, f"不支持的文件類型: {file_ext}"

        # 文件大小檢查（這裡簡化處理）
        # 實際應用中需要檢查實際文件大小

        return True, ""


class PerformanceMonitor:
    """性能監控器"""

    def __init__(self):
        """初始化性能監控器"""
        self.metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_duration": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }

    def record_query(self, duration: float, success: bool, cache_hit: bool):
        """
        記錄查詢指標

        Args:
            duration: 執行時間
            success: 是否成功
            cache_hit: 是否命中緩存
        """
        self.metrics["total_queries"] += 1
        if success:
            self.metrics["successful_queries"] += 1
        else:
            self.metrics["failed_queries"] += 1

        self.metrics["total_duration"] += duration

        if cache_hit:
            self.metrics["cache_hits"] += 1
        else:
            self.metrics["cache_misses"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """
        獲取性能指標

        Returns:
            性能指標字典
        """
        metrics = self.metrics.copy()

        if metrics["total_queries"] > 0:
            metrics["avg_duration"] = metrics["total_duration"] / metrics["total_queries"]
            metrics["success_rate"] = metrics["successful_queries"] / metrics["total_queries"]
            metrics["cache_hit_rate"] = metrics["cache_hits"] / metrics["total_queries"]
        else:
            metrics["avg_duration"] = 0
            metrics["success_rate"] = 0
            metrics["cache_hit_rate"] = 0

        return metrics

    def reset(self):
        """重置指標"""
        self.metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "total_duration": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }


class EnterpriseGraphRAG:
    """企業級 GraphRAG 系統"""

    def __init__(self, config: GraphRAGConfig):
        """
        初始化企業級 GraphRAG

        Args:
            config: 配置對象
        """
        self.config = config
        self.logger = EnterpriseLogger()
        self.cache = CacheManager(ttl=config.cache_ttl) if config.enable_cache else None
        self.security = SecurityValidator(config)
        self.monitor = PerformanceMonitor()

        print(f"✅ 企業級 GraphRAG 系統已初始化")
        print(f"   配置: {self.config.llm_model}")
        print(f"   緩存: {'啟用' if config.enable_cache else '禁用'}")
        print(f"   認證: {'啟用' if config.enable_auth else '禁用'}")

    def query(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        執行查詢（企業級）

        Args:
            query: 查詢文本
            user_id: 用戶 ID（用於認證和日誌）

        Returns:
            查詢結果
        """
        start_time = time.time()
        cache_hit = False

        try:
            # 1. 安全驗證
            is_valid, error_msg = self.security.validate_query(query)
            if not is_valid:
                raise ValueError(f"查詢驗證失敗: {error_msg}")

            # 2. 檢查緩存
            if self.cache:
                cache_key = f"query:{query}"
                cached_result = self.cache.get(cache_key)
                if cached_result:
                    print(f"   ✓ 緩存命中")
                    cache_hit = True
                    duration = time.time() - start_time
                    self.monitor.record_query(duration, True, cache_hit)
                    return cached_result

            # 3. 執行實際查詢
            # 這裡應該調用實際的 GraphRAG 搜索引擎
            # result = self.search_engine.search(query)
            result = self._mock_query(query)

            # 4. 緩存結果
            if self.cache and not cache_hit:
                self.cache.set(cache_key, result)

            # 5. 記錄日誌和指標
            duration = time.time() - start_time
            self.logger.log_query(query, result, duration)
            self.monitor.record_query(duration, True, cache_hit)

            return result

        except Exception as e:
            # 錯誤處理
            duration = time.time() - start_time
            self.logger.log_error(e, f"query: {query}")
            self.monitor.record_query(duration, False, cache_hit)

            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _mock_query(self, query: str) -> Dict[str, Any]:
        """
        模擬查詢執行

        Args:
            query: 查詢文本

        Returns:
            查詢結果
        """
        # 模擬處理延遲
        time.sleep(0.5)

        return {
            "success": True,
            "answer": f"這是對查詢「{query}」的答案。",
            "confidence": 0.88,
            "strategy": "hybrid",
            "entities": ["實體A", "實體B"],
            "timestamp": datetime.now().isoformat()
        }

    def index_documents(self, document_dir: str) -> Dict[str, Any]:
        """
        索引文檔（企業級）

        Args:
            document_dir: 文檔目錄

        Returns:
            索引結果
        """
        print(f"\n📚 開始索引文檔: {document_dir}")

        try:
            # 1. 驗證文檔
            files = list(Path(document_dir).glob("*"))
            valid_files = []

            for file_path in files:
                is_valid, error_msg = self.security.validate_file(str(file_path))
                if is_valid:
                    valid_files.append(file_path)
                else:
                    print(f"   ⚠️  跳過文件 {file_path.name}: {error_msg}")

            print(f"   ✓ 驗證通過 {len(valid_files)} 個文件")

            # 2. 執行索引
            # 實際應用中這裡會調用 GraphRAG 的索引流程
            # result = self.indexer.build_index(valid_files)

            result = {
                "success": True,
                "indexed_files": len(valid_files),
                "entities_extracted": len(valid_files) * 10,  # 模擬
                "relationships_extracted": len(valid_files) * 15,  # 模擬
                "communities_detected": len(valid_files) * 2,  # 模擬
                "timestamp": datetime.now().isoformat()
            }

            print(f"   ✅ 索引完成")
            print(f"      文件數: {result['indexed_files']}")
            print(f"      實體數: {result['entities_extracted']}")
            print(f"      關係數: {result['relationships_extracted']}")

            return result

        except Exception as e:
            self.logger.log_error(e, "index_documents")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_health_status(self) -> Dict[str, Any]:
        """
        獲取系統健康狀態

        Returns:
            健康狀態字典
        """
        metrics = self.monitor.get_metrics()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "config": {
                "llm_model": self.config.llm_model,
                "embedding_model": self.config.embedding_model,
                "cache_enabled": self.config.enable_cache
            },
            "metrics": metrics
        }


def main():
    """
    主函數：演示企業級部署
    """
    print("=" * 70)
    print("🏢 GraphRAG 企業應用示例".center(70))
    print("=" * 70)
    print()

    # 加載環境變量
    load_dotenv()

    # 步驟 1: 配置系統
    print("步驟 1: 配置企業級 GraphRAG 系統")
    print("=" * 70)

    config = GraphRAGConfig(
        llm_model="gpt-4-turbo-preview",
        enable_cache=True,
        cache_ttl=3600,
        max_workers=4,
        enable_auth=True
    )

    print(f"配置已創建:")
    print(f"  LLM 模型: {config.llm_model}")
    print(f"  嵌入模型: {config.embedding_model}")
    print(f"  緩存: {'啟用' if config.enable_cache else '禁用'}")
    print()

    # 步驟 2: 初始化系統
    print("\n步驟 2: 初始化系統")
    print("=" * 70)

    graphrag = EnterpriseGraphRAG(config)
    print()

    # 步驟 3: 索引文檔（示例）
    print("\n步驟 3: 索引文檔")
    print("=" * 70)

    # 這裡使用示例目錄，實際應用中使用真實文檔目錄
    # index_result = graphrag.index_documents("./data/input")
    print("   (跳過實際索引，使用已有索引)")
    print()

    # 步驟 4: 執行查詢
    print("\n步驟 4: 執行查詢")
    print("=" * 70)

    queries = [
        "什麼是 GraphRAG？",
        "深度學習的應用有哪些？",
        "AI 技術的未來趨勢？"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n查詢 {i}: {query}")
        print("-" * 70)

        result = graphrag.query(query, user_id="user_001")

        if result.get("success"):
            print(f"✅ 答案: {result['answer']}")
            print(f"   置信度: {result['confidence']:.2%}")
            print(f"   策略: {result['strategy']}")
        else:
            print(f"❌ 錯誤: {result['error']}")

    # 步驟 5: 健康檢查
    print("\n\n步驟 5: 系統健康檢查")
    print("=" * 70)

    health = graphrag.get_health_status()
    print(f"狀態: {health['status']}")
    print(f"\n性能指標:")
    metrics = health['metrics']
    print(f"  總查詢數: {metrics['total_queries']}")
    print(f"  成功率: {metrics['success_rate']:.2%}")
    print(f"  平均響應時間: {metrics['avg_duration']:.3f} 秒")
    print(f"  緩存命中率: {metrics['cache_hit_rate']:.2%}")
    print()

    # 總結
    print("\n" + "=" * 70)
    print("💡 企業級部署要點")
    print("=" * 70)
    print("""
    1. 配置管理：
       • 使用配置文件（YAML/JSON）
       • 環境變量管理敏感信息
       • 支持多環境配置（開發/測試/生產）

    2. 安全性：
       • 輸入驗證和過濾
       • 認證和授權
       • API 密鑰安全存儲
       • 審計日誌

    3. 性能優化：
       • 多級緩存（內存/Redis）
       • 批處理和並行化
       • 連接池管理
       • 速率限制

    4. 監控和日誌：
       • 結構化日誌
       • 性能指標收集
       • 異常告警
       • 追蹤和調試

    5. 高可用性：
       • 負載均衡
       • 故障轉移
       • 健康檢查
       • 降級策略

    6. 擴展性：
       • 水平擴展（多實例）
       • 垂直擴展（更大機器）
       • 微服務架構
       • 異步處理（消息隊列）

    7. 數據管理：
       • 增量索引更新
       • 版本控制
       • 備份和恢復
       • 數據清理和歸檔

    8. 成本優化：
       • LLM API 調用優化
       • 緩存策略
       • 批處理請求
       • 選擇合適的模型

    9. 部署架構示例：

       ┌─────────────────────────────────────────────┐
       │            負載均衡器 (Nginx/ALB)             │
       └─────────────────┬───────────────────────────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
       ┌───▼────┐   ┌───▼────┐   ┌───▼────┐
       │ API    │   │ API    │   │ API    │
       │ Server │   │ Server │   │ Server │
       │   1    │   │   2    │   │   3    │
       └───┬────┘   └───┬────┘   └───┬────┘
           │             │             │
           └─────────────┼─────────────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
       ┌───▼────┐   ┌───▼────┐   ┌───▼────┐
       │ Redis  │   │ Vector │   │ Graph  │
       │ Cache  │   │   DB   │   │   DB   │
       └────────┘   └────────┘   └────────┘

    10. 推薦技術棧：
        • Web 框架: FastAPI/Flask
        • 緩存: Redis
        • 向量數據庫: Weaviate/Qdrant/Pinecone
        • 圖數據庫: Neo4j (可選)
        • 監控: Prometheus + Grafana
        • 日誌: ELK Stack
        • 容器化: Docker + Kubernetes

    📚 資源：
       • GraphRAG 官方文檔
       • 企業部署最佳實踐
       • 性能調優指南
       • 安全加固清單
    """)

    print("\n✅ 企業應用示例完成！")
    print("\n🎉 恭喜！您已完成所有 GraphRAG 示例的學習。")


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
