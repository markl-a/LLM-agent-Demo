"""
Chainlit 自定義元素示例

本示例展示：
1. 圖片元素
2. 文件元素
3. 代碼塊
4. 表格展示
5. 音頻/視頻元素
6. 自定義組件

運行方式：
    chainlit run 06_自定義元素.py -w
"""

import chainlit as cl
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
import json


# ==================== 會話初始化 ====================

@cl.on_chat_start
async def on_chat_start():
    """初始化聊天會話"""
    try:
        welcome_msg = """
# 🎨 自定義元素示例

這個示例展示了 Chainlit 支持的各種自定義元素。

## 📦 支持的元素類型

- 🖼️ **圖片** - Image
- 📄 **文件** - File
- 💻 **代碼** - Code
- 📊 **表格** - Table (Markdown)
- 🎵 **音頻** - Audio
- 🎬 **視頻** - Video
- 📝 **文本** - Text
- 🔗 **PDF** - Pdf

## 🎮 試試這些命令

- `圖片` - 生成和顯示圖片
- `代碼` - 展示代碼塊
- `表格` - 顯示表格數據
- `文件` - 創建文件下載
- `全部` - 展示所有元素類型

**輸入命令開始體驗！** ✨
        """

        await cl.Message(content=welcome_msg, author="系統").send()

        print("✅ 自定義元素會話已初始化")

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

        if "圖片" in user_message or "image" in user_message:
            await demo_image_element()

        elif "代碼" in user_message or "code" in user_message:
            await demo_code_element()

        elif "表格" in user_message or "table" in user_message:
            await demo_table_element()

        elif "文件" in user_message or "file" in user_message:
            await demo_file_element()

        elif "全部" in user_message or "all" in user_message:
            await demo_all_elements()

        elif "圖表" in user_message or "chart" in user_message:
            await demo_chart_element()

        elif "json" in user_message:
            await demo_json_element()

        else:
            await show_help()

    except Exception as e:
        error_msg = f"❌ 處理失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 圖片元素 ====================

async def demo_image_element():
    """演示圖片元素"""
    try:
        # 創建一個簡單的圖表
        fig, ax = plt.subplots(figsize=(8, 6))

        # 數據
        categories = ['A', 'B', 'C', 'D', 'E']
        values = [23, 45, 56, 78, 32]

        # 繪製柱狀圖
        ax.bar(categories, values, color='skyblue')
        ax.set_xlabel('類別')
        ax.set_ylabel('數值')
        ax.set_title('示例圖表')
        ax.grid(True, alpha=0.3)

        # 保存到字節流
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close()

        # 創建臨時文件
        image_path = f"/tmp/chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        with open(image_path, 'wb') as f:
            f.write(buf.getvalue())

        # 創建圖片元素
        image = cl.Image(
            name="示例圖表",
            path=image_path,
            display="inline"  # inline 或 side
        )

        # 發送消息（附帶圖片）
        await cl.Message(
            content="""
## 🖼️ 圖片元素演示

這是一個動態生成的圖表！

### 📊 圖表信息
- **類型**: 柱狀圖
- **數據點**: 5 個
- **格式**: PNG
- **尺寸**: 800x600

圖片可以：
- ✅ 內聯顯示
- ✅ 側邊顯示
- ✅ 點擊放大
- ✅ 下載保存
            """,
            elements=[image],
            author="圖片演示"
        ).send()

    except Exception as e:
        await cl.Message(content=f"❌ 圖片生成失敗: {str(e)}").send()


# ==================== 代碼元素 ====================

async def demo_code_element():
    """演示代碼塊展示"""
    try:
        # Python 代碼示例
        python_code = '''
def fibonacci(n):
    """
    計算斐波那契數列的第 n 項

    Args:
        n: 項數

    Returns:
        第 n 項的值
    """
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 計算前 10 項
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
'''

        # JavaScript 代碼示例
        js_code = '''
// React 組件示例
function Welcome({ name }) {
  const [count, setCount] = useState(0);

  return (
    <div>
      <h1>Hello, {name}!</h1>
      <button onClick={() => setCount(count + 1)}>
        點擊次數: {count}
      </button>
    </div>
  );
}
'''

        # SQL 代碼示例
        sql_code = '''
-- 查詢用戶訂單統計
SELECT
    u.user_name,
    COUNT(o.order_id) AS total_orders,
    SUM(o.amount) AS total_amount,
    AVG(o.amount) AS avg_amount
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
WHERE o.created_at >= '2024-01-01'
GROUP BY u.user_id, u.user_name
HAVING COUNT(o.order_id) > 5
ORDER BY total_amount DESC;
'''

        content = f"""
## 💻 代碼元素演示

Chainlit 支持多種程式語言的語法高亮。

### Python 示例

```python
{python_code.strip()}
```

### JavaScript/React 示例

```javascript
{js_code.strip()}
```

### SQL 示例

```sql
{sql_code.strip()}
```

### 🎨 支持的語言

Python • JavaScript • TypeScript • Java • C++ • Go • Rust • Ruby
PHP • Swift • Kotlin • SQL • HTML • CSS • YAML • JSON • Markdown
... 等 100+ 種語言

### ✨ 功能特點

- ✅ 語法高亮
- ✅ 代碼複製按鈕
- ✅ 行號顯示
- ✅ 主題自適應
        """

        await cl.Message(content=content, author="代碼演示").send()

    except Exception as e:
        await cl.Message(content=f"❌ 代碼展示失敗: {str(e)}").send()


