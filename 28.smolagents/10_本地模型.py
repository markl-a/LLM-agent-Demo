"""
本地模型 - 使用 Ollama 和開源模型
================================

不想依賴雲端 API？使用本地模型！
smolagents 支持 Ollama 等本地部署方案。

本範例展示：
1. 使用 Ollama 模型
2. 使用 Hugging Face 模型
3. 自定義模型接口
4. 性能優化
5. 本地部署最佳實踐
"""

from smolagents import CodeAgent, tool
import os


# ============================================================================
# 範例 1: 為什麼使用本地模型
# ============================================================================

def example_1_why_local_models():
    """為什麼使用本地模型"""
    print("\n" + "="*70)
    print("範例 1: 為什麼使用本地模型")
    print("="*70)

    print("\n本地模型的優勢：\n")

    advantages = [
        ("隱私保護", "數據不離開本地，完全私密"),
        ("成本控制", "無 API 調用費用，一次性硬件投資"),
        ("無限使用", "不受 API 配額限制"),
        ("離線工作", "不需要網絡連接"),
        ("自定義", "可以微調模型以適應特定任務"),
        ("延遲", "本地推理可能更快（取決於硬件）"),
    ]

    for advantage, description in advantages:
        print(f"✓ {advantage}")
        print(f"  {description}\n")

    print("適用場景：")
    print("  - 處理敏感數據")
    print("  - 企業內部部署")
    print("  - 開發和測試")
    print("  - 成本敏感的應用")
    print("  - 離線環境")


# ============================================================================
# 範例 2: 使用 Ollama
# ============================================================================

def example_2_ollama():
    """使用 Ollama 運行本地模型"""
    print("\n" + "="*70)
    print("範例 2: 使用 Ollama")
    print("="*70)

    print("\nOllama 是最簡單的本地模型方案\n")

    print("1. 安裝 Ollama")
    print("   訪問 https://ollama.ai")
    print("   下載並安裝適合您系統的版本")

    print("\n2. 下載模型")
    print("   ollama pull llama3.2        # Meta Llama 3.2")
    print("   ollama pull mistral         # Mistral")
    print("   ollama pull codellama       # Code Llama")
    print("   ollama pull qwen2.5:7b      # Qwen 2.5")

    print("\n3. 在 smolagents 中使用")
    print("```python")
    print("from smolagents import CodeAgent, LiteLLMModel, tool")
    print("")
    print("# 創建 Ollama 模型接口")
    print("model = LiteLLMModel(")
    print("    model_id='ollama/llama3.2',  # Ollama 模型")
    print("    api_base='http://localhost:11434'  # Ollama 服務地址")
    print(")")
    print("")
    print("# 準備工具")
    print("@tool")
    print("def calculator(a: int, b: int, op: str) -> int:")
    print("    if op == 'add': return a + b")
    print("    elif op == 'sub': return a - b")
    print("    elif op == 'mul': return a * b")
    print("    elif op == 'div': return a // b if b != 0 else 0")
    print("")
    print("# 創建 Agent")
    print("agent = CodeAgent(")
    print("    tools=[calculator],")
    print("    model=model,")
    print("    max_steps=5")
    print(")")
    print("")
    print("# 運行任務")
    print("result = agent.run('計算 (15 + 25) * 3')")
    print("print(result)")
    print("```")

    print("\n推薦的 Ollama 模型：")
    models = [
        ("llama3.2:3b", "小型，快速，8GB RAM"),
        ("llama3.2:7b", "中型，平衡，16GB RAM"),
        ("mistral:7b", "優秀性能，16GB RAM"),
        ("qwen2.5:7b", "多語言支持，16GB RAM"),
        ("codellama:7b", "代碼專用，16GB RAM"),
    ]

    for model, desc in models:
        print(f"  - {model}: {desc}")


# ============================================================================
# 範例 3: 使用 Hugging Face 本地模型
# ============================================================================

