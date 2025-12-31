"""
Strands Agents Amazon Bedrock 整合示例

這個示例展示了如何將 Strands Agents 與 Amazon Bedrock 整合：
1. Bedrock 客戶端配置
2. 多種基礎模型的使用（Claude、Llama、Titan等）
3. 流式響應處理
4. 模型參數調優
5. 成本優化策略
6. 錯誤處理和重試
7. 模型切換和回退
8. 自定義模型調用

Amazon Bedrock 提供了多種領先的基礎模型，
Strands Agents 可以無縫整合這些模型來構建智能應用。

作者: Strands Agents Team
日期: 2025-01
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional, Iterator, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Bedrock 模型配置
# ============================================================================

class BedrockModel(Enum):
    """
    Amazon Bedrock 支援的模型列表
    """
    # Anthropic Claude 系列
    CLAUDE_3_5_SONNET = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    CLAUDE_3_OPUS = "anthropic.claude-3-opus-20240229-v1:0"
    CLAUDE_3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"

    # Meta Llama 系列
    LLAMA_3_2_1B = "meta.llama3-2-1b-instruct-v1:0"
    LLAMA_3_2_3B = "meta.llama3-2-3b-instruct-v1:0"
    LLAMA_3_1_8B = "meta.llama3-1-8b-instruct-v1:0"
    LLAMA_3_1_70B = "meta.llama3-1-70b-instruct-v1:0"

    # Amazon Titan 系列
    TITAN_TEXT_EXPRESS = "amazon.titan-text-express-v1"
    TITAN_TEXT_LITE = "amazon.titan-text-lite-v1"

    # AI21 Labs Jurassic
    JURASSIC_2_ULTRA = "ai21.j2-ultra-v1"
    JURASSIC_2_MID = "ai21.j2-mid-v1"


@dataclass
class ModelConfig:
    """
    模型配置

    Attributes:
        model_id: 模型 ID
        temperature: 溫度參數（0-1）
        max_tokens: 最大生成 token 數
        top_p: nucleus sampling 參數
        top_k: top-k sampling 參數
        stop_sequences: 停止序列
    """
    model_id: str
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    top_k: int = 250
    stop_sequences: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "model_id": self.model_id,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "stop_sequences": self.stop_sequences
        }


# ============================================================================
# Bedrock 客戶端模擬
# ============================================================================

class BedrockClient:
    """
    Amazon Bedrock 客戶端（模擬實現）

    實際使用時應該使用 boto3 的 bedrock-runtime 客戶端
    """

    def __init__(
        self,
        region: str = "us-east-1",
        profile: Optional[str] = None
    ):
        self.region = region
        self.profile = profile

        logger.info(f"初始化 Bedrock 客戶端: region={region}")

        # 在實際實現中，這裡會創建 boto3 客戶端
        # import boto3
        # session = boto3.Session(profile_name=profile)
        # self.client = session.client('bedrock-runtime', region_name=region)

    def invoke_model(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        config: ModelConfig
    ) -> Dict[str, Any]:
        """
        調用 Bedrock 模型

        Args:
            model_id: 模型 ID
            messages: 消息列表
            config: 模型配置

        Returns:
            Dict: 模型響應
        """
        logger.info(f"調用模型: {model_id}")

        # 構建請求體（根據不同模型格式會有所不同）
        request_body = self._build_request_body(model_id, messages, config)

        # 模擬 API 調用
        # 實際實現:
        # response = self.client.invoke_model(
        #     modelId=model_id,
        #     body=json.dumps(request_body)
        # )
        # response_body = json.loads(response['body'].read())

        # 模擬響應
        response_body = self._simulate_response(model_id, messages, config)

        return response_body

    def invoke_model_stream(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        config: ModelConfig
    ) -> Iterator[Dict[str, Any]]:
        """
        流式調用 Bedrock 模型

        Args:
            model_id: 模型 ID
            messages: 消息列表
            config: 模型配置

        Yields:
            Dict: 流式響應塊
        """
        logger.info(f"流式調用模型: {model_id}")

        request_body = self._build_request_body(model_id, messages, config)

        # 實際實現:
        # response = self.client.invoke_model_with_response_stream(
        #     modelId=model_id,
        #     body=json.dumps(request_body)
        # )
        # for event in response['body']:
        #     yield json.loads(event['chunk']['bytes'])

        # 模擬流式響應
        yield from self._simulate_stream_response(model_id, messages, config)

    def _build_request_body(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        config: ModelConfig
    ) -> Dict[str, Any]:
        """
        構建請求體

        不同的模型有不同的請求格式
        """
        if "anthropic.claude" in model_id:
            # Claude 模型格式
            return {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "top_k": config.top_k,
                "stop_sequences": config.stop_sequences
            }

        elif "meta.llama" in model_id:
            # Llama 模型格式
            prompt = self._messages_to_prompt(messages)
            return {
                "prompt": prompt,
                "max_gen_len": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p
            }

        elif "amazon.titan" in model_id:
            # Titan 模型格式
            prompt = self._messages_to_prompt(messages)
            return {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": config.max_tokens,
                    "temperature": config.temperature,
                    "topP": config.top_p,
                    "stopSequences": config.stop_sequences
                }
            }

        else:
            # 通用格式
            return {
                "messages": messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature
            }

    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """將消息列表轉換為提示詞"""
        parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            parts.append(f"{role.upper()}: {content}")
        return "\n\n".join(parts)

    def _simulate_response(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        config: ModelConfig
    ) -> Dict[str, Any]:
        """模擬模型響應"""
        time.sleep(0.5)  # 模擬網絡延遲

        user_message = messages[-1]["content"] if messages else "你好"

        response_text = f"這是來自 {model_id} 的響應。收到您的訊息：{user_message}"

        if "anthropic.claude" in model_id:
            return {
                "id": f"msg_{int(time.time())}",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": response_text}],
                "model": model_id,
                "stop_reason": "end_turn",
                "usage": {
                    "input_tokens": 20,
                    "output_tokens": 50
                }
            }

        elif "meta.llama" in model_id:
            return {
                "generation": response_text,
                "prompt_token_count": 20,
                "generation_token_count": 50,
                "stop_reason": "stop"
            }

        elif "amazon.titan" in model_id:
            return {
                "results": [{
                    "tokenCount": 50,
                    "outputText": response_text,
                    "completionReason": "FINISH"
                }],
                "inputTextTokenCount": 20
            }

        else:
            return {"response": response_text}

    def _simulate_stream_response(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        config: ModelConfig
    ) -> Iterator[Dict[str, Any]]:
        """模擬流式響應"""
        user_message = messages[-1]["content"] if messages else "你好"
        full_response = f"這是來自 {model_id} 的流式響應。{user_message}"

        # 分塊發送
        words = full_response.split()
        for i, word in enumerate(words):
            time.sleep(0.1)  # 模擬延遲

            if "anthropic.claude" in model_id:
                yield {
                    "type": "content_block_delta",
                    "delta": {"type": "text_delta", "text": word + " "},
                    "index": 0
                }
            else:
                yield {"chunk": {"bytes": (word + " ").encode()}}

        # 發送結束事件
        if "anthropic.claude" in model_id:
            yield {
                "type": "message_stop",
                "amazon-bedrock-invocationMetrics": {
                    "inputTokenCount": 20,
                    "outputTokenCount": len(words)
                }
            }


# ============================================================================
# Bedrock Agent 實現
# ============================================================================

class BedrockAgent:
    """
    基於 Bedrock 的 Agent

    整合 Amazon Bedrock 模型的智能代理
    """

    def __init__(
        self,
        name: str,
        model_config: ModelConfig,
        system_prompt: Optional[str] = None,
        region: str = "us-east-1"
    ):
        self.name = name
        self.model_config = model_config
        self.system_prompt = system_prompt
        self.client = BedrockClient(region=region)
        self.conversation_history: List[Dict[str, str]] = []

        if system_prompt:
            self.conversation_history.append({
                "role": "system",
                "content": system_prompt
            })

        logger.info(f"創建 Bedrock Agent: {name} (model: {model_config.model_id})")

    def chat(self, user_message: str) -> str:
        """
        與 Agent 對話

        Args:
            user_message: 用戶消息

        Returns:
            str: Agent 響應
        """
        # 添加用戶消息
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # 調用模型
        response = self.client.invoke_model(
            model_id=self.model_config.model_id,
            messages=self.conversation_history,
            config=self.model_config
        )

        # 提取響應文本
        assistant_message = self._extract_response_text(response)

        # 添加助手響應到歷史
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def chat_stream(self, user_message: str) -> Iterator[str]:
        """
        流式對話

        Args:
            user_message: 用戶消息

        Yields:
            str: 響應文本塊
        """
        # 添加用戶消息
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # 流式調用模型
        full_response = []

        for chunk in self.client.invoke_model_stream(
            model_id=self.model_config.model_id,
            messages=self.conversation_history,
            config=self.model_config
        ):
            text = self._extract_chunk_text(chunk)
            if text:
                full_response.append(text)
                yield text

        # 添加完整響應到歷史
        self.conversation_history.append({
            "role": "assistant",
            "content": "".join(full_response)
        })

    def _extract_response_text(self, response: Dict[str, Any]) -> str:
        """從響應中提取文本"""
        model_id = self.model_config.model_id

        if "anthropic.claude" in model_id:
            return response["content"][0]["text"]
        elif "meta.llama" in model_id:
            return response["generation"]
        elif "amazon.titan" in model_id:
            return response["results"][0]["outputText"]
        else:
            return response.get("response", "")

    def _extract_chunk_text(self, chunk: Dict[str, Any]) -> Optional[str]:
        """從流式響應塊中提取文本"""
        model_id = self.model_config.model_id

        if "anthropic.claude" in model_id:
            if chunk.get("type") == "content_block_delta":
                return chunk["delta"].get("text", "")
        else:
            if "chunk" in chunk:
                return chunk["chunk"]["bytes"].decode()

        return None

    def clear_history(self):
        """清空對話歷史（保留系統提示）"""
        if self.system_prompt:
            self.conversation_history = [{
                "role": "system",
                "content": self.system_prompt
            }]
        else:
            self.conversation_history = []

        logger.info("清空對話歷史")


# ============================================================================
# 多模型管理
# ============================================================================

class MultiModelManager:
    """
    多模型管理器

    支援多個模型的切換和負載均衡
    """

    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.models: Dict[str, ModelConfig] = {}
        self.client = BedrockClient(region=region)

        logger.info("初始化多模型管理器")

    def register_model(self, name: str, config: ModelConfig):
        """註冊模型"""
        self.models[name] = config
        logger.info(f"註冊模型: {name} ({config.model_id})")

    def invoke(
        self,
        model_name: str,
        messages: List[Dict[str, str]],
        fallback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        調用模型（支援回退）

        Args:
            model_name: 模型名稱
            messages: 消息列表
            fallback: 回退模型名稱

        Returns:
            Dict: 響應
        """
        if model_name not in self.models:
            raise ValueError(f"模型未註冊: {model_name}")

        config = self.models[model_name]

        try:
            response = self.client.invoke_model(
                model_id=config.model_id,
                messages=messages,
                config=config
            )
            return response

        except Exception as e:
            logger.error(f"模型調用失敗 {model_name}: {str(e)}")

            # 嘗試回退模型
            if fallback and fallback in self.models:
                logger.info(f"使用回退模型: {fallback}")
                fallback_config = self.models[fallback]

                response = self.client.invoke_model(
                    model_id=fallback_config.model_id,
                    messages=messages,
                    config=fallback_config
                )
                return response

            raise

    def compare_models(
        self,
        messages: List[Dict[str, str]],
        model_names: List[str]
    ) -> Dict[str, Any]:
        """
        比較多個模型的響應

        Args:
            messages: 消息列表
            model_names: 要比較的模型名稱列表

        Returns:
            Dict: 各個模型的響應
        """
        results = {}

        for model_name in model_names:
            if model_name in self.models:
                try:
                    config = self.models[model_name]
                    response = self.client.invoke_model(
                        model_id=config.model_id,
                        messages=messages,
                        config=config
                    )
                    results[model_name] = {
                        "success": True,
                        "response": response
                    }
                except Exception as e:
                    results[model_name] = {
                        "success": False,
                        "error": str(e)
                    }

        return results


