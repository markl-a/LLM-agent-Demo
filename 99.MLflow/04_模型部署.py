"""
MLflow 模型部署示例 - 模型服務和部署

主要功能：本地服務、Docker部署、批量推理、模型加載
作者: MLflow Team | 日期: 2025-01-01
"""

import mlflow
import mlflow.pyfunc
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import numpy as np


def save_model_for_serving():
    """保存模型用於服務"""
    print("\n" + "="*60)
    print("保存模型用於服務")
    print("="*60)

    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    with mlflow.start_run():
        clf = RandomForestClassifier(n_estimators=100)
        clf.fit(X_train, y_train)

        # 保存模型並創建簽名
        from mlflow.models.signature import infer_signature

        signature = infer_signature(X_train, clf.predict(X_train))

        mlflow.sklearn.log_model(
            clf,
            "model",
            signature=signature,
            registered_model_name="iris-serving-model"
        )

        print("✅ 模型已保存，可用於服務")
        print("\n💡 啟動服務:")
        print("   mlflow models serve -m models:/iris-serving-model/1 -p 5001")


def load_and_predict():
    """加載模型並預測"""
    print("\n" + "="*60)
    print("加載模型並預測")
    print("="*60)

    try:
        # 加載生產模型
        model_uri = "models:/iris-serving-model/Production"
        model = mlflow.pyfunc.load_model(model_uri)

        # 測試數據
        test_data = np.array([[5.1, 3.5, 1.4, 0.2]])

        # 預測
        prediction = model.predict(test_data)

        print(f"✅ 預測結果: {prediction}")

    except Exception as e:
        print(f"⚠️  無法加載模型: {e}")
        print("   請先註冊模型並設置為 Production 階段")


def batch_inference():
    """批量推理示例"""
    print("\n" + "="*60)
    print("批量推理")
    print("="*60)

    X, y = load_iris(return_X_y=True)

    # 訓練並保存模型
    with mlflow.start_run():
        clf = RandomForestClassifier()
        clf.fit(X[:100], y[:100])

        model_path = "sklearn-model"
        mlflow.sklearn.log_model(clf, model_path)

        run_id = mlflow.active_run().info.run_id

    # 加載模型進行批量推理
    model_uri = f"runs:/{run_id}/{model_path}"
    loaded_model = mlflow.sklearn.load_model(model_uri)

    # 批量預測
    predictions = loaded_model.predict(X[100:110])

    print(f"✅ 批量預測完成: {len(predictions)} 個樣本")
    print(f"   預測結果: {predictions}")


def main():
    """主函數"""
    print("\n" + "="*70)
    print("MLflow 模型部署示例")
    print("="*70)

    try:
        save_model_for_serving()
        load_and_predict()
        batch_inference()
        print("\n✅ 完成！")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
