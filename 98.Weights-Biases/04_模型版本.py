"""
Weights & Biases 模型版本管理示例

這個示例展示了如何使用 W&B Artifacts 進行模型版本管理。
包含模型註冊、版本追蹤、血統關係和模型部署管理。

主要功能：
1. 模型工件創建和註冊
2. 版本管理和標籤
3. 模型血統追蹤
4. 模型下載和加載
5. 模型比較和基準測試
6. 部署狀態管理
7. 數據集版本管理
8. 模型註冊表最佳實踐

作者: W&B Team
日期: 2025-01-01
"""

import wandb
import torch
import torch.nn as nn
import json
import os
from typing import Dict, Any, List
from datetime import datetime


# ============================================================================
# 第一部分：模型定義
# ============================================================================

class ModelV1(nn.Module):
    """模型版本 1"""

    def __init__(self):
        super(ModelV1, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(10, 50),
            nn.ReLU(),
            nn.Linear(50, 1)
        )

    def forward(self, x):
        return self.fc(x)


class ModelV2(nn.Module):
    """模型版本 2 - 改進版"""

    def __init__(self):
        super(ModelV2, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(10, 100),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(100, 50),
            nn.ReLU(),
            nn.Linear(50, 1)
        )

    def forward(self, x):
        return self.fc(x)


# ============================================================================
# 第二部分：創建和保存模型工件
# ============================================================================

def create_model_artifact():
    """
    創建模型工件示例

    展示如何創建和註冊模型工件。
    """
    print("\n" + "="*60)
    print("創建模型工件")
    print("="*60)

    run = wandb.init(
        project="model-versioning",
        name="create-model-v1",
        job_type="train"
    )

    print("\n🏗️  訓練模型...")

    # 創建和訓練模型
    model = ModelV1()

    # 模擬訓練
    X = torch.randn(100, 10)
    y = torch.randn(100, 1)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    for epoch in range(10):
        optimizer.zero_grad()
        pred = model(X)
        loss = criterion(pred, y)
        loss.backward()
        optimizer.step()

    final_loss = loss.item()
    print(f"✅ 訓練完成，最終損失: {final_loss:.4f}")

    # 保存模型
    model_path = "/tmp/model_v1.pth"
    torch.save({
        'model_state_dict': model.state_dict(),
        'loss': final_loss,
        'architecture': 'ModelV1'
    }, model_path)

    # 創建元數據
    metadata = {
        "architecture": "ModelV1",
        "framework": "PyTorch",
        "loss": final_loss,
        "training_samples": 100,
        "epochs": 10,
        "created_at": datetime.now().isoformat()
    }

    # 創建模型工件
    print("\n📦 創建模型工件...")

    artifact = wandb.Artifact(
        name="classification-model",
        type="model",
        description="基礎分類模型 V1",
        metadata=metadata
    )

    # 添加文件
    artifact.add_file(model_path)

    # 添加模型架構描述
    model_info = {
        "input_size": 10,
        "output_size": 1,
        "layers": ["Linear(10, 50)", "ReLU", "Linear(50, 1)"]
    }

    info_path = "/tmp/model_info.json"
    with open(info_path, 'w') as f:
        json.dump(model_info, f, indent=2)

    artifact.add_file(info_path, name="model_info.json")

    # 記錄工件
    run.log_artifact(artifact)

    print(f"✅ 模型工件已創建: {artifact.name}:v{artifact.version}")
    print(f"   類型: {artifact.type}")
    print(f"   描述: {artifact.description}")

    # 清理
    os.remove(model_path)
    os.remove(info_path)

    wandb.finish()


# ============================================================================
# 第三部分：版本管理和標籤
# ============================================================================

