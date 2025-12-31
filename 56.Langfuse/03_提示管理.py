"""
Langfuse 提示管理示例

這個示例展示 Langfuse 的提示詞管理功能，包括：
- 提示詞版本控制
- 集中式提示管理
- 動態提示載入
- 提示模板編譯
- A/B 測試
- 提示優化追蹤

主要內容：
1. 提示詞創建和管理
2. 版本控制系統
3. 模板變量處理
4. 提示鏈管理
5. A/B 測試實施
6. 提示性能追蹤
7. 最佳實踐

作者: Langfuse Team
日期: 2025-01-01
"""

import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from langfuse import Langfuse
from openai import OpenAI
import random


# ============================================================================
# 第一部分：提示詞基礎管理
# ============================================================================

class PromptManager:
    """
    提示詞管理器

    提供完整的提示詞管理功能，包括創建、更新、版本控制等。
    """

    def __init__(self, langfuse: Langfuse):
        """
        初始化提示詞管理器

        Args:
            langfuse: Langfuse 客戶端實例
        """
        self.langfuse = langfuse
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "sk-demo")
        )

    def create_basic_prompt(self):
        """
        創建基礎提示詞示例

        展示如何在 Langfuse 中創建和管理提示詞。
        注意：在實際使用中，提示詞通常通過 Langfuse UI 創建。
        這裡我們展示如何使用和追蹤提示詞。
        """
        print("\n" + "="*60)
        print("基礎提示詞管理示例")
        print("="*60)

        # 模擬從 Langfuse 獲取提示詞
        # 在實際應用中，這會從 Langfuse 服務器載入
        prompt_config = {
            "name": "customer-support-assistant",
            "version": 1,
            "type": "chat",
            "template": """你是一個專業的客戶支援助手。

客戶信息：
- 姓名：{{customer_name}}
- 會員等級：{{tier}}
- 問題類型：{{issue_type}}

請根據以下客戶問題提供專業、友善的回答：
{{customer_message}}

注意事項：
1. 保持禮貌和專業
2. 提供具體的解決方案
3. 如果需要，提供後續步驟
4. 確認客戶是否滿意""",
            "config": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 500
            }
        }

        print(f"📝 提示詞配置:")
        print(f"   名稱: {prompt_config['name']}")
        print(f"   版本: {prompt_config['version']}")
        print(f"   類型: {prompt_config['type']}")
        print(f"   模型: {prompt_config['config']['model']}")

        return prompt_config

    def compile_prompt_template(self, template: str, variables: Dict[str, Any]) -> str:
        """
        編譯提示詞模板

        將模板中的變量替換為實際值。

        Args:
            template: 提示詞模板
            variables: 變量字典

        Returns:
            編譯後的提示詞
        """
        compiled = template

        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            compiled = compiled.replace(placeholder, str(value))

        return compiled

    def use_prompt_example(self):
        """
        使用提示詞示例

        展示如何載入提示詞並在實際應用中使用。
        """
        print("\n" + "="*60)
        print("提示詞使用示例")
        print("="*60)

        # 獲取提示詞配置
        prompt_config = self.create_basic_prompt()

        # 準備變量
        variables = {
            "customer_name": "張小明",
            "tier": "黃金會員",
            "issue_type": "產品故障",
            "customer_message": "我的筆記本電腦無法開機，按電源鍵沒有任何反應。"
        }

        print(f"\n🔧 編譯提示詞...")
        print(f"   變量: {list(variables.keys())}")

        # 編譯提示詞
        compiled_prompt = self.compile_prompt_template(
            prompt_config["template"],
            variables
        )

        print(f"\n📄 編譯結果:")
        print("-" * 60)
        print(compiled_prompt)
        print("-" * 60)

        # 創建追蹤
        trace = self.langfuse.trace(
            name="customer-support-query",
            user_id="customer-zhang-001",
            metadata={
                "prompt_name": prompt_config["name"],
                "prompt_version": prompt_config["version"],
                "variables": variables
            }
        )

        # 創建 generation 並使用提示詞
        generation = trace.generation(
            name="support-response",
            model=prompt_config["config"]["model"],
            input=[{"role": "user", "content": compiled_prompt}],
            metadata={
                "prompt_name": prompt_config["name"],
                "prompt_version": prompt_config["version"],
                "temperature": prompt_config["config"]["temperature"]
            },
            prompt={
                "name": prompt_config["name"],
                "version": prompt_config["version"]
            }
        )

        try:
            # 調用 LLM
            response = self.openai_client.chat.completions.create(
                model=prompt_config["config"]["model"],
                messages=[{"role": "user", "content": compiled_prompt}],
                temperature=prompt_config["config"]["temperature"],
                max_tokens=prompt_config["config"]["max_tokens"]
            )

            output = response.choices[0].message.content

            generation.end(
                output=output,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )

            print(f"\n💬 AI 回應:")
            print(output)

        except Exception as e:
            generation.end(level="ERROR", status_message=str(e))
            print(f"❌ 錯誤: {e}")

        print(f"\n✅ 提示詞使用完成")

        return trace


