#!/usr/bin/env python3
"""
Goose 多模型支持示例

展示如何在 Goose 中使用不同的 LLM:
1. OpenAI GPT 系列
2. Anthropic Claude
3. Google Gemini
4. 本地模型（Ollama）
5. Azure OpenAI
6. 模型選擇策略

作者: AI Agent
日期: 2024
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """模型配置"""
    provider: str
    model: str
    description: str
    strengths: List[str]
    best_for: List[str]
    pricing: str


class MultiModelDemo:
    """多模型支持演示"""

    def __init__(self):
        """初始化"""
        self.models = self._load_model_configs()

    def _load_model_configs(self) -> List[ModelConfig]:
        """載入模型配置"""
        return [
            ModelConfig(
                provider="OpenAI",
                model="gpt-4-turbo-preview",
                description="最新的 GPT-4 模型，128K 上下文",
                strengths=["推理能力強", "代碼生成優秀", "長上下文"],
                best_for=["複雜代碼", "架構設計", "代碼審查"],
                pricing="$0.01/1K tokens (輸入), $0.03/1K tokens (輸出)"
            ),
            ModelConfig(
                provider="Anthropic",
                model="claude-3-opus-20240229",
                description="Claude 3 最強模型，200K 上下文",
                strengths=["分析能力強", "安全意識高", "長文本理解"],
                best_for=["代碼審查", "文檔生成", "複雜問題"],
                pricing="$15/1M tokens (輸入), $75/1M tokens (輸出)"
            ),
        ]

    def openai_configuration(self):
        """
        OpenAI 配置示例
        """
        print("\n" + "="*70)
        print("OpenAI 配置")
        print("="*70)

        config = """# OpenAI 配置
# ~/.config/goose/config.yaml

provider:
  type: openai
  model: gpt-4-turbo-preview
  api_key: ${OPENAI_API_KEY}

  # 可選配置
  base_url: null  # 自定義 API 端點
  organization: null  # 組織 ID

  # 模型參數
  temperature: 0.7
  max_tokens: 4096
  top_p: 1.0
  frequency_penalty: 0.0
  presence_penalty: 0.0

# 環境變量設置
# export OPENAI_API_KEY="sk-..."

# 可用模型:
# - gpt-4-turbo-preview (最新, 128K)
# - gpt-4-0125-preview (穩定版)
# - gpt-4 (標準版, 8K)
# - gpt-3.5-turbo (快速, 經濟)
# - gpt-3.5-turbo-16k (16K 上下文)
"""

        print(config)

        # 命令行切換模型
        cli_examples = """
# 臨時切換模型
$ goose --model gpt-4 "重構這個函數"
$ goose --model gpt-3.5-turbo "快速生成測試"

# 設置默認模型
$ goose config set provider.model gpt-4-turbo-preview

# 查看當前配置
$ goose config get provider.model
"""

        print("\n命令行使用:")
        print("-"*70)
        print(cli_examples)

    def anthropic_configuration(self):
        """
        Anthropic Claude 配置
        """
        print("\n" + "="*70)
        print("Anthropic Claude 配置")
        print("="*70)

        config = """# Anthropic Claude 配置
# ~/.config/goose/config.yaml

provider:
  type: anthropic
  model: claude-3-opus-20240229
  api_key: ${ANTHROPIC_API_KEY}

  # 模型參數
  temperature: 0.7
  max_tokens: 4096
  top_p: 1.0
  top_k: 0

# 環境變量設置
# export ANTHROPIC_API_KEY="sk-ant-..."

# 可用模型:
# Claude 3 系列:
# - claude-3-opus-20240229 (最強, 200K)
# - claude-3-sonnet-20240229 (平衡, 200K)
# - claude-3-haiku-20240307 (快速, 200K)

# Claude 2 系列:
# - claude-2.1 (100K)
# - claude-2.0

