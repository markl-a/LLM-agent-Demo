"""
CopilotKit 前端狀態管理範例

這個範例展示如何在 CopilotKit 中管理前端狀態，包括：
1. 使用 useCopilotReadable 讓 AI 讀取狀態
2. 使用 useCopilotAction 讓 AI 修改狀態
3. 與 React 狀態管理整合（useState, useReducer, Context）
4. 狀態同步和持久化
5. 複雜狀態結構的最佳實踐
"""

import os
from typing import Any, Dict, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from copilotkit import CopilotKitSDK, Action
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from pydantic import BaseModel
import uvicorn


# ============================================================================
# Python 後端部分（支持狀態持久化）
# ============================================================================

# 模擬數據庫存儲
USER_STATES_DB: Dict[str, Dict[str, Any]] = {}


app = FastAPI(title="CopilotKit 狀態管理範例")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StateModel(BaseModel):
    user_id: str
    state_data: Dict[str, Any]


# 狀態持久化 Actions
def save_state(user_id: str, state_data: Dict[str, Any]) -> Dict[str, Any]:
    """保存用戶狀態到服務器"""
    USER_STATES_DB[user_id] = state_data
    return {"success": True, "message": "狀態已保存"}


def load_state(user_id: str) -> Dict[str, Any]:
    """從服務器加載用戶狀態"""
    state = USER_STATES_DB.get(user_id)
    if state:
        return {"success": True, "state": state}
    return {"success": False, "message": "未找到狀態"}


# 初始化 SDK
sdk = CopilotKitSDK()

sdk.add_action(Action(
    name="save_state",
    description="保存當前應用狀態到服務器",
    parameters=[
        {"name": "user_id", "type": "string", "required": True},
        {"name": "state_data", "type": "object", "required": True}
    ],
    handler=save_state
))

sdk.add_action(Action(
    name="load_state",
    description="從服務器加載已保存的狀態",
    parameters=[
        {"name": "user_id", "type": "string", "required": True}
    ],
    handler=load_state
))

add_fastapi_endpoint(app, sdk, "/copilotkit")

@app.get("/")
async def root():
    return {"message": "CopilotKit 狀態管理範例"}


# ============================================================================
# React + TypeScript 前端部分
# ============================================================================