def version_management():
    """
    版本管理示例

    展示如何管理模型的不同版本和添加別名。
    """
    print("\n" + "="*60)
    print("模型版本管理")
    print("="*60)

    # 創建多個版本
    versions = [
        {"name": "v1", "model": ModelV1(), "description": "基礎版本"},
        {"name": "v2", "model": ModelV2(), "description": "改進版本"},
    ]

    for ver_info in versions:
        print(f"\n🚀 創建版本: {ver_info['name']}")

        run = wandb.init(
            project="model-versioning",
            name=f"train-{ver_info['name']}",
            job_type="train",
            reinit=True
        )

        model = ver_info['model']

        # 模擬訓練
        X = torch.randn(100, 10)
        y = torch.randn(100, 1)

        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

        for _ in range(15):
            optimizer.zero_grad()
            pred = model(X)
            loss = criterion(pred, y)
            loss.backward()
            optimizer.step()

        final_loss = loss.item()

        # 保存模型
        model_path = f"/tmp/model_{ver_info['name']}.pth"
        torch.save(model.state_dict(), model_path)

        # 創建工件
        artifact = wandb.Artifact(
            name="classification-model",  # 相同名稱，不同版本
            type="model",
            description=ver_info['description'],
            metadata={
                "version": ver_info['name'],
                "loss": final_loss,
                "num_parameters": sum(p.numel() for p in model.parameters())
            }
        )

        artifact.add_file(model_path)

        # 記錄工件
        logged_artifact = run.log_artifact(artifact)

        # 根據性能添加別名
        if final_loss < 1.0:
            logged_artifact.wait()
            artifact = run.use_artifact(f"classification-model:latest")
            artifact.aliases.append("production")
            artifact.save()
            print(f"   🏷️  添加別名: production")

        if final_loss < 0.5:
            logged_artifact.wait()
            artifact = run.use_artifact(f"classification-model:latest")
            artifact.aliases.append("best")
            artifact.save()
            print(f"   🏷️  添加別名: best")

        print(f"✅ 版本 {ver_info['name']} 已保存，損失: {final_loss:.4f}")

        os.remove(model_path)
        wandb.finish()

    print("\n💡 提示: 使用別名 (如 'production', 'best') 管理不同階段的模型")


# ============================================================================
# 第四部分：下載和加載模型
# ============================================================================

def download_and_load_model():
    """
    下載和加載模型示例

    展示如何從 W&B 下載並加載模型。
    """
    print("\n" + "="*60)
    print("下載和加載模型")
    print("="*60)

    run = wandb.init(
        project="model-versioning",
        name="load-model",
        job_type="inference"
    )

    print("\n📥 下載模型工件...")

    # 方法 1: 使用最新版本
    artifact = run.use_artifact(
        "classification-model:latest",
        type="model"
    )

    artifact_dir = artifact.download()
    print(f"✅ 已下載到: {artifact_dir}")

    # 查看元數據
    print(f"\n📋 模型元數據:")
    for key, value in artifact.metadata.items():
        print(f"   {key}: {value}")

    # 方法 2: 使用別名
    try:
        production_artifact = run.use_artifact(
            "classification-model:production",
            type="model"
        )
        print(f"\n✅ 獲取生產版本: v{production_artifact.version}")
    except:
        print("\n⚠️  尚未標記生產版本")

    # 方法 3: 使用特定版本
    try:
        v0_artifact = run.use_artifact(
            "classification-model:v0",
            type="model"
        )
        print(f"✅ 獲取特定版本: v0")
    except:
        print("⚠️  版本 v0 不存在")

    # 加載模型
    print("\n🔄 加載模型...")

    # 查找模型文件
    import glob
    model_files = glob.glob(os.path.join(artifact_dir, "*.pth"))

    if model_files:
        model_path = model_files[0]
        print(f"📄 找到模型文件: {os.path.basename(model_path)}")

        # 加載模型狀態
        try:
            checkpoint = torch.load(model_path, map_location='cpu')

            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                print("✅ 加載完整檢查點")
                state_dict = checkpoint['model_state_dict']
                print(f"   訓練損失: {checkpoint.get('loss', 'N/A')}")
            else:
                state_dict = checkpoint
                print("✅ 加載狀態字典")

            # 實例化模型並加載權重
            model = ModelV1()
            model.load_state_dict(state_dict)
            model.eval()

            print("✅ 模型加載成功")

            # 測試推理
            test_input = torch.randn(1, 10)
            with torch.no_grad():
                output = model(test_input)

            print(f"\n🧪 測試推理:")
            print(f"   輸入形狀: {test_input.shape}")
            print(f"   輸出: {output.item():.4f}")

        except Exception as e:
            print(f"❌ 加載模型時出錯: {e}")

    wandb.finish()


