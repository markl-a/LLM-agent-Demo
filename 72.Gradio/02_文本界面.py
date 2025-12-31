"""
Gradio 文本界面示例

本示例展示：
1. Textbox 組件的各種用法
2. 文本處理應用
3. 多輸入輸出組合
4. 文本分析和轉換

運行方式：
    python 02_文本界面.py
"""

import gradio as gr
import re
from typing import Tuple, Dict
from collections import Counter


# ==================== 文本處理函數 ====================

def text_statistics(text: str) -> str:
    """
    詳細的文本統計分析

    Args:
        text: 輸入文本

    Returns:
        統計結果
    """
    if not text:
        return "請輸入文本！"

    # 基礎統計
    total_chars = len(text)
    chars_no_space = len(text.replace(" ", "").replace("\n", "").replace("\t", ""))
    spaces = text.count(" ")
    lines = len(text.split("\n"))
    words = text.split()
    word_count = len(words)

    # 段落統計
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    paragraph_count = len(paragraphs)

    # 字符類型統計
    letters = sum(c.isalpha() for c in text)
    digits = sum(c.isdigit() for c in text)
    punctuation = sum(not c.isalnum() and not c.isspace() for c in text)

    # 中英文統計
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))

    # 平均值
    avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
    avg_line_length = total_chars / lines if lines > 0 else 0

    return f"""
📊 **詳細統計分析**

**基礎統計：**
• 總字符數：{total_chars}
• 字符數（無空格）：{chars_no_space}
• 空格數：{spaces}
• 單詞數：{word_count}
• 行數：{lines}
• 段落數：{paragraph_count}

**字符類型：**
• 字母：{letters}
• 數字：{digits}
• 標點符號：{punctuation}
• 中文字符：{chinese_chars}
• 英文字母：{english_chars}

**平均值：**
• 平均單詞長度：{avg_word_length:.2f} 字符
• 平均行長度：{avg_line_length:.2f} 字符

✅ 分析完成！
    """


def text_transformer(text: str, operation: str) -> str:
    """
    文本轉換器

    Args:
        text: 輸入文本
        operation: 轉換操作

    Returns:
        轉換後的文本
    """
    if not text:
        return "請輸入文本！"

    operations = {
        "轉大寫": text.upper(),
        "轉小寫": text.lower(),
        "首字母大寫": text.title(),
        "反轉文本": text[::-1],
        "移除空格": text.replace(" ", ""),
        "移除換行": text.replace("\n", " "),
        "每行首字母大寫": "\n".join(line.capitalize() for line in text.split("\n"))
    }

    result = operations.get(operation, text)

    return f"""
原文：
{text}

---

轉換結果（{operation}）：
{result}
    """


def word_frequency(text: str, top_n: int) -> str:
    """
    詞頻分析

    Args:
        text: 輸入文本
        top_n: 顯示前 N 個高頻詞

    Returns:
        詞頻統計結果
    """
    if not text:
        return "請輸入文本！"

    # 清理和分詞
    words = re.findall(r'\b\w+\b', text.lower())

    if not words:
        return "未找到有效單詞！"

    # 計算詞頻
    word_counts = Counter(words)
    top_words = word_counts.most_common(top_n)

    # 格式化輸出
    result = f"📊 **詞頻分析（前 {top_n} 名）**\n\n"
    result += f"總詞數：{len(words)}\n"
    result += f"唯一詞數：{len(word_counts)}\n\n"
    result += "排名 | 單詞 | 出現次數 | 百分比\n"
    result += "-" * 50 + "\n"

    for i, (word, count) in enumerate(top_words, 1):
        percentage = (count / len(words)) * 100
        result += f"{i:2d}. | {word:15s} | {count:4d} | {percentage:5.2f}%\n"

    return result


def find_and_replace(text: str, find: str, replace: str, case_sensitive: bool) -> Tuple[str, str]:
    """
    查找和替換

    Args:
        text: 原始文本
        find: 要查找的字符串
        replace: 替換字符串
        case_sensitive: 是否區分大小寫

    Returns:
        替換後的文本和統計信息
    """
    if not text:
        return "請輸入文本！", ""

    if not find:
        return text, "請輸入要查找的內容！"

    # 執行替換
    if case_sensitive:
        new_text = text.replace(find, replace)
        count = text.count(find)
    else:
        # 不區分大小寫的替換
        pattern = re.compile(re.escape(find), re.IGNORECASE)
        matches = pattern.findall(text)
        count = len(matches)
        new_text = pattern.sub(replace, text)

    # 統計信息
    stats = f"""
🔍 **查找和替換結果**

• 查找內容：{find}
• 替換為：{replace}
• 替換次數：{count}
• 區分大小寫：{'是' if case_sensitive else '否'}

{'✅ 替換完成！' if count > 0 else '⚠️ 未找到匹配項'}
    """

    return new_text, stats