REACT_CODE = """
// ===== types.ts =====
export interface User {
  id: string;
  name: string;
  email: string;
  preferences: {
    theme: 'light' | 'dark';
    language: string;
    notifications: boolean;
  };
}

export interface AppState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  data: {
    items: any[];
    selectedId: string | null;
    filters: Record<string, any>;
  };
}

// ===== App.tsx =====
import React, { useState, useReducer, useEffect } from 'react';
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import {
  useCopilotReadable,
  useCopilotAction,
} from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";

// ========== 1. 使用 useState 管理簡單狀態 ==========

function SimpleStateExample() {
  const [count, setCount] = useState(0);
  const [items, setItems] = useState<string[]>([]);

  // 讓 AI 可以讀取狀態
  useCopilotReadable({
    description: "當前計數器的值",
    value: count,
  });

  useCopilotReadable({
    description: "項目列表",
    value: items,
  });

  // 讓 AI 可以修改狀態
  useCopilotAction({
    name: "incrementCount",
    description: "增加計數器的值",
    parameters: [
      {
        name: "amount",
        type: "number",
        description: "增加的數量",
        required: false,
      },
    ],
    handler: async ({ amount = 1 }) => {
      setCount(prev => prev + amount);
      return `計數器增加了 ${amount}，現在是 ${count + amount}`;
    },
  });

  useCopilotAction({
    name: "addItem",
    description: "添加項目到列表",
    parameters: [
      {
        name: "item",
        type: "string",
        description: "要添加的項目",
        required: true,
      },
    ],
    handler: async ({ item }) => {
      setItems(prev => [...prev, item]);
      return `已添加項目：${item}`;
    },
  });

  return (
    <div>
      <h2>計數器：{count}</h2>
      <h3>項目列表：</h3>
      <ul>
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

// ========== 2. 使用 useReducer 管理複雜狀態 ==========

type Action =
  | { type: 'SET_USER'; payload: User }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string }
  | { type: 'ADD_DATA_ITEM'; payload: any }
  | { type: 'UPDATE_FILTER'; payload: { key: string; value: any } }
  | { type: 'RESET_STATE' };

const initialState: AppState = {
  user: null,
  isLoading: false,
  error: null,
  data: {
    items: [],
    selectedId: null,
    filters: {},
  },
};

function appReducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'ADD_DATA_ITEM':
      return {
        ...state,
        data: {
          ...state.data,
          items: [...state.data.items, action.payload],
        },
      };
    case 'UPDATE_FILTER':
      return {
        ...state,
        data: {
          ...state.data,
          filters: {
            ...state.data.filters,
            [action.payload.key]: action.payload.value,
          },
        },
      };
    case 'RESET_STATE':
      return initialState;
    default:
      return state;
  }
}

function ComplexStateExample() {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // 讓 AI 讀取整個應用狀態
  useCopilotReadable({
    description: "完整的應用狀態",
    value: state,
  });

  // 分別暴露重要的子狀態（提高 AI 理解效率）
  useCopilotReadable({
    description: "當前登錄用戶信息",
    value: state.user,
  });

  useCopilotReadable({
    description: "數據項目和過濾器",
    value: state.data,
  });

  // 定義狀態修改 Actions
  useCopilotAction({
    name: "updateUser",
    description: "更新用戶信息",
    parameters: [
      {
        name: "updates",
        type: "object",
        description: "要更新的用戶字段",
        required: true,
      },
    ],
    handler: async ({ updates }) => {
      if (!state.user) {
        return "沒有登錄的用戶";
      }
      dispatch({
        type: 'SET_USER',
        payload: { ...state.user, ...updates },
      });
      return "用戶信息已更新";
    },
  });

  useCopilotAction({
    name: "updatePreferences",
    description: "更新用戶偏好設置",
    parameters: [
      {
        name: "preferences",
        type: "object",
        description: "偏好設置對象",
        required: true,
      },
    ],
    handler: async ({ preferences }) => {
      if (!state.user) return "沒有登錄的用戶";

      dispatch({
        type: 'SET_USER',
        payload: {
          ...state.user,
          preferences: { ...state.user.preferences, ...preferences },
        },
      });
      return "偏好設置已更新";
    },
  });

  useCopilotAction({
    name: "addDataItem",
    description: "添加數據項目",
    parameters: [
      {
        name: "item",
        type: "object",
        description: "要添加的數據項目",
        required: true,
      },
    ],
    handler: async ({ item }) => {
      dispatch({ type: 'ADD_DATA_ITEM', payload: item });
      return "數據項目已添加";
    },
  });

  useCopilotAction({
    name: "setFilter",
    description: "設置數據過濾器",
    parameters: [
      {
        name: "key",
        type: "string",
        description: "過濾器鍵",
        required: true,
      },
      {
        name: "value",
        type: "string",
        description: "過濾器值",
        required: true,
      },
    ],
    handler: async ({ key, value }) => {
      dispatch({ type: 'UPDATE_FILTER', payload: { key, value } });
      return `過濾器 ${key} 已設置為 ${value}`;
    },
  });

  return (
    <div>
      <h2>複雜狀態管理</h2>
      {state.user && (
        <div>
          <h3>用戶：{state.user.name}</h3>
          <p>主題：{state.user.preferences.theme}</p>
        </div>
      )}
      <p>數據項目數量：{state.data.items.length}</p>
    </div>
  );
}

// ========== 3. 使用 Context 進行全局狀態管理 ==========

import { createContext, useContext } from 'react';

interface GlobalState {
  theme: 'light' | 'dark';
  locale: string;
  settings: Record<string, any>;
}

const GlobalStateContext = createContext<{
  state: GlobalState;
  setState: React.Dispatch<React.SetStateAction<GlobalState>>;
} | null>(null);

function GlobalStateProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<GlobalState>({
    theme: 'light',
    locale: 'zh-TW',
    settings: {},
  });

  return (
    <GlobalStateContext.Provider value={{ state, setState }}>
      {children}
    </GlobalStateContext.Provider>
  );
}

function useGlobalState() {
  const context = useContext(GlobalStateContext);
  if (!context) {
    throw new Error('useGlobalState must be used within GlobalStateProvider');
  }
  return context;
}

function GlobalStateExample() {
  const { state, setState } = useGlobalState();

  // 讓 AI 讀取全局狀態
  useCopilotReadable({
    description: "應用的全局設置",
    value: state,
  });

  // 讓 AI 修改全局狀態
  useCopilotAction({
    name: "changeTheme",
    description: "切換應用主題（light/dark）",
    parameters: [
      {
        name: "theme",
        type: "string",
        description: "主題名稱",
        required: true,
      },
    ],
    handler: async ({ theme }) => {
      setState(prev => ({ ...prev, theme }));
      return `主題已切換為 ${theme}`;
    },
  });

  useCopilotAction({
    name: "changeLocale",
    description: "更改應用語言",
    parameters: [
      {
        name: "locale",
        type: "string",
        description: "語言代碼（如：en, zh-TW）",
        required: true,
      },
    ],
    handler: async ({ locale }) => {
      setState(prev => ({ ...prev, locale }));
      return `語言已切換為 ${locale}`;
    },
  });

  return (
    <div>
      <h2>當前主題：{state.theme}</h2>
      <p>當前語言：{state.locale}</p>
    </div>
  );
}

// ========== 4. 狀態持久化範例 ==========

function StatePersistenceExample() {
  const [state, setState] = useState<any>({});
  const userId = "user123"; // 實際應用中從認證系統獲取

  // 保存狀態到服務器
  useCopilotAction({
    name: "saveToServer",
    description: "將當前狀態保存到服務器",
    parameters: [],
    handler: async () => {
      try {
        const response = await fetch('http://localhost:8000/copilotkit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'save_state',
            params: { user_id: userId, state_data: state },
          }),
        });
        return "狀態已保存到服務器";
      } catch (error) {
        return "保存失敗：" + error.message;
      }
    },
  });

  // 從服務器加載狀態
  useCopilotAction({
    name: "loadFromServer",
    description: "從服務器加載已保存的狀態",
    parameters: [],
    handler: async () => {
      try {
        const response = await fetch('http://localhost:8000/copilotkit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'load_state',
            params: { user_id: userId },
          }),
        });
        const data = await response.json();
        if (data.success) {
          setState(data.state);
          return "狀態已從服務器恢復";
        }
        return "未找到保存的狀態";
      } catch (error) {
        return "加載失敗：" + error.message;
      }
    },
  });

  // 保存到 localStorage
  useEffect(() => {
    const saved = localStorage.getItem('app_state');
    if (saved) {
      setState(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('app_state', JSON.stringify(state));
  }, [state]);

  return <div>狀態持久化示例</div>;
}

// ========== 5. 主應用 ==========

function MainApp() {
  return (
    <GlobalStateProvider>
      <div className="main-app" style={{ padding: '20px' }}>
        <h1>CopilotKit 狀態管理範例</h1>

        <div className="examples">
          <section>
            <SimpleStateExample />
          </section>

          <section>
            <ComplexStateExample />
          </section>

          <section>
            <GlobalStateExample />
          </section>

          <section>
            <StatePersistenceExample />
          </section>
        </div>

        <div className="ai-hints" style={{
          marginTop: '30px',
          padding: '20px',
          background: '#f0f0f0',
          borderRadius: '8px'
        }}>
          <h3>💡 試試對 AI 說：</h3>
          <ul>
            <li>"把計數器增加 5"</li>
            <li>"添加項目：學習狀態管理"</li>
            <li>"切換到深色主題"</li>
            <li>"更改語言為英文"</li>
            <li>"更新用戶偏好，開啟通知"</li>
            <li>"添加一個過濾器，類型為已完成"</li>
            <li>"保存當前狀態到服務器"</li>
          </ul>
        </div>
      </div>
    </GlobalStateProvider>
  );
}

function App() {
  return (
    <CopilotKit runtimeUrl="http://localhost:8000/copilotkit">
      <CopilotSidebar
        instructions="你是一個狀態管理助手。幫助用戶查看和修改應用狀態。"
        labels={{
          title: "狀態助手",
          initial: "我可以幫你管理應用狀態！",
        }}
        defaultOpen={true}
      >
        <MainApp />
      </CopilotSidebar>
    </CopilotKit>
  );
}

export default App;
"""