# ============================================================================
# 第五部分：模型血統追蹤
# ============================================================================

def model_lineage_tracking():
    """
    模型血統追蹤示例

    展示如何追蹤模型的訓練數據、配置和依賴關係。
    """
    print("\n" + "="*60)
    print("模型血統追蹤")
    print("="*60)

    # 步驟 1: 創建數據集工件
    print("\n📦 步驟 1: 創建數據集工件")

    run = wandb.init(
        project="model-versioning",
        name="create-dataset",
        job_type="data-preparation"
    )

    # 創建虛擬數據集
    dataset_path = "/tmp/training_data.pt"
    data = {
        'X': torch.randn(1000, 10),
        'y': torch.randn(1000, 1)
    }
    torch.save(data, dataset_path)

    dataset_artifact = wandb.Artifact(
        name="training-dataset",
        type="dataset",
        description="訓練數據集",
        metadata={
            "num_samples": 1000,
            "features": 10,
            "created_at": datetime.now().isoformat()
        }
    )

    dataset_artifact.add_file(dataset_path)
    run.log_artifact(dataset_artifact)

    print("✅ 數據集工件已創建")
    os.remove(dataset_path)
    wandb.finish()

    # 步驟 2: 使用數據集訓練模型
    print("\n🏋️  步驟 2: 使用數據集訓練模型")

    run = wandb.init(
        project="model-versioning",
        name="train-with-lineage",
        job_type="train"
    )

    # 使用數據集
    dataset = run.use_artifact("training-dataset:latest")
    dataset_dir = dataset.download()

    print(f"✅ 數據集已下載")

    # 訓練模型
    model = ModelV1()

    # ... 訓練代碼 ...

    # 保存模型並記錄血統
    model_path = "/tmp/model_with_lineage.pth"
    torch.save(model.state_dict(), model_path)

    model_artifact = wandb.Artifact(
        name="model-with-lineage",
        type="model",
        description="帶血統追蹤的模型",
        metadata={
            "training_dataset": dataset.name,
            "dataset_version": dataset.version,
            "trained_at": datetime.now().isoformat()
        }
    )

    model_artifact.add_file(model_path)

    # 記錄輸入工件（建立血統關係）
    model_artifact.add_reference(
        f"wandb-artifact://{dataset.id}/training_data.pt",
        name="training_data_source"
    )

    run.log_artifact(model_artifact)

    print("✅ 模型工件已創建，血統關係已記錄")

    os.remove(model_path)
    wandb.finish()

    print("\n💡 在 W&B UI 中可以看到完整的模型血統圖")


# ============================================================================
# 第六部分：模型比較
# ============================================================================

def compare_models():
    """
    模型比較示例

    比較不同版本模型的性能。
    """
    print("\n" + "="*60)
    print("模型比較")
    print("="*60)

    run = wandb.init(
        project="model-versioning",
        name="model-comparison",
        job_type="evaluation"
    )

    api = wandb.Api()

    print("\n📊 獲取所有模型版本...")

    # 獲取工件集合
    artifact_collection = api.artifact_type(
        type_name="model",
        project="model-versioning"
    )

    # 比較指標
    comparison_data = []

    for artifact_version in artifact_collection.collections():
        for artifact in artifact_version.versions():
            metadata = artifact.metadata
            comparison_data.append({
                "version": artifact.version,
                "loss": metadata.get("loss", None),
                "num_parameters": metadata.get("num_parameters", None),
                "created_at": artifact.created_at
            })

    # 記錄比較表格
    if comparison_data:
        table = wandb.Table(
            columns=list(comparison_data[0].keys()),
            data=[list(d.values()) for d in comparison_data]
        )

        wandb.log({"model_comparison": table})

        print("\n📈 模型比較:")
        print(f"   共 {len(comparison_data)} 個版本")

        for data in comparison_data:
            print(f"\n   版本 {data['version']}:")
            print(f"     損失: {data['loss']}")
            print(f"     參數量: {data['num_parameters']}")

    wandb.finish()


# ============================================================================
# 第七部分：模型註冊表最佳實踐
# ============================================================================

