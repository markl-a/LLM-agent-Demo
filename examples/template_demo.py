#!/usr/bin/env python3
"""模板引擎演示範例"""

import sys
from pathlib import Path

# 添加項目路徑
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_agent_demo.utils.templates import (
    PromptTemplate,
    TemplateLoader,
    create_template,
    load_template,
)


def demo_basic_template():
    """演示基本變數替換"""
    print("\n" + "=" * 60)
    print("1. 基本變數替換")
    print("=" * 60)

    template = create_template("你好，{name}！歡迎來到 {place}。")
    result = template.render(name="小明", place="LLM Agent 世界")
    print(result)


def demo_default_values():
    """演示默認值"""
    print("\n" + "=" * 60)
    print("2. 默認值")
    print("=" * 60)

    template = create_template("你好，{name|訪客}！")

    print("有提供變數：")
    print(template.render(name="小紅"))

    print("\n沒有提供變數（使用默認值）：")
    print(template.render())


def demo_conditions():
    """演示條件語句"""
    print("\n" + "=" * 60)
    print("3. 條件語句")
    print("=" * 60)

    template_text = """
用戶資訊：
- 姓名：{name}
{?email}- 電子郵件：{email}{/email}
{?!email}- 未提供電子郵件{/email}
{?age}- 年齡：{age} 歲{/age}
"""

    template = create_template(template_text.strip())

    print("提供所有變數：")
    print(template.render(name="小李", email="xiaoli@example.com", age=25))

    print("\n\n只提供部分變數：")
    print(template.render(name="小王", age=30))


def demo_loops():
    """演示循環語句"""
    print("\n" + "=" * 60)
    print("4. 循環語句")
    print("=" * 60)

    template_text = """
待辦事項清單：
{#items}
{index1}. {item}
{/items}
"""

    template = create_template(template_text.strip())

    result = template.render(
        items=[
            {"item": "完成報告"},
            {"item": "回覆郵件"},
            {"item": "參加會議"},
        ]
    )
    print(result)


def demo_filters():
    """演示過濾器"""
    print("\n" + "=" * 60)
    print("5. 過濾器")
    print("=" * 60)

    template_text = """
原始文本：{text}
大寫：{text|upper}
小寫：{text|lower}
首字母大寫：{text|capitalize}
長度：{text|length}
"""

    template = create_template(template_text.strip())
    result = template.render(text="Hello World")
    print(result)


def demo_custom_filters():
    """演示自定義過濾器"""
    print("\n" + "=" * 60)
    print("6. 自定義過濾器")
    print("=" * 60)

    def highlight(text):
        """高亮過濾器"""
        return f"*** {text} ***"

    def reverse(text):
        """反轉過濾器"""
        return str(text)[::-1]

    template = create_template(
        "原始：{text}\n高亮：{text|highlight}\n反轉：{text|reverse}",
        custom_filters={"highlight": highlight, "reverse": reverse},
    )

    result = template.render(text="LLM Agent")
    print(result)


def demo_nested_structures():
    """演示嵌套結構"""
    print("\n" + "=" * 60)
    print("7. 嵌套條件和循環")
    print("=" * 60)

    template_text = """
{?users}
用戶列表：
{#users}
  - 姓名：{name}
    {?roles}角色：{#roles}{item}{?!last}, {/last}{/roles}{/roles}
{/users}
{/users}
"""

    template = create_template(template_text.strip())

    result = template.render(
        users=[
            {
                "name": "Alice",
                "roles": [
                    {"item": "管理員"},
                    {"item": "編輯者"},
                ],
            },
            {
                "name": "Bob",
                "roles": [
                    {"item": "用戶"},
                ],
            },
        ]
    )
    print(result)


def demo_load_from_file():
    """演示從文件載入模板"""
    print("\n" + "=" * 60)
    print("8. 從文件載入模板")
    print("=" * 60)

    template_dir = Path(__file__).parent.parent / "templates"

    if (template_dir / "greeting.txt").exists():
        template = load_template(template_dir / "greeting.txt")

        result = template.render(
            name="小張",
            role="Python 開發者",
            tasks=[
                {"item": "學習模板引擎"},
                {"item": "編寫示例代碼"},
                {"item": "測試功能"},
            ],
        )
        print(result)

        print("\n\n沒有任務的情況：")
        result2 = template.render(
            name="小劉",
            role="項目經理",
        )
        print(result2)
    else:
        print(f"模板文件不存在：{template_dir / 'greeting.txt'}")


def demo_template_loader():
    """演示模板載入器"""
    print("\n" + "=" * 60)
    print("9. 批量載入模板")
    print("=" * 60)

    template_dir = Path(__file__).parent.parent / "templates"

    if template_dir.exists():
        loader = TemplateLoader(template_dir=template_dir)
        templates = loader.load_from_directory(pattern="*.txt")

        print(f"已載入 {len(templates)} 個模板：")
        for name, template in templates.items():
            print(f"  - {name}: {len(template.template)} 字符")

        # 使用系統提示詞模板
        if "system_prompt" in templates:
            print("\n系統提示詞示例：")
            result = templates["system_prompt"].render(
                role="LLM Agent 開發專家",
                capabilities=[
                    {"name": "代碼生成", "description": "生成高質量的 Python 代碼"},
                    {"name": "問題解答", "description": "回答技術問題"},
                    {"name": "架構設計", "description": "設計系統架構"},
                ],
                guidelines=[
                    {"item": "提供清晰、準確的答案"},
                    {"item": "使用最佳實踐"},
                    {"item": "考慮性能和可維護性"},
                ],
                language="繁體中文",
            )
            print(result)
    else:
        print(f"模板目錄不存在：{template_dir}")


def demo_strict_mode():
    """演示嚴格模式"""
    print("\n" + "=" * 60)
    print("10. 嚴格模式")
    print("=" * 60)

    template = create_template(
        "姓名：{name}\n年齡：{age}",
        required_vars=["name", "age"],
        strict=True,
    )

    print("提供所有必需變數：")
    print(template.render(name="小陳", age=28))

    print("\n缺少必需變數（將拋出異常）：")
    try:
        template.render(name="小陳")
    except Exception as e:
        print(f"錯誤：{type(e).__name__}: {e}")


def main():
    """主函數"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║           LLM Agent Demo - 模板引擎演示                    ║")
    print("╚════════════════════════════════════════════════════════════╝")

    demos = [
        demo_basic_template,
        demo_default_values,
        demo_conditions,
        demo_loops,
        demo_filters,
        demo_custom_filters,
        demo_nested_structures,
        demo_load_from_file,
        demo_template_loader,
        demo_strict_mode,
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n錯誤：{type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
