"""
MLflow 模型評估示例 - 模型性能評估和比較

主要功能：評估指標、混淆矩陣、ROC曲線、模型比較
作者: MLflow Team | 日期: 2025-01-01
"""

import mlflow
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import numpy as np


def comprehensive_evaluation():
    """綜合評估示例"""
    print("\n" + "="*60)
    print("綜合模型評估")
    print("="*60)

    X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    with mlflow.start_run(run_name="comprehensive-eval"):
        # 訓練模型
        clf = RandomForestClassifier(n_estimators=100)
        clf.fit(X_train, y_train)

        # 預測
        y_pred = clf.predict(X_test)

        # 計算多個指標
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred, average='weighted'),
            "precision": precision_score(y_test, y_pred, average='weighted'),
            "recall": recall_score(y_test, y_pred, average='weighted')
        }

        # 記錄所有指標
        mlflow.log_metrics(metrics)

        print("✅ 評估指標:")
        for metric, value in metrics.items():
            print(f"   {metric}: {value:.4f}")


def cross_validation_evaluation():
    """交叉驗證評估"""
    print("\n" + "="*60)
    print("交叉驗證評估")
    print("="*60)

    from sklearn.model_selection import cross_val_score

    X, y = make_classification(n_samples=500, n_features=10, random_state=42)

    with mlflow.start_run(run_name="cross-validation"):
        clf = RandomForestClassifier()

        # 交叉驗證
        scores = cross_val_score(clf, X, y, cv=5, scoring='accuracy')

        # 記錄結果
        mlflow.log_metric("cv_mean_accuracy", scores.mean())
        mlflow.log_metric("cv_std_accuracy", scores.std())

        for i, score in enumerate(scores):
            mlflow.log_metric(f"cv_fold_{i+1}_accuracy", score)

        print(f"✅ 交叉驗證準確率: {scores.mean():.4f} (+/- {scores.std():.4f})")


def model_comparison_evaluation():
    """模型比較評估"""
    print("\n" + "="*60)
    print("模型比較評估")
    print("="*60)

    X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    models = {
        "RandomForest": RandomForestClassifier(n_estimators=100),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100)
    }

    results = []

    for name, model in models.items():
        with mlflow.start_run(run_name=f"{name}-evaluation"):
            # 訓練
            model.fit(X_train, y_train)

            # 評估
            y_pred = model.predict(X_test)

            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')

            mlflow.log_param("model_type", name)
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("f1_score", f1)

            results.append((name, accuracy, f1))

            print(f"  {name}: accuracy={accuracy:.4f}, f1={f1:.4f}")

    # 找出最佳模型
    best_model = max(results, key=lambda x: x[1])
    print(f"\n🏆 最佳模型: {best_model[0]} (accuracy={best_model[1]:.4f})")


def main():
    """主函數"""
    print("\n" + "="*70)
    print("MLflow 模型評估示例")
    print("="*70)

    try:
        comprehensive_evaluation()
        cross_validation_evaluation()
        model_comparison_evaluation()
        print("\n✅ 完成！")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
