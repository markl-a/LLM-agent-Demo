"""
MLflow 模型服務示例 - 模型部署和服務

主要功能：本地服務、REST API、批量預測、模型更新
作者: MLflow Team | 日期: 2025-01-01
"""

import mlflow
import mlflow.pyfunc
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import numpy as np


def prepare_model_for_serving():
    """準備模型用於服務"""
    print("\n" + "="*60)
    print("準備模型用於服務")
    print("="*60)

    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    with mlflow.start_run():
        clf = RandomForestClassifier(n_estimators=100)
        clf.fit(X_train, y_train)

        # 創建模型簽名
        from mlflow.models.signature import infer_signature

        signature = infer_signature(X_train, clf.predict(X_train))

        # 保存模型
        mlflow.sklearn.log_model(
            clf,
            "model",
            signature=signature,
            input_example=X_train[:5],
            registered_model_name="iris-api-model"
        )

        print("✅ 模型已準備好服務")
        print("\n💡 啟動 REST API:")
        print("   mlflow models serve -m models:/iris-api-model/1 -p 5001 --no-conda")
        print("\n💡 測試 API:")
        print('   curl -X POST -H "Content-Type:application/json" \\')
        print('        --data \'{"inputs": [[5.1, 3.5, 1.4, 0.2]]}\' \\')
        print('        http://127.0.0.1:5001/invocations')


def local_model_loading():
    """本地模型加載"""
    print("\n" + "="*60)
    print("本地模型加載")
    print("="*60)

    # 訓練並保存模型
    X, y = load_iris(return_X_y=True)

    with mlflow.start_run():
        clf = RandomForestClassifier()
        clf.fit(X, y)

        model_path = "iris-local-model"
        mlflow.sklearn.log_model(clf, model_path)

        run_id = mlflow.active_run().info.run_id

    # 加載模型
    model_uri = f"runs:/{run_id}/{model_path}"
    loaded_model = mlflow.sklearn.load_model(model_uri)

    # 測試預測
    test_input = np.array([[5.1, 3.5, 1.4, 0.2]])
    prediction = loaded_model.predict(test_input)

    print(f"✅ 模型已加載並預測")
    print(f"   輸入: {test_input[0]}")
    print(f"   預測: {prediction[0]}")


def batch_prediction_example():
    """批量預測示例"""
    print("\n" + "="*60)
    print("批量預測")
    print("="*60)

    X, y = load_iris(return_X_y=True)

    # 訓練模型
    with mlflow.start_run():
        clf = RandomForestClassifier()
        clf.fit(X[:100], y[:100])

        mlflow.sklearn.log_model(clf, "batch-model")
        run_id = mlflow.active_run().info.run_id

    # 加載模型並進行批量預測
    model = mlflow.sklearn.load_model(f"runs:/{run_id}/batch-model")

    # 批量預測
    batch_data = X[100:120]
    predictions = model.predict(batch_data)

    print(f"✅ 批量預測完成")
    print(f"   預測樣本數: {len(predictions)}")
    print(f"   前 5 個預測: {predictions[:5]}")


def custom_pyfunc_model():
    """自定義 PyFunc 模型"""
    print("\n" + "="*60)
    print("自定義 PyFunc 模型")
    print("="*60)

    class CustomModel(mlflow.pyfunc.PythonModel):
        def __init__(self, multiplier=2):
            self.multiplier = multiplier

        def predict(self, context, model_input):
            return model_input * self.multiplier

    with mlflow.start_run():
        custom_model = CustomModel(multiplier=3)

        mlflow.pyfunc.log_model(
            "custom_model",
            python_model=custom_model
        )

        run_id = mlflow.active_run().info.run_id

    # 加載並使用
    loaded_model = mlflow.pyfunc.load_model(f"runs:/{run_id}/custom_model")

    test_data = np.array([[1, 2, 3]])
    result = loaded_model.predict(test_data)

    print(f"✅ 自定義模型預測")
    print(f"   輸入: {test_data[0]}")
    print(f"   輸出: {result[0]}")


def main():
    """主函數"""
    print("\n" + "="*70)
    print("MLflow 模型服務示例")
    print("="*70)

    try:
        prepare_model_for_serving()
        local_model_loading()
        batch_prediction_example()
        custom_pyfunc_model()
        print("\n✅ 完成！")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")


if __name__ == "__main__":
    main()
