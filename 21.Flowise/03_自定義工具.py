"""
Flowise 自定義工具範例
====================

本範例展示如何在 Flowise 中創建和使用自定義工具。

自定義工具功能：
1. JavaScript 自定義工具
2. Python 工具
3. API 工具
4. 工具組合

安裝依賴：
pip install requests
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass

# ============================================================
# 配置
# ============================================================

FLOWISE_API_URL = os.getenv("FLOWISE_API_URL", "http://localhost:3000")
FLOWISE_API_KEY = os.getenv("FLOWISE_API_KEY", "")


# ============================================================
# 工具定義
# ============================================================

@dataclass
class ToolParameter:
    """工具參數定義"""
    name: str
    type: str  # string, number, boolean, array, object
    description: str
    required: bool = True
    default: Any = None


@dataclass
class CustomTool:
    """自定義工具"""
    name: str
    description: str
    parameters: List[ToolParameter]
    func: Optional[Callable] = None
    code: str = ""

    def to_flowise_format(self) -> Dict[str, Any]:
        """轉換為 Flowise 格式"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    p.name: {
                        "type": p.type,
                        "description": p.description
                    }
                    for p in self.parameters
                },
                "required": [p.name for p in self.parameters if p.required]
            }
        }


# ============================================================
# 內建工具示例
# ============================================================

class CalculatorTool(CustomTool):
    """計算器工具"""

    def __init__(self):
        super().__init__(
            name="calculator",
            description="執行數學計算",
            parameters=[
                ToolParameter(
                    name="expression",
                    type="string",
                    description="數學表達式，如 '2 + 2' 或 '10 * 5'"
                )
            ]
        )
        self.code = """
function calculate(expression) {
    try {
        // 安全的數學計算
        const result = Function('"use strict"; return (' + expression + ')')();
        return { result: result };
    } catch (e) {
        return { error: e.message };
    }
}

return calculate($expression);
"""

    def execute(self, expression: str) -> Dict[str, Any]:
        """執行計算"""
        try:
            # 安全評估（只允許基本數學運算）
            allowed_chars = set("0123456789+-*/().  ")
            if not all(c in allowed_chars for c in expression):
                raise ValueError("不允許的字符")
            result = eval(expression)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class WeatherTool(CustomTool):
    """天氣查詢工具"""

    def __init__(self, api_key: str = ""):
        super().__init__(
            name="weather",
            description="查詢城市天氣信息",
            parameters=[
                ToolParameter(
                    name="city",
                    type="string",
                    description="城市名稱"
                ),
                ToolParameter(
                    name="unit",
                    type="string",
                    description="溫度單位：celsius 或 fahrenheit",
                    required=False,
                    default="celsius"
                )
            ]
        )
        self.api_key = api_key
        self.code = """
async function getWeather(city, unit = 'celsius') {
    const apiKey = '$API_KEY';
    const url = `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=${unit === 'celsius' ? 'metric' : 'imperial'}`;

    try {
        const response = await fetch(url);
        const data = await response.json();
        return {
            city: data.name,
            temperature: data.main.temp,
            description: data.weather[0].description,
            humidity: data.main.humidity
        };
    } catch (e) {
        return { error: e.message };
    }
}

return await getWeather($city, $unit);
"""


class SearchTool(CustomTool):
    """搜索工具"""

    def __init__(self):
        super().__init__(
            name="web_search",
            description="在網路上搜索信息",
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="搜索查詢"
                ),
                ToolParameter(
                    name="num_results",
                    type="number",
                    description="返回結果數量",
                    required=False,
                    default=5
                )
            ]
        )


class DatabaseTool(CustomTool):
    """數據庫查詢工具"""

    def __init__(self):
        super().__init__(
            name="database_query",
            description="執行數據庫查詢",
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="SQL 查詢語句"
                ),
                ToolParameter(
                    name="database",
                    type="string",
                    description="數據庫名稱",
                    required=False,
                    default="default"
                )
            ]
        )
        self.code = """
async function queryDatabase(query, database = 'default') {
    // 模擬數據庫查詢
    // 實際使用時應連接真實數據庫

    // 安全檢查
    const forbidden = ['DROP', 'DELETE', 'UPDATE', 'INSERT'];
    if (forbidden.some(word => query.toUpperCase().includes(word))) {
        return { error: '不允許的操作' };
    }

    return {
        query: query,
        database: database,
        results: [
            { id: 1, name: 'Item 1' },
            { id: 2, name: 'Item 2' }
        ]
    };
}

return await queryDatabase($query, $database);
"""


