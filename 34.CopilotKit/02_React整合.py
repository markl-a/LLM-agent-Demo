"""
CopilotKit React 整合範例

這個範例展示了 CopilotKit 在 React 中的完整整合，包括：
1. 所有核心 Hooks 的使用
2. 不同的 UI 組件配置
3. 自定義 Actions 和狀態管理
4. 最佳實踐和常見模式

注意：這個文件包含 Python 後端和 TypeScript/React 前端代碼
"""

import os
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from copilotkit import CopilotKitSDK, Action
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from pydantic import BaseModel
import uvicorn


# ============================================================================
# Python 後端部分
# ============================================================================

# 模擬數據庫
TASKS_DB: List[Dict[str, Any]] = [
    {"id": 1, "title": "學習 CopilotKit", "completed": False},
    {"id": 2, "title": "構建 AI 應用", "completed": False},
]

app = FastAPI(title="CopilotKit React 整合")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 數據模型
class Task(BaseModel):
    title: str
    completed: bool = False


# Actions
def add_task(title: str) -> Dict[str, Any]:
    """添加新任務"""
    task = {
        "id": len(TASKS_DB) + 1,
        "title": title,
        "completed": False
    }
    TASKS_DB.append(task)
    return {"success": True, "task": task}


def toggle_task(task_id: int) -> Dict[str, Any]:
    """切換任務完成狀態"""
    for task in TASKS_DB:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            return {"success": True, "task": task}
    return {"success": False, "error": "Task not found"}


def get_tasks() -> Dict[str, Any]:
    """獲取所有任務"""
    return {"success": True, "tasks": TASKS_DB}


# 初始化 SDK
sdk = CopilotKitSDK()

sdk.add_action(Action(
    name="add_task",
    description="添加新的待辦任務",
    parameters=[{
        "name": "title",
        "type": "string",
        "description": "任務標題",
        "required": True
    }],
    handler=add_task
))

sdk.add_action(Action(
    name="toggle_task",
    description="切換任務的完成狀態",
    parameters=[{
        "name": "task_id",
        "type": "number",
        "description": "任務 ID",
        "required": True
    }],
    handler=toggle_task
))

sdk.add_action(Action(
    name="get_tasks",
    description="獲取所有任務列表",
    parameters=[],
    handler=get_tasks
))

add_fastapi_endpoint(app, sdk, "/copilotkit")

@app.get("/")
async def root():
    return {"message": "CopilotKit React 整合範例"}


# ============================================================================
# React + TypeScript 前端部分
# ============================================================================