def model_registry_best_practices():
    """
    模型註冊表最佳實踐

    展示組織和管理模型註冊表的最佳實踐。
    """
    print("\n" + "="*60)
    print("模型註冊表最佳實踐")
    print("="*60)

    run = wandb.init(
        project="model-versioning",
        name="best-practices",
        job_type="train"
    )

    print("\n✅ 最佳實踐示例:")

    # 1. 使用語義化版本號
    print("\n1. 語義化版本號和標籤")

    model = ModelV1()
    model_path = "/tmp/best_practice_model.pth"
    torch.save(model.state_dict(), model_path)

    # 創建工件時使用詳細的元數據
    artifact = wandb.Artifact(
        name="production-model",
        type="model",
        description="生產環境分類模型",
        metadata={
            # 版本信息
            "semantic_version": "1.2.0",
            "changelog": "修復了過擬合問題",

            # 性能指標
            "metrics": {
                "accuracy": 0.95,
                "f1_score": 0.93,
                "inference_time_ms": 15
            },

            # 訓練信息
            "training": {
                "epochs": 50,
                "batch_size": 32,
                "learning_rate": 0.001
            },

            # 環境信息
            "environment": {
                "framework": "PyTorch",
                "python_version": "3.10",
                "cuda_version": "11.8"
            },

            # 數據信息
            "data": {
                "training_samples": 10000,
                "validation_samples": 2000,
                "data_version": "v2.1"
            },

            # 審批信息
            "approval": {
                "status": "approved",
                "reviewer": "data-scientist-team",
                "date": datetime.now().isoformat()
            }
        }
    )

    artifact.add_file(model_path)
    run.log_artifact(artifact)

    print("   ✓ 使用詳細的元數據")
    print("   ✓ 記錄性能指標")
    print("   ✓ 追蹤環境信息")
    print("   ✓ 包含審批流程")

    # 2. 使用別名管理部署階段
    print("\n2. 使用別名管理部署階段")
    print("   ✓ development - 開發版本")
    print("   ✓ staging - 預發布版本")
    print("   ✓ production - 生產版本")
    print("   ✓ deprecated - 已棄用版本")

    # 3. 文檔和README
    print("\n3. 為模型添加文檔")

    readme_content = """
# Production Classification Model v1.2.0

## 概述
這是用於生產環境的分類模型，已通過所有性能和安全測試。

## 性能
- 準確率: 95%
- F1 分數: 93%
- 推理時間: 15ms

## 使用方法
```python
model = load_model("production-model:production")
predictions = model.predict(data)
```

## 變更日誌
### v1.2.0
- 修復過擬合問題
- 提升驗證集準確率 3%
- 優化推理速度

## 審批
- 審批人: Data Science Team
- 審批日期: 2025-01-01
- 狀態: 已批準
"""

    readme_path = "/tmp/MODEL_README.md"
    with open(readme_path, 'w') as f:
        f.write(readme_content)

    artifact.add_file(readme_path, name="README.md")
    print("   ✓ 添加了 README.md")

    os.remove(model_path)
    os.remove(readme_path)

    wandb.finish()

    print("\n💡 遵循這些最佳實踐可以更好地管理模型生命週期")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：運行所有示例
    """
    print("\n" + "="*70)
    print("Weights & Biases 模型版本管理示例")
    print("="*70)

    try:
        # 1. 創建模型工件
        create_model_artifact()

        # 2. 版本管理
        version_management()

        # 3. 下載和加載
        download_and_load_model()

        # 4. 血統追蹤
        model_lineage_tracking()

        # 5. 模型比較
        # compare_models()  # 需要已有的工件

        # 6. 最佳實踐
        model_registry_best_practices()

        print("\n" + "="*70)
        print("✅ 所有模型版本管理示例完成！")
        print("="*70)
        print("\n💡 提示:")
        print("   - 使用語義化版本號")
        print("   - 添加詳細的元數據和文檔")
        print("   - 使用別名管理不同部署階段")
        print("   - 追蹤模型血統和依賴關係")
        print("   - 定期審查和清理舊版本")

    except Exception as e:
        print(f"\n❌ 運行示例時出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
