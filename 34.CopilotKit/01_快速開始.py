"""
CopilotKit 快速開始範例

這個範例展示了 CopilotKit 的基本設置和使用，包括：
1. 後端 API 設置（FastAPI）
2. 基礎 Agent 配置
3. 簡單的 Action 定義
4. 前端整合示例（TypeScript/React）

官方文檔：https://docs.copilotkit.ai/
"""

import os
from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from copilotkit import CopilotKitSDK, Action
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from pydantic import BaseModel
import uvicorn


# ============================================================================
# 第一部分：基礎配置
# ============================================================================

# 環境變量設置
os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key")

# 創建 FastAPI 應用
app = FastAPI(
    title="CopilotKit 快速開始",
    description="CopilotKit 基礎範例",
    version="1.0.0"
)

# 配置 CORS（允許前端訪問）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 開發服務器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# 第二部分：定義數據模型
# ============================================================================

class UserMessage(BaseModel):
    """用戶消息模型"""
    content: str
    role: str = "user"


class CalculatorParams(BaseModel):
    """計算器參數模型"""
    expression: str


# ============================================================================
# 第三部分：定義 Actions（AI 可執行的操作）
# ============================================================================

def calculator_action(expression: str) -> Dict[str, Any]:
    """
    簡單計算器 Action

    Args:
        expression: 數學表達式（例如："2 + 2"）

    Returns:
        計算結果
    """
    try:
        # 安全評估數學表達式
        # 注意：生產環境應使用更安全的方法
        result = eval(expression, {"__builtins__": {}}, {})
        return {
            "success": True,
            "expression": expression,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "expression": expression,
            "error": str(e)
        }


def get_current_time() -> Dict[str, Any]:
    """獲取當前時間 Action"""
    from datetime import datetime
    now = datetime.now()
    return {
        "success": True,
        "time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp": now.timestamp()
    }


# ============================================================================
# 第四部分：初始化 CopilotKit SDK
# ============================================================================

# 創建 SDK 實例
sdk = CopilotKitSDK()

# 註冊 Actions
sdk.add_action(
    Action(
        name="calculator",
        description="執行數學計算。支持基本運算符：+, -, *, /, **(冪), %(取模)",
        parameters=[
            {
                "name": "expression",
                "type": "string",
                "description": "要計算的數學表達式，例如：'2 + 2' 或 '10 * 5'",
                "required": True
            }
        ],
        handler=calculator_action
    )
)

sdk.add_action(
    Action(
        name="get_time",
        description="獲取當前系統時間",
        parameters=[],
        handler=get_current_time
    )
)


# ============================================================================
# 第五部分：添加 CopilotKit 端點
# ============================================================================

# 將 CopilotKit 整合到 FastAPI
add_fastapi_endpoint(
    app,
    sdk,
    "/copilotkit",  # API 端點路徑
    # 可選配置
    # model="gpt-4",  # 指定 LLM 模型
    # temperature=0.7,  # 控制響應隨機性
)


# ============================================================================
# 第六部分：額外的 REST API 端點
# ============================================================================