def example_3_huggingface_local():
    """使用 Hugging Face 本地部署"""
    print("\n" + "="*70)
    print("範例 3: Hugging Face 本地部署")
    print("="*70)

    print("\n使用 transformers 庫運行本地模型\n")

    print("1. 安裝依賴")
    print("   pip install transformers torch accelerate")

    print("\n2. 創建自定義模型類")
    print("```python")
    print("from smolagents import Model")
    print("from transformers import pipeline")
    print("")
    print("class HuggingFaceLocalModel(Model):")
    print("    def __init__(self, model_id: str):")
    print("        self.pipe = pipeline(")
    print("            'text-generation',")
    print("            model=model_id,")
    print("            device_map='auto'  # 自動選擇 GPU/CPU")
    print("        )")
    print("    ")
    print("    def __call__(self, messages, **kwargs):")
    print("        # 將消息轉換為提示")
    print("        prompt = self._format_messages(messages)")
    print("        ")
    print("        # 生成響應")
    print("        response = self.pipe(")
    print("            prompt,")
    print("            max_new_tokens=512,")
    print("            temperature=0.7")
    print("        )")
    print("        ")
    print("        return response[0]['generated_text']")
    print("```")

    print("\n3. 使用自定義模型")
    print("```python")
    print("model = HuggingFaceLocalModel('HuggingFaceTB/SmolLM2-1.7B-Instruct')")
    print("agent = CodeAgent(tools=tools, model=model)")
    print("```")

    print("\n推薦的本地模型：")
    models = [
        ("SmolLM2-1.7B", "極小，快速，4GB RAM"),
        ("Llama-3.2-3B", "小型，性能好，8GB RAM"),
        ("Qwen2.5-7B", "中型，多語言，16GB RAM"),
        ("Mistral-7B", "性能優異，16GB RAM"),
    ]

    for model, desc in models:
        print(f"  - {model}: {desc}")


# ============================================================================
# 範例 4: 使用 vLLM 加速推理
# ============================================================================

def example_4_vllm():
    """使用 vLLM 加速本地推理"""
    print("\n" + "="*70)
    print("範例 4: vLLM 加速推理")
    print("="*70)

    print("\nvLLM 是高性能的推理引擎\n")

    print("1. 安裝 vLLM")
    print("   pip install vllm")

    print("\n2. 啟動 vLLM 服務器")
    print("   vllm serve meta-llama/Llama-3.2-3B-Instruct \\")
    print("     --port 8000 \\")
    print("     --gpu-memory-utilization 0.9")

    print("\n3. 在 smolagents 中使用")
    print("```python")
    print("from smolagents import LiteLLMModel")
    print("")
    print("model = LiteLLMModel(")
    print("    model_id='openai/llama-3.2-3b',")
    print("    api_base='http://localhost:8000/v1'")
    print(")")
    print("```")

    print("\nvLLM 優勢：")
    print("  - PagedAttention 提升吞吐量")
    print("  - 連續批處理")
    print("  - 優化的 CUDA 內核")
    print("  - 比標準 transformers 快 10-20 倍")


# ============================================================================
# 範例 5: 模型選擇指南
# ============================================================================

def example_5_model_selection():
    """模型選擇指南"""
    print("\n" + "="*70)
    print("範例 5: 模型選擇指南")
    print("="*70)

    print("\n根據硬件選擇模型：\n")

    hardware_guide = [
        {
            "硬件": "8GB RAM + 集成顯卡",
            "推薦模型": ["SmolLM2-360M", "Llama-3.2-1B"],
            "性能": "基本任務可用"
        },
        {
            "硬件": "16GB RAM",
            "推薦模型": ["Llama-3.2-3B", "Qwen2.5-3B"],
            "性能": "良好性能"
        },
        {
            "硬件": "32GB RAM + RTX 3060",
            "推薦模型": ["Llama-3.2-7B", "Mistral-7B", "Qwen2.5-7B"],
            "性能": "優秀性能"
        },
        {
            "硬件": "64GB RAM + RTX 4090",
            "推薦模型": ["Llama-3.1-70B", "Qwen2.5-72B"],
            "性能": "接近 GPT-4"
        },
    ]

    for guide in hardware_guide:
        print(f"{guide['硬件']}")
        print(f"  推薦: {', '.join(guide['推薦模型'])}")
        print(f"  性能: {guide['性能']}\n")

    print("任務類型建議：")
    print("  - 簡單對話：3B 模型足夠")
    print("  - 代碼生成：使用 CodeLlama 或 Qwen-Coder")
    print("  - 複雜推理：7B 以上模型")
    print("  - 多語言：Qwen2.5 系列")


