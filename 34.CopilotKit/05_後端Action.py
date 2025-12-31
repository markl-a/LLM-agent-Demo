"""
CopilotKit 後端 Action 定義範例

這個範例展示如何定義強大的後端 Actions，包括：
1. 基礎 Action 定義
2. 參數驗證和類型檢查
3. 錯誤處理
4. 異步操作
5. 數據庫集成
6. 第三方 API 調用
7. 文件操作
8. 認證和授權

後端 Actions 的優勢：
- 訪問數據庫和敏感資源
- 執行複雜計算
- 調用外部 API
- 保護業務邏輯
"""

import os
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from copilotkit import CopilotKitSDK, Action
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from pydantic import BaseModel, EmailStr, validator
import uvicorn
import httpx
import json


# ============================================================================
# 第一部分：數據模型定義
# ============================================================================

class User(BaseModel):
    """用戶模型"""
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('名稱不能為空')
        return v


class Task(BaseModel):
    """任務模型"""
    title: str
    description: Optional[str] = None
    priority: int = 1
    due_date: Optional[datetime] = None

    @validator('priority')
    def priority_must_be_valid(cls, v):
        if v < 1 or v > 5:
            raise ValueError('優先級必須在 1-5 之間')
        return v


# ============================================================================
# 第二部分：模擬數據庫
# ============================================================================

class Database:
    """簡單的內存數據庫"""

    def __init__(self):
        self.users: Dict[int, Dict] = {
            1: {"id": 1, "name": "張三", "email": "zhang@example.com",
                "created_at": datetime.now().isoformat()}
        }
        self.tasks: List[Dict] = []
        self.next_user_id = 2
        self.next_task_id = 1

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """獲取用戶"""
        await asyncio.sleep(0.1)  # 模擬數據庫延遲
        return self.users.get(user_id)

    async def create_user(self, name: str, email: str) -> Dict:
        """創建用戶"""
        user = {
            "id": self.next_user_id,
            "name": name,
            "email": email,
            "created_at": datetime.now().isoformat()
        }
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        return user

    async def create_task(self, task_data: Dict) -> Dict:
        """創建任務"""
        task = {
            "id": self.next_task_id,
            **task_data,
            "created_at": datetime.now().isoformat()
        }
        self.tasks.append(task)
        self.next_task_id += 1
        return task

    async def search_tasks(self, query: str) -> List[Dict]:
        """搜索任務"""
        await asyncio.sleep(0.1)
        return [
            task for task in self.tasks
            if query.lower() in task.get("title", "").lower()
        ]


db = Database()


# ============================================================================
# 第三部分：工具函數
# ============================================================================

async def fetch_external_data(url: str) -> Dict[str, Any]:
    """從外部 API 獲取數據"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except httpx.HTTPError as e:
            return {"success": False, "error": str(e)}


def validate_email(email: str) -> bool:
    """驗證郵箱格式"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# ============================================================================
# 第四部分：FastAPI 應用設置
# ============================================================================

