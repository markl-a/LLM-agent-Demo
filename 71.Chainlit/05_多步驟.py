"""
Chainlit 多步驟處理示例

本示例展示：
1. Step 組件的使用
2. 嵌套步驟
3. 進度追蹤
4. 執行時間統計
5. 複雜工作流可視化

運行方式：
    chainlit run 05_多步驟.py -w
"""

import chainlit as cl
import asyncio
from datetime import datetime
from typing import List, Dict
import random


# ==================== 會話初始化 ====================

@cl.on_chat_start
async def on_chat_start():
    """初始化聊天會話"""
    try:
        welcome_msg = """
# 🔄 多步驟處理示例

這個示例展示了如何使用 Chainlit 的 Step 組件來可視化複雜的處理流程。

## ✨ 功能特點

- 📊 **步驟追蹤** - 實時顯示執行進度
- ⏱️ **時間統計** - 自動記錄每個步驟的執行時間
- 🔗 **嵌套步驟** - 支持多層次的任務分解
- 📈 **進度可視化** - 直觀展示處理流程

## 🎮 試試這些命令

- `分析數據` - 演示數據分析流程
- `生成報告` - 演示報告生成流程
- `處理文件` - 演示文件處理流程
- `複雜任務` - 演示複雜的嵌套步驟
- `並行任務` - 演示並行處理

**輸入命令開始體驗！** 🚀
        """

        await cl.Message(content=welcome_msg, author="系統").send()

        print("✅ 多步驟處理會話已初始化")

    except Exception as e:
        error_msg = f"❌ 初始化失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 消息處理 ====================

@cl.on_message
async def on_message(message: cl.Message):
    """處理用戶消息"""
    try:
        user_message = message.content.strip().lower()

        # 路由到不同的處理流程
        if "分析數據" in user_message or "analyze" in user_message:
            await analyze_data_workflow()

        elif "生成報告" in user_message or "report" in user_message:
            await generate_report_workflow()

        elif "處理文件" in user_message or "process" in user_message:
            await process_files_workflow()

        elif "複雜任務" in user_message or "complex" in user_message:
            await complex_nested_workflow()

        elif "並行任務" in user_message or "parallel" in user_message:
            await parallel_tasks_workflow()

        else:
            await show_help()

    except Exception as e:
        error_msg = f"❌ 處理失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 工作流示例 1: 數據分析 ====================

async def analyze_data_workflow():
    """
    演示數據分析工作流
    包含多個連續步驟
    """
    try:
        # 步驟 1: 載入數據
        async with cl.Step(name="📥 載入數據") as step:
            step.input = "data.csv"
            await asyncio.sleep(1)  # 模擬處理時間

            # 模擬數據載入
            data_info = {
                "rows": 1000,
                "columns": 15,
                "size": "2.3 MB"
            }

            step.output = f"✅ 成功載入 {data_info['rows']} 行數據"
            step.language = "json"

        # 步驟 2: 數據清洗
        async with cl.Step(name="🧹 數據清洗") as step:
            step.input = f"{data_info['rows']} 行原始數據"
            await asyncio.sleep(1.5)

            # 模擬清洗過程
            cleaned_rows = data_info['rows'] - 50
            step.output = f"""
清洗完成：
- 刪除重複行: 30
- 處理缺失值: 20
- 剩餘有效數據: {cleaned_rows} 行
            """

        # 步驟 3: 特徵工程
        async with cl.Step(name="⚙️ 特徵工程") as step:
            await asyncio.sleep(1.2)

            features = ["特徵A", "特徵B", "特徵C", "特徵D"]
            step.output = f"""
生成特徵：
{chr(10).join(f'- {f}' for f in features)}
總計: {len(features)} 個特徵
            """

        # 步驟 4: 統計分析
        async with cl.Step(name="📊 統計分析") as step:
            await asyncio.sleep(1)

            stats = {
                "均值": 45.6,
                "標準差": 12.3,
                "最大值": 98.2,
                "最小值": 12.1
            }

            step.output = "\n".join(
                f"{k}: {v}" for k, v in stats.items()
            )

        # 完成消息
        await cl.Message(
            content="""
## ✅ 數據分析完成

所有步驟已成功執行！

### 📈 分析結果
- 處理數據: 950 行
- 生成特徵: 4 個
- 統計完成: ✓

你可以在上方查看每個步驟的詳細信息。
            """,
            author="分析引擎"
        ).send()

    except Exception as e:
        await cl.Message(content=f"❌ 分析失敗: {str(e)}").send()


