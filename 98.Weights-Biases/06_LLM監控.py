"""
Weights & Biases LLM 監控示例

這個示例展示了如何使用 W&B 監控大型語言模型的訓練和推理。
包含 Token 使用追蹤、成本計算、輸入輸出記錄和性能優化。

主要功能：
1. LLM 訓練追蹤
2. Token 使用統計
3. 成本追蹤和優化
4. 輸入輸出樣本記錄
5. 生成質量評估
6. Prompt 工程追蹤
7. 微調監控
8. 推理性能追蹤

作者: W&B Team
日期: 2025-01-01
"""

import wandb
import openai
import time
from typing import List, Dict, Any
import numpy as np


# ============================================================================
# 第一部分:LLM 推理追蹤
# ============================================================================

def llm_inference_tracking():
    """LLM 推理追蹤示例"""
    print("\n" + "="*60)
    print("LLM 推理追蹤")
    print("="*60)

    run = wandb.init(
        project="llm-monitoring",
        name="inference-tracking",
        config={
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 150
        }
    )

    print("\n🤖 開始 LLM 推理...")

    # 模擬多個推理請求
    prompts = [
        "解釋什麼是機器學習",
        "Python 和 JavaScript 的區別",
        "如何優化深度學習模型",
        "什麼是遷移學習",
        "推薦一些數據科學書籍"
    ]

    inference_logs = []

    for i, prompt in enumerate(prompts):
        start_time = time.time()

        # 模擬 API 調用
        # response = openai.ChatCompletion.create(...)

        # 模擬響應
        response_text = f"這是對提示 '{prompt[:20]}...' 的模擬回答"
        prompt_tokens = len(prompt.split()) * 2
        completion_tokens = len(response_text.split()) * 2
        total_tokens = prompt_tokens + completion_tokens

        latency = time.time() - start_time + np.random.random()

        # 計算成本 (假設 GPT-3.5-turbo 價格)
        cost_per_1k_prompt = 0.0015
        cost_per_1k_completion = 0.002

        cost = (prompt_tokens / 1000 * cost_per_1k_prompt +
                completion_tokens / 1000 * cost_per_1k_completion)

        # 記錄詳細指標
        log_data = {
            "request_id": i,
            "prompt_length": len(prompt),
            "response_length": len(response_text),
            "tokens/prompt": prompt_tokens,
            "tokens/completion": completion_tokens,
            "tokens/total": total_tokens,
            "cost_usd": cost,
            "latency_seconds": latency,
            "tokens_per_second": total_tokens / latency
        }

        wandb.log(log_data)

        # 記錄樣本
        inference_logs.append({
            "prompt": prompt,
            "response": response_text,
            **log_data
        })

        print(f"  請求 {i+1}: tokens={total_tokens}, cost=${cost:.6f}, "
              f"latency={latency:.2f}s")

        time.sleep(0.1)

    # 記錄樣本表格
    table = wandb.Table(
        columns=list(inference_logs[0].keys()),
        data=[list(log.values()) for log in inference_logs]
    )

    wandb.log({"inference_samples": table})

    # 記錄匯總統計
    total_tokens = sum(log["tokens/total"] for log in inference_logs)
    total_cost = sum(log["cost_usd"] for log in inference_logs)
    avg_latency = np.mean([log["latency_seconds"] for log in inference_logs])

    wandb.summary["total_tokens"] = total_tokens
    wandb.summary["total_cost_usd"] = total_cost
    wandb.summary["average_latency"] = avg_latency
    wandb.summary["requests_processed"] = len(inference_logs)

    print(f"\n📊 總結:")
    print(f"   總 Tokens: {total_tokens}")
    print(f"   總成本: ${total_cost:.6f}")
    print(f"   平均延遲: {avg_latency:.2f}s")

    wandb.finish()


# ============================================================================
# 第二部分:Prompt 追蹤
# ============================================================================

