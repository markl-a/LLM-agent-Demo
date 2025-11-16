#!/usr/bin/env python3
"""
使用 Gemini API 來生成和增強教程內容的輔助腳本
"""

import google.generativeai as genai
import os
import json

# 配置 Gemini API
GEMINI_API_KEY = "AIzaSyCdEHuSZdPmppwd6xQWeZxJIUVT5UJmXHc"
genai.configure(api_key=GEMINI_API_KEY)

# 使用 Gemini 1.5 Flash（免費且快速）
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_tutorial_content(topic, framework, tutorial_type="beginner"):
    """
    使用 Gemini 生成教程內容

    Args:
        topic: 教程主題
        framework: 框架名稱
        tutorial_type: 教程類型（beginner, intermediate, advanced）

    Returns:
        生成的內容字符串
    """
    prompt = f"""
請為以下主題生成一個詳細的 Jupyter Notebook 教程內容（繁體中文）：

框架: {framework}
主題: {topic}
難度: {tutorial_type}

請包括：
1. 清晰的學習目標
2. 完整的可執行代碼範例
3. 詳細的註解說明
4. 實際應用場景
5. 常見問題和解決方案
6. 最佳實踐建議

格式要求：
- 使用 Markdown 格式
- 代碼塊使用 ```python
- 包含實際可運行的範例
- 避免過於理論化，注重實踐

請直接輸出教程內容，不需要額外的解釋。
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"生成內容時出錯: {e}")
        return None

def enhance_readme(framework_name, current_content=""):
    """增強 README 內容"""
    prompt = f"""
請為 {framework_name} 框架生成一個詳細的 README.md 內容（繁體中文）。

當前內容:
{current_content}

請包括：
1. 框架簡介和核心特性
2. 與其他框架的對比
3. 安裝指南
4. 快速開始範例
5. 學習路徑建議
6. 實際應用場景
7. 相關資源鏈接

請使用 Markdown 格式，內容要專業、實用、易懂。
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"增強 README 時出錯: {e}")
        return None

def generate_comparison_doc():
    """生成框架對比文檔"""
    prompt = """
請生成一份詳細的 LLM Agent 框架對比文檔（繁體中文），對比以下框架：
- LangChain
- LlamaIndex
- AutoGen
- CrewAI
- MetaGPT
- LangGraph

對比維度：
1. 核心功能和定位
2. 學習曲線和易用性
3. 性能和效率
4. 社區支持和生態系統
5. 適用場景
6. 優缺點分析
7. 選擇建議

請使用 Markdown 表格和列表，內容要客觀、詳細、實用。
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"生成對比文檔時出錯: {e}")
        return None

def generate_best_practices():
    """生成最佳實踐文檔"""
    prompt = """
請生成一份 LLM Agent 開發最佳實踐指南（繁體中文）。

包括：
1. 架構設計原則
2. 性能優化技巧
3. 錯誤處理和調試
4. 安全性考慮
5. 成本控制策略
6. 測試和驗證
7. 生產環境部署
8. 監控和維護

請使用 Markdown 格式，提供具體的代碼範例和實踐建議。
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"生成最佳實踐時出錯: {e}")
        return None

if __name__ == "__main__":
    print("Gemini 內容生成輔助腳本已準備就緒")
    print("使用範例:")
    print("  from generate_content_helper import generate_tutorial_content")
    print("  content = generate_tutorial_content('快速開始', 'LlamaIndex')")