# ============================================================
# 工具管理器
# ============================================================

class ToolManager:
    """
    工具管理器

    管理和註冊自定義工具
    """

    def __init__(self, api_url: str, api_key: str = ""):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.tools: Dict[str, CustomTool] = {}

    def register_tool(self, tool: CustomTool):
        """註冊工具"""
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[CustomTool]:
        """獲取工具"""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """列出所有工具"""
        return list(self.tools.keys())

    def export_tools(self) -> List[Dict[str, Any]]:
        """導出工具定義"""
        return [tool.to_flowise_format() for tool in self.tools.values()]

    def save_tools_to_file(self, file_path: str):
        """保存工具到文件"""
        tools_data = self.export_tools()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(tools_data, f, indent=2, ensure_ascii=False)


# ============================================================
# Flowise 工具節點配置
# ============================================================

CUSTOM_TOOL_NODE = '''
{
    "nodes": [
        {
            "id": "customTool_0",
            "type": "customTool",
            "data": {
                "label": "Calculator Tool",
                "name": "calculator",
                "description": "執行數學計算",
                "inputVariables": [
                    {
                        "name": "expression",
                        "type": "string"
                    }
                ],
                "code": "function calculate(expression) {\\n    try {\\n        const result = eval(expression);\\n        return { result: result };\\n    } catch (e) {\\n        return { error: e.message };\\n    }\\n}\\n\\nreturn calculate($expression);"
            }
        }
    ]
}
'''

API_TOOL_NODE = '''
{
    "nodes": [
        {
            "id": "apiTool_0",
            "type": "customTool",
            "data": {
                "label": "Weather API",
                "name": "weather_api",
                "description": "獲取天氣信息",
                "inputVariables": [
                    {
                        "name": "city",
                        "type": "string"
                    }
                ],
                "code": "async function getWeather(city) {\\n    const response = await fetch(`https://api.example.com/weather?city=${city}`);\\n    return await response.json();\\n}\\n\\nreturn await getWeather($city);"
            }
        }
    ]
}
'''


# ============================================================
# 使用範例
# ============================================================

def example_calculator_tool():
    """
    範例 1: 計算器工具

    展示如何創建計算器工具
    """
    print("=" * 50)
    print("範例 1: 計算器工具")
    print("=" * 50)

    tool = CalculatorTool()

    print(f"工具名稱: {tool.name}")
    print(f"工具描述: {tool.description}")
    print(f"參數: {[p.name for p in tool.parameters]}")

    # 測試計算
    results = [
        tool.execute("2 + 2"),
        tool.execute("10 * 5"),
        tool.execute("100 / 4"),
    ]

    print("\n測試結果:")
    for r in results:
        print(f"  {r}")


def example_custom_tool_definition():
    """
    範例 2: 自定義工具定義

    展示如何定義自定義工具
    """
    print("\n" + "=" * 50)
    print("範例 2: 自定義工具定義")
    print("=" * 50)

    # 創建自定義工具
    email_tool = CustomTool(
        name="send_email",
        description="發送電子郵件",
        parameters=[
            ToolParameter(
                name="to",
                type="string",
                description="收件人郵箱地址"
            ),
            ToolParameter(
                name="subject",
                type="string",
                description="郵件主題"
            ),
            ToolParameter(
                name="body",
                type="string",
                description="郵件內容"
            )
        ],
        code="""
async function sendEmail(to, subject, body) {
    // 這裡實現發送郵件的邏輯
    console.log(`發送郵件到 ${to}`);
    return { status: 'sent', to: to };
}

return await sendEmail($to, $subject, $body);
"""
    )

    print("工具定義:")
    print(json.dumps(email_tool.to_flowise_format(), indent=2, ensure_ascii=False))