def text_cleaner(text: str) -> Tuple[str, str]:
    """
    文本清理器

    Args:
        text: 原始文本

    Returns:
        清理後的文本和報告
    """
    if not text:
        return "請輸入文本！", ""

    original_length = len(text)

    # 清理操作
    cleaned = text

    # 1. 移除多餘空格
    spaces_removed = len(re.findall(r'\s+', cleaned)) - len(re.findall(r'\s+', re.sub(r'\s+', ' ', cleaned)))
    cleaned = re.sub(r'\s+', ' ', cleaned)

    # 2. 移除首尾空格
    cleaned = cleaned.strip()

    # 3. 移除多餘的換行
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    # 4. 移除特殊字符（可選）
    # cleaned = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()\"\'，。！？；：（）""'']', '', cleaned)

    cleaned_length = len(cleaned)
    chars_removed = original_length - cleaned_length

    report = f"""
🧹 **文本清理報告**

• 原始長度：{original_length} 字符
• 清理後長度：{cleaned_length} 字符
• 移除字符數：{chars_removed}
• 移除的空格：{spaces_removed}

清理操作：
✅ 合併多餘空格
✅ 移除首尾空格
✅ 規範化換行

清理完成！
    """

    return cleaned, report


def text_splitter(text: str, split_by: str, max_parts: int) -> str:
    """
    文本分割器

    Args:
        text: 輸入文本
        split_by: 分割符
        max_parts: 最大顯示部分數

    Returns:
        分割結果
    """
    if not text:
        return "請輸入文本！"

    # 根據不同的分割方式
    if split_by == "空格":
        parts = text.split(" ")
    elif split_by == "換行":
        parts = text.split("\n")
    elif split_by == "逗號":
        parts = text.split(",")
    elif split_by == "句號":
        parts = re.split(r'[.。]', text)
    else:
        parts = [text]

    # 清理空白部分
    parts = [p.strip() for p in parts if p.strip()]

    total_parts = len(parts)
    display_parts = parts[:max_parts]

    result = f"📄 **文本分割結果**\n\n"
    result += f"分割方式：{split_by}\n"
    result += f"總分段數：{total_parts}\n"
    result += f"顯示：前 {min(max_parts, total_parts)} 段\n\n"
    result += "-" * 50 + "\n\n"

    for i, part in enumerate(display_parts, 1):
        result += f"【第 {i} 段】\n{part}\n\n"

    if total_parts > max_parts:
        result += f"\n... 還有 {total_parts - max_parts} 段未顯示"

    return result


# ==================== Gradio 界面 ====================

