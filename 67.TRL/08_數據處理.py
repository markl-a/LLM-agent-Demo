"""
TRL 數據處理與準備

這個文件演示了 TRL 訓練的數據處理，包括：
1. 不同訓練方法的數據格式
2. 數據加載與預處理
3. 數據質量控制
4. 數據增強技巧
5. 自定義數據集創建

高質量的數據是成功訓練的關鍵，
這個文件提供了完整的數據處理流程。
"""

import os
import sys
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
import warnings
import json

warnings.filterwarnings('ignore')


def explain_data_formats():
    """
    解釋不同訓練方法的數據格式
    """
    print("\n" + "=" * 60)
    print("TRL 訓練數據格式")
    print("=" * 60)

    explanation = """
1. SFT (Supervised Fine-Tuning) 數據格式:

   格式 A: 單一文本字段
   {
       "text": "### Human: 問題\\n### Assistant: 回答"
   }

   格式 B: 分離的輸入輸出
   {
       "prompt": "### Human: 問題\\n### Assistant:",
       "completion": "回答"
   }

   格式 C: 對話格式
   {
       "messages": [
           {"role": "user", "content": "問題"},
           {"role": "assistant", "content": "回答"}
       ]
   }

2. 獎勵模型數據格式:

   成對比較格式:
   {
       "prompt": "問題",
       "chosen": "好的回答",
       "rejected": "差的回答"
   }

   注意:
   • chosen 應該明顯優於 rejected
   • 差異要有意義（不要太接近）
   • 保持格式一致性

3. DPO/ORPO 數據格式:

   與獎勵模型相同:
   {
       "prompt": "問題",
       "chosen": "偏好的回答",
       "rejected": "不偏好的回答"
   }

   質量要求:
   • chosen 要明確更好
   • rejected 不一定是錯誤，只是相對較差
   • 避免主觀性太強的比較

4. PPO 數據格式:

   查詢列表:
   [
       "問題 1",
       "問題 2",
       ...
   ]

   注意:
   • 只需要問題/提示
   • 回答由模型生成
   • 獎勵由獎勵模型評分

5. 通用最佳實踐:

   ✓ 格式統一: 保持所有樣本格式一致
   ✓ 長度控制: 避免過長或過短
   ✓ 質量把控: 移除低質量樣本
   ✓ 平衡性: 保持不同類型的平衡
   ✓ 多樣性: 涵蓋不同主題和風格
"""

    print(explanation)