# 特點:
# - 超長上下文（最高 200K tokens）
# - 優秀的代碼理解能力
# - 強大的安全性和拒絕有害請求
# - 出色的指令遵循能力
"""

        print(config)

        # 使用建議
        recommendations = """
Claude 模型選擇建議:

1. claude-3-opus (最強)
   - 複雜代碼架構設計
   - 深度代碼審查
   - 需要最高質量的場景

2. claude-3-sonnet (平衡)
   - 日常開發任務
   - 代碼生成和重構
   - 性價比最高

3. claude-3-haiku (快速)
   - 簡單任務
   - 快速原型
   - 大量請求的場景

切換示例:
$ goose --model claude-3-sonnet-20240229 "生成 API 文檔"
$ goose --model claude-3-haiku-20240307 "快速格式化代碼"
"""

        print("\n使用建議:")
        print("-"*70)
        print(recommendations)

    def google_gemini_configuration(self):
        """
        Google Gemini 配置
        """
        print("\n" + "="*70)
        print("Google Gemini 配置")
        print("="*70)

        config = """# Google Gemini 配置
# ~/.config/goose/config.yaml

provider:
  type: google
  model: gemini-pro
  api_key: ${GOOGLE_API_KEY}

  # 模型參數
  temperature: 0.7
  max_output_tokens: 2048
  top_p: 0.95
  top_k: 40

# 環境變量設置
# export GOOGLE_API_KEY="..."

# 可用模型:
# - gemini-pro (文本, 32K 輸入, 2K 輸出)
# - gemini-pro-vision (多模態)
# - gemini-ultra (最強, 預覽中)

# 特點:
# - 免費配額較高
# - 支持多模態（圖片+文本）
# - 快速響應
# - 適合原型開發
"""

        print(config)

    def ollama_local_models(self):
        """
        Ollama 本地模型配置
        """
        print("\n" + "="*70)
        print("Ollama 本地模型")
        print("="*70)

        setup = """# Ollama 安裝和配置

# 1. 安裝 Ollama
$ curl -fsSL https://ollama.ai/install.sh | sh

# 或使用 Homebrew (macOS)
$ brew install ollama

# 2. 下載模型
$ ollama pull llama2           # Meta Llama 2 (7B)
$ ollama pull codellama        # Code Llama (7B/13B/34B)
$ ollama pull mistral          # Mistral (7B)
$ ollama pull mixtral          # Mixtral (8x7B)
$ ollama pull deepseek-coder   # DeepSeek Coder

# 3. 運行 Ollama 服務
$ ollama serve

# 4. 測試模型
$ ollama run llama2 "Hello, how are you?"

# 5. 查看已安裝的模型
$ ollama list

# 6. 配置 Goose
# ~/.config/goose/config.yaml
provider:
  type: ollama
  model: codellama
  base_url: http://localhost:11434

  # 模型參數
  temperature: 0.7
  num_ctx: 4096  # 上下文長度

# 環境變量（可選）
# export OLLAMA_HOST="http://localhost:11434"
"""

        print(setup)

        # 推薦模型
        models = """
推薦的本地模型:

1. CodeLlama (代碼專用)
   - codellama:7b (快速, 7GB RAM)
   - codellama:13b (平衡, 13GB RAM)
   - codellama:34b (最強, 34GB RAM)

   下載: ollama pull codellama
   特點: Meta 專門訓練的代碼模型

2. DeepSeek Coder (代碼專用)
   - deepseek-coder:6.7b (快速)
   - deepseek-coder:33b (強大)

   下載: ollama pull deepseek-coder
   特點: 優秀的代碼理解和生成

3. Mistral (通用)
   - mistral:7b (輕量, 高效)

   下載: ollama pull mistral
   特點: 性能優秀的開源模型

4. Mixtral (通用)
   - mixtral:8x7b (強大)

   下載: ollama pull mixtral
   特點: MoE 架構，性能接近 GPT-3.5

使用示例:
$ goose --model codellama "重構這個函數"
$ goose --model deepseek-coder "生成單元測試"
"""

        print("\n推薦模型:")
        print("-"*70)
        print(models)

        # 優缺點
        pros_cons = """