# ============================================================================
# 示例和測試
# ============================================================================

def demonstrate_basic_bedrock():
    """演示基本 Bedrock 調用"""
    print("\n" + "="*60)
    print("示例 1: 基本 Bedrock 模型調用")
    print("="*60 + "\n")

    config = ModelConfig(
        model_id=BedrockModel.CLAUDE_3_5_SONNET.value,
        temperature=0.7,
        max_tokens=1024
    )

    agent = BedrockAgent(
        name="助手",
        model_config=config,
        system_prompt="你是一個友善的 AI 助手。"
    )

    # 對話
    questions = [
        "什麼是 Amazon Bedrock？",
        "它有什麼優勢？"
    ]

    for question in questions:
        print(f"用戶: {question}")
        response = agent.chat(question)
        print(f"Agent: {response}\n")


def demonstrate_streaming():
    """演示流式響應"""
    print("\n" + "="*60)
    print("示例 2: 流式響應")
    print("="*60 + "\n")

    config = ModelConfig(
        model_id=BedrockModel.CLAUDE_3_HAIKU.value,
        temperature=0.7
    )

    agent = BedrockAgent(
        name="流式助手",
        model_config=config
    )

    print("用戶: 請介紹 Strands Agents 框架")
    print("Agent: ", end="", flush=True)

    for chunk in agent.chat_stream("請介紹 Strands Agents 框架"):
        print(chunk, end="", flush=True)

    print("\n")


