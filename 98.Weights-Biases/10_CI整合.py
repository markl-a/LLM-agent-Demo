"""
Weights & Biases CI/CD 整合示例

這個示例展示了如何將 W&B 整合到 CI/CD 流程中。
包含 GitHub Actions、自動化測試、模型驗證和部署追蹤。

主要功能：
1. CI/CD 流程整合
2. 自動化訓練追蹤
3. 模型驗證
4. 性能回歸測試
5. 自動化報告
6. 部署追蹤
7. 告警和通知
8. 版本控制整合

作者: W&B Team
日期: 2025-01-01
"""

import wandb
import numpy as np
import os
from datetime import datetime


def ci_training_job():
    """CI 訓練作業"""
    print("\n" + "="*60)
    print("CI 訓練作業")
    print("="*60)

    # 模擬 CI 環境變量
    ci_env = {
        "CI": "true",
        "GITHUB_SHA": "abc123def456",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_RUN_ID": "12345",
        "GITHUB_ACTOR": "ci-bot"
    }

    run = wandb.init(
        project="ci-cd-integration",
        name=f"ci-run-{ci_env['GITHUB_RUN_ID']}",
        tags=["ci", "automated"],
        config={
            "git_commit": ci_env["GITHUB_SHA"],
            "git_branch": ci_env["GITHUB_REF"].split("/")[-1],
            "ci_run_id": ci_env["GITHUB_RUN_ID"]
        },
        notes=f"自動化訓練 - Commit {ci_env['GITHUB_SHA'][:7]}"
    )

    print(f"\n🤖 CI 訓練開始...")
    print(f"   Commit: {ci_env['GITHUB_SHA'][:7]}")
    print(f"   Branch: {run.config.git_branch}")

    # 模擬訓練
    for epoch in range(10):
        loss = 1.0 / (epoch + 1) + np.random.random() * 0.1
        accuracy = epoch / 10 + np.random.random() * 0.05

        wandb.log({
            "epoch": epoch,
            "loss": loss,
            "accuracy": accuracy
        })

    # 記錄 CI 特定的元數據
    wandb.summary.update({
        "ci_status": "success",
        "ci_duration_seconds": 120,
        "final_accuracy": accuracy,
        "git_commit": ci_env["GITHUB_SHA"]
    })

    print(f"✅ CI 訓練完成")
    print(f"   最終準確率: {accuracy:.2%}")

    wandb.finish()


def model_validation_ci():
    """模型驗證 CI 流程"""
    print("\n" + "="*60)
    print("模型驗證 CI 流程")
    print("="*60)

    run = wandb.init(
        project="ci-cd-integration",
        name="model-validation",
        job_type="validation"
    )

    print("\n🔍 驗證模型...")

    # 定義驗證標準
    validation_criteria = {
        "min_accuracy": 0.85,
        "max_latency_ms": 100,
        "max_model_size_mb": 500
    }

    # 模擬模型指標
    model_metrics = {
        "accuracy": 0.90,
        "latency_ms": 75,
        "model_size_mb": 320
    }

    # 驗證
    validation_results = {}
    all_passed = True

    for criterion, threshold in validation_criteria.items():
        metric_name = criterion.replace("min_", "").replace("max_", "")
        actual_value = model_metrics.get(metric_name, 0)

        if "min_" in criterion:
            passed = actual_value >= threshold
        else:  # max_
            passed = actual_value <= threshold

        validation_results[criterion] = {
            "threshold": threshold,
            "actual": actual_value,
            "passed": passed
        }

        all_passed = all_passed and passed

        status = "✅" if passed else "❌"
        print(f"  {status} {criterion}: {actual_value} (閾值: {threshold})")

    # 記錄驗證結果
    wandb.log({
        "validation/all_passed": all_passed,
        **{f"validation/{k}": v["passed"]
           for k, v in validation_results.items()}
    })

    wandb.summary["validation_status"] = "passed" if all_passed else "failed"

    if all_passed:
        print("\n✅ 模型驗證通過")
    else:
        print("\n❌ 模型驗證失敗")

    wandb.finish()

    return all_passed


def regression_test():
    """回歸測試"""
    print("\n" + "="*60)
    print("性能回歸測試")
    print("="*60)

    run = wandb.init(
        project="ci-cd-integration",
        name="regression-test",
        job_type="test"
    )

    # 基準性能
    baseline_accuracy = 0.85

    # 當前性能
    current_accuracy = 0.87

    # 計算變化
    improvement = current_accuracy - baseline_accuracy
    improvement_pct = (improvement / baseline_accuracy) * 100

    print(f"\n📊 性能比較:")
    print(f"   基準準確率: {baseline_accuracy:.2%}")
    print(f"   當前準確率: {current_accuracy:.2%}")
    print(f"   改進: {improvement_pct:+.2f}%")

    wandb.log({
        "baseline_accuracy": baseline_accuracy,
        "current_accuracy": current_accuracy,
        "improvement": improvement,
        "improvement_pct": improvement_pct
    })

    # 檢查是否有回歸
    has_regression = current_accuracy < baseline_accuracy * 0.95  # 允許5%的下降

    wandb.summary["has_regression"] = has_regression
    wandb.summary["test_status"] = "failed" if has_regression else "passed"

    if has_regression:
        print("❌ 檢測到性能回歸！")
    else:
        print("✅ 無性能回歸")

    wandb.finish()


def deployment_tracking():
    """部署追蹤"""
    print("\n" + "="*60)
    print("部署追蹤")
    print("="*60)

    run = wandb.init(
        project="ci-cd-integration",
        name="deployment-tracking",
        job_type="deployment"
    )

    deployment_info = {
        "environment": "production",
        "model_version": "v1.2.0",
        "deployed_at": datetime.now().isoformat(),
        "deployed_by": "ci-bot",
        "instances": 3,
        "region": "us-west-2"
    }

    print(f"\n🚀 部署信息:")
    for key, value in deployment_info.items():
        print(f"   {key}: {value}")

    # 記錄部署元數據
    wandb.config.update(deployment_info)

    # 模擬部署後的性能監控
    print("\n📊 監控部署後性能...")

    for minute in range(10):
        requests_per_min = 100 + np.random.randint(-10, 10)
        avg_latency = 50 + np.random.random() * 20
        error_rate = np.random.random() * 0.5

        wandb.log({
            "minute": minute,
            "requests_per_minute": requests_per_min,
            "latency_ms": avg_latency,
            "error_rate_pct": error_rate
        })

    wandb.summary["deployment_status"] = "healthy"

    print("✅ 部署監控完成")

    wandb.finish()


def main():
    """主函數"""
    print("\n" + "="*70)
    print("Weights & Biases CI/CD 整合示例")
    print("="*70)

    try:
        # 1. CI 訓練作業
        ci_training_job()

        # 2. 模型驗證
        validation_passed = model_validation_ci()

        # 3. 回歸測試
        regression_test()

        # 4. 部署追蹤 (僅在驗證通過時)
        if validation_passed:
            deployment_tracking()

        print("\n✅ 所有 CI/CD 示例完成！")
        print("\n💡 提示:")
        print("   - 將 W&B 整合到 GitHub Actions")
        print("   - 設置自動化驗證門檻")
        print("   - 追蹤每次部署的性能")
        print("   - 配置告警通知")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