本地模型優缺點:

優點:
✓ 完全離線使用
✓ 無 API 成本
✓ 數據隱私保護
✓ 無速率限制
✓ 可自定義訓練

缺點:
✗ 需要較多 RAM/VRAM
✗ 性能不如雲端大模型
✗ 首次下載模型較大
✗ 推理速度較慢（無 GPU 時）

推薦配置:
- 最低: 16GB RAM, codellama:7b
- 推薦: 32GB RAM + GPU, codellama:13b
- 高配: 64GB RAM + GPU, mixtral:8x7b
"""

        print("\n優缺點分析:")
        print("-"*70)
        print(pros_cons)

    def azure_openai_configuration(self):
        """
        Azure OpenAI 配置
        """
        print("\n" + "="*70)
        print("Azure OpenAI 配置")
        print("="*70)

        config = """# Azure OpenAI 配置
# ~/.config/goose/config.yaml

provider:
  type: azure
  model: gpt-4  # 你的部署名稱
  api_key: ${AZURE_OPENAI_API_KEY}
  base_url: ${AZURE_OPENAI_ENDPOINT}
  api_version: "2024-02-15-preview"

  # Azure 特定配置
  deployment_name: your-deployment-name

# 環境變量設置
# export AZURE_OPENAI_API_KEY="..."
# export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
# export AZURE_OPENAI_DEPLOYMENT="your-deployment-name"

# Azure 特點:
# - 企業級安全和合規
# - 數據駐留保證
# - SLA 保證
# - 與 Azure 服務集成
# - 更嚴格的內容過濾

# 注意事項:
# 1. model 字段填寫你的部署名稱，而非 OpenAI 模型名
# 2. 需要在 Azure Portal 中創建資源和部署
# 3. 價格可能與 OpenAI 直接 API 不同
"""

        print(config)

    def model_selection_strategy(self):
        """
        模型選擇策略
        """
        print("\n" + "="*70)
        print("模型選擇策略")
        print("="*70)

        strategy = """
根據任務選擇模型:

1. 複雜代碼生成和架構設計
   推薦: GPT-4 Turbo, Claude 3 Opus
   原因: 強大的推理能力，深度理解需求

2. 日常代碼編寫和重構
   推薦: GPT-4, Claude 3 Sonnet, CodeLlama 34B
   原因: 性能與成本平衡

3. 快速原型和簡單任務
   推薦: GPT-3.5 Turbo, Claude 3 Haiku, Gemini Pro
   原因: 響應快速，成本低

4. 代碼審查和安全分析
   推薦: Claude 3 Opus, GPT-4
   原因: 優秀的分析能力，注重安全

5. 文檔生成和技術寫作
   推薦: Claude 3 Sonnet, GPT-4
   原因: 清晰的表達能力

6. 大規模代碼庫分析
   推薦: Claude 3 系列（200K 上下文）
   原因: 超長上下文窗口

7. 離線/私密項目
   推薦: CodeLlama, DeepSeek Coder (本地)
   原因: 數據不離開本地

8. 預算有限
   推薦: GPT-3.5 Turbo, Gemini Pro, 本地模型
   原因: 成本低或免費

9. 企業合規要求
   推薦: Azure OpenAI, Claude (企業版)
   原因: 合規保證，數據駐留

10. 多模態需求（圖片+代碼）
    推薦: GPT-4 Vision, Gemini Pro Vision
    原因: 支持多模態輸入
"""

        print(strategy)

    def dynamic_model_switching(self):
        """
        動態模型切換
        """
        print("\n" + "="*70)
        print("動態模型切換")
        print("="*70)

        switching_config = """# 動態模型切換配置
# .goose/config.yaml

