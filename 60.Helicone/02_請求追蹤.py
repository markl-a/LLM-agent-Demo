"""
Helicone 請求追蹤與日誌記錄
===========================

本文件展示如何使用 Helicone 進行詳細的請求追蹤和日誌記錄。
追蹤每個 API 請求對於調試、優化和成本控制至關重要。

主要內容:
1. 基本請求追蹤
2. 自定義屬性和元數據
3. 會話和用戶追蹤
4. 請求分組和分類
5. 錯誤追蹤和調試
6. 性能監控
7. 導出和分析日誌數據

作者: Helicone Team
日期: 2025-12-31
"""

import os
import sys
import time
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from dotenv import load_dotenv

try:
    import openai
    from loguru import logger
    import pandas as pd
    from rich.console import Console
    from rich.table import Table
    from rich.progress import track
except ImportError as e:
    print(f"❌ 缺少必要的依賴: {e}")
    print("請運行: pip install openai loguru pandas rich")
    sys.exit(1)


class RequestType(Enum):
    """請求類型枚舉"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    IMAGE = "image"
    AUDIO = "audio"


class Priority(Enum):
    """請求優先級"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RequestMetadata:
    """
    請求元數據結構

    這個類定義了我們想要追蹤的所有信息。
    使用結構化的數據類可以確保一致性和類型安全。
    """
    request_id: str
    user_id: str
    session_id: str
    timestamp: str
    request_type: str
    model: str
    environment: str
    feature: str
    version: str
    priority: str
    custom_tags: Dict[str, str]


