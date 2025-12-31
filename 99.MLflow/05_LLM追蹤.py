"""
MLflow LLM 追蹤示例 - 大型語言模型追蹤

主要功能：LLM 推理追蹤、Prompt 記錄、Token 統計、評估
作者: MLflow Team | 日期: 2025-01-01
"""

import mlflow
import numpy as np


def llm_inference_tracking():
    """LLM 推理追蹤"""
    print("\n" + "="*60)
    print("LLM 推理追蹤")
    print("="*60)

    with mlflow.start_run(run_name="llm-inference"):
        # 模擬 LLM 推理
        prompt = "什麼是機器學習？"
        response = "機器學習是人工智能的一個分支..."

        # 記錄 Prompt 和響應
        mlflow.log_param("prompt", prompt)
        mlflow.log_param("max_tokens", 150)
        mlflow.log_param("temperature", 0.7)
        mlflow.log_param("model", "gpt-3.5-turbo")

        # 記錄 Token 使用
        prompt_tokens = 10
        completion_tokens = 50
        total_tokens = prompt_tokens + completion_tokens

        mlflow.log_metric("prompt_tokens", prompt_tokens)
        mlflow.log_metric("completion_tokens", completion_tokens)
        mlflow.log_metric("total_tokens", total_tokens)

        # 計算成本
        cost = (prompt_tokens * 0.0015 + completion_tokens * 0.002) / 1000

        mlflow.log_metric("cost_usd", cost)

        # 記錄響應
        mlflow.log_text(response, "response.txt")

        print(f"✅ LLM 推理已追蹤")
        print(f"   Tokens: {total_tokens}")
        print(f"   成本: ${cost:.6f}")


def prompt_engineering_tracking():
    """Prompt 工程追蹤"""
    print("\n" + "="*60)
    print("Prompt 工程追蹤")
    print("="*60)

    prompts = [
        "簡單提示",
        "詳細的結構化提示",
        "帶示例的提示"
    ]

    for i, prompt in enumerate(prompts):
        with mlflow.start_run(run_name=f"prompt-v{i+1}"):
            mlflow.log_param("prompt_version", f"v{i+1}")
            mlflow.log_param("prompt", prompt)

            # 模擬質量分數
            quality = 0.7 + np.random.random() * 0.3

            mlflow.log_metric("quality_score", quality)
            mlflow.log_metric("user_satisfaction", np.random.randint(1, 6))

            print(f"  Prompt v{i+1}: quality={quality:.2f}")


def llm_evaluation():
    """LLM 評估"""
    print("\n" + "="*60)
    print("LLM 評估")
    print("="*60)

    with mlflow.start_run(run_name="llm-evaluation"):
        # 評估指標
        metrics = {
            "bleu_score": 0.85,
            "rouge_score": 0.78,
            "perplexity": 15.3,
            "coherence": 4.2,
            "relevance": 4.5
        }

        mlflow.log_metrics(metrics)

        print("✅ LLM 評估指標已記錄")
        for key, value in metrics.items():
            print(f"   {key}: {value}")


def main():
    """主函數"""
    print("\n" + "="*70)
    print("MLflow LLM 追蹤示例")
    print("="*70)

    try:
        llm_inference_tracking()
        prompt_engineering_tracking()
        llm_evaluation()
        print("\n✅ 完成！")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