@app.get("/")
async def root():
    """健康檢查端點"""
    return {
        "message": "CopilotKit 後端運行中",
        "status": "healthy",
        "endpoints": {
            "copilotkit": "/copilotkit",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """詳細健康檢查"""
    return {
        "status": "healthy",
        "service": "copilotkit-backend",
        "version": "1.0.0",
        "actions": [
            {
                "name": "calculator",
                "description": "數學計算器"
            },
            {
                "name": "get_time",
                "description": "獲取當前時間"
            }
        ]
    }


# ============================================================================
# 第七部分：前端整合代碼（React + TypeScript）
# ============================================================================

# 以下是前端代碼示例，需要在 React 項目中使用

FRONTEND_CODE = """
// ===== 安裝依賴 =====
// npm install @copilotkit/react-core @copilotkit/react-ui

// ===== App.tsx =====
import React from 'react';
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotPopup } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

function App() {
  return (
    <CopilotKit
      runtimeUrl="http://localhost:8000/copilotkit"
      // 可選配置
      // showDevConsole={true}  // 顯示調試控制台
    >
      <div className="App">
        <h1>CopilotKit 快速開始</h1>
        <p>點擊右下角的 AI 助手圖標開始對話</p>

        {/* 你的應用內容 */}
        <div className="content">
          <h2>功能演示</h2>
          <ul>
            <li>試試問：「2 + 2 等於多少？」</li>
            <li>試試問：「現在幾點？」</li>
            <li>試試問：「計算 15 * 23」</li>
          </ul>
        </div>
      </div>

      {/* CopilotKit UI 組件 */}
      <CopilotPopup
        instructions="你是一個友好的 AI 助手。你可以幫助用戶進行數學計算和查詢時間。"
        labels={{
          title: "AI 助手",
          initial: "有什麼可以幫你的嗎？",
          placeholder: "輸入訊息..."
        }}
        defaultOpen={true}  // 默認打開
      />
    </CopilotKit>
  );
}

export default App;

// ===== package.json (部分) =====
/*
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@copilotkit/react-core": "^latest",
    "@copilotkit/react-ui": "^latest"
  }
}
*/
"""


# ============================================================================
# 第八部分：運行服務器
# ============================================================================

def print_startup_info():
    """打印啟動信息"""
    print("\n" + "="*60)
    print("CopilotKit 快速開始範例")
    print("="*60)
    print("\n後端服務已啟動：")
    print("  - API 端點: http://localhost:8000")
    print("  - CopilotKit: http://localhost:8000/copilotkit")
    print("  - API 文檔: http://localhost:8000/docs")
    print("  - 健康檢查: http://localhost:8000/health")
    print("\n可用的 Actions:")
    print("  1. calculator - 執行數學計算")
    print("  2. get_time - 獲取當前時間")
    print("\n前端設置：")
    print("  1. 創建 React 項目：npx create-react-app my-app --template typescript")
    print("  2. 安裝依賴：npm install @copilotkit/react-core @copilotkit/react-ui")
    print("  3. 使用上面的 FRONTEND_CODE 更新 App.tsx")
    print("  4. 啟動前端：npm start")
    print("\n提示：")
    print("  - 確保已設置 OPENAI_API_KEY 環境變量")
    print("  - 前端將在 http://localhost:3000 運行")
    print("="*60 + "\n")


if __name__ == "__main__":
    print_startup_info()

    # 運行服務器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


# ============================================================================
# 第九部分：使用說明和測試
# ============================================================================

"""
運行步驟：

1. 設置環境變量：
   export OPENAI_API_KEY=your_openai_api_key

2. 安裝依賴：
   pip install copilotkit fastapi uvicorn

3. 運行後端：
   python 01_快速開始.py

4. 設置前端（另一個終端）：
   # 創建 React 應用
   npx create-react-app copilot-demo --template typescript
   cd copilot-demo

   # 安裝 CopilotKit
   npm install @copilotkit/react-core @copilotkit/react-ui

   # 複製上面的 FRONTEND_CODE 到 src/App.tsx

   # 啟動前端
   npm start

5. 測試：
   - 打開瀏覽器訪問 http://localhost:3000
   - 點擊右下角的 AI 助手圖標
   - 嘗試以下對話：
     * "2 + 2 等於多少？"
     * "現在幾點？"
     * "計算 15 * 23"

預期行為：
- AI 會識別需要使用的 Action（calculator 或 get_time）
- 自動調用相應的後端函數
- 返回格式化的結果

常見問題：

Q: CORS 錯誤？
A: 確保後端的 CORS 配置包含前端地址（http://localhost:3000）

Q: API Key 錯誤？
A: 檢查 OPENAI_API_KEY 是否正確設置

Q: Actions 未執行？
A: 檢查後端日誌，確認 Action 已正確註冊

擴展建議：
1. 添加更多 Actions（天氣查詢、數據庫操作等）
2. 實現用戶認證
3. 添加會話存儲
4. 自定義 UI 主題
5. 添加錯誤處理和日誌

下一步：
- 查看 02_React整合.py 學習更多前端整合技巧
- 查看 03_CoAgent.py 了解 Agent 協作
- 查看 05_後端Action.py 學習複雜 Action 定義
"""
