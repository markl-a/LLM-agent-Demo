"""
MLflow 快速開始示例

這個示例展示了如何快速開始使用 MLflow 進行 ML 實驗追蹤。
包含基本的運行管理、參數和指標記錄功能。

主要功能：
1. MLflow 基本配置
2. 開始和管理運行
3. 記錄參數和指標
4. 記錄工件
5. 使用追蹤 URI
6. 實驗管理
7. 運行比較
8. UI 使用

作者: MLflow Team
日期: 2025-01-01
"""

import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris, make_classification
from sklearn.model_split import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
import os


# ============================================================================
# 第一部分：基本配置
# ============================================================================

def basic_setup():
    """基本配置示例"""
    print("\n" + "="*60)
    print("MLflow 基本配置")
    print("="*60)

    # 設置追蹤 URI（默認為本地 ./mlruns）
    mlflow.set_tracking_uri("file:./mlruns")

    print(f"✅ 追蹤 URI: {mlflow.get_tracking_uri()}")

    # 設置實驗
    experiment_name = "quickstart-experiment"
    mlflow.set_experiment(experiment_name)

    print(f"✅ 實驗名稱: {experiment_name}")

    # 獲取當前實驗信息
    experiment = mlflow.get_experiment_by_name(experiment_name)

    print(f"\n📋 實驗信息:")
    print(f"   實驗 ID: {experiment.experiment_id}")
    print(f"   名稱: {experiment.name}")
    print(f"   工件位置: {experiment.artifact_location}")


# ============================================================================
# 第二部分：基本運行
# ============================================================================

def basic_run_example():
    """基本運行示例"""
    print("\n" + "="*60)
    print("基本運行示例")
    print("="*60)

    # 開始運行
    with mlflow.start_run(run_name="basic-run") as run:
        print(f"\n🏃 運行開始...")
        print(f"   運行 ID: {run.info.run_id}")
        print(f"   運行名稱: basic-run")

        # 記錄參數
        mlflow.log_param("learning_rate", 0.001)
        mlflow.log_param("batch_size", 32)
        mlflow.log_param("epochs", 10)

        print("\n📝 參數已記錄:")
        print("   learning_rate: 0.001")
        print("   batch_size: 32")
        print("   epochs: 10")

        # 模擬訓練並記錄指標
        for epoch in range(10):
            loss = 1.0 / (epoch + 1) + np.random.random() * 0.1
            accuracy = epoch / 10 + np.random.random() * 0.05

            mlflow.log_metric("loss", loss, step=epoch)
            mlflow.log_metric("accuracy", accuracy, step=epoch)

        print("\n📊 指標已記錄")

        # 記錄標籤
        mlflow.set_tag("model_type", "demo")
        mlflow.set_tag("framework", "sklearn")

        print("\n🏷️  標籤已設置")

        print(f"\n✅ 運行完成")


# ============================================================================
# 第三部分：Sklearn 模型訓練
# ============================================================================

def sklearn_training_example():
    """Sklearn 模型訓練示例"""
    print("\n" + "="*60)
    print("Sklearn 模型訓練")
    print("="*60)

    # 準備數據
    print("\n📦 準備數據...")
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"   訓練樣本: {len(X_train)}")
    print(f"   測試樣本: {len(X_test)}")

    # 開始運行
    with mlflow.start_run(run_name="sklearn-iris") as run:
        print(f"\n🏃 訓練模型...")

        # 配置
        n_estimators = 100
        max_depth = 5

        # 記錄參數
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("dataset", "iris")

        # 訓練模型
        clf = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42
        )

        clf.fit(X_train, y_train)

        # 評估
        train_accuracy = clf.score(X_train, y_train)
        test_accuracy = clf.score(X_test, y_test)

        # 記錄指標
        mlflow.log_metric("train_accuracy", train_accuracy)
        mlflow.log_metric("test_accuracy", test_accuracy)

        print(f"\n📊 性能指標:")
        print(f"   訓練準確率: {train_accuracy:.2%}")
        print(f"   測試準確率: {test_accuracy:.2%}")

        # 記錄模型
        mlflow.sklearn.log_model(
            clf,
            "model",
            input_example=X_train[:5]
        )

        print(f"\n💾 模型已保存")

        # 記錄額外工件
        # 創建特徵重要性文件
        import pandas as pd

        feature_importance = pd.DataFrame({
            'feature': [f'feature_{i}' for i in range(X.shape[1])],
            'importance': clf.feature_importances_
        }).sort_values('importance', ascending=False)

        importance_path = "/tmp/feature_importance.csv"
        feature_importance.to_csv(importance_path, index=False)

        mlflow.log_artifact(importance_path, "feature_analysis")

        os.remove(importance_path)

        print(f"✅ 工件已保存")