def prompt_tracking():
    """Prompt 追蹤示例"""
    print("\n" + "="*60)
    print("Prompt 追蹤")
    print("="*60)

    run = wandb.init(
        project="llm-monitoring",
        name="prompt-tracking"
    )

    print("\n📝 測試不同的 Prompts...")

    # 定義多個 prompt 變體
    prompt_variants = {
        "v1_simple": "解釋機器學習",
        "v2_detailed": "請詳細解釋什麼是機器學習，包括其定義和應用",
        "v3_structured": """請按以下格式解釋機器學習:
1. 定義
2. 主要類型
3. 實際應用""",
        "v4_with_context": "你是一個AI教育專家。請解釋機器學習給初學者聽。"
    }

    results = []

    for variant_name, prompt in prompt_variants.items():
        # 模擬 LLM 調用
        response_quality = np.random.random()  # 0-1 的質量分數
        tokens_used = len(prompt.split()) * 15

        result = {
            "variant": variant_name,
            "prompt": prompt,
            "prompt_length": len(prompt),
            "tokens_used": tokens_used,
            "quality_score": response_quality,
            "user_satisfaction": np.random.choice([1, 2, 3, 4, 5])
        }

        results.append(result)

        wandb.log({
            f"prompts/{variant_name}/quality": response_quality,
            f"prompts/{variant_name}/tokens": tokens_used,
            f"prompts/{variant_name}/satisfaction": result["user_satisfaction"]
        })

        print(f"  {variant_name}: quality={response_quality:.2f}, "
              f"tokens={tokens_used}")

    # 記錄 prompt 比較表格
    table = wandb.Table(
        columns=list(results[0].keys()),
        data=[list(r.values()) for r in results]
    )

    wandb.log({"prompt_comparison": table})

    # 找出最佳 prompt
    best_prompt = max(results, key=lambda x: x["quality_score"])

    print(f"\n🏆 最佳 Prompt: {best_prompt['variant']}")
    print(f"   質量分數: {best_prompt['quality_score']:.2f}")

    wandb.summary["best_prompt_variant"] = best_prompt["variant"]
    wandb.summary["best_prompt_quality"] = best_prompt["quality_score"]

    wandb.finish()


# ============================================================================
# 第三部分:成本優化追蹤
# ============================================================================

def cost_optimization_tracking():
    """成本優化追蹤示例"""
    print("\n" + "="*60)
    print("成本優化追蹤")
    print("="*60)

    run = wandb.init(
        project="llm-monitoring",
        name="cost-optimization"
    )

    print("\n💰 追蹤不同配置的成本...")

    # 測試不同的模型配置
    configurations = [
        {"model": "gpt-3.5-turbo", "max_tokens": 100, "cost_per_1k": 0.002},
        {"model": "gpt-3.5-turbo", "max_tokens": 500, "cost_per_1k": 0.002},
        {"model": "gpt-4", "max_tokens": 100, "cost_per_1k": 0.03},
        {"model": "gpt-4", "max_tokens": 500, "cost_per_1k": 0.03},
    ]

    for i, config in enumerate(configurations):
        # 模擬100個請求
        num_requests = 100
        avg_tokens_per_request = config["max_tokens"] * 0.8

        total_tokens = num_requests * avg_tokens_per_request
        total_cost = (total_tokens / 1000) * config["cost_per_1k"]

        # 模擬質量分數
        quality_score = 0.7 + np.random.random() * 0.3

        # 計算性價比
        cost_per_quality_point = total_cost / quality_score

        wandb.log({
            "config_id": i,
            "model": config["model"],
            "max_tokens": config["max_tokens"],
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "quality_score": quality_score,
            "cost_per_quality": cost_per_quality_point,
            "cost_per_request": total_cost / num_requests
        })

        print(f"  配置 {i+1}: {config['model']}, "
              f"max_tokens={config['max_tokens']}, "
              f"cost=${total_cost:.2f}, quality={quality_score:.2f}")

    # 記錄成本趨勢
    for day in range(30):
        daily_requests = 1000 + np.random.randint(-100, 100)
        daily_cost = daily_requests * 0.002

        wandb.log({
            "day": day,
            "daily_requests": daily_requests,
            "daily_cost": daily_cost,
            "cumulative_cost": daily_cost * (day + 1)
        })

    print("\n✅ 成本優化數據已記錄")

    wandb.finish()


# ============================================================================
# 第四部分:LLM 微調監控
# ============================================================================

def finetuning_monitoring():
    """LLM 微調監控示例"""
    print("\n" + "="*60)
    print("LLM 微調監控")
    print("="*60)

    run = wandb.init(
        project="llm-monitoring",
        name="finetuning",
        config={
            "base_model": "gpt-3.5-turbo",
            "training_samples": 1000,
            "epochs": 3,
            "learning_rate": 0.0001
        }
    )

    print("\n🎯 監控微調過程...")

    # 模擬微調過程
    for epoch in range(wandb.config.epochs):
        for step in range(50):
            # 模擬訓練指標
            train_loss = 2.0 * np.exp(-step / 20) + np.random.random() * 0.1
            val_loss = train_loss * 1.1

            # Token 統計
            tokens_processed = (epoch * 50 + step) * 1000

            wandb.log({
                "epoch": epoch,
                "step": step,
                "train_loss": train_loss,
                "val_loss": val_loss,
                "tokens_processed": tokens_processed,
                "learning_rate": wandb.config.learning_rate * (0.95 ** epoch)
            })

        print(f"  Epoch {epoch+1}/{wandb.config.epochs} 完成")

    # 記錄微調後的性能提升
    wandb.summary.update({
        "final_train_loss": train_loss,
        "final_val_loss": val_loss,
        "total_tokens_processed": tokens_processed,
        "performance_improvement": "25%"
    })

    print("✅ 微調監控完成")

    wandb.finish()


