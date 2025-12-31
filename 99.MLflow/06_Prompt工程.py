"""
MLflow Prompt 工程示例 - Prompt 優化和追蹤

主要功能：Prompt 模板、版本比較、A/B 測試、最佳 Prompt 選擇
作者: MLflow Team | 日期: 2025-01-01
"""

import mlflow
import numpy as np


def prompt_template_management():
    """Prompt 模板管理"""
    print("\n" + "="*60)
    print("Prompt 模板管理")
    print("="*60)

    templates = {
        "basic": "回答問題: {question}",
        "detailed": "請詳細回答以下問題，包含例子:\n問題: {question}",
        "structured": "請按以下格式回答:\n1. 定義\n2. 例子\n3. 應用\n\n問題: {question}"
    }

    for name, template in templates.items():
        with mlflow.start_run(run_name=f"template-{name}"):
            mlflow.log_param("template_name", name)
            mlflow.log_param("template", template)

            # 測試問題
            question = "什麼是深度學習？"
            prompt = template.format(question=question)

            mlflow.log_text(prompt, "generated_prompt.txt")

            print(f"✅ 模板 '{name}' 已記錄")


def prompt_ab_testing():
    """Prompt A/B 測試"""
    print("\n" + "="*60)
    print("Prompt A/B 測試")
    print("="*60)

    variants = {
        "A": "簡潔的提示",
        "B": "詳細的提示帶上下文"
    }

    for variant, prompt in variants.items():
        with mlflow.start_run(run_name=f"variant-{variant}"):
            mlflow.log_param("variant", variant)
            mlflow.log_param("prompt", prompt)

            # 模擬性能指標
            response_quality = 0.7 + np.random.random() * 0.3
            user_rating = np.random.uniform(3.5, 5.0)
            tokens_used = len(prompt.split()) * 15

            mlflow.log_metric("response_quality", response_quality)
            mlflow.log_metric("user_rating", user_rating)
            mlflow.log_metric("tokens_used", tokens_used)
            mlflow.log_metric("cost_per_request", tokens_used * 0.00002)

            print(f"  Variant {variant}: quality={response_quality:.2f}, rating={user_rating:.2f}")


def prompt_optimization_tracking():
    """Prompt 優化追蹤"""
    print("\n" + "="*60)
    print("Prompt 優化追蹤")
    print("="*60)

    iterations = 5

    for i in range(iterations):
        with mlflow.start_run(run_name=f"optimization-iter-{i+1}"):
            mlflow.log_param("iteration", i+1)

            # 模擬優化過程
            performance = 0.5 + (i / iterations) * 0.4 + np.random.random() * 0.05

            mlflow.log_metric("performance", performance)

            print(f"  迭代 {i+1}: performance={performance:.2f}")


def main():
    """主函數"""
    print("\n" + "="*70)
    print("MLflow Prompt 工程示例")
    print("="*70)

    try:
        prompt_template_management()
        prompt_ab_testing()
        prompt_optimization_tracking()
        print("\n✅ 完成！")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
