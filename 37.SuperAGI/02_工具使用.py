"""
SuperAGI 工具使用示例

這個示例展示了如何:
1. 使用內建工具
2. 組合多個工具
3. 工具鏈設計
4. 工具參數配置
5. 工具錯誤處理

SuperAGI 提供 70+ 內建工具，覆蓋搜索、文件、代碼、API 等各種場景。
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod


# ==================== 工具基類 ====================

class BaseTool(ABC):
    """工具基類"""

    def __init__(self, name: str, description: str):
        """
        初始化工具

        參數:
            name: 工具名稱
            description: 工具描述
        """
        self.name = name
        self.description = description
        self.execution_count = 0
        self.total_cost = 0.0

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        執行工具

        返回:
            執行結果
        """
        pass

    def validate_input(self, **kwargs) -> bool:
        """驗證輸入參數"""
        return True

    def log_execution(self, result: Dict):
        """記錄執行"""
        self.execution_count += 1
        print(f"  [{self.name}] 執行 #{self.execution_count}")

    def get_stats(self) -> Dict:
        """獲取統計信息"""
        return {
            "name": self.name,
            "executions": self.execution_count,
            "total_cost": self.total_cost
        }


# ==================== 搜索工具 ====================

class GoogleSearchTool(BaseTool):
    """Google 搜索工具"""

    def __init__(self):
        super().__init__(
            name="GoogleSearchTool",
            description="使用 Google 搜索信息"
        )

    def execute(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        執行搜索

        參數:
            query: 搜索查詢
            num_results: 返回結果數量

        返回:
            搜索結果
        """
        print(f"\n🔍 Google 搜索: {query}")

        # 模擬搜索結果
        results = [
            {
                "title": f"關於 {query} 的結果 {i+1}",
                "url": f"https://example.com/result-{i+1}",
                "snippet": f"這是關於 {query} 的相關信息..."
            }
            for i in range(num_results)
        ]

        result = {
            "success": True,
            "query": query,
            "num_results": len(results),
            "results": results,
            "cost": 0.01
        }

        self.total_cost += result["cost"]
        self.log_execution(result)

        return result


class WebScraperTool(BaseTool):
    """網頁爬取工具"""

    def __init__(self):
        super().__init__(
            name="WebScraperTool",
            description="爬取網頁內容"
        )

    def execute(self, url: str, extract: str = "text") -> Dict[str, Any]:
        """
        爬取網頁

        參數:
            url: 網頁 URL
            extract: 提取類型 (text/html/links)

        返回:
            爬取結果
        """
        print(f"\n🌐 爬取網頁: {url}")

        # 模擬爬取
        if extract == "text":
            content = f"這是從 {url} 提取的文本內容..."
        elif extract == "links":
            content = [f"{url}/page-{i}" for i in range(5)]
        else:
            content = f"<html>...</html>"

        result = {
            "success": True,
            "url": url,
            "extract_type": extract,
            "content": content,
            "cost": 0.005
        }

        self.total_cost += result["cost"]
        self.log_execution(result)

        return result


# ==================== 文件工具 ====================

class FileReadTool(BaseTool):
    """文件讀取工具"""

    def __init__(self):
        super().__init__(
            name="FileReadTool",
            description="讀取文件內容"
        )

    def execute(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """
        讀取文件

        參數:
            file_path: 文件路徑
            encoding: 文件編碼

        返回:
            文件內容
        """
        print(f"\n📖 讀取文件: {file_path}")

        try:
            # 模擬讀取
            content = f"文件內容: {file_path}\n這是模擬的文件內容..."

            result = {
                "success": True,
                "file_path": file_path,
                "content": content,
                "size": len(content),
                "cost": 0.001
            }

        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "cost": 0.001
            }

        self.total_cost += result["cost"]
        self.log_execution(result)

        return result


class FileWriteTool(BaseTool):
    """文件寫入工具"""

    def __init__(self):
        super().__init__(
            name="FileWriteTool",
            description="寫入文件內容"
        )

    def execute(
        self,
        file_path: str,
        content: str,
        mode: str = "w",
        encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """
        寫入文件

        參數:
            file_path: 文件路徑
            content: 文件內容
            mode: 寫入模式 (w/a)
            encoding: 文件編碼

        返回:
            寫入結果
        """
        print(f"\n📝 寫入文件: {file_path}")

        try:
            # 模擬寫入
            bytes_written = len(content)

            result = {
                "success": True,
                "file_path": file_path,
                "bytes_written": bytes_written,
                "mode": mode,
                "cost": 0.002
            }

        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "cost": 0.002
            }

        self.total_cost += result["cost"]
        self.log_execution(result)

        return result


# ==================== 數據處理工具 ====================

class DataAnalysisTool(BaseTool):
    """數據分析工具"""

    def __init__(self):
        super().__init__(
            name="DataAnalysisTool",
            description="分析數據並生成統計信息"
        )

    def execute(self, data: List[Dict], analysis_type: str = "summary") -> Dict[str, Any]:
        """
        分析數據

        參數:
            data: 數據列表
            analysis_type: 分析類型 (summary/stats/trends)

        返回:
            分析結果
        """
        print(f"\n📊 數據分析: {analysis_type}")

        # 模擬分析
        if analysis_type == "summary":
            analysis = {
                "total_records": len(data),
                "columns": ["col1", "col2", "col3"],
                "data_types": {"col1": "string", "col2": "number"}
            }
        elif analysis_type == "stats":
            analysis = {
                "mean": 42.5,
                "median": 40.0,
                "std_dev": 12.3,
                "min": 10.0,
                "max": 100.0
            }
        else:
            analysis = {
                "trend": "increasing",
                "correlation": 0.85
            }

        result = {
            "success": True,
            "analysis_type": analysis_type,
            "analysis": analysis,
            "cost": 0.02
        }

        self.total_cost += result["cost"]
        self.log_execution(result)

        return result


class CSVProcessorTool(BaseTool):
    """CSV 處理工具"""

    def __init__(self):
        super().__init__(
            name="CSVProcessorTool",
            description="處理 CSV 文件"
        )

    def execute(
        self,
        file_path: str,
        operation: str = "read",
        **kwargs
    ) -> Dict[str, Any]:
        """
        處理 CSV

        參數:
            file_path: CSV 文件路徑
            operation: 操作類型 (read/write/filter/sort)
            **kwargs: 其他參數

        返回:
            處理結果
        """
        print(f"\n📊 CSV 操作: {operation} - {file_path}")

        # 模擬處理
        if operation == "read":
            data = [
                {"name": "Alice", "age": 30, "score": 95},
                {"name": "Bob", "age": 25, "score": 87},
                {"name": "Charlie", "age": 35, "score": 92}
            ]
        elif operation == "filter":
            data = [{"name": "Alice", "age": 30, "score": 95}]
        else:
            data = []

        result = {
            "success": True,
            "operation": operation,
            "file_path": file_path,
            "data": data,
            "rows": len(data),
            "cost": 0.01
        }

        self.total_cost += result["cost"]
        self.log_execution(result)

        return result


# ==================== 代碼工具 ====================

class CodeExecutionTool(BaseTool):
    """代碼執行工具"""

    def __init__(self):
        super().__init__(
            name="CodeExecutionTool",
            description="執行 Python 代碼"
        )

    def execute(
        self,
        code: str,
        timeout: int = 30,
        safe_mode: bool = True
    ) -> Dict[str, Any]:
        """
        執行代碼

        參數:
            code: Python 代碼
            timeout: 超時時間（秒）
            safe_mode: 安全模式

        返回:
            執行結果
        """
        print(f"\n💻 執行代碼:")
        print(f"  {code[:50]}...")

        # 模擬執行
        if safe_mode:
            # 檢查危險操作
            dangerous_keywords = ["os.system", "subprocess", "eval", "exec"]
            if any(keyword in code for keyword in dangerous_keywords):
                result = {
                    "success": False,
                    "error": "安全模式禁止執行此代碼",
                    "cost": 0.005
                }
            else:
                result = {
                    "success": True,
                    "output": "代碼執行成功\n輸出: 42",
                    "execution_time": 0.123,
                    "cost": 0.01
                }
        else:
            result = {
                "success": True,
                "output": "代碼執行成功",
                "cost": 0.01
            }

        self.total_cost += result["cost"]
        self.log_execution(result)

        return result


class GitTool(BaseTool):
    """Git 操作工具"""

    def __init__(self):
        super().__init__(
            name="GitTool",
            description="執行 Git 操作"
        )

    def execute(
        self,
        operation: str,
        repo_path: str = ".",
        **kwargs
    ) -> Dict[str, Any]:
        """
        執行 Git 操作

        參數:
            operation: Git 操作 (status/commit/push/pull)
            repo_path: 倉庫路徑
            **kwargs: 其他參數

        返回:
            操作結果
        """
        print(f"\n🔧 Git 操作: {operation}")

        # 模擬 Git 操作
        if operation == "status":
            output = "On branch main\nnothing to commit, working tree clean"
        elif operation == "commit":
            output = f"[main abc123] {kwargs.get('message', 'commit message')}"
        elif operation == "push":
            output = "Pushing to origin...\nDone."
        else:
            output = f"Git {operation} completed"

        result = {
            "success": True,
            "operation": operation,
            "output": output,
            "cost": 0.005
        }

        self.total_cost += result["cost"]
        self.log_execution(result)

        return result


# ==================== API 工具 ====================

class APICallTool(BaseTool):
    """API 調用工具"""

    def __init__(self):
        super().__init__(
            name="APICallTool",
            description="調用 REST API"
        )

    def execute(
        self,
        url: str,
        method: str = "GET",
        headers: Dict = None,
        data: Dict = None
    ) -> Dict[str, Any]:
        """
        調用 API

        參數:
            url: API URL
            method: HTTP 方法
            headers: 請求頭
            data: 請求數據

        返回:
            API 響應
        """
        print(f"\n🌐 API 調用: {method} {url}")

        # 模擬 API 調用
        response = {
            "status_code": 200,
            "data": {
                "success": True,
                "message": "API call successful",
                "timestamp": datetime.now().isoformat()
            }
        }

        result = {
            "success": True,
            "url": url,
            "method": method,
            "response": response,
            "cost": 0.003
        }

        self.total_cost += result["cost"]
        self.log_execution(result)

        return result


# ==================== 工具管理器 ====================

class ToolManager:
    """工具管理器"""

    def __init__(self):
        """初始化工具管理器"""
        self.tools: Dict[str, BaseTool] = {}
        self.register_default_tools()

    def register_default_tools(self):
        """註冊默認工具"""
        default_tools = [
            GoogleSearchTool(),
            WebScraperTool(),
            FileReadTool(),
            FileWriteTool(),
            DataAnalysisTool(),
            CSVProcessorTool(),
            CodeExecutionTool(),
            GitTool(),
            APICallTool()
        ]

        for tool in default_tools:
            self.register_tool(tool)

    def register_tool(self, tool: BaseTool):
        """註冊工具"""
        self.tools[tool.name] = tool
        print(f"✅ 註冊工具: {tool.name}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """獲取工具"""
        return self.tools.get(name)

    def list_tools(self):
        """列出所有工具"""
        print("\n=== 可用工具 ===")
        for name, tool in self.tools.items():
            print(f"\n📦 {name}")
            print(f"   {tool.description}")
            stats = tool.get_stats()
            print(f"   執行次數: {stats['executions']}, 總成本: ${stats['total_cost']:.4f}")

    def get_total_stats(self) -> Dict:
        """獲取總體統計"""
        total_executions = sum(t.execution_count for t in self.tools.values())
        total_cost = sum(t.total_cost for t in self.tools.values())

        return {
            "total_tools": len(self.tools),
            "total_executions": total_executions,
            "total_cost": total_cost
        }


# ==================== 工具鏈 ====================

class ToolChain:
    """工具鏈 - 組合多個工具完成複雜任務"""

    def __init__(self, name: str, tools: List[BaseTool]):
        """
        初始化工具鏈

        參數:
            name: 工具鏈名稱
            tools: 工具列表
        """
        self.name = name
        self.tools = tools

    def execute(self, input_data: Any) -> Dict[str, Any]:
        """
        執行工具鏈

        參數:
            input_data: 輸入數據

        返回:
            最終結果
        """
        print(f"\n🔗 執行工具鏈: {self.name}")
        print("=" * 50)

        data = input_data
        results = []

        for i, tool in enumerate(self.tools, 1):
            print(f"\n步驟 {i}/{len(self.tools)}: {tool.name}")

            # 執行工具
            result = self._execute_tool(tool, data)
            results.append(result)

            # 檢查是否成功
            if not result.get("success", False):
                print(f"❌ 工具執行失敗，停止工具鏈")
                break

            # 傳遞數據到下一個工具
            data = result

        print("\n✅ 工具鏈執行完成")

        return {
            "chain_name": self.name,
            "steps": results,
            "final_result": data
        }

    def _execute_tool(self, tool: BaseTool, data: Any) -> Dict:
        """執行單個工具"""
        # 這裡需要根據具體工具類型處理數據
        # 簡化示例，實際需要更智能的數據轉換
        if isinstance(tool, GoogleSearchTool):
            return tool.execute(query=str(data))
        elif isinstance(tool, FileWriteTool):
            return tool.execute(file_path="output.txt", content=str(data))
        else:
            return {"success": True, "data": data}


# ==================== 示例場景 ====================

def example_1_basic_tools():
    """示例 1: 基本工具使用"""
    print("\n" + "=" * 60)
    print("示例 1: 基本工具使用")
    print("=" * 60)

    # 創建工具管理器
    manager = ToolManager()

    # 使用搜索工具
    search_tool = manager.get_tool("GoogleSearchTool")
    result = search_tool.execute(query="SuperAGI framework", num_results=3)
    print(f"\n搜索結果: {result['num_results']} 個")

    # 使用文件工具
    file_tool = manager.get_tool("FileWriteTool")
    content = json.dumps(result, indent=2, ensure_ascii=False)
    file_result = file_tool.execute(file_path="search_results.json", content=content)
    print(f"\n寫入文件: {file_result['bytes_written']} 字節")

    # 顯示統計
    manager.list_tools()


def example_2_data_processing_chain():
    """示例 2: 數據處理工具鏈"""
    print("\n" + "=" * 60)
    print("示例 2: 數據處理工具鏈")
    print("=" * 60)

    # 創建工具鏈
    chain = ToolChain(
        name="DataProcessingChain",
        tools=[
            FileReadTool(),      # 1. 讀取文件
            CSVProcessorTool(),  # 2. 處理 CSV
            DataAnalysisTool(),  # 3. 分析數據
            FileWriteTool()      # 4. 保存結果
        ]
    )

    # 執行工具鏈
    result = chain.execute(input_data="data.csv")

    print(f"\n工具鏈結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def example_3_research_workflow():
    """示例 3: 研究工作流"""
    print("\n" + "=" * 60)
    print("示例 3: 研究工作流")
    print("=" * 60)

    manager = ToolManager()

    # 步驟 1: 搜索
    print("\n步驟 1: 搜索資料")
    search = manager.get_tool("GoogleSearchTool")
    search_results = search.execute(query="AI Agent frameworks 2024", num_results=5)

    # 步驟 2: 爬取網頁
    print("\n步驟 2: 爬取詳細內容")
    scraper = manager.get_tool("WebScraperTool")
    contents = []
    for result in search_results["results"][:2]:
        content = scraper.execute(url=result["url"], extract="text")
        contents.append(content)

    # 步驟 3: 保存結果
    print("\n步驟 3: 保存研究結果")
    writer = manager.get_tool("FileWriteTool")
    report = {
        "topic": "AI Agent Frameworks",
        "search_results": search_results,
        "detailed_content": contents,
        "timestamp": datetime.now().isoformat()
    }
    writer.execute(
        file_path="research_report.json",
        content=json.dumps(report, indent=2, ensure_ascii=False)
    )

    # 顯示總體統計
    stats = manager.get_total_stats()
    print(f"\n總體統計:")
    print(f"  總工具數: {stats['total_tools']}")
    print(f"  總執行次數: {stats['total_executions']}")
    print(f"  總成本: ${stats['total_cost']:.4f}")


def example_4_code_development():
    """示例 4: 代碼開發工作流"""
    print("\n" + "=" * 60)
    print("示例 4: 代碼開發工作流")
    print("=" * 60)

    manager = ToolManager()

    # 讀取代碼
    reader = manager.get_tool("FileReadTool")
    code_content = reader.execute(file_path="app.py")

    # 執行代碼分析
    code_exec = manager.get_tool("CodeExecutionTool")
    test_code = """
def test_function():
    result = 2 + 2
    assert result == 4
    return result

print(test_function())
"""
    exec_result = code_exec.execute(code=test_code, safe_mode=True)
    print(f"\n代碼執行輸出:")
    print(exec_result.get("output", ""))

    # Git 操作
    git = manager.get_tool("GitTool")
    status = git.execute(operation="status")
    print(f"\nGit 狀態:")
    print(status["output"])


def example_5_api_integration():
    """示例 5: API 整合"""
    print("\n" + "=" * 60)
    print("示例 5: API 整合")
    print("=" * 60)

    manager = ToolManager()
    api_tool = manager.get_tool("APICallTool")

    # GET 請求
    get_result = api_tool.execute(
        url="https://api.example.com/data",
        method="GET",
        headers={"Authorization": "Bearer token"}
    )
    print(f"\nGET 請求結果:")
    print(json.dumps(get_result["response"], indent=2))

    # POST 請求
    post_result = api_tool.execute(
        url="https://api.example.com/data",
        method="POST",
        headers={"Content-Type": "application/json"},
        data={"key": "value"}
    )
    print(f"\nPOST 請求結果:")
    print(json.dumps(post_result["response"], indent=2))


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("\n" + "🔧 " * 20)
    print("SuperAGI 工具使用教程")
    print("🔧 " * 20)

    try:
        # 示例 1: 基本工具
        example_1_basic_tools()

        # 示例 2: 工具鏈
        example_2_data_processing_chain()

        # 示例 3: 研究工作流
        example_3_research_workflow()

        # 示例 4: 代碼開發
        example_4_code_development()

        # 示例 5: API 整合
        example_5_api_integration()

        print("\n" + "=" * 60)
        print("✅ 所有工具示例執行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 執行出錯: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
