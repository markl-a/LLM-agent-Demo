"""
DSPy Optimizer 優化範例
======================

本範例展示如何使用 DSPy 的優化器來改進提示。

優化器類型：
1. BootstrapFewShot - 少樣本學習
2. BootstrapFewShotWithRandomSearch - 隨機搜索
3. MIPRO - 多指令優化
4. BayesianSignatureOptimizer - 貝葉斯優化

安裝依賴：
pip install dspy-ai
"""

import dspy
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# ============================================================
# 配置
# ============================================================

# 配置語言模型
turbo = dspy.OpenAI(model='gpt-3.5-turbo')
dspy.settings.configure(lm=turbo)


# ============================================================
# 基本 Signature 和 Module
# ============================================================

class QASignature(dspy.Signature):
    """回答問題的簽名"""
    question = dspy.InputField(desc="用戶問題")
    context = dspy.InputField(desc="相關背景資料")
    answer = dspy.OutputField(desc="詳細準確的回答")


class QAModule(dspy.Module):
    """問答模組"""

    def __init__(self):
        super().__init__()
        self.generate_answer = dspy.ChainOfThought(QASignature)

    def forward(self, question: str, context: str):
        return self.generate_answer(question=question, context=context)


# ============================================================
# 1. BootstrapFewShot 優化器
# ============================================================

BOOTSTRAP_EXAMPLE = '''
from dspy.teleprompt import BootstrapFewShot

# 定義訓練數據
trainset = [
    dspy.Example(
        question="什麼是機器學習？",
        context="機器學習是人工智能的一個分支...",
        answer="機器學習是讓計算機從數據中自動學習和改進的技術..."
    ).with_inputs("question", "context"),
    # 更多訓練樣本...
]

# 定義評估指標
def qa_metric(gold, pred, trace=None):
    """評估答案質量"""
    # 檢查關鍵詞
    keywords = gold.answer.lower().split()[:5]
    pred_lower = pred.answer.lower()
    matches = sum(1 for kw in keywords if kw in pred_lower)
    return matches / len(keywords) if keywords else 0

# 創建優化器
optimizer = BootstrapFewShot(
    metric=qa_metric,
    max_bootstrapped_demos=4,  # 最多 4 個示範
    max_labeled_demos=16,      # 最多 16 個標記示範
    max_rounds=1               # 優化輪數
)

# 編譯優化
compiled_qa = optimizer.compile(QAModule(), trainset=trainset)

# 使用優化後的模組
result = compiled_qa(
    question="什麼是深度學習？",
    context="深度學習是機器學習的一個子領域..."
)
print(result.answer)
'''


# ============================================================
# 2. BootstrapFewShotWithRandomSearch 優化器
# ============================================================

RANDOM_SEARCH_EXAMPLE = '''
from dspy.teleprompt import BootstrapFewShotWithRandomSearch

# 訓練集和驗證集
trainset = [...]  # 訓練數據
valset = [...]    # 驗證數據

# 創建優化器
optimizer = BootstrapFewShotWithRandomSearch(
    metric=qa_metric,
    max_bootstrapped_demos=8,
    max_labeled_demos=8,
    num_candidate_programs=10,  # 候選程序數量
    num_threads=4               # 並行線程數
)

# 編譯優化
compiled_qa = optimizer.compile(
    QAModule(),
    trainset=trainset,
    valset=valset
)

# 查看最佳配置
print("最佳 demos:", compiled_qa.demos)
'''


# ============================================================
# 3. MIPRO 優化器
# ============================================================

MIPRO_EXAMPLE = '''
from dspy.teleprompt import MIPRO

# 創建 MIPRO 優化器
optimizer = MIPRO(
    metric=qa_metric,
    num_candidates=10,           # 候選數量
    init_temperature=1.0,        # 初始溫度
    prompt_model=turbo,          # 提示生成模型
    task_model=turbo,            # 任務執行模型
    verbose=True
)

# 編譯優化
compiled_qa = optimizer.compile(
    QAModule(),
    trainset=trainset,
    num_batches=10,              # 批次數量
    max_bootstrapped_demos=3,
    max_labeled_demos=5,
    eval_kwargs=dict(num_threads=4)
)

# MIPRO 會自動優化：
# 1. 指令文本
# 2. 示範選擇
# 3. 示範順序
'''


# ============================================================
# 4. 自定義評估指標
# ============================================================

class CustomMetrics:
    """自定義評估指標集合"""

    @staticmethod
    def exact_match(gold, pred, trace=None):
        """精確匹配"""
        return gold.answer.strip().lower() == pred.answer.strip().lower()

    @staticmethod
    def f1_score(gold, pred, trace=None):
        """F1 分數"""
        gold_tokens = set(gold.answer.lower().split())
        pred_tokens = set(pred.answer.lower().split())

        if not gold_tokens or not pred_tokens:
            return 0.0

        common = gold_tokens & pred_tokens
        precision = len(common) / len(pred_tokens)
        recall = len(common) / len(gold_tokens)

        if precision + recall == 0:
            return 0.0

        return 2 * precision * recall / (precision + recall)

    @staticmethod
    def semantic_similarity(gold, pred, trace=None):
        """語義相似度（需要嵌入模型）"""
        # 簡化版本：使用詞重疊
        gold_words = set(gold.answer.lower().split())
        pred_words = set(pred.answer.lower().split())

        if not gold_words:
            return 0.0

        overlap = len(gold_words & pred_words)
        return overlap / len(gold_words)

    @staticmethod
    def combined_metric(gold, pred, trace=None):
        """組合指標"""
        f1 = CustomMetrics.f1_score(gold, pred, trace)
        semantic = CustomMetrics.semantic_similarity(gold, pred, trace)

        # 加權組合
        return 0.5 * f1 + 0.5 * semantic