# ==================== 工作流示例 2: 報告生成 ====================

async def generate_report_workflow():
    """
    演示報告生成工作流
    包含嵌套步驟
    """
    try:
        # 主步驟: 生成報告
        async with cl.Step(name="📝 生成報告") as main_step:

            # 子步驟 1: 收集數據
            async with cl.Step(name="📦 收集數據") as substep:
                await asyncio.sleep(0.8)
                substep.output = "收集了 5 個數據源"

            # 子步驟 2: 生成圖表
            async with cl.Step(name="📊 生成圖表") as substep:
                await asyncio.sleep(1.2)

                charts = ["趨勢圖", "餅圖", "柱狀圖"]
                substep.output = f"生成 {len(charts)} 個圖表:\n" + "\n".join(
                    f"- {c}" for c in charts
                )

            # 子步驟 3: 編寫內容
            async with cl.Step(name="✍️ 編寫內容") as substep:
                await asyncio.sleep(1.5)
                substep.output = """
報告章節:
1. 摘要
2. 數據分析
3. 結論
4. 建議

總字數: 2,500 字
                """

            # 子步驟 4: 格式化
            async with cl.Step(name="🎨 格式化") as substep:
                await asyncio.sleep(0.8)
                substep.output = "應用模板並格式化完成"

            main_step.output = "✅ 報告生成成功"

        # 發送完成消息（附帶模擬的報告）
        report_content = """
## 📄 分析報告

### 📊 執行摘要
報告已成功生成，包含以下內容：

### 📈 關鍵發現
1. 數據質量良好
2. 趨勢呈上升態勢
3. 異常值已標記

### 💡 建議
- 建議 A
- 建議 B
- 建議 C

---
*報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
        """

        await cl.Message(content=report_content, author="報告生成器").send()

    except Exception as e:
        await cl.Message(content=f"❌ 報告生成失敗: {str(e)}").send()


# ==================== 工作流示例 3: 文件處理 ====================

async def process_files_workflow():
    """
    演示文件處理工作流
    展示進度追蹤
    """
    try:
        files = [
            "document1.pdf",
            "image1.png",
            "data.csv",
            "report.docx",
            "presentation.pptx"
        ]

        # 主步驟
        async with cl.Step(name=f"📁 處理 {len(files)} 個文件") as main_step:

            processed_count = 0

            # 處理每個文件
            for i, filename in enumerate(files, 1):
                async with cl.Step(name=f"處理 {filename}") as file_step:
                    # 模擬處理時間
                    await asyncio.sleep(random.uniform(0.5, 1.5))

                    # 隨機決定成功或需要注意
                    success = random.random() > 0.2

                    if success:
                        file_step.output = f"✅ 成功處理"
                        processed_count += 1
                    else:
                        file_step.output = f"⚠️ 需要人工檢查"

                # 更新主步驟進度
                main_step.output = f"進度: {i}/{len(files)} ({i/len(files)*100:.0f}%)"

            # 最終統計
            main_step.output = f"""
處理完成:
- 成功: {processed_count}
- 需要檢查: {len(files) - processed_count}
- 總計: {len(files)}
            """

        # 發送摘要
        await cl.Message(
            content=f"""
## ✅ 文件處理完成

**處理結果:**
- ✓ 成功處理: {processed_count} 個
- ⚠ 需要檢查: {len(files) - processed_count} 個

所有文件已處理完畢！
            """,
            author="文件處理器"
        ).send()

    except Exception as e:
        await cl.Message(content=f"❌ 處理失敗: {str(e)}").send()


# ==================== 工作流示例 4: 複雜嵌套 ====================

