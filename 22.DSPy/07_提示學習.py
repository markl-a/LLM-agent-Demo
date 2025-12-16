"""
DSPy 提示學習範例
================

本範例展示 DSPy 中的提示學習技術。

提示學習類型：
1. 自動提示優化
2. 指令調優
3. 上下文學習
4. 元提示

安裝依賴：
pip install dspy-ai
"""

import dspy
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

# ============================================================
# 配置
# ============================================================

turbo = dspy.OpenAI(model='gpt-3.5-turbo')
dspy.settings.configure(lm=turbo)


# ============================================================
# 1. 自動提示優化
# ============================================================

class AutoPromptSignature(dspy.Signature):
    """自動優化的提示簽名"""
    instruction = dspy.InputField(desc="任務指令")
    input_text = dspy.InputField(desc="輸入文本")
    output = dspy.OutputField(desc="處理後的輸出")


class AutoPromptModule(dspy.Module):
    """自動提示優化模組"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(AutoPromptSignature)

    def forward(self, instruction: str, input_text: str):
        return self.predictor(instruction=instruction, input_text=input_text)


AUTO_PROMPT_EXAMPLE = '''
from dspy.teleprompt import BootstrapFewShot

# 訓練數據
trainset = [
    dspy.Example(
        instruction="總結以下文本",
        input_text="人工智能正在改變各行各業...",
        output="AI 正在推動產業變革"
    ).with_inputs("instruction", "input_text"),
    # 更多示例...
]

# 評估指標
def quality_metric(gold, pred, trace=None):
    # 檢查輸出質量
    if not pred.output:
        return 0.0
    # 長度合理性
    if 10 <= len(pred.output) <= 500:
        return 1.0
    return 0.5

# 優化
optimizer = BootstrapFewShot(metric=quality_metric)
optimized = optimizer.compile(AutoPromptModule(), trainset=trainset)
'''


# ============================================================
# 2. 指令調優
# ============================================================

class InstructionTuner:
    """指令調優器"""

    def __init__(self, base_instructions: List[str]):
        self.base_instructions = base_instructions
        self.instruction_scores = {}

    def generate_variations(self, instruction: str, num_variations: int = 5) -> List[str]:
        """生成指令變體"""
        variations = [instruction]

        # 簡單變體生成策略
        templates = [
            "請{action}",
            "你需要{action}",
            "{action}，確保準確",
            "仔細{action}",
            "認真{action}，並提供詳細信息"
        ]

        # 提取動作
        action = instruction.replace("請", "").replace("你需要", "").strip()

        for template in templates[:num_variations-1]:
            variation = template.format(action=action)
            if variation not in variations:
                variations.append(variation)

        return variations

    def evaluate_instruction(
        self,
        instruction: str,
        module: dspy.Module,
        dataset: List[dspy.Example],
        metric: callable
    ) -> float:
        """評估指令效果"""
        scores = []

        for example in dataset:
            try:
                # 替換指令並執行
                pred = module(instruction=instruction, **example.inputs())
                score = metric(example, pred)
                scores.append(score)
            except Exception:
                scores.append(0.0)

        return sum(scores) / len(scores) if scores else 0.0

    def tune(
        self,
        module: dspy.Module,
        dataset: List[dspy.Example],
        metric: callable
    ) -> str:
        """調優指令"""
        best_instruction = None
        best_score = 0.0

        for base_instruction in self.base_instructions:
            variations = self.generate_variations(base_instruction)

            for instruction in variations:
                score = self.evaluate_instruction(instruction, module, dataset, metric)
                self.instruction_scores[instruction] = score

                if score > best_score:
                    best_score = score
                    best_instruction = instruction

        return best_instruction


# ============================================================
# 3. 上下文學習 (In-Context Learning)
# ============================================================

class ICLSignature(dspy.Signature):
    """上下文學習簽名"""
    examples = dspy.InputField(desc="示範例子")
    query = dspy.InputField(desc="當前查詢")
    response = dspy.OutputField(desc="基於示範的回應")


class InContextLearner(dspy.Module):
    """上下文學習模組"""

    def __init__(self, num_examples: int = 3):
        super().__init__()
        self.num_examples = num_examples
        self.predictor = dspy.Predict(ICLSignature)
        self.example_pool = []

    def add_examples(self, examples: List[Dict[str, str]]):
        """添加示範例子"""
        self.example_pool.extend(examples)

    def select_examples(self, query: str) -> List[Dict[str, str]]:
        """選擇相關示範"""
        if not self.example_pool:
            return []

        # 簡單的相關性選擇
        query_words = set(query.lower().split())
        scored_examples = []

        for ex in self.example_pool:
            ex_words = set(ex.get('input', '').lower().split())
            score = len(query_words & ex_words)
            scored_examples.append((score, ex))

        scored_examples.sort(reverse=True, key=lambda x: x[0])
        return [ex for _, ex in scored_examples[:self.num_examples]]

    def format_examples(self, examples: List[Dict[str, str]]) -> str:
        """格式化示範"""
        formatted = []
        for i, ex in enumerate(examples, 1):
            formatted.append(f"例子 {i}:")
            formatted.append(f"  輸入: {ex.get('input', '')}")
            formatted.append(f"  輸出: {ex.get('output', '')}")
        return "\n".join(formatted)

    def forward(self, query: str):
        examples = self.select_examples(query)
        examples_str = self.format_examples(examples)
        return self.predictor(examples=examples_str, query=query)


# ============================================================
# 4. 元提示 (Meta-Prompting)
# ============================================================

class MetaPromptSignature(dspy.Signature):
    """元提示簽名 - 生成任務特定的提示"""
    task_description = dspy.InputField(desc="任務描述")
    input_format = dspy.InputField(desc="輸入格式說明")
    output_format = dspy.InputField(desc="期望的輸出格式")
    generated_prompt = dspy.OutputField(desc="生成的任務提示")


class MetaPrompter(dspy.Module):
    """元提示生成器"""

    def __init__(self):
        super().__init__()
        self.meta_generator = dspy.ChainOfThought(MetaPromptSignature)

    def generate_prompt(
        self,
        task_description: str,
        input_format: str,
        output_format: str
    ) -> str:
        """生成任務特定的提示"""
        result = self.meta_generator(
            task_description=task_description,
            input_format=input_format,
            output_format=output_format
        )
        return result.generated_prompt


class TaskExecutorSignature(dspy.Signature):
    """任務執行簽名"""
    prompt = dspy.InputField(desc="任務提示")
    input_data = dspy.InputField(desc="輸入數據")
    result = dspy.OutputField(desc="執行結果")


class AdaptiveTaskExecutor(dspy.Module):
    """自適應任務執行器"""

    def __init__(self):
        super().__init__()
        self.meta_prompter = MetaPrompter()
        self.executor = dspy.Predict(TaskExecutorSignature)
        self.prompt_cache = {}

    def forward(
        self,
        task_type: str,
        input_data: str,
        task_description: str = None,
        input_format: str = None,
        output_format: str = None
    ):
        # 檢查緩存
        if task_type in self.prompt_cache:
            prompt = self.prompt_cache[task_type]
        else:
            # 生成新提示
            prompt = self.meta_prompter.generate_prompt(
                task_description=task_description or f"執行 {task_type} 任務",
                input_format=input_format or "文本輸入",
                output_format=output_format or "文本輸出"
            )
            self.prompt_cache[task_type] = prompt

        return self.executor(prompt=prompt, input_data=input_data)


# ============================================================
# 5. 提示模板庫
# ============================================================

class PromptTemplate:
    """提示模板"""

    def __init__(self, template: str, variables: List[str]):
        self.template = template
        self.variables = variables

    def fill(self, **kwargs) -> str:
        """填充模板"""
        result = self.template
        for var in self.variables:
            if var in kwargs:
                result = result.replace(f"{{{var}}}", str(kwargs[var]))
        return result


class PromptLibrary:
    """提示模板庫"""

    def __init__(self):
        self.templates = {}

    def add_template(self, name: str, template: str, variables: List[str]):
        """添加模板"""
        self.templates[name] = PromptTemplate(template, variables)

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """獲取模板"""
        return self.templates.get(name)

    def list_templates(self) -> List[str]:
        """列出所有模板"""
        return list(self.templates.keys())


# 預定義模板
DEFAULT_TEMPLATES = {
    "summarize": {
        "template": "請將以下{text_type}總結成{length}：\n\n{content}",
        "variables": ["text_type", "length", "content"]
    },
    "translate": {
        "template": "請將以下文本從{source_lang}翻譯成{target_lang}：\n\n{content}",
        "variables": ["source_lang", "target_lang", "content"]
    },
    "qa": {
        "template": "根據以下背景資料回答問題。\n\n背景：{context}\n\n問題：{question}",
        "variables": ["context", "question"]
    },
    "classify": {
        "template": "請將以下文本分類到這些類別之一：{categories}\n\n文本：{content}",
        "variables": ["categories", "content"]
    }
}


# ============================================================
# 6. 提示鏈
# ============================================================

class PromptChain:
    """提示鏈 - 組合多個提示步驟"""

    def __init__(self):
        self.steps = []

    def add_step(self, name: str, signature: type, **kwargs):
        """添加步驟"""
        self.steps.append({
            "name": name,
            "signature": signature,
            "kwargs": kwargs
        })

    def build(self) -> dspy.Module:
        """構建鏈式模組"""
        chain = self

        class ChainModule(dspy.Module):
            def __init__(self):
                super().__init__()
                self.predictors = {}
                for step in chain.steps:
                    self.predictors[step["name"]] = dspy.Predict(step["signature"])

            def forward(self, **initial_inputs):
                current_inputs = initial_inputs
                results = {}

                for step in chain.steps:
                    predictor = self.predictors[step["name"]]
                    # 合併輸入
                    step_inputs = {**current_inputs, **step.get("kwargs", {})}
                    result = predictor(**step_inputs)
                    results[step["name"]] = result

                    # 更新輸入
                    for field in dir(result):
                        if not field.startswith('_'):
                            current_inputs[field] = getattr(result, field)

                return results

        return ChainModule()


# ============================================================
# 使用範例
# ============================================================

def example_auto_prompt():
    """範例 1: 自動提示優化"""
    print("=" * 50)
    print("範例 1: 自動提示優化")
    print("=" * 50)
    print(AUTO_PROMPT_EXAMPLE)


def example_instruction_tuning():
    """範例 2: 指令調優"""
    print("\n" + "=" * 50)
    print("範例 2: 指令調優")
    print("=" * 50)

    tuner = InstructionTuner([
        "總結文本",
        "提取關鍵信息",
        "概括主要內容"
    ])

    # 生成變體
    variations = tuner.generate_variations("總結文本", 5)
    print("指令變體:")
    for i, v in enumerate(variations, 1):
        print(f"  {i}. {v}")


def example_icl():
    """範例 3: 上下文學習"""
    print("\n" + "=" * 50)
    print("範例 3: 上下文學習")
    print("=" * 50)

    learner = InContextLearner(num_examples=3)

    # 添加示範
    learner.add_examples([
        {"input": "今天天氣很好", "output": "正面"},
        {"input": "這個產品太差了", "output": "負面"},
        {"input": "還可以吧", "output": "中性"},
        {"input": "我非常滿意", "output": "正面"},
        {"input": "完全不推薦", "output": "負面"}
    ])

    # 選擇相關示範
    query = "這個服務讓我很滿意"
    examples = learner.select_examples(query)
    print(f"查詢: {query}")
    print(f"\n選擇的示範:")
    for ex in examples:
        print(f"  {ex}")


def example_meta_prompting():
    """範例 4: 元提示"""
    print("\n" + "=" * 50)
    print("範例 4: 元提示")
    print("=" * 50)

    print("""
