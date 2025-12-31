"""
Strands Agents AWS Lambda 部署示例

這個示例展示了如何將 Strands Agents 部署到 AWS Lambda：
1. Lambda 函數結構設計
2. 冷啟動優化
3. 環境變數配置
4. 層（Layers）管理
5. API Gateway 整合
6. 事件源映射
7. 資源限制和優化
8. 部署自動化

AWS Lambda 是理想的 Agent 部署平台，
提供按需擴展、低成本和高可用性。

作者: Strands Agents Team
日期: 2025-01
"""

import os
import sys
import json
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import base64

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Lambda 處理器基類
# ============================================================================

class LambdaHandler:
    """
    Lambda 處理器基類

    提供 Lambda 函數的標準結構和工具方法
    """

    def __init__(self):
        self.cold_start = True
        self.init_time = time.time()

        logger.info("Lambda 處理器初始化")

    def handle(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        處理 Lambda 事件

        Args:
            event: Lambda 事件對象
            context: Lambda 上下文對象

        Returns:
            Dict: 響應對象
        """
        try:
            # 記錄冷啟動狀態
            if self.cold_start:
                logger.info("冷啟動")
                self.cold_start = False
            else:
                logger.info("熱啟動")

            # 記錄請求信息
            self._log_request_info(event, context)

            # 執行業務邏輯
            result = self.process(event, context)

            # 構建響應
            response = self._build_response(200, result)

            return response

        except Exception as e:
            logger.error(f"處理錯誤: {str(e)}", exc_info=True)

            error_response = {
                "error": str(e),
                "type": type(e).__name__
            }

            return self._build_response(500, error_response)

    def process(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        處理業務邏輯（子類應重寫此方法）

        Args:
            event: Lambda 事件
            context: Lambda 上下文

        Returns:
            Dict: 處理結果
        """
        raise NotImplementedError("子類必須實現 process 方法")

    def _log_request_info(self, event: Dict[str, Any], context: Any):
        """記錄請求信息"""
        logger.info(f"請求 ID: {getattr(context, 'request_id', 'N/A')}")
        logger.info(f"函數名稱: {getattr(context, 'function_name', 'N/A')}")
        logger.info(f"剩餘時間: {getattr(context, 'get_remaining_time_in_millis', lambda: 0)()}ms")

    def _build_response(
        self,
        status_code: int,
        body: Any,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        構建 Lambda 響應

        Args:
            status_code: HTTP 狀態碼
            body: 響應體
            headers: HTTP 頭

        Returns:
            Dict: Lambda 響應對象
        """
        default_headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }

        if headers:
            default_headers.update(headers)

        return {
            "statusCode": status_code,
            "headers": default_headers,
            "body": json.dumps(body, ensure_ascii=False)
        }


# ============================================================================
# Agent Lambda 處理器
# ============================================================================

class AgentLambdaHandler(LambdaHandler):
    """
    Agent Lambda 處理器

    專門用於處理 Agent 請求的 Lambda 函數
    """

    def __init__(self):
        super().__init__()

        # 初始化 Agent（在冷啟動時完成）
        self.agent = self._initialize_agent()

        logger.info("Agent Lambda 處理器初始化完成")

    def _initialize_agent(self):
        """
        初始化 Agent

        在冷啟動時執行，結果會被重用
        """
        from datetime import datetime

        # 模擬 Agent 初始化
        logger.info("初始化 Agent...")

        # 實際實現中，這裡會創建真實的 Strands Agent
        # from strands_agents import Agent, BedrockModel
        #
        # model = BedrockModel(
        #     model_id=os.environ.get('MODEL_ID'),
        #     region=os.environ.get('AWS_REGION', 'us-east-1')
        # )
        #
        # agent = Agent(
        #     name="lambda_agent",
        #     model=model,
        #     tools=[...],
        #     system_prompt=os.environ.get('SYSTEM_PROMPT')
        # )

        agent = {
            "name": "lambda_agent",
            "initialized_at": datetime.now().isoformat(),
            "status": "ready"
        }

        return agent

    def process(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        處理 Agent 請求

        支持多種事件源：
        - API Gateway
        - EventBridge
        - SQS
        - SNS
        """
        # 解析事件源
        event_source = self._identify_event_source(event)
        logger.info(f"事件源: {event_source}")

        # 根據事件源處理
        if event_source == "api_gateway":
            return self._handle_api_gateway(event, context)
        elif event_source == "eventbridge":
            return self._handle_eventbridge(event, context)
        elif event_source == "sqs":
            return self._handle_sqs(event, context)
        else:
            return self._handle_direct_invoke(event, context)

    def _identify_event_source(self, event: Dict[str, Any]) -> str:
        """識別事件源"""
        if "httpMethod" in event:
            return "api_gateway"
        elif "Records" in event:
            if event["Records"][0].get("eventSource") == "aws:sqs":
                return "sqs"
        elif "source" in event and event["source"].startswith("aws.events"):
            return "eventbridge"
        else:
            return "direct"

    def _handle_api_gateway(
        self,
        event: Dict[str, Any],
        context: Any
    ) -> Dict[str, Any]:
        """處理 API Gateway 請求"""
        # 解析請求體
        body = event.get("body", "{}")
        if event.get("isBase64Encoded", False):
            body = base64.b64decode(body).decode('utf-8')

        request_data = json.loads(body) if isinstance(body, str) else body

        # 提取參數
        message = request_data.get("message", "")
        session_id = request_data.get("session_id")

        logger.info(f"API Gateway 請求: message={message[:50]}...")

        # 調用 Agent 處理
        response = self._process_message(message, session_id)

        return {
            "message": message,
            "response": response,
            "session_id": session_id,
            "agent": self.agent.get("name"),
            "timestamp": datetime.now().isoformat()
        }

    def _handle_eventbridge(
        self,
        event: Dict[str, Any],
        context: Any
    ) -> Dict[str, Any]:
        """處理 EventBridge 事件"""
        detail = event.get("detail", {})

        logger.info(f"EventBridge 事件: {detail}")

        # 處理事件
        result = {
            "event_processed": True,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        }

        return result

    def _handle_sqs(
        self,
        event: Dict[str, Any],
        context: Any
    ) -> Dict[str, Any]:
        """處理 SQS 消息"""
        results = []

        for record in event.get("Records", []):
            body = json.loads(record.get("body", "{}"))
            message = body.get("message", "")

            logger.info(f"處理 SQS 消息: {message[:50]}...")

            response = self._process_message(message)

            results.append({
                "message_id": record.get("messageId"),
                "response": response
            })

        return {
            "processed_count": len(results),
            "results": results
        }

    def _handle_direct_invoke(
        self,
        event: Dict[str, Any],
        context: Any
    ) -> Dict[str, Any]:
        """處理直接調用"""
        message = event.get("message", "")

        logger.info(f"直接調用: {message[:50]}...")

        response = self._process_message(message)

        return {
            "message": message,
            "response": response
        }

    def _process_message(
        self,
        message: str,
        session_id: Optional[str] = None
    ) -> str:
        """
        處理消息

        實際實現中會調用真實的 Agent

        Args:
            message: 用戶消息
            session_id: 會話 ID

        Returns:
            str: Agent 響應
        """
        # 模擬 Agent 處理
        # 實際實現:
        # response = self.agent.run(message, session_id=session_id)

        response = f"這是對 '{message}' 的響應（來自 Lambda Agent）"

        return response


# ============================================================================
# Lambda 優化工具
# ============================================================================

class LambdaOptimizer:
    """
    Lambda 優化工具

    提供各種優化策略
    """

    @staticmethod
    def lazy_import(module_name: str):
        """
        延遲導入

        只在需要時才導入重型庫，減少冷啟動時間
        """
        import importlib

        logger.info(f"延遲導入: {module_name}")

        return importlib.import_module(module_name)

    @staticmethod
    def cache_result(ttl: int = 300):
        """
        結果緩存裝飾器

        Args:
            ttl: 緩存時間（秒）
        """
        cache = {}

        def decorator(func):
            def wrapper(*args, **kwargs):
                # 生成緩存鍵
                cache_key = str(args) + str(kwargs)

                # 檢查緩存
                if cache_key in cache:
                    cached_value, cached_time = cache[cache_key]

                    if time.time() - cached_time < ttl:
                        logger.info("使用緩存結果")
                        return cached_value

                # 執行函數
                result = func(*args, **kwargs)

                # 更新緩存
                cache[cache_key] = (result, time.time())

                return result

            return wrapper

        return decorator

    @staticmethod
    def warmup_handler():
        """
        預熱處理器

        處理預熱請求，保持函數熱啟動
        """
        def decorator(func):
            def wrapper(event, context):
                # 檢查是否為預熱請求
                if event.get("source") == "warmup":
                    logger.info("收到預熱請求")
                    return {
                        "statusCode": 200,
                        "body": json.dumps({"status": "warmed"})
                    }

                # 正常處理
                return func(event, context)

            return wrapper

        return decorator


# ============================================================================
# Lambda 部署配置
# ============================================================================

@dataclass
class LambdaConfig:
    """
    Lambda 配置

    定義 Lambda 函數的各項配置
    """
    function_name: str
    handler: str
    runtime: str = "python3.11"
    memory_size: int = 1024  # MB
    timeout: int = 300  # 秒
    environment_variables: Dict[str, str] = None
    layers: List[str] = None
    vpc_config: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """轉換為 CloudFormation/SAM 格式"""
        config = {
            "FunctionName": self.function_name,
            "Handler": self.handler,
            "Runtime": self.runtime,
            "MemorySize": self.memory_size,
            "Timeout": self.timeout
        }

        if self.environment_variables:
            config["Environment"] = {
                "Variables": self.environment_variables
            }

        if self.layers:
            config["Layers"] = self.layers

        if self.vpc_config:
            config["VpcConfig"] = self.vpc_config

        return config


class DeploymentManager:
    """
    部署管理器

    管理 Lambda 函數的部署和更新
    """

    def __init__(self, region: str = "us-east-1"):
        self.region = region

        logger.info(f"初始化部署管理器: region={region}")

    def create_deployment_package(
        self,
        source_dir: str,
        output_file: str = "lambda_function.zip"
    ) -> str:
        """
        創建部署包

        Args:
            source_dir: 源代碼目錄
            output_file: 輸出文件名

        Returns:
            str: 部署包路徑
        """
        import zipfile

        logger.info(f"創建部署包: {output_file}")

        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)

        logger.info(f"部署包創建完成: {output_file}")

        return output_file

    def generate_sam_template(
        self,
        config: LambdaConfig
    ) -> Dict[str, Any]:
        """
        生成 SAM 模板

        Args:
            config: Lambda 配置

        Returns:
            Dict: SAM 模板
        """
        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Transform": "AWS::Serverless-2016-10-31",
            "Description": "Strands Agents Lambda Deployment",
            "Resources": {
                config.function_name: {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {
                        "FunctionName": config.function_name,
                        "Handler": config.handler,
                        "Runtime": config.runtime,
                        "CodeUri": ".",
                        "MemorySize": config.memory_size,
                        "Timeout": config.timeout,
                        "Policies": [
                            "AWSLambdaBasicExecutionRole",
                            {
                                "Statement": [{
                                    "Effect": "Allow",
                                    "Action": [
                                        "bedrock:InvokeModel",
                                        "bedrock:InvokeModelWithResponseStream"
                                    ],
                                    "Resource": "*"
                                }]
                            }
                        ],
                        "Events": {
                            "ApiEvent": {
                                "Type": "Api",
                                "Properties": {
                                    "Path": "/agent",
                                    "Method": "POST"
                                }
                            }
                        }
                    }
                }
            }
        }

        if config.environment_variables:
            template["Resources"][config.function_name]["Properties"]["Environment"] = {
                "Variables": config.environment_variables
            }

        if config.layers:
            template["Resources"][config.function_name]["Properties"]["Layers"] = config.layers

        return template