REACT_CODE = """
// ===== 安裝依賴 =====
// npm install @copilotkit/react-core @copilotkit/react-ui
// npm install @copilotkit/react-textarea (可選，用於智能文本框)

// ===== types.ts =====
export interface Task {
  id: number;
  title: string;
  completed: boolean;
}

// ===== App.tsx =====
import React from 'react';
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import TodoApp from './TodoApp';

function App() {
  return (
    <CopilotKit runtimeUrl="http://localhost:8000/copilotkit">
      <CopilotSidebar
        instructions="你是一個待辦事項助手。幫助用戶管理任務。"
        labels={{
          title: "待辦助手",
          initial: "我可以幫你管理任務！",
        }}
        defaultOpen={true}
      >
        <TodoApp />
      </CopilotSidebar>
    </CopilotKit>
  );
}

export default App;

// ===== TodoApp.tsx - 主要組件 =====
import React, { useState } from 'react';
import {
  useCopilotAction,
  useCopilotReadable,
  useCopilotContext,
} from "@copilotkit/react-core";
import { Task } from './types';

function TodoApp() {
  const [tasks, setTasks] = useState<Task[]>([
    { id: 1, title: "學習 CopilotKit", completed: false },
    { id: 2, title: "構建 AI 應用", completed: false },
  ]);
  const [newTaskTitle, setNewTaskTitle] = useState("");

  // ========== 1. useCopilotReadable：讓 AI 讀取應用狀態 ==========
  useCopilotReadable({
    description: "當前的待辦任務列表",
    value: tasks,
  });

  useCopilotReadable({
    description: "任務統計信息",
    value: {
      total: tasks.length,
      completed: tasks.filter(t => t.completed).length,
      pending: tasks.filter(t => !t.completed).length,
    },
  });

  // ========== 2. useCopilotAction：定義 AI 可執行的操作 ==========

  // Action 1: 添加任務
  useCopilotAction({
    name: "addTask",
    description: "添加新的待辦任務到列表",
    parameters: [
      {
        name: "title",
        type: "string",
        description: "任務的標題或描述",
        required: true,
      },
    ],
    handler: async ({ title }) => {
      const newTask: Task = {
        id: Date.now(),
        title,
        completed: false,
      };
      setTasks(prev => [...prev, newTask]);
      return `已添加任務：${title}`;
    },
  });

  // Action 2: 切換任務狀態
  useCopilotAction({
    name: "toggleTask",
    description: "標記任務為已完成或未完成",
    parameters: [
      {
        name: "taskId",
        type: "number",
        description: "要切換的任務 ID",
        required: true,
      },
    ],
    handler: async ({ taskId }) => {
      setTasks(prev =>
        prev.map(task =>
          task.id === taskId
            ? { ...task, completed: !task.completed }
            : task
        )
      );
      const task = tasks.find(t => t.id === taskId);
      return `已更新任務：${task?.title}`;
    },
  });

  // Action 3: 刪除任務
  useCopilotAction({
    name: "deleteTask",
    description: "從列表中刪除指定的任務",
    parameters: [
      {
        name: "taskId",
        type: "number",
        description: "要刪除的任務 ID",
        required: true,
      },
    ],
    handler: async ({ taskId }) => {
      const task = tasks.find(t => t.id === taskId);
      setTasks(prev => prev.filter(t => t.id !== taskId));
      return `已刪除任務：${task?.title}`;
    },
  });

  // Action 4: 批量操作
  useCopilotAction({
    name: "clearCompleted",
    description: "刪除所有已完成的任務",
    parameters: [],
    handler: async () => {
      const completedCount = tasks.filter(t => t.completed).length;
      setTasks(prev => prev.filter(t => !t.completed));
      return `已清除 ${completedCount} 個已完成的任務`;
    },
  });

  // Action 5: 智能建議
  useCopilotAction({
    name: "suggestTasks",
    description: "根據當前任務建議新的相關任務",
    parameters: [
      {
        name: "category",
        type: "string",
        description: "任務類別（如：工作、學習、生活）",
        required: false,
      },
    ],
    handler: async ({ category }) => {
      // 這裡可以整合 AI 生成建議
      const suggestions = [
        "複習今天學到的內容",
        "準備明天的計劃",
        "整理工作筆記",
      ];
      return `建議的任務：\\n${suggestions.join("\\n")}`;
    },
  });

  // ========== 3. useCopilotContext：訪問 Copilot 上下文 ==========
  const context = useCopilotContext();

  // 手動添加任務
  const handleAddTask = () => {
    if (newTaskTitle.trim()) {
      const newTask: Task = {
        id: Date.now(),
        title: newTaskTitle,
        completed: false,
      };
      setTasks([...tasks, newTask]);
      setNewTaskTitle("");
    }
  };

  // UI 渲染
  return (
    <div className="todo-app" style={{ padding: '20px' }}>
      <h1>AI 驅動的待辦事項</h1>

      {/* 統計信息 */}
      <div className="stats" style={{
        marginBottom: '20px',
        padding: '10px',
        background: '#f0f0f0',
        borderRadius: '5px'
      }}>
        <p>總任務：{tasks.length}</p>
        <p>已完成：{tasks.filter(t => t.completed).length}</p>
        <p>待完成：{tasks.filter(t => !t.completed).length}</p>
      </div>

      {/* 添加任務表單 */}
      <div className="add-task" style={{ marginBottom: '20px' }}>
        <input
          type="text"
          value={newTaskTitle}
          onChange={(e) => setNewTaskTitle(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleAddTask()}
          placeholder="輸入新任務..."
          style={{
            padding: '10px',
            width: '70%',
            marginRight: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        />
        <button
          onClick={handleAddTask}
          style={{
            padding: '10px 20px',
            background: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          添加
        </button>
      </div>

      {/* AI 提示 */}
      <div className="ai-hints" style={{
        marginBottom: '20px',
        padding: '15px',
        background: '#e3f2fd',
        borderRadius: '5px',
        border: '1px solid #2196F3'
      }}>
        <h3>💡 試試對 AI 說：</h3>
        <ul>
          <li>"添加一個任務：學習 React Hooks"</li>
          <li>"標記第一個任務為已完成"</li>
          <li>"刪除所有已完成的任務"</li>
          <li>"給我一些學習相關的任務建議"</li>
          <li>"目前有多少未完成的任務？"</li>
        </ul>
      </div>

      {/* 任務列表 */}
      <div className="task-list">
        {tasks.length === 0 ? (
          <p style={{ color: '#999', textAlign: 'center' }}>
            沒有任務。添加一個或讓 AI 幫你添加！
          </p>
        ) : (
          tasks.map(task => (
            <div
              key={task.id}
              className="task-item"
              style={{
                padding: '15px',
                marginBottom: '10px',
                background: 'white',
                border: '1px solid #ddd',
                borderRadius: '5px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                <input
                  type="checkbox"
                  checked={task.completed}
                  onChange={() => {
                    setTasks(tasks.map(t =>
                      t.id === task.id
                        ? { ...t, completed: !t.completed }
                        : t
                    ));
                  }}
                  style={{ marginRight: '15px', cursor: 'pointer' }}
                />
                <span
                  style={{
                    textDecoration: task.completed ? 'line-through' : 'none',
                    color: task.completed ? '#999' : '#000',
                  }}
                >
                  {task.title}
                </span>
              </div>
              <button
                onClick={() => setTasks(tasks.filter(t => t.id !== task.id))}
                style={{
                  padding: '5px 10px',
                  background: '#f44336',
                  color: 'white',
                  border: 'none',
                  borderRadius: '3px',
                  cursor: 'pointer'
                }}
              >
                刪除
              </button>
            </div>
          ))
        )}
      </div>

      {/* 批量操作 */}
      {tasks.filter(t => t.completed).length > 0 && (
        <button
          onClick={() => setTasks(tasks.filter(t => !t.completed))}
          style={{
            marginTop: '20px',
            padding: '10px 20px',
            background: '#ff9800',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          清除已完成任務 ({tasks.filter(t => t.completed).length})
        </button>
      )}
    </div>
  );
}

export default TodoApp;

// ===== 進階範例：使用 CopilotTextarea =====
import { CopilotTextarea } from "@copilotkit/react-textarea";

function SmartNotepad() {
  const [content, setContent] = useState("");

  return (
    <div>
      <h2>AI 輔助筆記本</h2>
      <CopilotTextarea
        className="smart-textarea"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="開始寫作...按 Ctrl+K 呼叫 AI 助手"
        autosuggestionsConfig={{
          textareaPurpose: "筆記本，用於記錄想法和任務",
          chatApiConfigs: {
            suggestionsApiConfig: {
              forwardedParams: {
                max_tokens: 20,
                stop: [".", "\\n"],
              },
            },
          },
        }}
        style={{
          width: '100%',
          minHeight: '200px',
          padding: '10px',
          fontSize: '16px',
        }}
      />
    </div>
  );
}

// ===== 不同的 UI 組件配置 =====

// 1. 側邊欄模式（CopilotSidebar）- 如上所示

// 2. 彈出窗口模式（CopilotPopup）
import { CopilotPopup } from "@copilotkit/react-ui";

<CopilotPopup
  instructions="你是一個待辦助手"
  labels={{
    title: "AI 助手",
    initial: "需要幫助嗎？",
    placeholder: "輸入消息..."
  }}
  defaultOpen={false}  // 默認關閉
  clickOutsideToClose={true}  // 點擊外部關閉
/>

// 3. 對話框模式（CopilotDialog）
import { CopilotDialog } from "@copilotkit/react-ui";

function DialogExample() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button onClick={() => setIsOpen(true)}>
        打開 AI 助手
      </button>
      <CopilotDialog
        open={isOpen}
        onClose={() => setIsOpen(false)}
        instructions="你是一個友好的助手"
      />
    </>
  );
}

// 4. 自定義聊天界面（CopilotChat）
import { CopilotChat } from "@copilotkit/react-ui";

function CustomChatExample() {
  return (
    <div style={{ height: '500px', border: '1px solid #ddd' }}>
      <CopilotChat
        instructions="你是專業的任務管理助手"
        labels={{
          title: "任務助手",
          initial: "你好！我可以幫助你管理任務。",
          placeholder: "輸入消息...",
        }}
        makeSystemMessage={(message) => {
          return `系統：${message}`;
        }}
        showResponseButton={true}  // 顯示響應按鈕
      />
    </div>
  );
}
"""