if __name__ == "__main__":
    print("\\n" + "="*70)
    print("CopilotKit 前端狀態管理範例")
    print("="*70)
    print("\\n核心概念：")
    print("  • useCopilotReadable - 讓 AI 讀取狀態")
    print("  • useCopilotAction - 讓 AI 修改狀態")
    print("  • 支持 useState, useReducer, Context")
    print("  • 狀態持久化（localStorage + 服務器）")
    print("="*70 + "\\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)


"""
狀態管理最佳實踐：

1. 狀態暴露策略
   ✓ 暴露對 AI 有用的狀態
   ✓ 提供清晰的描述
   ✗ 避免暴露敏感信息
   ✗ 不要暴露過於底層的實現細節

2. 狀態修改
   ✓ 通過 Actions 提供明確的修改接口
   ✓ 驗證輸入參數
   ✓ 提供友好的反饋消息
   ✗ 避免直接暴露 setState

3. 性能優化
   ✓ 使用 useMemo 避免不必要的重算
   ✓ 合理拆分狀態（避免巨大的對象）
   ✓ 按需暴露狀態（不是全部）
   ✗ 避免在 Action handler 中執行耗時操作

4. 類型安全
   ✓ 使用 TypeScript 定義狀態類型
   ✓ 為 Action 參數提供明確的類型
   ✓ 使用 discriminated unions 處理複雜 Action

5. 持久化
   ✓ 敏感數據：服務器端持久化
   ✓ 用戶偏好：localStorage
   ✓ 臨時數據：sessionStorage
   ✗ 不要在客戶端存儲機密信息

狀態管理模式對比：

| 模式 | 適用場景 | 複雜度 | AI 整合難度 |
|------|----------|--------|-------------|
| useState | 簡單局部狀態 | 低 | 容易 |
| useReducer | 複雜邏輯 | 中 | 中等 |
| Context | 全局狀態 | 中 | 中等 |
| Redux | 大型應用 | 高 | 較難 |
| Zustand | 靈活狀態 | 低 | 容易 |

下一步：
- 查看 05_後端Action.py 學習後端 Action 定義
- 查看 06_流式輸出.py 學習實時更新
- 查看 10_最佳實踐.py 了解生產級實現
"""