元提示工作流程:
    1. 描述任務類型
    2. 指定輸入/輸出格式
    3. 自動生成最佳提示
    4. 使用生成的提示執行任務

示例:
    meta_prompter = MetaPrompter()
    prompt = meta_prompter.generate_prompt(
        task_description="情感分析",
        input_format="用戶評論文本",
        output_format="正面/負面/中性"
    )
    print(f"生成的提示: {prompt}")
""")


def example_prompt_library():
    """範例 5: 提示模板庫"""
    print("\n" + "=" * 50)
    print("範例 5: 提示模板庫")
    print("=" * 50)

    library = PromptLibrary()

    # 添加模板
    for name, config in DEFAULT_TEMPLATES.items():
        library.add_template(name, config["template"], config["variables"])

    print(f"可用模板: {library.list_templates()}")

    # 使用模板
    template = library.get_template("summarize")
    if template:
        prompt = template.fill(
            text_type="文章",
            length="100字以內",
            content="人工智能正在快速發展..."
        )
        print(f"\n填充後的提示:\n{prompt}")


def example_prompt_chain():
    """範例 6: 提示鏈"""
    print("\n" + "=" * 50)
    print("範例 6: 提示鏈")
    print("=" * 50)

    print("""
提示鏈構建:
    chain = PromptChain()

    # 添加步驟
    chain.add_step("extract", ExtractSignature)
    chain.add_step("analyze", AnalyzeSignature)
    chain.add_step("summarize", SummarizeSignature)

    # 構建並使用
    module = chain.build()
    results = module(input_text="...")

    print(results["extract"])
    print(results["analyze"])
    print(results["summarize"])
""")


if __name__ == "__main__":
    print("DSPy 提示學習範例\n")
    example_auto_prompt()
    example_instruction_tuning()
    example_icl()
    example_meta_prompting()
    example_prompt_library()
    example_prompt_chain()