def example_tool_manager():
    """
    範例 3: 工具管理器

    展示如何管理多個工具
    """
    print("\n" + "=" * 50)
    print("範例 3: 工具管理器")
    print("=" * 50)

    manager = ToolManager(FLOWISE_API_URL, FLOWISE_API_KEY)

    # 註冊工具
    manager.register_tool(CalculatorTool())
    manager.register_tool(WeatherTool())
    manager.register_tool(SearchTool())
    manager.register_tool(DatabaseTool())

    print(f"已註冊工具: {manager.list_tools()}")

    # 導出工具
    exported = manager.export_tools()
    print(f"\n導出的工具數量: {len(exported)}")


def example_javascript_tool():
    """
    範例 4: JavaScript 工具

    展示 Flowise 中的 JavaScript 工具代碼
    """
    print("\n" + "=" * 50)
    print("範例 4: JavaScript 工具")
    print("=" * 50)

    js_code = """
// Flowise 自定義 JavaScript 工具示例

// 文本處理工具
function processText(text, operation) {
    switch(operation) {
        case 'uppercase':
            return text.toUpperCase();
        case 'lowercase':
            return text.toLowerCase();
        case 'reverse':
            return text.split('').reverse().join('');
        case 'word_count':
            return text.split(/\\s+/).filter(w => w).length;
        default:
            return text;
    }
}

// 日期工具
function formatDate(date, format) {
    const d = new Date(date);
    const options = {
        'short': { year: 'numeric', month: 'short', day: 'numeric' },
        'long': { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' },
        'iso': null
    };

    if (format === 'iso') {
        return d.toISOString();
    }

    return d.toLocaleDateString('zh-TW', options[format] || options['short']);
}

// JSON 處理工具
function processJSON(jsonString, path) {
    try {
        const obj = JSON.parse(jsonString);
        const keys = path.split('.');
        let result = obj;

        for (const key of keys) {
            if (result && typeof result === 'object') {
                result = result[key];
            } else {
                return null;
            }
        }

        return result;
    } catch (e) {
        return { error: e.message };
    }
}

// 導出
return {
    processText: processText($text, $operation),
    formatDate: formatDate($date, $format),
    processJSON: processJSON($json, $path)
};
"""

    print("JavaScript 工具代碼示例:")
    print(js_code)


def example_api_tool():
    """
    範例 5: API 工具

    展示如何創建調用外部 API 的工具
    """
    print("\n" + "=" * 50)
    print("範例 5: API 工具")
    print("=" * 50)

    api_tool_code = """
// API 調用工具

async function callAPI(url, method, headers, body) {
    const options = {
        method: method || 'GET',
        headers: {
            'Content-Type': 'application/json',
            ...headers
        }
    };

    if (body && method !== 'GET') {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, options);
        const data = await response.json();

        return {
            status: response.status,
            data: data
        };
    } catch (error) {
        return {
            error: error.message
        };
    }
}

return await callAPI($url, $method, $headers, $body);
"""

    print("API 工具代碼:")
    print(api_tool_code)

    print("\n工具節點配置:")
    print(API_TOOL_NODE)


def example_tool_chain():
    """
    範例 6: 工具鏈

    展示如何組合多個工具
    """
    print("\n" + "=" * 50)
    print("範例 6: 工具鏈")
    print("=" * 50)

    print("工具鏈配置示例:")
    print("""
{
    "name": "Research Tool Chain",
    "description": "研究助手工具鏈",
    "tools": [
        {
            "name": "web_search",
            "description": "搜索網路信息"
        },
        {
            "name": "summarize",
            "description": "總結搜索結果"
        },
        {
            "name": "translate",
            "description": "翻譯結果"
        }
    ],
    "flow": [
        {
            "step": 1,
            "tool": "web_search",
            "input": "$query"
        },
        {
            "step": 2,
            "tool": "summarize",
            "input": "$step1.results"
        },
        {
            "step": 3,
            "tool": "translate",
            "input": "$step2.summary",
            "params": {
                "target_lang": "$target_language"
            }
        }
    ]
}
""")


def example_flowise_node_config():
    """
    範例 7: Flowise 節點配置

    展示完整的工具節點配置
    """
    print("\n" + "=" * 50)
    print("範例 7: Flowise 節點配置")
    print("=" * 50)

    print("自定義工具節點配置:")
    print(CUSTOM_TOOL_NODE)


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("Flowise 自定義工具範例")
    print()

    example_calculator_tool()
    example_custom_tool_definition()
    example_tool_manager()
    example_javascript_tool()
    example_api_tool()
    example_tool_chain()
    example_flowise_node_config()
