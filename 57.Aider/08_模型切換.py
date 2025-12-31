"""
Aider 模型切換功能
==================

本範例展示 Aider 支援的多種 AI 模型及切換方法，包括：
- OpenAI 模型（GPT-4, GPT-3.5）
- Anthropic 模型（Claude）
- Google 模型（Gemini）
- 本地模型（Ollama）
- 自定義 API 端點

作者：AI Agent Demo
日期：2025-12-31
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json


class ModelProvider(Enum):
    """AI 模型提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    AZURE = "azure"
    CUSTOM = "custom"


@dataclass
class ModelConfig:
    """
    模型配置

    包含模型的詳細配置資訊。
    """
    name: str
    provider: ModelProvider
    max_tokens: int
    cost_per_1k_input: float  # 每 1K input tokens 的成本
    cost_per_1k_output: float  # 每 1K output tokens 的成本
    supports_function_calling: bool = True
    supports_vision: bool = False
    context_window: int = 4096

    def __str__(self) -> str:
        return f"{self.name} ({self.provider.value})"


class AiderModelManager:
    """
    Aider 模型管理器

    管理和切換不同的 AI 模型。
    """

    # 預定義的模型配置
    MODELS: Dict[str, ModelConfig] = {
        # OpenAI 模型
        "gpt-4-turbo": ModelConfig(
            name="gpt-4-turbo",
            provider=ModelProvider.OPENAI,
            max_tokens=4096,
            cost_per_1k_input=0.01,
            cost_per_1k_output=0.03,
            context_window=128000,
            supports_vision=True
        ),
        "gpt-4": ModelConfig(
            name="gpt-4",
            provider=ModelProvider.OPENAI,
            max_tokens=8192,
            cost_per_1k_input=0.03,
            cost_per_1k_output=0.06,
            context_window=8192
        ),
        "gpt-3.5-turbo": ModelConfig(
            name="gpt-3.5-turbo",
            provider=ModelProvider.OPENAI,
            max_tokens=4096,
            cost_per_1k_input=0.0005,
            cost_per_1k_output=0.0015,
            context_window=16385
        ),

        # Anthropic 模型
        "claude-3-5-sonnet-20241022": ModelConfig(
            name="claude-3-5-sonnet-20241022",
            provider=ModelProvider.ANTHROPIC,
            max_tokens=8192,
            cost_per_1k_input=0.003,
            cost_per_1k_output=0.015,
            context_window=200000,
            supports_vision=True
        ),
        "claude-3-opus-20240229": ModelConfig(
            name="claude-3-opus-20240229",
            provider=ModelProvider.ANTHROPIC,
            max_tokens=4096,
            cost_per_1k_input=0.015,
            cost_per_1k_output=0.075,
            context_window=200000,
            supports_vision=True
        ),

        # Google 模型
        "gemini-pro": ModelConfig(
            name="gemini-pro",
            provider=ModelProvider.GOOGLE,
            max_tokens=2048,
            cost_per_1k_input=0.00025,
            cost_per_1k_output=0.0005,
            context_window=32000
        ),

        # 本地模型（Ollama）
        "ollama/codellama": ModelConfig(
            name="ollama/codellama",
            provider=ModelProvider.OLLAMA,
            max_tokens=2048,
            cost_per_1k_input=0.0,
            cost_per_1k_output=0.0,
            context_window=4096
        ),
    }

    def __init__(self, default_model: str = "gpt-4-turbo"):
        """
        初始化模型管理器

        Args:
            default_model: 默認模型名稱
        """
        self.current_model = default_model
        self.usage_stats: Dict[str, Dict] = {}

    @staticmethod
    def list_available_models() -> None:
        """列出所有可用的模型"""
        print("\n" + "=" * 80)
        print("可用的 AI 模型")
        print("=" * 80)

        print("\n## OpenAI 模型")
        print("-" * 80)
        print(f"{'模型名稱':<30} {'上下文窗口':<15} {'成本 (input/output)':<25}")
        print("-" * 80)

        for name, config in AiderModelManager.MODELS.items():
            if config.provider == ModelProvider.OPENAI:
                cost_info = f"${config.cost_per_1k_input:.4f}/${config.cost_per_1k_output:.4f}"
                print(f"{name:<30} {config.context_window:<15,} {cost_info:<25}")

        print("\n## Anthropic 模型 (Claude)")
        print("-" * 80)
        print(f"{'模型名稱':<30} {'上下文窗口':<15} {'成本 (input/output)':<25}")
        print("-" * 80)

        for name, config in AiderModelManager.MODELS.items():
            if config.provider == ModelProvider.ANTHROPIC:
                cost_info = f"${config.cost_per_1k_input:.4f}/${config.cost_per_1k_output:.4f}"
                print(f"{name:<30} {config.context_window:<15,} {cost_info:<25}")

        print("\n## Google 模型")
        print("-" * 80)

        for name, config in AiderModelManager.MODELS.items():
            if config.provider == ModelProvider.GOOGLE:
                cost_info = f"${config.cost_per_1k_input:.4f}/${config.cost_per_1k_output:.4f}"
                print(f"{name:<30} {config.context_window:<15,} {cost_info:<25}")

        print("\n## 本地模型 (Ollama)")
        print("-" * 80)

        for name, config in AiderModelManager.MODELS.items():
            if config.provider == ModelProvider.OLLAMA:
                print(f"{name:<30} {config.context_window:<15,} {'免費':<25}")

    @staticmethod
    def demonstrate_model_switching():
        """
        演示模型切換

        展示如何在 Aider 中切換不同的模型。
        """
        print("\n" + "=" * 80)
        print("模型切換指南")
        print("=" * 80)

        print("""
## 1. 啟動時指定模型

### 使用 OpenAI GPT-4

```bash
aider --model gpt-4-turbo
```

### 使用 Claude 3.5 Sonnet

```bash
# 設置 API 金鑰
export ANTHROPIC_API_KEY="your-api-key"

# 啟動 Aider
aider --model claude-3-5-sonnet-20241022
```

### 使用 Google Gemini

```bash
export GOOGLE_API_KEY="your-api-key"
aider --model gemini-pro
```

### 使用本地模型 (Ollama)

```bash
# 首先啟動 Ollama
ollama serve

# 下載模型
ollama pull codellama

# 使用 Aider
aider --model ollama/codellama
```

## 2. 會話中切換模型

在 Aider 會話中動態切換模型：

```bash
$ aider

> /model gpt-4-turbo
Switched to gpt-4-turbo

> 請實現一個複雜的算法
# 使用 GPT-4 處理複雜任務

> /model gpt-3.5-turbo
Switched to gpt-3.5-turbo

> 請添加一些簡單的註釋
# 使用 GPT-3.5 處理簡單任務（節省成本）
```

## 3. 雙模型模式

使用兩個模型協作（架構師 + 編輯器）：

```bash
# 架構師模型用於規劃，編輯器模型用於實現
aider --model gpt-4-turbo --editor-model gpt-3.5-turbo

# 或使用 Claude 作為架構師
aider --model claude-3-5-sonnet-20241022 --editor-model gpt-3.5-turbo
```

工作流程：
1. 架構師模型分析需求並規劃
2. 編輯器模型執行具體修改
3. 成本優化：複雜思考用昂貴模型，簡單編輯用便宜模型

## 4. 根據任務選擇模型

### 複雜算法和架構設計
```bash
aider --model gpt-4-turbo
aider --model claude-3-opus-20240229
```

推薦理由：
✓ 更強的推理能力
✓ 更好的代碼品質
✓ 適合複雜問題

### 日常開發和重構
```bash
aider --model gpt-4-turbo
aider --model claude-3-5-sonnet-20241022
```

推薦理由：
✓ 性價比高
✓ 速度快
✓ 足夠的能力

### 簡單任務和註釋
```bash
aider --model gpt-3.5-turbo
```

推薦理由：
✓ 成本低
✓ 速度快
✓ 能力足夠

### 離線開發
```bash
aider --model ollama/codellama
aider --model ollama/deepseek-coder
```

推薦理由：
✓ 完全免費
✓ 隱私保護
✓ 無需網路

## 5. 模型特性比較

### 上下文窗口

**超大上下文 (200K tokens):**
- Claude 3.5 Sonnet
- Claude 3 Opus

適合：處理大型代碼庫

**大上下文 (128K tokens):**
- GPT-4 Turbo

**標準上下文 (8K-32K tokens):**
- GPT-4
- GPT-3.5 Turbo
- Gemini Pro

### 代碼生成質量

**最佳:**
- GPT-4 Turbo
- Claude 3.5 Sonnet
- Claude 3 Opus

**良好:**
- GPT-3.5 Turbo
- Gemini Pro

**基本:**
- Ollama 本地模型

### 成本效益

**最經濟:**
- Ollama（免費）
- Gemini Pro
- GPT-3.5 Turbo

**中等:**
- Claude 3.5 Sonnet
- GPT-4 Turbo

**昂貴:**
- GPT-4
- Claude 3 Opus

## 6. API 配置

### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_API_BASE="https://api.openai.com/v1"  # 可選
```

### Anthropic

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Google

```bash
export GOOGLE_API_KEY="..."
```

### Azure OpenAI

```bash
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment"

aider --model azure/gpt-4
```

### 自定義 API

```bash
export OPENAI_API_KEY="your-key"
export OPENAI_API_BASE="https://your-custom-endpoint.com/v1"

aider --model custom/your-model
```

## 7. 配置文件

創建 `.aider.models.yml`:

```yaml
models:
  # 默認模型
  default: gpt-4-turbo

  # 按任務類型選擇模型
  task_models:
    complex: gpt-4-turbo
    standard: claude-3-5-sonnet-20241022
    simple: gpt-3.5-turbo
    offline: ollama/codellama

  # 雙模型配置
  architect: gpt-4-turbo
  editor: gpt-3.5-turbo

  # API 設置
  api:
    openai:
      base_url: "https://api.openai.com/v1"
      timeout: 60
    anthropic:
      timeout: 120
```

## 8. 成本追蹤

在配置中啟用成本追蹤：

```bash
aider --show-costs

# 會話中查看成本
> /costs

Session costs:
- Input tokens: 12,450 ($0.12)
- Output tokens: 3,280 ($0.10)
- Total: $0.22
```

## 9. 模型性能建議

### 開發階段

**原型開發:**
- 使用 GPT-3.5 Turbo（快速迭代）

**功能實現:**
- 使用 GPT-4 Turbo 或 Claude 3.5 Sonnet

**代碼審查:**
- 使用 GPT-4 Turbo（更嚴格）

### 項目類型

**小型項目 (<1000 行):**
- GPT-3.5 Turbo 足夠

**中型項目 (1000-10000 行):**
- Claude 3.5 Sonnet（大上下文）

**大型項目 (>10000 行):**
- Claude 3 Opus（最大上下文）

**企業項目:**
- Azure OpenAI（合規性）
        """)

    @staticmethod
    def demonstrate_cost_optimization():
        """
        演示成本優化策略
        """
        print("\n" + "=" * 80)
        print("成本優化策略")
        print("=" * 80)

        print("""
## 1. 智能模型選擇

### 按任務複雜度選擇

```python
# 複雜算法設計
$ aider --model gpt-4-turbo algorithm.py
> 請設計一個高效的圖遍歷算法

# 簡單代碼修改
$ aider --model gpt-3.5-turbo utils.py
> 請添加類型註解

# 離線重構
$ aider --model ollama/codellama refactor.py
> 請重命名這些變數
```

### 成本對比

假設處理 10K input tokens, 5K output tokens:

**GPT-4:**
- Input: 10K × $0.03 = $0.30
- Output: 5K × $0.06 = $0.30
- Total: $0.60

**GPT-3.5 Turbo:**
- Input: 10K × $0.0005 = $0.005
- Output: 5K × $0.0015 = $0.0075
- Total: $0.0125

**節省: $0.5875 (98%)**

## 2. 雙模型策略

使用昂貴模型規劃，便宜模型執行：

```bash
aider --model gpt-4-turbo --editor-model gpt-3.5-turbo

# GPT-4 分析和規劃（少量 tokens）
> 請分析這個系統並提出重構方案

# GPT-3.5 執行具體修改（大量 tokens）
> 根據方案執行重構
```

預計節省: 40-60%

## 3. 上下文優化

減少發送的上下文：

```bash
# 只添加必要的文件
aider specific_file.py

# 而不是
aider src/**/*.py  # 會消耗大量 tokens
```

## 4. 批處理操作

將多個小任務合併：

```bash
# 低效（多次 API 調用）
> 添加類型註解
> 添加文檔字符串
> 格式化代碼

# 高效（一次 API 調用）
> 請執行以下操作：
> 1. 添加類型註解
> 2. 添加文檔字符串
> 3. 格式化代碼
```

## 5. 使用本地模型

對於隱私不敏感的任務：

```bash
# 完全免費
ollama pull codellama
aider --model ollama/codellama

# 適合：
# - 重構
# - 添加註釋
# - 簡單功能實現
```

## 6. 成本監控

設置預算警告：

```yaml
# .aider.yml
costs:
  daily_limit: 10.0  # USD
  warn_at: 0.8  # 80%
  stop_at: 1.0  # 100%
```

## 7. 緩存策略

Aider 自動緩存：
- Repository map
- 文件內容
- 對話歷史

不要頻繁重啟會話。

## 8. 實際案例

### 案例 1: 功能開發

**需求:** 實現用戶認證系統

**策略:**
1. 使用 GPT-4 設計架構（$0.10）
2. 使用 GPT-3.5 實現代碼（$0.15）
3. 使用 GPT-3.5 生成測試（$0.10）

**總成本:** $0.35

如果全用 GPT-4: $2.50
**節省:** $2.15 (86%)

### 案例 2: 代碼重構

**需求:** 重構 5000 行代碼

**策略:**
1. 使用 Claude 3.5 Sonnet（大上下文）
2. 分批處理（每次 1000 行）
3. 使用 repository map 減少重複

**總成本:** $1.50

如果使用 GPT-4: $4.50
**節省:** $3.00 (67%)
        """)

    def estimate_cost(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int
    ) -> Dict[str, float]:
        """
        估算使用成本

        Args:
            model_name: 模型名稱
            input_tokens: 輸入 token 數
            output_tokens: 輸出 token 數

        Returns:
            成本詳情字典
        """
        if model_name not in self.MODELS:
            return {"error": "未知模型"}

        config = self.MODELS[model_name]

        input_cost = (input_tokens / 1000) * config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * config.cost_per_1k_output
        total_cost = input_cost + output_cost

        return {
            "model": model_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": round(input_cost, 4),
            "output_cost": round(output_cost, 4),
            "total_cost": round(total_cost, 4)
        }

    def compare_models(
        self,
        input_tokens: int,
        output_tokens: int
    ) -> None:
        """
        比較不同模型的成本

        Args:
            input_tokens: 輸入 token 數
            output_tokens: 輸出 token 數
        """
        print(f"\n成本比較 ({input_tokens:,} input + {output_tokens:,} output tokens)")
        print("=" * 60)
        print(f"{'模型':<35} {'成本':<15}")
        print("-" * 60)

        costs = []
        for model_name in self.MODELS:
            cost = self.estimate_cost(model_name, input_tokens, output_tokens)
            costs.append((model_name, cost["total_cost"]))

        # 排序
        costs.sort(key=lambda x: x[1])

        for model_name, total_cost in costs:
            print(f"{model_name:<35} ${total_cost:<14.4f}")


def main():
    """
    主函數

    運行模型切換演示。
    """
    print("=" * 80)
    print("Aider 模型切換與優化")
    print("=" * 80)

    manager = AiderModelManager()

    # 列出可用模型
    manager.list_available_models()

    # 演示模型切換
    manager.demonstrate_model_switching()

    # 演示成本優化
    manager.demonstrate_cost_optimization()

    # 比較成本
    print("\n")
    manager.compare_models(input_tokens=10000, output_tokens=5000)


if __name__ == "__main__":
    main()