# ============================================================
# 5. 優化工作流程
# ============================================================

@dataclass
class OptimizationConfig:
    """優化配置"""
    optimizer_type: str = "bootstrap"
    max_demos: int = 4
    num_candidates: int = 10
    num_threads: int = 4
    metric: str = "f1"


class OptimizationPipeline:
    """優化流水線"""

    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.metrics = {
            "exact": CustomMetrics.exact_match,
            "f1": CustomMetrics.f1_score,
            "semantic": CustomMetrics.semantic_similarity,
            "combined": CustomMetrics.combined_metric
        }

    def get_optimizer(self):
        """獲取優化器"""
        metric = self.metrics.get(self.config.metric, CustomMetrics.f1_score)

        if self.config.optimizer_type == "bootstrap":
            from dspy.teleprompt import BootstrapFewShot
            return BootstrapFewShot(
                metric=metric,
                max_bootstrapped_demos=self.config.max_demos
            )
        elif self.config.optimizer_type == "random_search":
            from dspy.teleprompt import BootstrapFewShotWithRandomSearch
            return BootstrapFewShotWithRandomSearch(
                metric=metric,
                max_bootstrapped_demos=self.config.max_demos,
                num_candidate_programs=self.config.num_candidates,
                num_threads=self.config.num_threads
            )
        else:
            raise ValueError(f"Unknown optimizer: {self.config.optimizer_type}")

    def optimize(self, module, trainset, valset=None):
        """執行優化"""
        optimizer = self.get_optimizer()

        if valset:
            return optimizer.compile(module, trainset=trainset, valset=valset)
        return optimizer.compile(module, trainset=trainset)


# ============================================================
# 6. 保存和加載優化結果
# ============================================================

SAVE_LOAD_EXAMPLE = '''
import json

# 保存優化後的模組
def save_optimized_module(module, path):
    """保存優化後的模組"""
    state = {
        "demos": module.demos if hasattr(module, "demos") else [],
        "config": {
            "num_demos": len(module.demos) if hasattr(module, "demos") else 0
        }
    }
    with open(path, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"模組已保存到 {path}")

# 加載優化後的模組
def load_optimized_module(module_class, path):
    """加載優化後的模組"""
    with open(path, "r") as f:
        state = json.load(f)

    module = module_class()
    if "demos" in state:
        module.demos = state["demos"]

    return module

# 使用示例
save_optimized_module(compiled_qa, "optimized_qa.json")
loaded_qa = load_optimized_module(QAModule, "optimized_qa.json")
'''


# ============================================================
# 使用範例
# ============================================================

def example_bootstrap():
    """範例 1: BootstrapFewShot"""
    print("=" * 50)
    print("範例 1: BootstrapFewShot 優化器")
    print("=" * 50)
    print(BOOTSTRAP_EXAMPLE)


def example_random_search():
    """範例 2: RandomSearch"""
    print("\n" + "=" * 50)
    print("範例 2: BootstrapFewShotWithRandomSearch 優化器")
    print("=" * 50)
    print(RANDOM_SEARCH_EXAMPLE)


def example_mipro():
    """範例 3: MIPRO"""
    print("\n" + "=" * 50)
    print("範例 3: MIPRO 優化器")
    print("=" * 50)
    print(MIPRO_EXAMPLE)


def example_metrics():
    """範例 4: 自定義評估指標"""
    print("\n" + "=" * 50)
    print("範例 4: 自定義評估指標")
    print("=" * 50)

    # 模擬數據
    @dataclass
    class MockExample:
        answer: str

    gold = MockExample(answer="機器學習是一種讓計算機自動學習的技術")
    pred = MockExample(answer="機器學習是計算機從數據中學習的方法")

    print(f"Gold: {gold.answer}")
    print(f"Pred: {pred.answer}")
    print(f"\nExact Match: {CustomMetrics.exact_match(gold, pred)}")
    print(f"F1 Score: {CustomMetrics.f1_score(gold, pred):.4f}")
    print(f"Semantic: {CustomMetrics.semantic_similarity(gold, pred):.4f}")
    print(f"Combined: {CustomMetrics.combined_metric(gold, pred):.4f}")


def example_pipeline():
    """範例 5: 優化流水線"""
    print("\n" + "=" * 50)
    print("範例 5: 優化流水線")
    print("=" * 50)

    config = OptimizationConfig(
        optimizer_type="bootstrap",
        max_demos=4,
        metric="combined"
    )

    print(f"優化配置:")
    print(f"  - 優化器類型: {config.optimizer_type}")
    print(f"  - 最大示範數: {config.max_demos}")
    print(f"  - 評估指標: {config.metric}")
    print(f"  - 候選數量: {config.num_candidates}")


def example_save_load():
    """範例 6: 保存和加載"""
    print("\n" + "=" * 50)
    print("範例 6: 保存和加載優化結果")
    print("=" * 50)
    print(SAVE_LOAD_EXAMPLE)


if __name__ == "__main__":
    print("DSPy Optimizer 優化範例\n")
    example_bootstrap()
    example_random_search()
    example_mipro()
    example_metrics()
    example_pipeline()
    example_save_load()