# ============================================================================
# 第五部分:生成質量評估
# ============================================================================

def generation_quality_assessment():
    """生成質量評估示例"""
    print("\n" + "="*60)
    print("生成質量評估")
    print("="*60)

    run = wandb.init(
        project="llm-monitoring",
        name="quality-assessment"
    )

    print("\n⭐ 評估生成質量...")

    # 模擬多個生成任務
    tasks = ["summarization", "translation", "question-answering", "code-generation"]

    for task in tasks:
        # 生成多個樣本
        for i in range(10):
            # 模擬質量指標
            metrics = {
                "task": task,
                "sample_id": i,
                "bleu_score": np.random.random() * 100 if task == "translation" else None,
                "rouge_score": np.random.random() if task == "summarization" else None,
                "accuracy": np.random.random() if task == "question-answering" else None,
                "pass_rate": np.random.random() if task == "code-generation" else None,
                "fluency": np.random.uniform(3, 5),  # 1-5 分
                "relevance": np.random.uniform(3, 5),
                "coherence": np.random.uniform(3, 5)
            }

            # 只記錄非 None 的指標
            log_metrics = {k: v for k, v in metrics.items() if v is not None}

            wandb.log(log_metrics)

        avg_fluency = 4.2  # 模擬平均值
        print(f"  {task}: avg_fluency={avg_fluency:.2f}")

    print("✅ 質量評估完成")

    wandb.finish()


# ============================================================================
# 第六部分:實時監控儀表板
# ============================================================================

def realtime_monitoring_dashboard():
    """實時監控儀表板示例"""
    print("\n" + "="*60)
    print("實時監控儀表板")
    print("="*60)

    run = wandb.init(
        project="llm-monitoring",
        name="realtime-dashboard"
    )

    print("\n📊 模擬實時監控...")

    # 模擬一段時間的實時數據
    for minute in range(60):
        # 系統指標
        cpu_usage = 50 + np.random.random() * 30
        memory_usage = 60 + np.random.random() * 20
        gpu_usage = 70 + np.random.random() * 25

        # LLM 指標
        requests_per_minute = 100 + np.random.randint(-20, 20)
        avg_latency = 0.5 + np.random.random() * 0.3
        error_rate = np.random.random() * 2  # 百分比

        # 成本指標
        cost_per_minute = requests_per_minute * 0.002

        wandb.log({
            "minute": minute,
            "system/cpu_usage": cpu_usage,
            "system/memory_usage": memory_usage,
            "system/gpu_usage": gpu_usage,
            "llm/requests_per_minute": requests_per_minute,
            "llm/avg_latency": avg_latency,
            "llm/error_rate": error_rate,
            "cost/per_minute": cost_per_minute,
            "cost/cumulative": cost_per_minute * (minute + 1)
        })

        if minute % 10 == 0:
            print(f"  {minute} 分鐘: {requests_per_minute} req/min, "
                  f"latency={avg_latency:.2f}s, errors={error_rate:.2f}%")

        time.sleep(0.05)  # 模擬實時更新

    print("✅ 實時監控完成")

    wandb.finish()


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函數：運行所有示例"""
    print("\n" + "="*70)
    print("Weights & Biases LLM 監控示例")
    print("="*70)

    try:
        # 1. 推理追蹤
        llm_inference_tracking()

        # 2. Prompt 追蹤
        prompt_tracking()

        # 3. 成本優化
        cost_optimization_tracking()

        # 4. 微調監控
        finetuning_monitoring()

        # 5. 質量評估
        generation_quality_assessment()

        # 6. 實時監控
        realtime_monitoring_dashboard()

        print("\n" + "="*70)
        print("✅ 所有 LLM 監控示例完成！")
        print("="*70)
        print("\n💡 提示:")
        print("   - 追蹤每個請求的成本和性能")
        print("   - 比較不同 prompt 的效果")
        print("   - 監控實時系統狀態")
        print("   - 評估生成質量")

    except Exception as e:
        print(f"\n❌ 運行示例時出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
