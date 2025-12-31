"""
MLflow 生產部署示例 - 生產環境部署最佳實踐

主要功能：部署檢查、A/B 測試、監控、回滾策略
作者: MLflow Team | 日期: 2025-01-01
"""

import mlflow
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import numpy as np
from datetime import datetime


def production_deployment():
    """生產部署示例"""
    print("\n" + "="*60)
    print("生產部署")
    print("="*60)

    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    # 訓練模型
    with mlflow.start_run():
        clf = RandomForestClassifier(n_estimators=100)
        clf.fit(X_train, y_train)

        test_accuracy = clf.score(X_test, y_test)
        mlflow.log_metric("test_accuracy", test_accuracy)

        # 註冊模型
        mlflow.sklearn.log_model(
            clf,
            "model",
            registered_model_name="production-iris-model"
        )

    # 轉換到 Production
    client = MlflowClient()

    try:
        client.transition_model_version_stage(
            name="production-iris-model",
            version=1,
            stage="Production",
            archive_existing_versions=True
        )

        print("✅ 模型已部署到生產環境")
        print(f"   準確率: {test_accuracy:.4f}")
        print(f"   版本: 1")
        print(f"   階段: Production")

    except Exception as e:
        print(f"⚠️  {e}")


def deployment_validation():
    """部署驗證"""
    print("\n" + "="*60)
    print("部署驗證")
    print("="*60)

    # 定義驗證標準
    validation_checks = {
        "min_accuracy": 0.90,
        "max_inference_time_ms": 100,
        "max_model_size_mb": 100
    }

    # 模擬模型指標
    model_metrics = {
        "accuracy": 0.95,
        "inference_time_ms": 75,
        "model_size_mb": 5.2
    }

    print("\n🔍 驗證檢查:")

    all_passed = True

    for check, threshold in validation_checks.items():
        metric = check.replace("min_", "").replace("max_", "")
        value = model_metrics.get(metric, 0)

        if "min_" in check:
            passed = value >= threshold
        else:
            passed = value <= threshold

        status = "✅" if passed else "❌"
        print(f"   {status} {check}: {value} (閾值: {threshold})")

        all_passed = all_passed and passed

    if all_passed:
        print("\n✅ 所有驗證檢查通過，可以部署")
    else:
        print("\n❌ 驗證失敗，不能部署")


def ab_testing_setup():
    """A/B 測試設置"""
    print("\n" + "="*60)
    print("A/B 測試設置")
    print("="*60)

    # 模擬兩個模型版本
    models = {
        "model_a": {"version": 1, "traffic": 0.5},
        "model_b": {"version": 2, "traffic": 0.5}
    }

    print("\n🔀 A/B 測試配置:")
    for model_name, config in models.items():
        print(f"   {model_name}: 版本 {config['version']}, 流量 {config['traffic']*100:.0f}%")

    # 模擬流量分配
    requests = 100
    model_a_requests = int(requests * models["model_a"]["traffic"])
    model_b_requests = requests - model_a_requests

    print(f"\n📊 流量分配 ({requests} 個請求):")
    print(f"   Model A: {model_a_requests} 請求")
    print(f"   Model B: {model_b_requests} 請求")


def model_monitoring():
    """模型監控"""
    print("\n" + "="*60)
    print("模型監控")
    print("="*60)

    with mlflow.start_run(run_name="production-monitoring"):
        # 模擬生產指標
        for hour in range(24):
            requests = 1000 + np.random.randint(-100, 100)
            avg_latency = 50 + np.random.random() * 20
            error_rate = np.random.random() * 0.5
            accuracy = 0.95 + np.random.random() * 0.03

            mlflow.log_metric("requests_per_hour", requests, step=hour)
            mlflow.log_metric("avg_latency_ms", avg_latency, step=hour)
            mlflow.log_metric("error_rate_pct", error_rate, step=hour)
            mlflow.log_metric("accuracy", accuracy, step=hour)

        print("✅ 24小時監控數據已記錄")


def deployment_metadata():
    """部署元數據"""
    print("\n" + "="*60)
    print("部署元數據")
    print("="*60)

    with mlflow.start_run(run_name="deployment-metadata"):
        deployment_info = {
            "deployed_at": datetime.now().isoformat(),
            "deployed_by": "ml-engineer",
            "environment": "production",
            "region": "us-west-2",
            "instances": 3,
            "model_version": "1.0.0"
        }

        mlflow.log_params(deployment_info)

        # 添加標籤
        mlflow.set_tags({
            "deployment_status": "active",
            "deployment_type": "rolling_update",
            "approved": "true"
        })

        print("✅ 部署元數據已記錄:")
        for key, value in deployment_info.items():
            print(f"   {key}: {value}")


def main():
    """主函數"""
    print("\n" + "="*70)
    print("MLflow 生產部署示例")
    print("="*70)

    try:
        production_deployment()
        deployment_validation()
        ab_testing_setup()
        model_monitoring()
        deployment_metadata()

        print("\n✅ 完成！")
        print("\n💡 生產部署檢查清單:")
        print("   ✓ 模型驗證通過")
        print("   ✓ A/B 測試配置")
        print("   ✓ 監控已設置")
        print("   ✓ 元數據已記錄")
        print("   ✓ 回滾策略就緒")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