# ============================================================================
# 運行和使用說明
# ============================================================================

if __name__ == "__main__":
    print("\\n" + "="*60)
    print("CopilotKit React 整合範例")
    print("="*60)
    print("\\n啟動後端服務器...")
    print("\\n前端代碼請查看上面的 REACT_CODE 變量")
    print("="*60 + "\\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
核心 Hooks 總結：

1. useCopilotAction
   - 定義 AI 可執行的操作
   - 連接 AI 推理和應用邏輯
   - 支持參數驗證

2. useCopilotReadable
   - 讓應用狀態對 AI 可見
   - AI 可以理解當前上下文
   - 支持任何可序列化數據

3. useCopilotContext
   - 訪問 Copilot 運行時信息
   - 控制對話流程
   - 獲取當前狀態

4. useMakeCopilotDocumentReadable
   - 讓文檔內容可被 AI 讀取
   - 適用於長文本場景

5. useMakeCopilotActionable
   - 簡化 Action 定義
   - 提供類型安全

UI 組件對比：

| 組件 | 用途 | 顯示方式 | 適用場景 |
|------|------|----------|----------|
| CopilotSidebar | 側邊欄 | 固定在側邊 | 主要功能 |
| CopilotPopup | 彈出窗口 | 右下角浮動 | 輔助功能 |
| CopilotDialog | 對話框 | 模態窗口 | 臨時互動 |
| CopilotChat | 聊天界面 | 嵌入式 | 自定義布局 |

最佳實踐：

1. 狀態管理
   - 使用 useCopilotReadable 暴露必要狀態
   - 避免暴露敏感信息
   - 提供清晰的描述

2. Action 設計
   - 單一職責原則
   - 清晰的參數定義
   - 友好的返回消息

3. 用戶體驗
   - 提供使用提示
   - 實時反饋
   - 錯誤處理

4. 性能優化
   - 合理使用 useMemo
   - 避免過度渲染
   - 懶加載大數據

下一步：
- 查看 03_CoAgent.py 學習 Agent 協作
- 查看 04_前端狀態.py 深入狀態管理
- 查看 07_自定義UI.py 學習 UI 定制
"""