app = FastAPI(
    title="CopilotKit 後端 Actions",
    description="展示強大的後端 Action 功能",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設置環境變量
os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key")


# ============================================================================
# 第五部分：定義後端 Actions
# ============================================================================

# Action 1: 基礎數據庫操作
async def get_user_info(user_id: int) -> Dict[str, Any]:
    """
    獲取用戶信息

    Args:
        user_id: 用戶 ID

    Returns:
        用戶信息或錯誤消息
    """
    try:
        user = await db.get_user(user_id)
        if user:
            return {
                "success": True,
                "user": user
            }
        return {
            "success": False,
            "error": f"未找到用戶 ID: {user_id}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"獲取用戶失敗: {str(e)}"
        }


async def create_user(name: str, email: str) -> Dict[str, Any]:
    """
    創建新用戶

    Args:
        name: 用戶名稱
        email: 用戶郵箱

    Returns:
        創建的用戶信息
    """
    try:
        # 驗證郵箱
        if not validate_email(email):
            return {
                "success": False,
                "error": "無效的郵箱格式"
            }

        # 檢查重複
        for user in db.users.values():
            if user["email"] == email:
                return {
                    "success": False,
                    "error": "郵箱已存在"
                }

        # 創建用戶
        user = await db.create_user(name, email)
        return {
            "success": True,
            "user": user,
            "message": f"用戶 {name} 創建成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"創建用戶失敗: {str(e)}"
        }


# Action 2: 複雜業務邏輯
async def create_task_with_validation(
    title: str,
    description: Optional[str] = None,
    priority: int = 1,
    due_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    創建帶驗證的任務

    Args:
        title: 任務標題
        description: 任務描述
        priority: 優先級 (1-5)
        due_date: 截止日期 (ISO格式)

    Returns:
        創建的任務信息
    """
    try:
        # 驗證輸入
        if not title or len(title.strip()) == 0:
            return {"success": False, "error": "任務標題不能為空"}

        if priority < 1 or priority > 5:
            return {"success": False, "error": "優先級必須在 1-5 之間"}

        # 解析截止日期
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date)
                if parsed_due_date < datetime.now():
                    return {"success": False, "error": "截止日期不能在過去"}
            except ValueError:
                return {"success": False, "error": "無效的日期格式"}

        # 創建任務
        task_data = {
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": parsed_due_date.isoformat() if parsed_due_date else None,
            "status": "pending"
        }

        task = await db.create_task(task_data)

        return {
            "success": True,
            "task": task,
            "message": f"任務 '{title}' 創建成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"創建任務失敗: {str(e)}"
        }


# Action 3: 調用外部 API
async def get_weather(city: str) -> Dict[str, Any]:
    """
    獲取天氣信息（示例）

    Args:
        city: 城市名稱

    Returns:
        天氣信息
    """
    # 注意：這是一個示例，實際應用需要真實的 API key
    try:
        # 模擬 API 調用
        await asyncio.sleep(0.5)

        # 實際使用時：
        # url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
        # result = await fetch_external_data(url)

        # 模擬響應
        return {
            "success": True,
            "city": city,
            "weather": {
                "temperature": 25,
                "condition": "晴天",
                "humidity": 60
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"獲取天氣失敗: {str(e)}"
        }


# Action 4: 數據分析和處理
async def analyze_tasks() -> Dict[str, Any]:
    """
    分析任務統計信息

    Returns:
        任務分析結果
    """
    try:
        tasks = db.tasks

        if not tasks:
            return {
                "success": True,
                "message": "沒有任務數據",
                "stats": {}
            }

        # 統計分析
        total = len(tasks)
        by_priority = {}
        by_status = {}
        overdue = 0

        now = datetime.now()

        for task in tasks:
            # 按優先級統計
            priority = task.get("priority", 1)
            by_priority[priority] = by_priority.get(priority, 0) + 1

            # 按狀態統計
            status = task.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1

            # 逾期任務
            due_date_str = task.get("due_date")
            if due_date_str:
                due_date = datetime.fromisoformat(due_date_str)
                if due_date < now and task.get("status") != "completed":
                    overdue += 1

        return {
            "success": True,
            "stats": {
                "total": total,
                "by_priority": by_priority,
                "by_status": by_status,
                "overdue": overdue
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"分析失敗: {str(e)}"
        }


# Action 5: 批量操作
async def bulk_update_tasks(task_ids: List[int], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    批量更新任務

    Args:
        task_ids: 任務 ID 列表
        updates: 更新的字段

    Returns:
        更新結果
    """
    try:
        updated_count = 0
        errors = []

        for task_id in task_ids:
            task = next((t for t in db.tasks if t["id"] == task_id), None)
            if task:
                task.update(updates)
                updated_count += 1
            else:
                errors.append(f"任務 {task_id} 不存在")

        return {
            "success": True,
            "updated_count": updated_count,
            "errors": errors if errors else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"批量更新失敗: {str(e)}"
        }


# Action 6: 複雜查詢
async def search_and_filter_tasks(
    query: Optional[str] = None,
    priority: Optional[int] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    搜索和過濾任務

    Args:
        query: 搜索關鍵字
        priority: 優先級過濾
        status: 狀態過濾

    Returns:
        符合條件的任務列表
    """
    try:
        results = db.tasks.copy()

        # 關鍵字搜索
        if query:
            results = [
                t for t in results
                if query.lower() in t.get("title", "").lower()
                or query.lower() in t.get("description", "").lower()
            ]

        # 優先級過濾
        if priority:
            results = [t for t in results if t.get("priority") == priority]

        # 狀態過濾
        if status:
            results = [t for t in results if t.get("status") == status]

        return {
            "success": True,
            "count": len(results),
            "tasks": results
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"搜索失敗: {str(e)}"
        }


# ============================================================================
# 第六部分：註冊 Actions 到 CopilotKit SDK
# ============================================================================

sdk = CopilotKitSDK()

# 註冊所有 Actions
sdk.add_action(Action(
    name="get_user_info",
    description="獲取指定用戶的詳細信息",
    parameters=[
        {
            "name": "user_id",
            "type": "number",
            "description": "用戶的唯一標識符",
            "required": True
        }
    ],
    handler=get_user_info
))

sdk.add_action(Action(
    name="create_user",
    description="創建新用戶賬號",
    parameters=[
        {
            "name": "name",
            "type": "string",
            "description": "用戶姓名",
            "required": True
        },
        {
            "name": "email",
            "type": "string",
            "description": "用戶郵箱地址",
            "required": True
        }
    ],
    handler=create_user
))

sdk.add_action(Action(
    name="create_task",
    description="創建新任務，支持設置標題、描述、優先級和截止日期",
    parameters=[
        {
            "name": "title",
            "type": "string",
            "description": "任務標題",
            "required": True
        },
        {
            "name": "description",
            "type": "string",
            "description": "任務詳細描述",
            "required": False
        },
        {
            "name": "priority",
            "type": "number",
            "description": "優先級 (1-5，1最低，5最高)",
            "required": False
        },
        {
            "name": "due_date",
            "type": "string",
            "description": "截止日期 (ISO格式，如: 2024-12-31T23:59:59)",
            "required": False
        }
    ],
    handler=create_task_with_validation
))

sdk.add_action(Action(
    name="get_weather",
    description="獲取指定城市的天氣信息",
    parameters=[
        {
            "name": "city",
            "type": "string",
            "description": "城市名稱",
            "required": True
        }
    ],
    handler=get_weather
))

sdk.add_action(Action(
    name="analyze_tasks",
    description="分析任務統計信息，包括總數、優先級分布、狀態分布和逾期任務",
    parameters=[],
    handler=analyze_tasks
))

sdk.add_action(Action(
    name="search_tasks",
    description="根據多個條件搜索和過濾任務",
    parameters=[
        {
            "name": "query",
            "type": "string",
            "description": "搜索關鍵字",
            "required": False
        },
        {
            "name": "priority",
            "type": "number",
            "description": "按優先級過濾",
            "required": False
        },
        {
            "name": "status",
            "type": "string",
            "description": "按狀態過濾 (pending, in_progress, completed)",
            "required": False
        }
    ],
    handler=search_and_filter_tasks
))

# 添加 CopilotKit 端點
add_fastapi_endpoint(app, sdk, "/copilotkit")


# ============================================================================
# 第七部分：REST API 端點
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "CopilotKit 後端 Actions 範例",
        "actions": [
            "get_user_info", "create_user", "create_task",
            "get_weather", "analyze_tasks", "search_tasks"
        ]
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": {
            "users": len(db.users),
            "tasks": len(db.tasks)
        }
    }


# ============================================================================
# 第八部分：運行說明
# ============================================================================

if __name__ == "__main__":
    print("\\n" + "="*70)
    print("CopilotKit 後端 Actions 範例")
    print("="*70)
    print("\\n已註冊的 Actions:")
    print("  1. get_user_info - 獲取用戶信息")
    print("  2. create_user - 創建用戶")
    print("  3. create_task - 創建任務（帶驗證）")
    print("  4. get_weather - 獲取天氣（調用外部 API）")
    print("  5. analyze_tasks - 分析任務統計")
    print("  6. search_tasks - 搜索和過濾任務")
    print("\\n特點：")
    print("  • 完整的參數驗證")
    print("  • 異步操作支持")
    print("  • 錯誤處理")
    print("  • 數據庫集成")
    print("  • 外部 API 調用")
    print("="*70 + "\\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)


"""
後端 Action 最佳實踐：

1. 參數驗證
   ✓ 使用 Pydantic 模型驗證
   ✓ 提供清晰的錯誤消息
   ✓ 驗證業務規則
   ✗ 不要信任任何輸入

2. 錯誤處理
   ✓ 使用 try-except 捕獲異常
   ✓ 返回結構化的錯誤信息
   ✓ 記錄錯誤日誌
   ✗ 不要暴露敏感錯誤細節

3. 異步操作
   ✓ 使用 async/await
   ✓ 設置合理的超時
   ✓ 並行處理獨立任務
   ✗ 避免阻塞操作

4. 安全性
   ✓ 驗證用戶權限
   ✓ 清理和轉義輸入
   ✓ 使用環境變量存儲機密
   ✗ 不要在代碼中硬編碼機密

5. 性能
   ✓ 使用數據庫索引
   ✓ 實現緩存機制
   ✓ 限制返回數據量
   ✗ 避免 N+1 查詢

前端 vs 後端 Actions：

| 特性 | 前端 Action | 後端 Action |
|------|------------|-------------|
| 執行位置 | 瀏覽器 | 服務器 |
| 訪問權限 | 受限 | 完全訪問 |
| 安全性 | 低（可被檢查） | 高（不可見） |
| 數據庫訪問 | 否 | 是 |
| 響應速度 | 快 | 稍慢（網絡） |
| 適用場景 | UI 操作 | 業務邏輯 |

何時使用後端 Actions：
- 需要訪問數據庫
- 涉及敏感操作
- 調用外部 API
- 複雜計算
- 需要認證授權

下一步：
- 查看 06_流式輸出.py 學習實時響應
- 查看 08_多Agent.py 學習複雜協作
- 查看 09_部署指南.py 了解生產部署
"""