def demonstrate_model_comparison():
    """演示多模型比較"""
    print("\n" + "="*60)
    print("示例 3: 多模型比較")
    print("="*60 + "\n")

    manager = MultiModelManager()

    # 註冊多個模型
    manager.register_model("claude-sonnet", ModelConfig(
        model_id=BedrockModel.CLAUDE_3_5_SONNET.value,
        temperature=0.7
    ))

    manager.register_model("claude-haiku", ModelConfig(
        model_id=BedrockModel.CLAUDE_3_HAIKU.value,
        temperature=0.7
    ))

    manager.register_model("llama", ModelConfig(
        model_id=BedrockModel.LLAMA_3_1_8B.value,
        temperature=0.7
    ))

    # 比較響應
    messages = [{"role": "user", "content": "解釋量子計算"}]
    results = manager.compare_models(
        messages=messages,
        model_names=["claude-sonnet", "claude-haiku", "llama"]
    )

    print("各模型響應:")
    for model_name, result in results.items():
        print(f"\n{model_name}:")
        if result["success"]:
            print(f"  成功")
        else:
            print(f"  失敗: {result['error']}")


def demonstrate_parameter_tuning():
    """演示參數調優"""
    print("\n" + "="*60)
    print("示例 4: 模型參數調優")
    print("="*60 + "\n")

    # 測試不同溫度參數
    temperatures = [0.3, 0.7, 1.0]

    for temp in temperatures:
        print(f"\n溫度 = {temp}:")
        config = ModelConfig(
            model_id=BedrockModel.CLAUDE_3_HAIKU.value,
            temperature=temp,
            max_tokens=100
        )

        agent = BedrockAgent("測試", config)
        response = agent.chat("寫一個創意故事的開頭")
        print(f"響應: {response[:100]}...")


def main():
    """主函數"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*12 + "Amazon Bedrock 整合示例" + " "*17 + "║")
    print("╚" + "="*58 + "╝")

    try:
        demonstrate_basic_bedrock()
        demonstrate_streaming()
        demonstrate_model_comparison()
        demonstrate_parameter_tuning()

        print("\n" + "="*60)
        print("所有示例執行完成！")
        print("="*60)

    except Exception as e:
        logger.error(f"執行錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