# ============================================================================
# 第二部分：提示詞版本控制
# ============================================================================

class PromptVersioning:
    """
    提示詞版本管理

    展示如何管理提示詞的不同版本。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "sk-demo")
        )

    def version_evolution_example(self):
        """
        版本演化示例

        展示提示詞如何隨時間演化和改進。
        """
        print("\n" + "="*60)
        print("提示詞版本演化示例")
        print("="*60)

        # 定義不同版本的提示詞
        prompt_versions = {
            1: {
                "template": "將以下文本翻譯成英文：{{text}}",
                "description": "初始版本 - 簡單直接",
                "created": "2024-01-01"
            },
            2: {
                "template": """請將以下文本翻譯成英文。

原文：{{text}}

要求：
- 保持原意
- 使用自然流暢的英文""",
                "description": "v2 - 添加了格式和要求",
                "created": "2024-02-01"
            },
            3: {
                "template": """你是一位專業的翻譯專家。請將以下{{source_lang}}文本翻譯成{{target_lang}}。

原文：{{text}}

翻譯要求：
- 準確傳達原文含義
- 使用地道的目標語言表達
- 保持原文的語氣和風格
- 如有專業術語，請確保準確性

翻譯：""",
                "description": "v3 - 添加角色定位和詳細要求",
                "created": "2024-03-01"
            },
            4: {
                "template": """你是一位經驗豐富的專業翻譯，精通{{source_lang}}和{{target_lang}}。

背景信息：
- 領域：{{domain}}
- 目標受眾：{{audience}}

原文：
{{text}}

翻譯要求：
1. 準確性：確保翻譯準確無誤
2. 自然性：使用目標語言的自然表達
3. 一致性：保持術語翻譯一致
4. 可讀性：確保譯文流暢易懂
5. 文化適應：考慮文化差異，適當調整

請提供高質量的專業翻譯：""",
                "description": "v4 - 添加背景信息和結構化要求（當前最佳版本）",
                "created": "2024-04-01"
            }
        }

        # 顯示版本歷史
        print("📚 提示詞版本歷史:")
        for version, config in prompt_versions.items():
            print(f"\n   版本 {version} ({config['created']}):")
            print(f"   描述: {config['description']}")

        # 使用最新版本
        latest_version = max(prompt_versions.keys())
        print(f"\n🎯 使用最新版本: v{latest_version}")

        # 測試最新版本
        variables = {
            "source_lang": "中文",
            "target_lang": "英文",
            "domain": "科技",
            "audience": "技術專業人士",
            "text": "人工智慧正在改變我們的生活方式。"
        }

        prompt_manager = PromptManager(self.langfuse)
        compiled = prompt_manager.compile_prompt_template(
            prompt_versions[latest_version]["template"],
            variables
        )

        print(f"\n編譯後的提示詞（部分）:")
        print(compiled[:200] + "...")

        # 創建追蹤
        trace = self.langfuse.trace(
            name="translation-task",
            metadata={
                "prompt_version": latest_version,
                "prompt_history": [
                    {"version": v, "date": c["created"]}
                    for v, c in prompt_versions.items()
                ]
            }
        )

        print(f"\n✅ 版本追蹤已記錄")

        return trace

    def compare_versions_example(self):
        """
        版本比較示例

        展示如何比較不同版本的提示詞效果。
        """
        print("\n" + "="*60)
        print("提示詞版本比較示例")
        print("="*60)

        # 兩個版本的提示詞
        v1_template = "總結以下內容：{{content}}"
        v2_template = """請用 3-5 個要點總結以下內容：