# ==================== 表格元素 ====================

async def demo_table_element():
    """演示表格展示"""
    try:
        content = """
## 📊 表格元素演示

### 簡單表格

| 姓名 | 年齡 | 職位 | 部門 |
|------|------|------|------|
| 張三 | 28 | 工程師 | 技術部 |
| 李四 | 32 | 設計師 | 設計部 |
| 王五 | 25 | 產品經理 | 產品部 |
| 趙六 | 30 | 數據分析師 | 數據部 |

### 對齊方式

| 左對齊 | 居中對齊 | 右對齊 |
|:-------|:--------:|-------:|
| 內容 A | 內容 B | 內容 C |
| 長長長長的內容 | 中 | 123 |

### 複雜表格

| 項目 | Q1 | Q2 | Q3 | Q4 | 年度總計 |
|------|----:|----:|----:|----:|----------:|
| 收入 | $1.2M | $1.5M | $1.8M | $2.1M | **$6.6M** |
| 成本 | $0.8M | $0.9M | $1.1M | $1.3M | **$4.1M** |
| 利潤 | $0.4M | $0.6M | $0.7M | $0.8M | **$2.5M** |

### 狀態表格

| 任務 | 狀態 | 進度 | 負責人 |
|------|------|------|--------|
| 功能開發 | ✅ 完成 | 100% | 張三 |
| 測試 | 🔄 進行中 | 60% | 李四 |
| 部署 | ⏸️ 待開始 | 0% | 王五 |
| 文檔 | ⚠️ 延遲 | 30% | 趙六 |

### 💡 Markdown 表格特點

- ✅ 自動對齊
- ✅ 響應式設計
- ✅ 支持 Emoji
- ✅ 支持格式化文本（**粗體**、*斜體*）
- ✅ 支持內聯代碼 `code`
        """

        await cl.Message(content=content, author="表格演示").send()

    except Exception as e:
        await cl.Message(content=f"❌ 表格展示失敗: {str(e)}").send()


# ==================== 文件元素 ====================

async def demo_file_element():
    """演示文件下載"""
    try:
        # 創建示例文本文件
        text_content = """這是一個示例文本文件

內容包括：
1. 文本數據
2. 配置信息
3. 日誌記錄

創建時間: {}
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        text_path = f"/tmp/example_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text_content)

        # 創建 JSON 文件
        json_data = {
            "name": "示例數據",
            "version": "1.0.0",
            "data": {
                "users": 1000,
                "active": 750,
                "growth": "25%"
            },
            "timestamp": datetime.now().isoformat()
        }

        json_path = f"/tmp/data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        # 創建文件元素
        text_file = cl.File(
            name="example.txt",
            path=text_path,
        )

        json_file = cl.File(
            name="data.json",
            path=json_path,
        )

        # 發送消息（附帶文件）
        await cl.Message(
            content="""
## 📁 文件元素演示

已創建 2 個可下載的文件！

### 📄 文件列表

1. **example.txt** - 文本文件
   - 包含示例文本內容
   - UTF-8 編碼

2. **data.json** - JSON 數據文件
   - 包含結構化數據
   - 格式化輸出

### 💾 下載方式

點擊下方的文件即可下載到本地。

### ✨ 用途

- 導出數據
- 保存報告
- 下載日誌
- 分享文件
            """,
            elements=[text_file, json_file],
            author="文件演示"
        ).send()

    except Exception as e:
        await cl.Message(content=f"❌ 文件創建失敗: {str(e)}").send()


# ==================== 圖表元素 ====================

async def demo_chart_element():
    """演示多種圖表"""
    try:
        # 創建多個圖表
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

        # 1. 折線圖
        x = range(10)
        y = [i**2 for i in x]
        ax1.plot(x, y, marker='o', color='blue', linewidth=2)
        ax1.set_title('折線圖示例')
        ax1.grid(True, alpha=0.3)

        # 2. 餅圖
        sizes = [30, 25, 20, 15, 10]
        labels = ['A', 'B', 'C', 'D', 'E']
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']
        ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax2.set_title('餅圖示例')

        # 3. 散點圖
        import numpy as np
        x = np.random.randn(50)
        y = np.random.randn(50)
        colors_scatter = np.random.rand(50)
        ax3.scatter(x, y, c=colors_scatter, s=100, alpha=0.6, cmap='viridis')
        ax3.set_title('散點圖示例')
        ax3.grid(True, alpha=0.3)

        # 4. 箱形圖
        data = [np.random.normal(0, std, 100) for std in range(1, 5)]
        ax4.boxplot(data, labels=['A', 'B', 'C', 'D'])
        ax4.set_title('箱形圖示例')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()

        # 保存圖表
        chart_path = f"/tmp/charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()

        # 創建圖片元素
        chart_image = cl.Image(
            name="綜合圖表",
            path=chart_path,
            display="inline"
        )

        await cl.Message(
            content="""