# ============================================================================
# 範例 6: 性能優化技巧
# ============================================================================

def example_6_performance_optimization():
    """性能優化技巧"""
    print("\n" + "="*70)
    print("範例 6: 性能優化")
    print("="*70)

    print("\n1. 量化模型")
    print("   - 4-bit 量化：節省 75% 內存")
    print("   - 8-bit 量化：節省 50% 內存")
    print("   - 使用 GPTQ 或 AWQ")

    print("\n   ```bash")
    print("   # Ollama 自動使用量化")
    print("   ollama pull llama3.2:3b-q4_0  # 4-bit 量化")
    print("   ```")

    print("\n2. 批處理")
    print("   - 對多個請求進行批處理")
    print("   - vLLM 自動優化批處理")

    print("\n3. KV 緩存")
    print("   - 緩存注意力鍵值")
    print("   - 減少重複計算")

    print("\n4. Flash Attention")
    print("   - 使用優化的注意力實現")
    print("   - 提升速度，減少內存")

    print("\n5. 硬件加速")
    print("   - 使用 GPU 推理")
    print("   - 多 GPU 並行（對大模型）")
    print("   - Apple Silicon：使用 MLX")

    print("\n6. 模型緩存")
    print("   - 保持模型在內存中")
    print("   - 避免重複載入")


# ============================================================================
# 範例 7: 本地部署最佳實踐
# ============================================================================

def example_7_best_practices():
    """本地部署最佳實踐"""
    print("\n" + "="*70)
    print("範例 7: 本地部署最佳實踐")
    print("="*70)

    print("\n1. 開發環境")
    print("   - 使用較小模型（3B）")
    print("   - 快速迭代")
    print("   - Ollama 最簡單")

    print("\n2. 生產環境")
    print("   - 使用 vLLM 或 TGI")
    print("   - 適當的監控")
    print("   - 負載均衡")

    print("\n3. 資源管理")
    print("   - 監控內存使用")
    print("   - 設置請求超時")
    print("   - 限制並發請求")

    print("\n4. 模型更新")
    print("   - 定期更新模型")
    print("   - 測試新版本")
    print("   - 保持回滾能力")

    print("\n5. 安全考慮")
    print("   - 限制模型訪問")
    print("   - 輸入驗證")
    print("   - 輸出過濾")

    print("\n6. 備份方案")
    print("   - 準備雲端 API 備份")
    print("   - 模型失敗時降級")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*70)
    print("本地模型 - 使用 Ollama 和開源模型")
    print("="*70)

    examples = [
        ("範例 1: 為什麼使用本地模型", example_1_why_local_models),
        ("範例 2: 使用 Ollama", example_2_ollama),
        ("範例 3: Hugging Face 本地", example_3_huggingface_local),
        ("範例 4: vLLM 加速", example_4_vllm),
        ("範例 5: 模型選擇", example_5_model_selection),
        ("範例 6: 性能優化", example_6_performance_optimization),
        ("範例 7: 最佳實踐", example_7_best_practices),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n{name} 執行失敗: {e}")

    print("\n" + "="*70)
    print("本地模型完成！")
    print("="*70)

    print("\n關鍵要點：")
    print("  - Ollama 是最簡單的本地方案")
    print("  - 根據硬件選擇合適模型")
    print("  - vLLM 提供最佳性能")
    print("  - 量化節省內存")
    print("  - 本地部署適合隱私和成本敏感場景")

    print("\n下一步: 查看 11_流式輸出.py 學習流式響應處理")


if __name__ == "__main__":
    main()
