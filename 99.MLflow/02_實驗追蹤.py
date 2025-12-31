"""
MLflow 實驗追蹤示例

這個示例展示了 MLflow 的實驗追蹤功能。

主要功能：
1. 實驗創建和管理
2. 參數記錄
3. 指標追蹤
4. 工件管理
5. 運行搜索和過濾
6. 性能比較
7. 標籤和元數據
8. 運行刪除和恢復

作者: MLflow Team
日期: 2025-01-01
"""

import mlflow
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split


def experiment_management():
    """實驗管理示例"""
    print("\n" + "="*60)
    print("實驗管理")
    print("="*60)

    # 創建實驗
    experiment_name = "model-comparison-experiment"

    try:
        experiment_id = mlflow.create_experiment(
            experiment_name,
            artifact_location="./mlruns/artifacts",
            tags={"team": "ml-team", "project": "classification"}
        )
        print(f"✅ 創建實驗: {experiment_name}")
    except:
        experiment = mlflow.get_experiment_by_name(experiment_name)
        experiment_id = experiment.experiment_id
        print(f"✅ 使用現有實驗: {experiment_name}")

    mlflow.set_experiment(experiment_name)


def parameter_tracking():
    """參數追蹤示例"""
    print("\n" + "="*60)
    print("參數追蹤")
    print("="*60)

    with mlflow.start_run(run_name="parameter-demo"):
        # 記錄單個參數
        mlflow.log_param("learning_rate", 0.001)

        # 記錄多個參數
        mlflow.log_params({
            "batch_size": 32,
            "epochs": 100,
            "optimizer": "adam"
        })

        # 記錄嵌套配置
        config = {
            "model": {
                "type": "random_forest",
                "n_estimators": 100,
                "max_depth": 10
            },
            "data": {
                "train_size": 0.8,
                "validation_size": 0.1
            }
        }

        # 展平並記錄
        for section, params in config.items():
            for key, value in params.items():
                mlflow.log_param(f"{section}.{key}", value)

        print("✅ 參數已記錄")


def metric_tracking():
    """指標追蹤示例"""
    print("\n" + "="*60)
    print("指標追蹤")
    print("="*60)

    with mlflow.start_run(run_name="metric-demo"):
        # 記錄訓練過程
        for epoch in range(50):
            train_loss = 2.0 * np.exp(-epoch / 10) + np.random.random() * 0.1
            val_loss = train_loss * 1.1

            # 記錄帶步驟的指標
            mlflow.log_metric("train_loss", train_loss, step=epoch)
            mlflow.log_metric("val_loss", val_loss, step=epoch)

        # 記錄最終指標
        mlflow.log_metric("final_accuracy", 0.95)

        print("✅ 指標已記錄")


def artifact_logging():
    """工件記錄示例"""
    print("\n" + "="*60)
    print("工件記錄")
    print("="*60)

    with mlflow.start_run(run_name="artifact-demo"):
        # 記錄文本文件
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # 創建文件
            report_path = os.path.join(tmpdir, "report.txt")
            with open(report_path, "w") as f:
                f.write("實驗報告\n")
                f.write("準確率: 95%\n")

            # 記錄文件
            mlflow.log_artifact(report_path)

            # 創建目錄並記錄
            results_dir = os.path.join(tmpdir, "results")
            os.makedirs(results_dir)

            for i in range(3):
                file_path = os.path.join(results_dir, f"result_{i}.txt")
                with open(file_path, "w") as f:
                    f.write(f"Result {i}\n")

            mlflow.log_artifacts(results_dir, "results")

        print("✅ 工件已記錄")


def model_comparison():
    """模型比較示例"""
    print("\n" + "="*60)
    print("模型比較")
    print("="*60)

    # 準備數據
    X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    models = {
        "RandomForest": RandomForestClassifier(n_estimators=100),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100)
    }

    for model_name, model in models.items():
        with mlflow.start_run(run_name=f"{model_name}-model"):
            # 記錄模型類型
            mlflow.log_param("model_type", model_name)

            # 訓練
            model.fit(X_train, y_train)

            # 評估
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)

            mlflow.log_metric("train_accuracy", train_score)
            mlflow.log_metric("test_accuracy", test_score)

            # 記錄模型
            mlflow.sklearn.log_model(model, "model")

            print(f"  {model_name}: test_acc={test_score:.2%}")


def main():
    """主函數"""
    print("\n" + "="*70)
    print("MLflow 實驗追蹤示例")
    print("="*70)

    try:
        experiment_management()
        parameter_tracking()
        metric_tracking()
        artifact_logging()
        model_comparison()

        print("\n✅ 所有示例完成！")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
