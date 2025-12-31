"""
MLflow 流水線示例 - ML 流水線管理

主要功能：Pipeline 追蹤、特徵工程、端到端流程、可重現性
作者: MLflow Team | 日期: 2025-01-01
"""

import mlflow
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split


def sklearn_pipeline_tracking():
    """Sklearn Pipeline 追蹤"""
    print("\n" + "="*60)
    print("Sklearn Pipeline 追蹤")
    print("="*60)

    X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    with mlflow.start_run(run_name="sklearn-pipeline"):
        # 創建 Pipeline
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('pca', PCA(n_components=10)),
            ('classifier', RandomForestClassifier(n_estimators=100))
        ])

        # 訓練
        pipeline.fit(X_train, y_train)

        # 評估
        score = pipeline.score(X_test, y_test)

        # 記錄參數
        mlflow.log_param("pipeline_steps", len(pipeline.steps))
        mlflow.log_param("pca_components", 10)
        mlflow.log_param("n_estimators", 100)

        # 記錄指標
        mlflow.log_metric("test_accuracy", score)

        # 記錄 Pipeline
        mlflow.sklearn.log_model(pipeline, "pipeline")

        print(f"✅ Pipeline 已追蹤，準確率: {score:.4f}")


def feature_engineering_pipeline():
    """特徵工程流水線"""
    print("\n" + "="*60)
    print("特徵工程流水線")
    print("="*60)

    X, y = make_classification(n_samples=500, n_features=15, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    with mlflow.start_run(run_name="feature-engineering"):
        # 多階段處理
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        mlflow.log_param("scaling_method", "StandardScaler")

        # PCA 降維
        pca = PCA(n_components=0.95)  # 保留 95% 方差
        X_train_pca = pca.fit_transform(X_train_scaled)
        X_test_pca = pca.transform(X_test_scaled)

        n_components = pca.n_components_
        mlflow.log_param("pca_components", n_components)
        mlflow.log_metric("explained_variance_ratio", pca.explained_variance_ratio_.sum())

        # 訓練模型
        clf = RandomForestClassifier()
        clf.fit(X_train_pca, y_train)

        score = clf.score(X_test_pca, y_test)
        mlflow.log_metric("test_accuracy", score)

        print(f"✅ 特徵工程完成")
        print(f"   原始特徵: 15 -> PCA 特徵: {n_components}")
        print(f"   準確率: {score:.4f}")


def end_to_end_pipeline():
    """端到端流水線"""
    print("\n" + "="*60)
    print("端到端流水線")
    print("="*60)

    with mlflow.start_run(run_name="end-to-end-pipeline"):
        # 步驟 1: 數據準備
        X, y = make_classification(n_samples=800, n_features=20, random_state=42)
        mlflow.log_param("n_samples", 800)
        mlflow.log_param("n_features", 20)

        # 步驟 2: 數據分割
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        mlflow.log_param("test_size", 0.2)

        # 步驟 3: 特徵處理
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # 步驟 4: 模型訓練
        clf = RandomForestClassifier(n_estimators=50, max_depth=10)
        clf.fit(X_train_scaled, y_train)

        mlflow.log_params({
            "n_estimators": 50,
            "max_depth": 10
        })

        # 步驟 5: 評估
        train_score = clf.score(X_train_scaled, y_train)
        test_score = clf.score(X_test_scaled, y_test)

        mlflow.log_metrics({
            "train_accuracy": train_score,
            "test_accuracy": test_score
        })

        print(f"✅ 端到端流水線完成")
        print(f"   訓練準確率: {train_score:.4f}")
        print(f"   測試準確率: {test_score:.4f}")


def main():
    """主函數"""
    print("\n" + "="*70)
    print("MLflow 流水線示例")
    print("="*70)

    try:
        sklearn_pipeline_tracking()
        feature_engineering_pipeline()
        end_to_end_pipeline()
        print("\n✅ 完成！")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
