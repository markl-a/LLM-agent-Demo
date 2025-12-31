"""
MLflow 模型註冊示例 - 模型註冊表管理

主要功能：模型版本管理、階段轉換、標籤和註釋、模型搜索
作者: MLflow Team | 日期: 2025-01-01
"""

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from mlflow.tracking import MlflowClient


def register_model_example():
    """註冊模型示例"""
    print("\n" + "="*60)
    print("模型註冊")
    print("="*60)

    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    with mlflow.start_run(run_name="model-for-registry"):
        clf = RandomForestClassifier(n_estimators=100)
        clf.fit(X_train, y_train)

        mlflow.log_metric("test_accuracy", clf.score(X_test, y_test))

        # 記錄並註冊模型
        mlflow.sklearn.log_model(
            clf,
            "model",
            registered_model_name="iris-classifier"
        )

        print("✅ 模型已註冊: iris-classifier")


def model_versioning():
    """模型版本管理"""
    print("\n" + "="*60)
    print("模型版本管理")
    print("="*60)

    client = MlflowClient()
    model_name = "iris-classifier"

    # 獲取所有版本
    versions = client.search_model_versions(f"name='{model_name}'")

    print(f"\n📦 模型版本:")
    for version in versions[:3]:
        print(f"   版本 {version.version}: {version.current_stage}")


def stage_transition():
    """階段轉換示例"""
    print("\n" + "="*60)
    print("階段轉換")
    print("="*60)

    client = MlflowClient()
    model_name = "iris-classifier"

    try:
        # 轉換到 Staging
        client.transition_model_version_stage(
            name=model_name,
            version=1,
            stage="Staging"
        )

        print(f"✅ 版本 1 -> Staging")

        # 添加描述
        client.update_model_version(
            name=model_name,
            version=1,
            description="首個穩定版本"
        )

    except Exception as e:
        print(f"⚠️  {e}")


def main():
    """主函數"""
    print("\n" + "="*70)
    print("MLflow 模型註冊示例")
    print("="*70)

    try:
        register_model_example()
        model_versioning()
        stage_transition()
        print("\n✅ 完成！")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