內容：
{{content}}

總結要點："""

        test_content = "Langfuse 是一個開源的 LLM 可觀測性平台。它提供追蹤、提示管理和評估功能。開發者可以使用它來監控和優化 AI 應用。"

        versions = [
            ("v1-simple", v1_template),
            ("v2-structured", v2_template)
        ]

        results = []

        for version_name, template in versions:
            print(f"\n測試 {version_name}...")

            prompt_manager = PromptManager(self.langfuse)
            compiled = prompt_manager.compile_prompt_template(
                template,
                {"content": test_content}
            )

            # 創建追蹤
            trace = self.langfuse.trace(
                name=f"version-comparison-{version_name}",
                metadata={
                    "test_type": "version_comparison",
                    "version": version_name
                }
            )

            generation = trace.generation(
                name="summarization",
                model="gpt-3.5-turbo",
                input=[{"role": "user", "content": compiled}],
                metadata={"version": version_name}
            )

            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": compiled}],
                    temperature=0.7
                )

                output = response.choices[0].message.content

                generation.end(
                    output=output,
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                )

                results.append({
                    "version": version_name,
                    "output": output,
                    "tokens": response.usage.total_tokens
                })

                print(f"   ✓ {version_name} 完成")
                print(f"   Token 使用: {response.usage.total_tokens}")

            except Exception as e:
                generation.end(level="ERROR", status_message=str(e))
                print(f"   ✗ {version_name} 失敗: {e}")

        # 顯示比較結果
        print(f"\n📊 版本比較結果:")
        for result in results:
            print(f"\n{result['version']}:")
            print(f"輸出: {result['output'][:100]}...")
            print(f"Token: {result['tokens']}")

        print(f"\n✅ 版本比較完成")


# ============================================================================
# 第三部分：提示鏈管理
# ============================================================================

class PromptChaining:
    """
    提示鏈管理

    展示如何組合多個提示詞形成處理鏈。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "sk-demo")
        )

    def sequential_prompt_chain(self):
        """
        順序提示鏈示例

        展示如何使用多個提示詞進行順序處理。
        """
        print("\n" + "="*60)
        print("順序提示鏈示例")
        print("="*60)

        # 定義提示鏈
        prompt_chain = {
            "step1_extract": {
                "name": "information-extraction",
                "template": """從以下文本中提取關鍵信息：

文本：{{text}}

請提取：
1. 主要主題
2. 關鍵實體
3. 重要數據

以 JSON 格式返回。"""
            },
            "step2_analyze": {
                "name": "sentiment-analysis",
                "template": """分析以下信息的情感傾向：

{{extracted_info}}

請評估：
1. 整體情感（正面/中性/負面）
2. 情感強度（1-10）
3. 主要情感因素"""
            },
            "step3_summarize": {
                "name": "final-summary",
                "template": """基於以下分析結果，生成執行摘要：

提取的信息：
{{extracted_info}}

情感分析：
{{sentiment_analysis}}

請生成一個簡潔的執行摘要（100 字以內）。"""
            }
        }

        # 創建追蹤
        trace = self.langfuse.trace(
            name="prompt-chain-demo",
            metadata={"chain_length": len(prompt_chain)}
        )

        print(f"🔗 執行 {len(prompt_chain)} 步提示鏈...")

        # 初始輸入
        initial_text = "Langfuse 是一個令人興奮的開源項目！它為 LLM 應用提供了強大的可觀測性功能，包括詳細的追蹤、靈活的提示管理和全面的評估系統。開發者反饋非常積極，社區快速成長。"

        # Step 1: 信息提取
        print("\n📍 步驟 1: 信息提取")
        prompt_manager = PromptManager(self.langfuse)

        step1_prompt = prompt_manager.compile_prompt_template(
            prompt_chain["step1_extract"]["template"],
            {"text": initial_text}
        )

        step1_gen = trace.generation(
            name="step1-extraction",
            model="gpt-3.5-turbo",
            input=[{"role": "user", "content": step1_prompt}],
            metadata={"step": 1, "prompt_name": "information-extraction"}
        )

        try:
            step1_response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": step1_prompt}]
            )

            extracted_info = step1_response.choices[0].message.content

            step1_gen.end(
                output=extracted_info,
                usage={
                    "prompt_tokens": step1_response.usage.prompt_tokens,
                    "completion_tokens": step1_response.usage.completion_tokens,
                    "total_tokens": step1_response.usage.total_tokens
                }
            )

            print(f"   ✓ 完成")

        except Exception as e:
            step1_gen.end(level="ERROR", status_message=str(e))
            print(f"   ✗ 失敗: {e}")
            return

        # Step 2: 情感分析
        print("\n📍 步驟 2: 情感分析")

        step2_prompt = prompt_manager.compile_prompt_template(
            prompt_chain["step2_analyze"]["template"],
            {"extracted_info": extracted_info}
        )

        step2_gen = trace.generation(
            name="step2-sentiment",
            model="gpt-3.5-turbo",
            input=[{"role": "user", "content": step2_prompt}],
            metadata={"step": 2, "prompt_name": "sentiment-analysis"}
        )

        try:
            step2_response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": step2_prompt}]
            )

            sentiment_analysis = step2_response.choices[0].message.content

            step2_gen.end(
                output=sentiment_analysis,
                usage={
                    "prompt_tokens": step2_response.usage.prompt_tokens,
                    "completion_tokens": step2_response.usage.completion_tokens,
                    "total_tokens": step2_response.usage.total_tokens
                }
            )

            print(f"   ✓ 完成")

        except Exception as e:
            step2_gen.end(level="ERROR", status_message=str(e))
            print(f"   ✗ 失敗: {e}")
            return

        # Step 3: 最終總結
        print("\n📍 步驟 3: 生成摘要")

        step3_prompt = prompt_manager.compile_prompt_template(
            prompt_chain["step3_summarize"]["template"],
            {
                "extracted_info": extracted_info,
                "sentiment_analysis": sentiment_analysis
            }
        )

        step3_gen = trace.generation(
            name="step3-summary",
            model="gpt-3.5-turbo",
            input=[{"role": "user", "content": step3_prompt}],
            metadata={"step": 3, "prompt_name": "final-summary"}
        )

        try:
            step3_response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": step3_prompt}]
            )

            final_summary = step3_response.choices[0].message.content

            step3_gen.end(
                output=final_summary,
                usage={
                    "prompt_tokens": step3_response.usage.prompt_tokens,
                    "completion_tokens": step3_response.usage.completion_tokens,
                    "total_tokens": step3_response.usage.total_tokens
                }
            )

            print(f"   ✓ 完成")

            # 顯示最終結果
            print(f"\n📝 最終摘要:")
            print(final_summary)

        except Exception as e:
            step3_gen.end(level="ERROR", status_message=str(e))
            print(f"   ✗ 失敗: {e}")

        # 更新追蹤
        trace.update(
            output={"final_summary": final_summary if 'final_summary' in locals() else None},
            metadata={"chain_completed": True}
        )

        print(f"\n✅ 提示鏈執行完成")

        return trace