# ============================================================================
# Lambda 函數示例
# ============================================================================

# 初始化處理器（全局作用域，在冷啟動時執行）
handler_instance = AgentLambdaHandler()


@LambdaOptimizer.warmup_handler()
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda 入口函數

    這是 AWS Lambda 調用的主函數

    Args:
        event: Lambda 事件
        context: Lambda 上下文

    Returns:
        Dict: Lambda 響應
    """
    return handler_instance.handle(event, context)


# ============================================================================
# 示例和測試
# ============================================================================

def demonstrate_lambda_handler():
    """演示 Lambda 處理器"""
    print("\n" + "="*60)
    print("示例 1: Lambda 處理器")
    print("="*60 + "\n")

    # 模擬 Lambda 上下文
    class MockContext:
        request_id = "test-request-123"
        function_name = "agent-lambda"
        def get_remaining_time_in_millis(self):
            return 30000

    context = MockContext()

    # 模擬 API Gateway 事件
    event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "message": "你好，我想了解 Strands Agents",
            "session_id": "session_123"
        })
    }

    # 調用處理器
    response = lambda_handler(event, context)

    print("響應:")
    print(json.dumps(json.loads(response["body"]), indent=2, ensure_ascii=False))


def demonstrate_deployment_config():
    """演示部署配置"""
    print("\n" + "="*60)
    print("示例 2: 部署配置")
    print("="*60 + "\n")

    config = LambdaConfig(
        function_name="strands-agent-lambda",
        handler="lambda_function.lambda_handler",
        runtime="python3.11",
        memory_size=2048,
        timeout=300,
        environment_variables={
            "MODEL_ID": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "AWS_REGION": "us-east-1",
            "SYSTEM_PROMPT": "你是一個友善的 AI 助手"
        }
    )

    print("Lambda 配置:")
    print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))


def demonstrate_sam_template():
    """演示 SAM 模板生成"""
    print("\n" + "="*60)
    print("示例 3: SAM 模板")
    print("="*60 + "\n")

    manager = DeploymentManager()

    config = LambdaConfig(
        function_name="strands-agent-lambda",
        handler="lambda_function.lambda_handler",
        environment_variables={
            "MODEL_ID": "anthropic.claude-3-5-sonnet-20241022-v2:0"
        }
    )

    template = manager.generate_sam_template(config)

    print("SAM 模板:")
    print(json.dumps(template, indent=2, ensure_ascii=False))


def demonstrate_optimization():
    """演示優化策略"""
    print("\n" + "="*60)
    print("示例 4: 優化策略")
    print("="*60 + "\n")

    # 緩存示例
    @LambdaOptimizer.cache_result(ttl=60)
    def expensive_operation(query: str) -> str:
        print(f"執行耗時操作: {query}")
        time.sleep(0.1)
        return f"結果: {query}"

    # 第一次調用
    print("第一次調用:")
    result1 = expensive_operation("測試查詢")
    print(result1)

    # 第二次調用（使用緩存）
    print("\n第二次調用:")
    result2 = expensive_operation("測試查詢")
    print(result2)


def main():
    """主函數"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*13 + "AWS Lambda 部署示例" + " "*19 + "║")
    print("╚" + "="*58 + "╝")

    try:
        demonstrate_lambda_handler()
        demonstrate_deployment_config()
        demonstrate_sam_template()
        demonstrate_optimization()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

        print("\n部署步驟:")
        print("  1. 安裝 SAM CLI: pip install aws-sam-cli")
        print("  2. 構建: sam build")
        print("  3. 部署: sam deploy --guided")
        print("  4. 測試: sam local invoke")

    except Exception as e:
        logger.error(f"執行錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