def load_sft_dataset(dataset_path: Optional[str] = None):
    """
    加載和準備 SFT 數據集

    Args:
        dataset_path: 數據集路徑（可選）

    Returns:
        Dataset: 處理後的數據集
    """
    print("\n" + "=" * 60)
    print("加載 SFT 數據集")
    print("=" * 60)

    try:
        from datasets import Dataset, load_dataset

        if dataset_path:
            # 從文件加載
            print(f"從文件加載: {dataset_path}")
            if dataset_path.endswith('.json'):
                with open(dataset_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                dataset = Dataset.from_dict(data)
            elif dataset_path.endswith('.jsonl'):
                data = []
                with open(dataset_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        data.append(json.loads(line))
                dataset = Dataset.from_list(data)
            else:
                dataset = load_dataset(dataset_path, split="train")
        else:
            # 創建示例數據
            print("創建示例 SFT 數據集")
            data = {
                "text": [
                    "### Human: 什麼是機器學習？\n### Assistant: 機器學習是人工智能的一個分支，它使用算法和統計模型讓計算機從數據中學習和改進。",
                    "### Human: Python 的優點是什麼？\n### Assistant: Python 語法簡潔、生態豐富、社區活躍，特別適合數據科學和機器學習。",
                    "### Human: 如何開始學習 AI？\n### Assistant: 建議先學習 Python 編程，然後學習機器學習理論，最後通過實際項目鞏固知識。",
                    "### Human: 什麼是深度學習？\n### Assistant: 深度學習使用多層神經網絡學習數據的複雜特徵表示，是機器學習的一個子領域。",
                    "### Human: GPU 在深度學習中的作用？\n### Assistant: GPU 通過並行計算大幅加速深度學習訓練，相比 CPU 可以提升 10-100 倍速度。",
                ]
            }
            dataset = Dataset.from_dict(data)

        print(f"✓ 數據集加載成功: {len(dataset)} 個樣本")

        # 顯示樣本
        print(f"\n樣本示例:")
        print("-" * 60)
        print(dataset[0]["text"])
        print("-" * 60)

        return dataset

    except Exception as e:
        print(f"✗ 加載數據集失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def load_preference_dataset(dataset_path: Optional[str] = None):
    """
    加載和準備偏好數據集（用於 DPO/ORPO/獎勵模型）

    Args:
        dataset_path: 數據集路徑（可選）

    Returns:
        Dataset: 處理後的數據集
    """
    print("\n" + "=" * 60)
    print("加載偏好數據集")
    print("=" * 60)

    try:
        from datasets import Dataset

        if dataset_path:
            # 從文件加載
            print(f"從文件加載: {dataset_path}")
            with open(dataset_path, 'r', encoding='utf-8') as f:
                if dataset_path.endswith('.json'):
                    data = json.load(f)
                else:
                    data = [json.loads(line) for line in f]
            dataset = Dataset.from_list(data) if isinstance(data, list) else Dataset.from_dict(data)
        else:
            # 創建示例數據
            print("創建示例偏好數據集")
            data = {
                "prompt": [
                    "### Human: 什麼是機器學習？\n### Assistant:",
                    "### Human: Python 有什麼優點？\n### Assistant:",
                    "### Human: 如何學習 AI？\n### Assistant:",
                    "### Human: 什麼是深度學習？\n### Assistant:",
                    "### Human: GPU 的作用？\n### Assistant:",
                ],
                "chosen": [
                    "機器學習是人工智能的分支，通過算法和統計模型讓計算機從數據中學習。主要包括監督學習、無監督學習和強化學習。",
                    "Python 語法簡潔易學、擁有豐富的第三方庫、社區支持強大，特別適合數據科學和機器學習領域。",
                    "建議的學習路徑：先掌握 Python 編程基礎，然後學習數學基礎（線性代數、微積分、概率論），接著學習機器學習理論，最後通過實際項目鞏固。",
                    "深度學習是機器學習的子領域，使用多層神經網絡學習數據的複雜特徵表示。在圖像識別、語音識別、NLP 等領域取得突破。",
                    "GPU 通過並行計算架構大幅加速深度學習訓練。相比 CPU，GPU 可以將訓練速度提升 10-100 倍，是訓練大模型的關鍵硬件。",
                ],
                "rejected": [
                    "機器學習就是讓機器學習的技術。",
                    "Python 很好用。",
                    "直接開始學就可以了。",
                    "深度學習就是很深的學習。",
                    "GPU 是用來打遊戲的。",
                ],
            }
            dataset = Dataset.from_dict(data)

        print(f"✓ 偏好數據集加載成功: {len(dataset)} 個樣本")

        # 驗證數據格式
        required_fields = ["prompt", "chosen", "rejected"]
        if all(field in dataset.column_names for field in required_fields):
            print("✓ 數據格式驗證通過")
        else:
            print(f"⚠️  缺少必要字段: {required_fields}")

        # 顯示樣本
        print(f"\n樣本示例:")
        print("-" * 60)
        print(f"Prompt: {dataset[0]['prompt']}")
        print(f"Chosen: {dataset[0]['chosen'][:60]}...")
        print(f"Rejected: {dataset[0]['rejected'][:60]}...")
        print("-" * 60)

        return dataset

    except Exception as e:
        print(f"✗ 加載數據集失敗: {e}")
        import traceback
        traceback.print_exc()
        return None


def validate_data_quality(dataset, data_type: str = "sft"):
    """
    驗證數據質量

    Args:
        dataset: 數據集
        data_type: 數據類型（"sft" 或 "preference"）

    Returns:
        dict: 質量報告
    """
    print("\n" + "=" * 60)
    print("數據質量檢查")
    print("=" * 60)

    report = {
        "total_samples": len(dataset),
        "issues": [],
        "warnings": [],
        "statistics": {}
    }

    try:
        if data_type == "sft":
            # SFT 數據檢查
            text_field = "text"
            if text_field not in dataset.column_names:
                report["issues"].append(f"缺少 '{text_field}' 字段")
                return report

            # 長度統計
            lengths = [len(sample[text_field].split()) for sample in dataset]
            report["statistics"]["avg_length"] = sum(lengths) / len(lengths)
            report["statistics"]["min_length"] = min(lengths)
            report["statistics"]["max_length"] = max(lengths)

            # 檢查異常
            too_short = sum(1 for l in lengths if l < 10)
            too_long = sum(1 for l in lengths if l > 500)

            if too_short > 0:
                report["warnings"].append(f"{too_short} 個樣本過短（< 10 詞）")
            if too_long > 0:
                report["warnings"].append(f"{too_long} 個樣本過長（> 500 詞）")

        elif data_type == "preference":
            # 偏好數據檢查
            required_fields = ["prompt", "chosen", "rejected"]
            missing_fields = [f for f in required_fields if f not in dataset.column_names]

            if missing_fields:
                report["issues"].append(f"缺少字段: {missing_fields}")
                return report

            # 長度統計
            chosen_lengths = [len(sample["chosen"].split()) for sample in dataset]
            rejected_lengths = [len(sample["rejected"].split()) for sample in dataset]

            report["statistics"]["avg_chosen_length"] = sum(chosen_lengths) / len(chosen_lengths)
            report["statistics"]["avg_rejected_length"] = sum(rejected_lengths) / len(rejected_lengths)

            # 檢查 chosen 是否明顯更長（通常更詳細的回答更好）
            longer_chosen = sum(1 for c, r in zip(chosen_lengths, rejected_lengths) if c > r)
            report["statistics"]["chosen_longer_ratio"] = longer_chosen / len(dataset)

            # 檢查是否有相同的 chosen 和 rejected
            same_count = sum(1 for sample in dataset if sample["chosen"] == sample["rejected"])
            if same_count > 0:
                report["issues"].append(f"{same_count} 個樣本的 chosen 和 rejected 相同")

        # 打印報告
        print(f"\n總樣本數: {report['total_samples']}")

        print(f"\n統計信息:")
        for key, value in report["statistics"].items():
            print(f"  {key}: {value:.2f}" if isinstance(value, float) else f"  {key}: {value}")

        if report["issues"]:
            print(f"\n❌ 發現 {len(report['issues'])} 個問題:")
            for issue in report["issues"]:
                print(f"  • {issue}")

        if report["warnings"]:
            print(f"\n⚠️  {len(report['warnings'])} 個警告:")
            for warning in report["warnings"]:
                print(f"  • {warning}")

        if not report["issues"] and not report["warnings"]:
            print("\n✓ 數據質量良好")

        return report

    except Exception as e:
        print(f"✗ 質量檢查失敗: {e}")
        import traceback
        traceback.print_exc()
        return report


def filter_and_clean_dataset(dataset, data_type: str = "sft", min_length: int = 10, max_length: int = 512):
    """
    過濾和清理數據集

    Args:
        dataset: 原始數據集
        data_type: 數據類型
        min_length: 最小長度（詞數）
        max_length: 最大長度（詞數）

    Returns:
        Dataset: 清理後的數據集
    """
    print("\n" + "=" * 60)
    print("過濾和清理數據集")
    print("=" * 60)

    try:
        original_size = len(dataset)

        if data_type == "sft":
            # 過濾 SFT 數據
            def filter_fn(sample):
                text = sample.get("text", "")
                word_count = len(text.split())
                return min_length <= word_count <= max_length

            dataset = dataset.filter(filter_fn)

        elif data_type == "preference":
            # 過濾偏好數據
            def filter_fn(sample):
                prompt = sample.get("prompt", "")
                chosen = sample.get("chosen", "")
                rejected = sample.get("rejected", "")

                # 檢查長度
                chosen_len = len(chosen.split())
                rejected_len = len(rejected.split())

                # 檢查是否相同
                if chosen == rejected:
                    return False

                # 檢查長度範圍
                if chosen_len < min_length or chosen_len > max_length:
                    return False
                if rejected_len < min_length or rejected_len > max_length:
                    return False

                return True

            dataset = dataset.filter(filter_fn)

        filtered_size = len(dataset)
        removed = original_size - filtered_size

        print(f"原始樣本數: {original_size}")
        print(f"過濾後樣本數: {filtered_size}")
        print(f"移除樣本數: {removed} ({100 * removed / original_size:.1f}%)")

        return dataset

    except Exception as e:
        print(f"✗ 過濾失敗: {e}")
        import traceback
        traceback.print_exc()
        return dataset


def augment_sft_data(dataset, augmentation_factor: int = 2):
    """
    數據增強（簡單示例）

    Args:
        dataset: 原始數據集
        augmentation_factor: 增強倍數

    Returns:
        Dataset: 增強後的數據集
    """
    print("\n" + "=" * 60)
    print("數據增強")
    print("=" * 60)

    try:
        from datasets import Dataset

        print(f"增強倍數: {augmentation_factor}x")

        # 簡單的增強策略：變換格式
        augmented_data = []

        for sample in dataset:
            text = sample.get("text", "")

            # 原始樣本
            augmented_data.append({"text": text})

            # 增強樣本（這裡只是示例，實際應用中可以使用更複雜的策略）
            if augmentation_factor > 1:
                # 策略 1: 添加變體（實際中可以用同義詞替換、句子重組等）
                augmented_data.append({"text": text})  # 簡化示例

        augmented_dataset = Dataset.from_list(augmented_data[:len(dataset) * augmentation_factor])

        print(f"原始樣本數: {len(dataset)}")
        print(f"增強後樣本數: {len(augmented_dataset)}")

        print("\n注意: 這是簡化示例。實際增強策略包括:")
        print("  • 同義詞替換")
        print("  • 句子重組")
        print("  • 回譯（翻譯到其他語言再翻譯回來）")
        print("  • 使用 LLM 生成變體")

        return augmented_dataset

    except Exception as e:
        print(f"✗ 數據增強失敗: {e}")
        import traceback
        traceback.print_exc()
        return dataset


def split_dataset(dataset, train_ratio: float = 0.9, seed: int = 42):
    """
    分割數據集為訓練集和驗證集

    Args:
        dataset: 數據集
        train_ratio: 訓練集比例
        seed: 隨機種子

    Returns:
        tuple: (train_dataset, eval_dataset)
    """
    print("\n" + "=" * 60)
    print("分割數據集")
    print("=" * 60)

    try:
        split = dataset.train_test_split(test_size=1-train_ratio, seed=seed)
        train_dataset = split["train"]
        eval_dataset = split["test"]

        print(f"總樣本數: {len(dataset)}")
        print(f"訓練集: {len(train_dataset)} ({100*train_ratio:.0f}%)")
        print(f"驗證集: {len(eval_dataset)} ({100*(1-train_ratio):.0f}%)")

        return train_dataset, eval_dataset

    except Exception as e:
        print(f"✗ 分割失敗: {e}")
        import traceback
        traceback.print_exc()
        return dataset, None


def save_dataset(dataset, output_path: str, format: str = "json"):
    """
    保存數據集

    Args:
        dataset: 數據集
        output_path: 輸出路徑
        format: 格式（"json" 或 "jsonl"）
    """
    print("\n" + "=" * 60)
    print("保存數據集")
    print("=" * 60)

    try:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        if format == "json":
            # 保存為 JSON
            data = {key: dataset[key] for key in dataset.column_names}
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        elif format == "jsonl":
            # 保存為 JSONL
            with open(output_path, 'w', encoding='utf-8') as f:
                for sample in dataset:
                    f.write(json.dumps(sample, ensure_ascii=False) + '\n')

        print(f"✓ 數據集已保存到: {output_path}")
        print(f"  格式: {format}")
        print(f"  樣本數: {len(dataset)}")

        # 顯示文件大小
        file_size = os.path.getsize(output_path)
        print(f"  文件大小: {file_size / 1024:.2f} KB")

    except Exception as e:
        print(f"✗ 保存失敗: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_data_pipeline():
    """
    演示完整的數據處理流程
    """
    print("\n" + "=" * 60)
    print("完整數據處理流程示例")
    print("=" * 60)

    pipeline = """
標準數據處理流程:

1. 數據收集
   ├── 從公開數據集下載
   ├── 使用 API 收集
   ├── 人工標註
   └── 合成數據生成

2. 數據清理
   ├── 移除重複項
   ├── 過濾低質量樣本
   ├── 統一格式
   └── 處理缺失值

3. 數據驗證
   ├── 檢查格式正確性
   ├── 驗證字段完整性
   ├── 統計分析
   └── 質量評估

4. 數據增強（可選）
   ├── 同義詞替換
   ├── 句子重組
   ├── 回譯
   └── LLM 生成變體

5. 數據分割
   ├── 訓練集（80-90%）
   ├── 驗證集（10-15%）
   └── 測試集（5-10%）

6. 數據保存
   ├── JSON/JSONL 格式
   ├── Parquet 格式（大數據）
   └── HuggingFace Dataset 格式

質量控制檢查清單:
✓ 數據格式統一
✓ 無重複樣本
✓ 長度在合理範圍
✓ 無明顯錯誤
✓ 類別平衡（如適用）
✓ 多樣性足夠
✓ 標註一致性（偏好數據）
"""

    print(pipeline)


def main():
    """
    主函數：演示完整的數據處理流程
    """
    print("=" * 60)
    print("TRL 數據處理與準備")
    print("=" * 60)

    # 1. 解釋數據格式
    explain_data_formats()

    # 2. 加載 SFT 數據集
    sft_dataset = load_sft_dataset()
    if sft_dataset:
        # 驗證質量
        validate_data_quality(sft_dataset, data_type="sft")

        # 過濾清理
        sft_dataset = filter_and_clean_dataset(sft_dataset, data_type="sft")

        # 分割數據集
        train_sft, eval_sft = split_dataset(sft_dataset)

    # 3. 加載偏好數據集
    pref_dataset = load_preference_dataset()
    if pref_dataset:
        # 驗證質量
        validate_data_quality(pref_dataset, data_type="preference")

        # 過濾清理
        pref_dataset = filter_and_clean_dataset(pref_dataset, data_type="preference")

        # 分割數據集
        train_pref, eval_pref = split_dataset(pref_dataset)

    # 4. 演示數據處理流程
    demonstrate_data_pipeline()

    # 5. 保存示例（可選）
    # if train_sft:
    #     save_dataset(train_sft, "./data/sft_train.json", format="json")
    # if train_pref:
    #     save_dataset(train_pref, "./data/preference_train.jsonl", format="jsonl")

    # 6. 總結
    print("\n" + "=" * 60)
    print("數據處理演示完成！")
    print("=" * 60)

    print("\n數據處理的重要性:")
    print("  • 數據質量直接影響模型性能")
    print("  • 垃圾進，垃圾出（GIGO）")
    print("  • 花時間在數據上比調參更有效")

    print("\n數據收集建議:")
    print("  • 優先使用高質量公開數據集")
    print("  • 人工標註要保證一致性")
    print("  • 偏好數據要有明確的質量差異")
    print("  • 定期審查和更新數據")

    print("\n常用數據集:")
    print("  • OpenAssistant - 多語言對話數據")
    print("  • Anthropic HH-RLHF - 偏好數據")
    print("  • ShareGPT - 對話數據")
    print("  • Dolly - 指令數據")

    print("\n工具推薦:")
    print("  • datasets - HuggingFace 數據集庫")
    print("  • pandas - 數據分析")
    print("  • dvc - 數據版本控制")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行出錯: {e}")
        import traceback
        traceback.print_exc()