class HeliconeRequestTracker:
    """
    Helicone 請求追蹤器

    這個類提供了全面的請求追蹤功能,包括:
    - 自動生成追蹤 ID
    - 結構化日誌記錄
    - 性能測量
    - 錯誤追蹤
    - 數據導出
    """

    def __init__(self):
        """初始化追蹤器"""
        load_dotenv()

        # API 配置
        self.helicone_api_key = os.getenv("HELICONE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.helicone_base_url = "https://oai.helicone.ai/v1"

        # 初始化 OpenAI 客戶端
        self.client = openai.OpenAI(
            api_key=self.openai_api_key,
            base_url=self.helicone_base_url,
            default_headers={
                "Helicone-Auth": f"Bearer {self.helicone_api_key}"
            }
        )

        # 初始化 Rich Console 用於美化輸出
        self.console = Console()

        # 配置日誌記錄
        self._setup_logging()

        # 存儲請求歷史
        self.request_history: List[Dict[str, Any]] = []

        self.console.print("✅ [green]請求追蹤器已初始化[/green]")

    def _setup_logging(self):
        """
        配置結構化日誌記錄

        使用 loguru 進行高級日誌記錄:
        - 不同級別的日誌
        - 日誌輪換
        - JSON 格式化
        - 文件和控制台輸出
        """
        # 移除默認處理器
        logger.remove()

        # 添加控制台處理器 (帶顏色)
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level="INFO"
        )

        # 添加文件處理器 (JSON 格式)
        logger.add(
            "logs/helicone_requests_{time:YYYY-MM-DD}.log",
            format="{message}",
            level="DEBUG",
            rotation="1 day",
            retention="30 days",
            compression="zip",
            serialize=True  # JSON 格式
        )

        # 添加錯誤日誌文件
        logger.add(
            "logs/helicone_errors_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="ERROR",
            rotation="1 week",
            retention="90 days"
        )

    def generate_request_id(self, prefix: str = "req") -> str:
        """
        生成唯一的請求 ID

        格式: prefix_timestamp_uuid
        例如: req_20251231_a1b2c3d4
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]
        return f"{prefix}_{timestamp}_{short_uuid}"

    def generate_session_id(self, user_id: str) -> str:
        """
        為用戶生成會話 ID

        會話 ID 用於追蹤一系列相關的請求,
        例如一次完整的對話或工作流程。
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{user_id}_{timestamp}"

    def create_metadata(
        self,
        user_id: str,
        session_id: str,
        request_type: RequestType,
        model: str,
        feature: str,
        environment: str = "production",
        version: str = "v1.0",
        priority: Priority = Priority.MEDIUM,
        **custom_tags
    ) -> RequestMetadata:
        """
        創建請求元數據

        這個方法創建包含所有追蹤信息的結構化元數據。
        """
        request_id = self.generate_request_id()

        return RequestMetadata(
            request_id=request_id,
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            request_type=request_type.value,
            model=model,
            environment=environment,
            feature=feature,
            version=version,
            priority=priority.value,
            custom_tags=custom_tags
        )

    def build_helicone_headers(self, metadata: RequestMetadata) -> Dict[str, str]:
        """
        從元數據構建 Helicone headers

        Helicone 使用特殊的 HTTP headers 來追蹤請求。
        這個方法將我們的元數據轉換為 Helicone headers。
        """
        headers = {
            # 基本追蹤
            "Helicone-Request-Id": metadata.request_id,
            "Helicone-User-Id": metadata.user_id,
            "Helicone-Session-Id": metadata.session_id,

            # 標準屬性
            "Helicone-Property-Environment": metadata.environment,
            "Helicone-Property-Feature": metadata.feature,
            "Helicone-Property-Version": metadata.version,
            "Helicone-Property-Priority": metadata.priority,
            "Helicone-Property-RequestType": metadata.request_type,
            "Helicone-Property-Timestamp": metadata.timestamp,
        }

        # 添加自定義標籤
        for key, value in metadata.custom_tags.items():
            headers[f"Helicone-Property-{key}"] = str(value)

        return headers

    def track_request(
        self,
        prompt: str,
        metadata: RequestMetadata,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        追蹤單個請求

        這是核心方法,執行請求並記錄所有相關信息:
        - 請求參數
        - 響應內容
        - 性能指標
        - 成本信息
        - 錯誤(如果有)
        """
        start_time = time.time()

        try:
            logger.info(f"發送請求: {metadata.request_id}")
            logger.debug(f"元數據: {asdict(metadata)}")

            # 構建 headers
            headers = self.build_helicone_headers(metadata)

            # 發送請求
            response = self.client.chat.completions.create(
                model=metadata.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                extra_headers=headers,
                **kwargs
            )

            # 計算性能指標
            end_time = time.time()
            duration = end_time - start_time

            # 提取響應信息
            result = {
                "request_id": metadata.request_id,
                "user_id": metadata.user_id,
                "session_id": metadata.session_id,
                "timestamp": metadata.timestamp,
                "model": response.model,
                "prompt": prompt,
                "response": response.choices[0].message.content,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "performance": {
                    "duration_seconds": duration,
                    "tokens_per_second": response.usage.total_tokens / duration if duration > 0 else 0
                },
                "cost": self._calculate_cost(response),
                "metadata": asdict(metadata),
                "success": True,
                "error": None
            }

            # 記錄日誌
            logger.info(
                f"請求成功",
                extra={
                    "request_id": metadata.request_id,
                    "duration": duration,
                    "tokens": response.usage.total_tokens
                }
            )

            # 添加到歷史記錄
            self.request_history.append(result)

            return result

        except Exception as e:
            # 記錄錯誤
            end_time = time.time()
            duration = end_time - start_time

            error_result = {
                "request_id": metadata.request_id,
                "user_id": metadata.user_id,
                "session_id": metadata.session_id,
                "timestamp": metadata.timestamp,
                "model": metadata.model,
                "prompt": prompt,
                "response": None,
                "error": str(e),
                "error_type": type(e).__name__,
                "duration": duration,
                "success": False,
                "metadata": asdict(metadata)
            }

            logger.error(
                f"請求失敗: {str(e)}",
                extra={
                    "request_id": metadata.request_id,
                    "error_type": type(e).__name__
                }
            )

            self.request_history.append(error_result)

            return error_result

    def _calculate_cost(self, response) -> Dict[str, float]:
        """
        計算請求成本

        根據模型和 token 使用量計算成本。
        價格可能會變化,建議定期更新。
        """
        # 模型定價 (每 1000 tokens 的美元價格)
        pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        }

        # 獲取模型價格
        model_name = response.model.lower()
        price = None
        for key in pricing:
            if key in model_name:
                price = pricing[key]
                break

        if not price:
            # 默認價格
            price = {"input": 0.001, "output": 0.002}

        # 計算成本
        input_cost = (response.usage.prompt_tokens / 1000) * price["input"]
        output_cost = (response.usage.completion_tokens / 1000) * price["output"]
        total_cost = input_cost + output_cost

        return {
            "input_cost_usd": input_cost,
            "output_cost_usd": output_cost,
            "total_cost_usd": total_cost,
            "currency": "USD"
        }

    def track_conversation(
        self,
        messages: List[str],
        user_id: str,
        feature: str,
        model: str = "gpt-3.5-turbo"
    ) -> List[Dict[str, Any]]:
        """
        追蹤整個對話

        這個方法追蹤一系列相關的消息,
        使用相同的 session_id 將它們關聯起來。
        """
        self.console.print(f"\n🔄 [cyan]開始追蹤對話 (共 {len(messages)} 條消息)[/cyan]")

        # 為這個對話生成唯一的 session_id
        session_id = self.generate_session_id(user_id)

        results = []

        for i, message in enumerate(messages, 1):
            self.console.print(f"\n📨 消息 {i}/{len(messages)}")

            # 創建元數據
            metadata = self.create_metadata(
                user_id=user_id,
                session_id=session_id,
                request_type=RequestType.CHAT,
                model=model,
                feature=feature,
                message_index=i,
                total_messages=len(messages)
            )

            # 追蹤請求
            result = self.track_request(message, metadata)
            results.append(result)

            # 顯示結果
            if result and result["success"]:
                self.console.print(f"✅ [green]成功[/green] - {result['usage']['total_tokens']} tokens")
            else:
                self.console.print(f"❌ [red]失敗[/red] - {result.get('error', 'Unknown error')}")

            # 避免速率限制
            if i < len(messages):
                time.sleep(0.5)

        # 顯示對話摘要
        self._display_conversation_summary(results, session_id)

        return results

    def _display_conversation_summary(self, results: List[Dict], session_id: str):
        """顯示對話摘要"""
        self.console.print(f"\n📊 [bold]對話摘要[/bold] (Session: {session_id})")

        # 創建表格
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("消息", style="cyan")
        table.add_column("狀態", style="green")
        table.add_column("Tokens", justify="right")
        table.add_column("成本 (USD)", justify="right")
        table.add_column("耗時 (秒)", justify="right")

        total_tokens = 0
        total_cost = 0
        successful = 0

        for i, result in enumerate(results, 1):
            if result["success"]:
                tokens = result["usage"]["total_tokens"]
                cost = result["cost"]["total_cost_usd"]
                duration = result["performance"]["duration_seconds"]

                total_tokens += tokens
                total_cost += cost
                successful += 1

                table.add_row(
                    f"消息 {i}",
                    "✅ 成功",
                    str(tokens),
                    f"${cost:.6f}",
                    f"{duration:.2f}"
                )
            else:
                table.add_row(
                    f"消息 {i}",
                    "❌ 失敗",
                    "-",
                    "-",
                    "-"
                )

        self.console.print(table)

        # 總計
        self.console.print(f"\n總計:")
        self.console.print(f"  成功: {successful}/{len(results)}")
        self.console.print(f"  總 Tokens: {total_tokens}")
        self.console.print(f"  總成本: ${total_cost:.6f}")

    def export_to_csv(self, filename: str = "helicone_requests.csv"):
        """
        導出請求歷史到 CSV 文件

        這對於進一步的分析非常有用,
        可以使用 Excel 或其他數據分析工具。
        """
        if not self.request_history:
            self.console.print("⚠️  [yellow]沒有請求歷史可以導出[/yellow]")
            return

        # 扁平化數據結構
        flat_data = []
        for record in self.request_history:
            flat_record = {
                "request_id": record["request_id"],
                "user_id": record["user_id"],
                "session_id": record["session_id"],
                "timestamp": record["timestamp"],
                "model": record["model"],
                "success": record["success"],
                "error": record.get("error", "")
            }

            # 添加使用信息
            if record["success"] and "usage" in record:
                flat_record.update({
                    "prompt_tokens": record["usage"]["prompt_tokens"],
                    "completion_tokens": record["usage"]["completion_tokens"],
                    "total_tokens": record["usage"]["total_tokens"],
                    "duration_seconds": record["performance"]["duration_seconds"],
                    "tokens_per_second": record["performance"]["tokens_per_second"],
                    "cost_usd": record["cost"]["total_cost_usd"]
                })

            flat_data.append(flat_record)

        # 創建 DataFrame 並導出
        df = pd.DataFrame(flat_data)
        df.to_csv(filename, index=False)

        self.console.print(f"✅ [green]已導出 {len(flat_data)} 條記錄到 {filename}[/green]")

    def get_analytics(self) -> Dict[str, Any]:
        """
        獲取分析統計

        計算各種有用的統計信息:
        - 總請求數
        - 成功率
        - 平均響應時間
        - 總成本
        - 最常用的模型
        - 等等
        """
        if not self.request_history:
            return {"message": "沒有請求歷史"}

        successful_requests = [r for r in self.request_history if r["success"]]

        analytics = {
            "total_requests": len(self.request_history),
            "successful_requests": len(successful_requests),
            "failed_requests": len(self.request_history) - len(successful_requests),
            "success_rate": len(successful_requests) / len(self.request_history) * 100,
        }

        if successful_requests:
            analytics.update({
                "total_tokens": sum(r["usage"]["total_tokens"] for r in successful_requests),
                "total_cost_usd": sum(r["cost"]["total_cost_usd"] for r in successful_requests),
                "avg_tokens": sum(r["usage"]["total_tokens"] for r in successful_requests) / len(successful_requests),
                "avg_duration": sum(r["performance"]["duration_seconds"] for r in successful_requests) / len(successful_requests),
                "avg_cost_usd": sum(r["cost"]["total_cost_usd"] for r in successful_requests) / len(successful_requests),
            })

        return analytics


def demo_basic_tracking():
    """演示基本請求追蹤"""
    console = Console()
    console.print("\n[bold cyan]演示 1: 基本請求追蹤[/bold cyan]")
    console.print("=" * 80)

    tracker = HeliconeRequestTracker()

    # 創建元數據
    metadata = tracker.create_metadata(
        user_id="user_001",
        session_id="session_demo_001",
        request_type=RequestType.CHAT,
        model="gpt-3.5-turbo",
        feature="demo",
        environment="development"
    )

    # 發送請求
    result = tracker.track_request(
        prompt="什麼是人工智能?用一句話回答。",
        metadata=metadata,
        max_tokens=50
    )

    # 顯示結果
    if result and result["success"]:
        console.print(f"\n✅ 請求成功!")
        console.print(f"請求 ID: {result['request_id']}")
        console.print(f"響應: {result['response']}")
        console.print(f"Tokens: {result['usage']['total_tokens']}")
        console.print(f"成本: ${result['cost']['total_cost_usd']:.6f}")


def demo_conversation_tracking():
    """演示對話追蹤"""
    console = Console()
    console.print("\n[bold cyan]演示 2: 對話追蹤[/bold cyan]")
    console.print("=" * 80)

    tracker = HeliconeRequestTracker()

    # 模擬一個對話
    messages = [
        "你好,我想學習機器學習。",
        "我應該從哪裡開始?",
        "Python 是最好的選擇嗎?"
    ]

    results = tracker.track_conversation(
        messages=messages,
        user_id="user_002",
        feature="learning-assistant",
        model="gpt-3.5-turbo"
    )

    return tracker


def main():
    """主函數"""
    console = Console()
    console.print("[bold green]🎯 Helicone 請求追蹤演示[/bold green]")

    try:
        # 演示 1: 基本追蹤
        demo_basic_tracking()

        # 演示 2: 對話追蹤
        tracker = demo_conversation_tracking()

        # 顯示分析
        console.print("\n[bold cyan]📊 總體分析[/bold cyan]")
        console.print("=" * 80)
        analytics = tracker.get_analytics()
        for key, value in analytics.items():
            console.print(f"{key}: {value}")

        # 導出數據
        tracker.export_to_csv("demo_requests.csv")

        console.print("\n✅ [green]演示完成![/green]")
        console.print("📊 前往 https://helicone.ai/dashboard 查看詳細追蹤信息")

    except Exception as e:
        console.print(f"\n❌ [red]錯誤: {str(e)}[/red]")


if __name__ == "__main__":
    main()