## 📈 圖表元素演示

展示了 4 種常見的數據可視化圖表：

### 📊 圖表類型

1. **折線圖** - 展示趨勢變化
2. **餅圖** - 展示比例分布
3. **散點圖** - 展示數據分布
4. **箱形圖** - 展示統計特徵

### 🎨 使用場景

- 數據分析報告
- 實時監控面板
- 統計結果展示
- 性能指標可視化

使用 Matplotlib 等庫可以生成任何類型的圖表！
            """,
            elements=[chart_image],
            author="圖表演示"
        ).send()

    except Exception as e:
        await cl.Message(content=f"❌ 圖表生成失敗: {str(e)}").send()


# ==================== JSON 元素 ====================

async def demo_json_element():
    """演示 JSON 數據展示"""
    try:
        json_data = {
            "user": {
                "id": 12345,
                "name": "張三",
                "email": "zhangsan@example.com",
                "roles": ["admin", "user"],
                "settings": {
                    "theme": "dark",
                    "language": "zh-TW",
                    "notifications": True
                }
            },
            "statistics": {
                "total_logins": 156,
                "last_login": "2024-12-30T10:30:00Z",
                "active_sessions": 2
            },
            "metadata": {
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-12-30T10:30:00Z",
                "version": "2.1.0"
            }
        }

        content = f"""
## 📋 JSON 元素演示

### 格式化的 JSON 數據

```json
{json.dumps(json_data, ensure_ascii=False, indent=2)}
```

### 💡 JSON 展示特點

- ✅ 語法高亮
- ✅ 自動縮進
- ✅ 折疊/展開
- ✅ 易於複製

### 🎯 適用場景

- API 響應展示
- 配置文件查看
- 數據結構演示
- 調試信息輸出
        """

        await cl.Message(content=content, author="JSON 演示").send()

    except Exception as e:
        await cl.Message(content=f"❌ JSON 展示失敗: {str(e)}").send()


# ==================== 全部元素演示 ====================

async def demo_all_elements():
    """演示所有元素類型"""
    try:
        await cl.Message(
            content="## 🎨 開始展示所有元素類型...",
            author="綜合演示"
        ).send()

        # 逐個演示
        await demo_image_element()
        await demo_code_element()
        await demo_table_element()
        await demo_file_element()

        # 總結
        await cl.Message(
            content="""
---

## ✅ 所有元素展示完成！

已展示的元素類型：
- 🖼️ 圖片元素
- 💻 代碼塊
- 📊 表格
- 📁 文件下載

### 💡 更多可能性

Chainlit 還支持：
- 🎵 音頻播放
- 🎬 視頻播放
- 📄 PDF 查看
- 🎨 自定義 HTML 組件

發揮你的創意，構建豐富的交互界面！
            """,
            author="綜合演示"
        ).send()

    except Exception as e:
        await cl.Message(content=f"❌ 綜合演示失敗: {str(e)}").send()


# ==================== 幫助信息 ====================

async def show_help():
    """顯示幫助信息"""
    help_msg = """
## 📚 可用命令

輸入以下命令查看不同的元素演示：

### 🎨 元素類型

- `圖片` - 動態生成圖表
- `代碼` - 多語言代碼高亮
- `表格` - Markdown 表格展示
- `文件` - 創建可下載文件
- `圖表` - 多種圖表類型
- `json` - JSON 數據展示
- `全部` - 展示所有元素

### 💡 提示

每種元素都有其特定的用途：
- **圖片**: 適合數據可視化、圖表展示
- **代碼**: 適合教程、技術文檔
- **表格**: 適合結構化數據展示
- **文件**: 適合數據導出、資源下載

**試試輸入上面的命令！** ✨
    """

    await cl.Message(content=help_msg, author="幫助").send()


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║   Chainlit 自定義元素示例                ║
╚══════════════════════════════════════════╝

運行命令：
    chainlit run 06_自定義元素.py -w

功能特點：
✅ 圖片元素（動態生成）
✅ 代碼塊（語法高亮）
✅ 表格展示（Markdown）
✅ 文件下載
✅ 圖表可視化
✅ JSON 數據展示

元素類型：
🖼️ Image - 圖片
📄 File - 文件
💻 Code - 代碼
📊 Table - 表格
🎵 Audio - 音頻
🎬 Video - 視頻
📝 Text - 文本

訪問 http://localhost:8000 體驗豐富的元素！
    """)


if __name__ == "__main__":
    main()