# ============================================================================
# 第四部分：運行比較
# ============================================================================

def run_comparison_example():
    """運行比較示例"""
    print("\n" + "="*60)
    print("運行比較示例")
    print("="*60)

    # 準備數據
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        random_state=42
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 測試不同的配置
    configs = [
        {"n_estimators": 50, "max_depth": 3},
        {"n_estimators": 100, "max_depth": 5},
        {"n_estimators": 200, "max_depth": 10},
    ]

    print(f"\n🔄 運行 {len(configs)} 個不同配置...")

    results = []

    for i, config in enumerate(configs):
        with mlflow.start_run(run_name=f"config-{i+1}"):
            # 記錄配置
            mlflow.log_params(config)

            # 訓練
            clf = RandomForestClassifier(**config, random_state=42)
            clf.fit(X_train, y_train)

            # 評估
            test_acc = clf.score(X_test, y_test)
            y_pred = clf.predict(X_test)
            f1 = f1_score(y_test, y_pred)

            # 記錄指標
            mlflow.log_metric("test_accuracy", test_acc)
            mlflow.log_metric("f1_score", f1)

            results.append({
                "config": config,
                "accuracy": test_acc,
                "f1": f1
            })

            print(f"  配置 {i+1}: n_estimators={config['n_estimators']}, "
                  f"max_depth={config['max_depth']} -> "
                  f"accuracy={test_acc:.2%}")

    # 找出最佳配置
    best = max(results, key=lambda x: x['accuracy'])

    print(f"\n🏆 最佳配置:")
    print(f"   {best['config']}")
    print(f"   準確率: {best['accuracy']:.2%}")


# ============================================================================
# 第五部分：父子運行
# ============================================================================

def nested_runs_example():
    """嵌套運行示例"""
    print("\n" + "="*60)
    print("嵌套運行示例")
    print("="*60)

    # 父運行
    with mlflow.start_run(run_name="parent-run") as parent_run:
        mlflow.log_param("parent_param", "value")

        print(f"\n👨 父運行: {parent_run.info.run_id[:8]}")

        # 子運行 1
        with mlflow.start_run(
            run_name="child-run-1",
            nested=True
        ) as child_run1:
            mlflow.log_param("child1_param", "value1")
            mlflow.log_metric("child1_metric", 0.8)

            print(f"   👶 子運行 1: {child_run1.info.run_id[:8]}")

        # 子運行 2
        with mlflow.start_run(
            run_name="child-run-2",
            nested=True
        ) as child_run2:
            mlflow.log_param("child2_param", "value2")
            mlflow.log_metric("child2_metric", 0.9)

            print(f"   👶 子運行 2: {child_run2.info.run_id[:8]}")

        # 聚合子運行的結果
        mlflow.log_metric("avg_child_metric", 0.85)

        print(f"\n✅ 嵌套運行完成")


# ============================================================================
# 第六部分：自動記錄
# ============================================================================

def autolog_example():
    """自動記錄示例"""
    print("\n" + "="*60)
    print("自動記錄示例")
    print("="*60)

    # 啟用自動記錄
    mlflow.sklearn.autolog()

    print("\n🤖 自動記錄已啟用")

    # 準備數據
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    # 訓練模型（自動記錄參數、指標、模型）
    with mlflow.start_run(run_name="autolog-example"):
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        score = clf.score(X_test, y_test)

        print(f"\n📊 測試準確率: {score:.2%}")
        print(f"✅ MLflow 自動記錄了參數、指標和模型")

    # 關閉自動記錄
    mlflow.sklearn.autolog(disable=True)


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函數：運行所有示例"""
    print("\n" + "="*70)
    print("MLflow 快速開始示例")
    print("="*70)

    try:
        # 1. 基本配置
        basic_setup()

        # 2. 基本運行
        basic_run_example()

        # 3. Sklearn 訓練
        sklearn_training_example()

        # 4. 運行比較
        run_comparison_example()

        # 5. 嵌套運行
        nested_runs_example()

        # 6. 自動記錄
        autolog_example()

        print("\n" + "="*70)
        print("✅ 所有示例運行完成！")
        print("="*70)
        print("\n💡 接下來的步驟:")
        print("   1. 運行 'mlflow ui' 啟動 UI")
        print("   2. 訪問 http://localhost:5000")
        print("   3. 瀏覽實驗和運行")
        print("   4. 比較不同配置的結果")

    except Exception as e:
        print(f"\n❌ 運行示例時出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