# ============================================================================
# 第四部分：A/B 測試
# ============================================================================

class PromptABTesting:
    """
    提示詞 A/B 測試

    展示如何進行提示詞的 A/B 測試。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "sk-demo")
        )

    def ab_test_example(self):
        """
        A/B 測試示例

        比較兩個提示詞變體的效果。
        """
        print("\n" + "="*60)
        print("提示詞 A/B 測試示例")
        print("="*60)

        # 定義兩個變體
        variants = {
            "variant_a": {
                "name": "direct-style",
                "template": "請為以下產品寫一個廣告文案：{{product}}",
                "description": "直接簡潔的風格"
            },
            "variant_b": {
                "name": "detailed-style",
                "template": """你是一位創意文案專家。請為以下產品創作一個吸引人的廣告文案。

產品：{{product}}

要求：
- 突出產品特點
- 吸引目標受眾
- 包含行動號召
- 控制在 50 字以內""",
                "description": "詳細指導的風格"
            }
        }

        # 測試產品
        test_product = "智能手錶 - 支持健康監測、運動追蹤、移動支付"

        results = {}

        # 運行 A/B 測試
        for variant_id, variant_config in variants.items():
            print(f"\n🧪 測試變體: {variant_id}")
            print(f"   描述: {variant_config['description']}")

            prompt_manager = PromptManager(self.langfuse)
            compiled = prompt_manager.compile_prompt_template(
                variant_config["template"],
                {"product": test_product}
            )

            # 創建追蹤（標記為 A/B 測試）
            trace = self.langfuse.trace(
                name="ab-test-copywriting",
                metadata={
                    "experiment": "prompt-ab-test-001",
                    "variant": variant_id,
                    "variant_name": variant_config["name"]
                },
                tags=["ab-test", variant_id]
            )

            generation = trace.generation(
                name="generate-copy",
                model="gpt-3.5-turbo",
                input=[{"role": "user", "content": compiled}],
                metadata={
                    "variant": variant_id,
                    "experiment_id": "prompt-ab-test-001"
                }
            )

            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": compiled}],
                    temperature=0.7
                )

                output = response.choices[0].message.content

                generation.end(
                    output=output,
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                )

                results[variant_id] = {
                    "output": output,
                    "tokens": response.usage.total_tokens,
                    "prompt_length": len(compiled)
                }

                print(f"   ✓ 生成完成")

            except Exception as e:
                generation.end(level="ERROR", status_message=str(e))
                print(f"   ✗ 失敗: {e}")

        # 顯示對比結果
        print(f"\n" + "="*60)
        print("📊 A/B 測試結果對比")
        print("="*60)

        for variant_id, result in results.items():
            variant_name = variants[variant_id]["name"]
            print(f"\n{variant_id.upper()} ({variant_name}):")
            print(f"文案: {result['output']}")
            print(f"Token 使用: {result['tokens']}")
            print(f"提示長度: {result['prompt_length']} 字符")

        print(f"\n💡 分析建議:")
        print("   - 在 Langfuse UI 中查看詳細的性能指標")
        print("   - 收集用戶反饋來評估文案質量")
        print("   - 根據業務指標選擇最佳變體")

        print(f"\n✅ A/B 測試完成")


# ============================================================================
# 第五部分：提示優化追蹤
# ============================================================================

class PromptOptimization:
    """
    提示詞優化追蹤

    追蹤提示詞的性能並進行優化。
    """

    def __init__(self, langfuse: Langfuse):
        self.langfuse = langfuse

    def track_prompt_performance(self):
        """
        追蹤提示詞性能示例

        記錄和分析提示詞的性能指標。
        """
        print("\n" + "="*60)
        print("提示詞性能追蹤示例")
        print("="*60)

        # 模擬多次使用同一提示詞
        prompt_name = "email-response-generator"
        prompt_version = 3

        print(f"📊 追蹤提示詞: {prompt_name} (v{prompt_version})")

        # 模擬 10 次調用
        metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_tokens": 0,
            "total_latency": 0,
            "total_cost": 0
        }

        for i in range(10):
            success = random.choice([True, True, True, True, False])  # 80% 成功率
            tokens = random.randint(100, 500)
            latency = random.uniform(0.5, 2.0)
            cost = tokens * 0.00002  # 假設每 token 0.00002 USD

            trace = self.langfuse.trace(
                name=f"email-generation-{i+1}",
                metadata={
                    "prompt_name": prompt_name,
                    "prompt_version": prompt_version,
                    "success": success,
                    "tokens": tokens,
                    "latency_seconds": latency,
                    "cost_usd": cost
                },
                tags=["performance-tracking", prompt_name]
            )

            metrics["total_calls"] += 1
            if success:
                metrics["successful_calls"] += 1
            else:
                metrics["failed_calls"] += 1

            metrics["total_tokens"] += tokens
            metrics["total_latency"] += latency
            metrics["total_cost"] += cost

            time.sleep(0.05)

        # 計算平均值
        avg_tokens = metrics["total_tokens"] / metrics["total_calls"]
        avg_latency = metrics["total_latency"] / metrics["total_calls"]
        avg_cost = metrics["total_cost"] / metrics["total_calls"]
        success_rate = (metrics["successful_calls"] / metrics["total_calls"]) * 100

        print(f"\n📈 性能指標:")
        print(f"   總調用次數: {metrics['total_calls']}")
        print(f"   成功率: {success_rate:.1f}%")
        print(f"   平均 Token 使用: {avg_tokens:.0f}")
        print(f"   平均延遲: {avg_latency:.2f}s")
        print(f"   平均成本: ${avg_cost:.5f}")
        print(f"   總成本: ${metrics['total_cost']:.4f}")

        print(f"\n💡 優化建議:")
        if avg_tokens > 300:
            print("   ⚠️  Token 使用偏高，考慮簡化提示詞")
        if avg_latency > 1.5:
            print("   ⚠️  延遲較高，考慮使用更快的模型")
        if success_rate < 90:
            print("   ⚠️  成功率偏低，需要改進提示詞")

        print(f"\n✅ 性能追蹤完成")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有提示管理示例
    """
    print("\n" + "="*70)
    print("Langfuse 提示管理示例")
    print("="*70)

    # 初始化 Langfuse
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "pk-demo"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY", "sk-demo"),
        debug=True
    )

    try:
        # 1. 基礎提示詞管理
        print("\n" + "="*70)
        print("第一部分：基礎提示詞管理")
        print("="*70)
        prompt_mgr = PromptManager(langfuse)
        prompt_mgr.use_prompt_example()

        # 2. 版本控制
        print("\n" + "="*70)
        print("第二部分：提示詞版本控制")
        print("="*70)
        versioning = PromptVersioning(langfuse)
        versioning.version_evolution_example()
        versioning.compare_versions_example()

        # 3. 提示鏈
        print("\n" + "="*70)
        print("第三部分：提示鏈管理")
        print("="*70)
        chaining = PromptChaining(langfuse)
        chaining.sequential_prompt_chain()

        # 4. A/B 測試
        print("\n" + "="*70)
        print("第四部分：A/B 測試")
        print("="*70)
        ab_testing = PromptABTesting(langfuse)
        ab_testing.ab_test_example()

        # 5. 性能優化
        print("\n" + "="*70)
        print("第五部分：提示詞優化")
        print("="*70)
        optimization = PromptOptimization(langfuse)
        optimization.track_prompt_performance()

        print("\n" + "="*70)
        print("✅ 所有提示管理示例運行完成！")
        print("="*70)

        print("\n💡 最佳實踐總結:")
        print("   1. 使用版本控制追蹤提示詞演化")
        print("   2. 通過 A/B 測試優化提示效果")
        print("   3. 持續監控提示詞性能指標")
        print("   4. 使用模板變量提高復用性")
        print("   5. 記錄詳細的元數據便於分析")

        # 刷新數據
        langfuse.flush()

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