async def complex_nested_workflow():
    """
    演示複雜的多層嵌套步驟
    """
    try:
        async with cl.Step(name="🎯 主任務") as level1:

            async with cl.Step(name="📋 階段 1: 準備") as level2_1:
                await asyncio.sleep(0.5)

                async with cl.Step(name="檢查環境") as level3:
                    await asyncio.sleep(0.3)
                    level3.output = "✅ 環境正常"

                async with cl.Step(name="載入配置") as level3:
                    await asyncio.sleep(0.3)
                    level3.output = "✅ 配置已載入"

                level2_1.output = "準備階段完成"

            async with cl.Step(name="⚙️ 階段 2: 執行") as level2_2:
                await asyncio.sleep(0.5)

                async with cl.Step(name="初始化") as level3:
                    await asyncio.sleep(0.4)
                    level3.output = "✅ 初始化完成"

                async with cl.Step(name="主要處理") as level3:
                    await asyncio.sleep(0.6)

                    async with cl.Step(name="子任務 A") as level4:
                        await asyncio.sleep(0.3)
                        level4.output = "完成"

                    async with cl.Step(name="子任務 B") as level4:
                        await asyncio.sleep(0.3)
                        level4.output = "完成"

                    level3.output = "所有子任務完成"

                level2_2.output = "執行階段完成"

            async with cl.Step(name="✅ 階段 3: 完成") as level2_3:
                await asyncio.sleep(0.5)

                async with cl.Step(name="驗證結果") as level3:
                    await asyncio.sleep(0.3)
                    level3.output = "✅ 驗證通過"

                async with cl.Step(name="保存輸出") as level3:
                    await asyncio.sleep(0.3)
                    level3.output = "✅ 已保存"

                level2_3.output = "完成階段完成"

            level1.output = "🎉 所有任務成功完成！"

        await cl.Message(
            content="""
## 🎉 複雜任務執行完成

展示了多層嵌套的步驟結構：
- 3 個主要階段
- 多個子步驟
- 最深 4 層嵌套

所有步驟都已成功執行！
            """,
            author="任務調度器"
        ).send()

    except Exception as e:
        await cl.Message(content=f"❌ 執行失敗: {str(e)}").send()


# ==================== 工作流示例 5: 並行任務 ====================

async def parallel_tasks_workflow():
    """
    演示並行任務處理
    注意：Chainlit Steps 是順序執行的，這裡用邏輯模擬並行
    """
    try:
        # 主步驟
        async with cl.Step(name="🚀 並行處理") as main_step:

            # 模擬啟動多個並行任務
            tasks = [
                {"name": "任務 A", "duration": 1.0},
                {"name": "任務 B", "duration": 1.2},
                {"name": "任務 C", "duration": 0.8},
                {"name": "任務 D", "duration": 1.5},
            ]

            main_step.output = f"啟動 {len(tasks)} 個並行任務..."

            # 實際上是順序執行，但模擬並行的概念
            start_time = datetime.now()

            for task in tasks:
                async with cl.Step(name=f"🔄 {task['name']}") as task_step:
                    await asyncio.sleep(task['duration'])
                    task_step.output = f"✅ 完成 (耗時 {task['duration']}s)"

            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()

            main_step.output = f"""
所有任務完成:
- 任務數: {len(tasks)}
- 總耗時: {total_time:.1f}s
- 平均耗時: {total_time/len(tasks):.1f}s
            """

        await cl.Message(
            content="""
## ✅ 並行任務完成

所有任務已按順序執行完畢。

💡 **說明**: Chainlit Steps 按順序顯示，但可以結合 asyncio 實現真正的並行處理。
            """,
            author="並行處理器"
        ).send()

    except Exception as e:
        await cl.Message(content=f"❌ 處理失敗: {str(e)}").send()


# ==================== 幫助信息 ====================

async def show_help():
    """顯示幫助信息"""
    help_msg = """
## 📚 可用命令

輸入以下命令查看不同的工作流示例：

### 🔄 工作流演示

1. **`分析數據`** - 數據分析流程
   - 載入數據 → 清洗 → 特徵工程 → 分析

2. **`生成報告`** - 報告生成流程（嵌套步驟）
   - 收集數據 → 生成圖表 → 編寫內容 → 格式化

3. **`處理文件`** - 批量文件處理
   - 演示進度追蹤和統計

4. **`複雜任務`** - 多層嵌套工作流
   - 展示 4 層嵌套的步驟結構

5. **`並行任務`** - 並行任務處理
   - 多個任務同時執行

### 💡 提示

- 每個步驟都會顯示執行時間
- 支持嵌套步驟（最多建議 3-4 層）
- 步驟可以有輸入、輸出和語言標記

**試試輸入上面的命令！** 🚀
    """

    await cl.Message(content=help_msg, author="幫助").send()


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║   Chainlit 多步驟處理示例                ║
╚══════════════════════════════════════════╝

運行命令：
    chainlit run 05_多步驟.py -w

功能特點：
✅ Step 組件使用
✅ 嵌套步驟（多層）
✅ 進度追蹤
✅ 執行時間統計
✅ 複雜工作流可視化
✅ 並行任務模擬

工作流示例：
📊 數據分析流程
📝 報告生成流程
📁 文件處理流程
🎯 複雜嵌套任務
🚀 並行任務處理

訪問 http://localhost:8000 體驗多步驟處理！
    """)


if __name__ == "__main__":
    main()