def create_demo():
    """創建 Gradio 應用"""

    with gr.Blocks(theme=gr.themes.Soft(), title="📝 Gradio 文本界面示例") as demo:

        gr.Markdown("# 📝 Gradio 文本處理工具集")
        gr.Markdown("展示 Textbox 組件的各種應用場景")

        with gr.Tabs():

            # Tab 1: 文本統計
            with gr.TabItem("📊 文本統計"):
                gr.Markdown("### 詳細的文本統計分析")

                with gr.Row():
                    with gr.Column():
                        input_stats = gr.Textbox(
                            label="輸入文本",
                            placeholder="在這裡輸入要分析的文本...",
                            lines=10
                        )
                        btn_stats = gr.Button("📊 開始分析", variant="primary")

                    with gr.Column():
                        output_stats = gr.Textbox(
                            label="統計結果",
                            lines=20
                        )

                btn_stats.click(
                    fn=text_statistics,
                    inputs=input_stats,
                    outputs=output_stats
                )

                gr.Examples(
                    examples=[
                        ["Hello World! This is a Gradio demo application."],
                        ["人工智能正在改變世界。AI is transforming our world."]
                    ],
                    inputs=input_stats
                )

            # Tab 2: 文本轉換
            with gr.TabItem("🔄 文本轉換"):
                gr.Markdown("### 多種文本轉換操作")

                with gr.Row():
                    with gr.Column():
                        input_transform = gr.Textbox(
                            label="輸入文本",
                            lines=5
                        )
                        operation = gr.Radio(
                            choices=[
                                "轉大寫",
                                "轉小寫",
                                "首字母大寫",
                                "反轉文本",
                                "移除空格",
                                "移除換行",
                                "每行首字母大寫"
                            ],
                            label="選擇轉換操作",
                            value="轉大寫"
                        )
                        btn_transform = gr.Button("🔄 轉換", variant="primary")

                    with gr.Column():
                        output_transform = gr.Textbox(
                            label="轉換結果",
                            lines=12
                        )

                btn_transform.click(
                    fn=text_transformer,
                    inputs=[input_transform, operation],
                    outputs=output_transform
                )

            # Tab 3: 詞頻分析
            with gr.TabItem("📈 詞頻分析"):
                gr.Markdown("### 統計文本中的詞頻")

                with gr.Row():
                    with gr.Column():
                        input_freq = gr.Textbox(
                            label="輸入文本",
                            lines=8
                        )
                        top_n = gr.Slider(
                            minimum=5,
                            maximum=50,
                            value=10,
                            step=5,
                            label="顯示前 N 個高頻詞"
                        )
                        btn_freq = gr.Button("📈 分析詞頻", variant="primary")

                    with gr.Column():
                        output_freq = gr.Textbox(
                            label="詞頻統計",
                            lines=15
                        )

                btn_freq.click(
                    fn=word_frequency,
                    inputs=[input_freq, top_n],
                    outputs=output_freq
                )

            # Tab 4: 查找替換
            with gr.TabItem("🔍 查找替換"):
                gr.Markdown("### 查找並替換文本")

                with gr.Row():
                    with gr.Column():
                        input_replace = gr.Textbox(
                            label="原始文本",
                            lines=6
                        )
                        find_text = gr.Textbox(
                            label="查找內容",
                            placeholder="要查找的字符串..."
                        )
                        replace_text = gr.Textbox(
                            label="替換為",
                            placeholder="替換的字符串..."
                        )
                        case_sensitive = gr.Checkbox(
                            label="區分大小寫",
                            value=True
                        )
                        btn_replace = gr.Button("🔍 查找並替換", variant="primary")

                    with gr.Column():
                        output_replaced = gr.Textbox(
                            label="替換後的文本",
                            lines=6
                        )
                        stats_replace = gr.Textbox(
                            label="統計信息",
                            lines=6
                        )

                btn_replace.click(
                    fn=find_and_replace,
                    inputs=[input_replace, find_text, replace_text, case_sensitive],
                    outputs=[output_replaced, stats_replace]
                )

            # Tab 5: 文本清理
            with gr.TabItem("🧹 文本清理"):
                gr.Markdown("### 自動清理和格式化文本")

                with gr.Row():
                    with gr.Column():
                        input_clean = gr.Textbox(
                            label="原始文本（可能包含多餘空格、換行等）",
                            lines=8
                        )
                        btn_clean = gr.Button("🧹 清理文本", variant="primary")

                    with gr.Column():
                        output_cleaned = gr.Textbox(
                            label="清理後的文本",
                            lines=8
                        )
                        report_clean = gr.Textbox(
                            label="清理報告",
                            lines=8
                        )

                btn_clean.click(
                    fn=text_cleaner,
                    inputs=input_clean,
                    outputs=[output_cleaned, report_clean]
                )

            # Tab 6: 文本分割
            with gr.TabItem("✂️ 文本分割"):
                gr.Markdown("### 按不同方式分割文本")

                with gr.Row():
                    with gr.Column():
                        input_split = gr.Textbox(
                            label="輸入文本",
                            lines=8
                        )
                        split_by = gr.Radio(
                            choices=["空格", "換行", "逗號", "句號"],
                            label="分割方式",
                            value="空格"
                        )
                        max_parts = gr.Slider(
                            minimum=5,
                            maximum=50,
                            value=10,
                            step=5,
                            label="最大顯示段數"
                        )
                        btn_split = gr.Button("✂️ 分割文本", variant="primary")

                    with gr.Column():
                        output_split = gr.Textbox(
                            label="分割結果",
                            lines=20
                        )

                btn_split.click(
                    fn=text_splitter,
                    inputs=[input_split, split_by, max_parts],
                    outputs=output_split
                )

        gr.Markdown("""
---
### 💡 使用提示

- **文本統計**：全面分析文本的各項統計指標
- **文本轉換**：快速轉換文本格式和大小寫
- **詞頻分析**：找出文本中最常出現的詞彙
- **查找替換**：批量替換文本內容
- **文本清理**：自動清理多餘空格和格式問題
- **文本分割**：按不同規則分割長文本

支持中英文混合文本處理！
        """)

    return demo


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║      Gradio 文本界面示例                 ║
╚══════════════════════════════════════════╝

功能特點：
✅ 6 種文本處理工具
✅ 詳細的統計分析
✅ 多種轉換操作
✅ 詞頻分析
✅ 查找替換
✅ 文本清理

啟動應用...
    """)

    demo = create_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )


if __name__ == "__main__":
    main()