# 定義多個模型配置
models:
  fast:
    provider: openai
    model: gpt-3.5-turbo
    temperature: 0.5

  balanced:
    provider: openai
    model: gpt-4
    temperature: 0.7

  powerful:
    provider: anthropic
    model: claude-3-opus-20240229
    temperature: 0.7

  local:
    provider: ollama
    model: codellama
    temperature: 0.7

# 默認模型
default_model: balanced

# 任務特定模型
task_models:
  simple_task: fast
  code_generation: balanced
  code_review: powerful
  offline: local

# 自動選擇規則
auto_select:
  enabled: true
  rules:
    # 簡單任務用快速模型
    - condition: "length < 100 and complexity == 'low'"
      model: fast

    # 複雜任務用強大模型
    - condition: "complexity == 'high' or task_type == 'architecture'"
      model: powerful

    # 離線時用本地模型
    - condition: "offline_mode == true"
      model: local
"""

        print(switching_config)

        # 使用示例
        usage = """
# 使用預定義的模型配置
$ goose --model-config fast "快速任務"
$ goose --model-config powerful "複雜審查"

# 按任務類型自動選擇
$ goose --task simple "列出文件"    # 使用 fast
$ goose --task review "審查代碼"     # 使用 powerful

# 在會話中切換模型
$ goose
> /model fast
切換到 gpt-3.5-turbo

> 簡單的任務...

> /model powerful
切換到 claude-3-opus

> 複雜的分析...
"""

        print("\n使用示例:")
        print("-"*70)
        print(usage)

    def cost_optimization(self):
        """
        成本優化策略
        """
        print("\n" + "="*70)
        print("成本優化")
        print("="*70)

        optimization = """
成本優化策略:

1. 使用分層模型
   - 簡單任務: GPT-3.5 Turbo ($0.001/1K)
   - 中等任務: GPT-4 ($0.03/1K)
   - 複雜任務: Claude 3 Opus ($0.075/1K)

2. 啟用緩存
   - 重複的查詢使用緩存結果
   - 節省 API 調用

3. 優化提示詞
   - 簡潔明確的指令
   - 減少不必要的上下文

4. 使用流式輸出
   - 提前發現問題，可提前停止
   - 避免完整生成無用內容

5. 批處理請求
   - 合併多個小請求
   - 減少 API 調用次數

6. 混合使用本地模型
   - 簡單任務用本地模型
   - 複雜任務才用雲端 API

7. 設置預算限制
   - 每日/每月 API 調用限制
   - 自動切換到免費/便宜模型

示例配置:
# .goose/config.yaml
budget:
  monthly_limit: 100.00  # USD
  daily_limit: 10.00

  # 達到 80% 時切換到便宜模型
  fallback_at_percentage: 80
  fallback_model: gpt-3.5-turbo

  # 達到限制時的行為
  on_limit_reached: switch_to_local  # switch_to_local, stop, warn
"""

        print(optimization)


def main():
    """主函數"""
    print("="*70)
    print("Goose 多模型支持教程")
    print("="*70)

    demo = MultiModelDemo()

    sections = [
        ("OpenAI 配置", demo.openai_configuration),
        ("Anthropic Claude", demo.anthropic_configuration),
        ("Google Gemini", demo.google_gemini_configuration),
        ("本地模型 (Ollama)", demo.ollama_local_models),
        ("Azure OpenAI", demo.azure_openai_configuration),
        ("模型選擇策略", demo.model_selection_strategy),
        ("動態模型切換", demo.dynamic_model_switching),
        ("成本優化", demo.cost_optimization),
    ]

    print("\n執行所有示例...\n")

    for name, func in sections:
        func()

    print("\n" + "="*70)
    print("教程完成！")
    print("="*70)

    print("\n關鍵要點:")
    print("1. Goose 支持多種 LLM 提供商")
    print("2. 根據任務選擇合適的模型")
    print("3. 本地模型適合隱私敏感場景")
    print("4. 動態切換模型優化性價比")
    print("5. 實施成本控制策略")

    print("\n下一步: 閱讀 08_工作流自動化.py")


if __name__ == "__main__":
    main()
