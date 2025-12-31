"""
CopilotKit 自定義 UI 範例

這個範例展示如何自定義 CopilotKit 的 UI 組件，包括：
1. 自定義聊天界面樣式
2. 自定義消息渲染
3. 主題定制
4. 自定義按鈕和控制項
5. 完全自定義的聊天組件
6. 品牌化設計

CopilotKit 提供的 UI 組件都支持高度自定義
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from copilotkit import CopilotKitSDK, Action
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from typing import Any, Dict
import uvicorn


# ============================================================================
# 後端部分（保持簡單，重點在前端 UI）
# ============================================================================

app = FastAPI(title="CopilotKit 自定義 UI 範例")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key")

sdk = CopilotKitSDK()

# 簡單的示例 Action
def greet(name: str) -> Dict[str, Any]:
    return {"success": True, "message": f"你好，{name}！"}

sdk.add_action(Action(
    name="greet",
    description="問候用戶",
    parameters=[{"name": "name", "type": "string", "required": True}],
    handler=greet
))

add_fastapi_endpoint(app, sdk, "/copilotkit")

@app.get("/")
async def root():
    return {"message": "CopilotKit 自定義 UI 範例"}


# ============================================================================
# React + TypeScript 前端部分 - 自定義 UI
# ============================================================================

REACT_CODE = """
// ===== 安裝額外依賴 =====
// npm install @copilotkit/react-core @copilotkit/react-ui
// npm install styled-components (可選，用於樣式管理)

// ===== CustomTheme.tsx - 主題定制 =====
import React from 'react';
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

// ========== 1. 使用 CSS 變量自定義主題 ==========

// styles/custom-theme.css
const customThemeCSS = `
/* 自定義 CopilotKit 主題 */
:root {
  /* 主色調 */
  --copilot-primary-color: #6366f1;
  --copilot-primary-hover: #4f46e5;

  /* 背景色 */
  --copilot-bg-primary: #ffffff;
  --copilot-bg-secondary: #f9fafb;
  --copilot-bg-tertiary: #f3f4f6;

  /* 文字顏色 */
  --copilot-text-primary: #111827;
  --copilot-text-secondary: #6b7280;
  --copilot-text-tertiary: #9ca3af;

  /* 邊框 */
  --copilot-border-color: #e5e7eb;
  --copilot-border-radius: 12px;

  /* 陰影 */
  --copilot-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --copilot-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --copilot-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);

  /* AI 消息氣泡 */
  --copilot-ai-message-bg: #f0f9ff;
  --copilot-ai-message-text: #0c4a6e;

  /* 用戶消息氣泡 */
  --copilot-user-message-bg: #6366f1;
  --copilot-user-message-text: #ffffff;
}

/* 深色主題 */
.dark-theme {
  --copilot-primary-color: #818cf8;
  --copilot-bg-primary: #1f2937;
  --copilot-bg-secondary: #111827;
  --copilot-text-primary: #f9fafb;
  --copilot-text-secondary: #d1d5db;
  --copilot-border-color: #374151;
}

/* 自定義聊天容器 */
.copilot-chat-container {
  font-family: 'Inter', -apple-system, sans-serif;
  border-radius: var(--copilot-border-radius);
  box-shadow: var(--copilot-shadow-lg);
}

/* 自定義消息氣泡 */
.copilot-message {
  border-radius: 18px;
  padding: 12px 16px;
  max-width: 80%;
  margin-bottom: 8px;
}

.copilot-message-ai {
  background: var(--copilot-ai-message-bg);
  color: var(--copilot-ai-message-text);
  align-self: flex-start;
}

.copilot-message-user {
  background: var(--copilot-user-message-bg);
  color: var(--copilot-user-message-text);
  align-self: flex-end;
}

/* 輸入框樣式 */
.copilot-input {
  border-radius: 24px;
  border: 2px solid var(--copilot-border-color);
  padding: 12px 20px;
  font-size: 14px;
  transition: all 0.2s;
}

.copilot-input:focus {
  border-color: var(--copilot-primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

/* 發送按鈕 */
.copilot-send-button {
  background: var(--copilot-primary-color);
  color: white;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.copilot-send-button:hover {
  background: var(--copilot-primary-hover);
  transform: scale(1.05);
}
`;

// ========== 2. 使用內聯樣式自定義 ==========

function CustomStyledSidebar() {
  return (
    <CopilotSidebar
      instructions="你是一個友好的助手"
      labels={{
        title: "🤖 AI 助手",
        initial: "嗨！我是你的智能助手",
        placeholder: "輸入訊息..."
      }}
      // 自定義樣式
      className="custom-copilot-sidebar"
      style={{
        width: '400px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '0',
      }}
      // 其他自定義選項
      defaultOpen={true}
      clickOutsideToClose={false}
    />
  );
}

// ========== 3. 完全自定義的聊天組件 ==========

import { useCopilotChat, useCopilotAction } from "@copilotkit/react-core";

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

function FullyCustomChat() {
  const [messages, setMessages] = React.useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '你好！我是你的專屬 AI 助手。有什麼可以幫你的嗎？',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // 這裡調用 CopilotKit API
    // 實際應用中會使用 useCopilotChat hook

    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '這是一個自定義的響應。',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '600px',
      maxWidth: '800px',
      margin: '0 auto',
      border: '1px solid #e5e7eb',
      borderRadius: '16px',
      overflow: 'hidden',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
    }}>
      {/* 頭部 */}
      <div style={{
        padding: '20px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          borderRadius: '50%',
          background: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '20px'
        }}>
          🤖
        </div>
        <div>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>
            AI 智能助手
          </h3>
          <p style={{ margin: 0, fontSize: '12px', opacity: 0.9 }}>
            在線 · 隨時為您服務
          </p>
        </div>
      </div>

      {/* 消息列表 */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '20px',
        background: '#f9fafb'
      }}>
        {messages.map((message) => (
          <div
            key={message.id}
            style={{
              display: 'flex',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '16px'
            }}
          >
            <div style={{
              maxWidth: '70%',
              padding: '12px 16px',
              borderRadius: '18px',
              background: message.role === 'user'
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                : 'white',
              color: message.role === 'user' ? 'white' : '#1f2937',
              boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
            }}>
              <p style={{ margin: 0, lineHeight: '1.5' }}>
                {message.content}
              </p>
              <small style={{
                display: 'block',
                marginTop: '4px',
                fontSize: '11px',
                opacity: 0.7
              }}>
                {message.timestamp.toLocaleTimeString()}
              </small>
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{
            display: 'flex',
            justifyContent: 'flex-start',
            marginBottom: '16px'
          }}>
            <div style={{
              padding: '12px 16px',
              borderRadius: '18px',
              background: 'white',
              boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
            }}>
              <div style={{ display: 'flex', gap: '4px' }}>
                <span className="dot" style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: '#9ca3af',
                  animation: 'bounce 1.4s infinite ease-in-out'
                }} />
                <span className="dot" style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: '#9ca3af',
                  animation: 'bounce 1.4s infinite ease-in-out 0.2s'
                }} />
                <span className="dot" style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: '#9ca3af',
                  animation: 'bounce 1.4s infinite ease-in-out 0.4s'
                }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 輸入區域 */}
      <div style={{
        padding: '16px',
        background: 'white',
        borderTop: '1px solid #e5e7eb',
        display: 'flex',
        gap: '8px'
      }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="輸入訊息..."
          disabled={isLoading}
          style={{
            flex: 1,
            padding: '12px 16px',
            border: '2px solid #e5e7eb',
            borderRadius: '24px',
            fontSize: '14px',
            outline: 'none',
            transition: 'border-color 0.2s'
          }}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '50%',
            border: 'none',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            fontSize: '20px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading || !input.trim() ? 0.5 : 1,
            transition: 'all 0.2s'
          }}
        >
          ➤
        </button>
      </div>
    </div>
  );
}

// ========== 4. 自定義消息渲染器 ==========

function CustomMessageRenderer({ message }: { message: any }) {
  const isUser = message.role === 'user';

  return (
    <div style={{
      display: 'flex',
      alignItems: 'flex-start',
      gap: '12px',
      marginBottom: '16px',
      flexDirection: isUser ? 'row-reverse' : 'row'
    }}>
      {/* 頭像 */}
      <div style={{
        width: '36px',
        height: '36px',
        borderRadius: '50%',
        background: isUser ? '#6366f1' : '#10b981',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: '18px',
        flexShrink: 0
      }}>
        {isUser ? '👤' : '🤖'}
      </div>

      {/* 消息內容 */}
      <div style={{
        flex: 1,
        maxWidth: '70%'
      }}>
        <div style={{
          background: isUser ? '#6366f1' : '#f3f4f6',
          color: isUser ? 'white' : '#1f2937',
          padding: '12px 16px',
          borderRadius: '12px',
          borderTopLeftRadius: isUser ? '12px' : '4px',
          borderTopRightRadius: isUser ? '4px' : '12px'
        }}>
          {message.content}
        </div>
        <div style={{
          fontSize: '12px',
          color: '#9ca3af',
          marginTop: '4px',
          textAlign: isUser ? 'right' : 'left'
        }}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}

// ========== 5. 主應用 ==========

function App() {
  const [theme, setTheme] = React.useState<'light' | 'dark'>('light');

  return (
    <div className={theme === 'dark' ? 'dark-theme' : ''}>
      <style>{customThemeCSS}</style>

      <CopilotKit runtimeUrl="http://localhost:8000/copilotkit">
        <div style={{ padding: '40px' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '30px'
          }}>
            <h1>CopilotKit 自定義 UI 範例</h1>
            <button
              onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: '1px solid #e5e7eb',
                background: 'white',
                cursor: 'pointer'
              }}
            >
              切換主題: {theme === 'light' ? '🌞' : '🌙'}
            </button>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '30px'
          }}>
            {/* 完全自定義聊天 */}
            <div>
              <h3>完全自定義聊天</h3>
              <FullyCustomChat />
            </div>
          </div>

          {/* 使用自定義樣式的 Sidebar */}
          <CustomStyledSidebar />
        </div>
      </CopilotKit>
    </div>
  );
}

export default App;
"""


if __name__ == "__main__":
    print("\\n" + "="*70)
    print("CopilotKit 自定義 UI 範例")
    print("="*70)
    print("\\n自定義選項：")
    print("  • CSS 變量主題定制")
    print("  • 自定義消息氣泡")
    print("  • 完全自定義聊天組件")
    print("  • 深色/淺色主題切換")
    print("  • 品牌化設計")
    print("="*70 + "\\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)


"""
UI 自定義最佳實踐：

1. 主題定制方法
   ✓ CSS 變量（最簡單）
   ✓ 自定義 CSS 類
   ✓ 內聯樣式
   ✓ CSS-in-JS 庫（styled-components）

2. 設計原則
   ✓ 保持一致的視覺風格
   ✓ 確保可訪問性（對比度、字體大小）
   ✓ 響應式設計
   ✓ 流暢的動畫過渡

3. 組件自定義
   ✓ 使用提供的 props
   ✓ 自定義渲染器
   ✓ 包裝組件添加功能
   ✗ 避免過度自定義影響性能

4. 品牌化
   ✓ 使用品牌顏色
   ✓ 自定義 logo 和圖標
   ✓ 一致的字體
   ✓ 品牌化的語氣

5. 可維護性
   ✓ 使用 CSS 變量便於維護
   ✓ 模塊化樣式
   ✓ 文檔化自定義內容
   ✓ 版本控制樣式文件

UI 組件對比：

| 組件 | 自定義難度 | 靈活性 | 推薦場景 |
|------|-----------|--------|---------|
| CopilotSidebar | 低 | 中 | 快速集成 |
| CopilotPopup | 低 | 中 | 輔助功能 |
| CopilotChat | 中 | 高 | 嵌入式聊天 |
| 完全自定義 | 高 | 極高 | 特殊需求 |

常見自定義需求：

1. 更改顏色和字體
   → 使用 CSS 變量

2. 自定義消息氣泡
   → 重寫消息組件樣式

3. 添加自定義按鈕
   → 使用 render props 或包裝組件

4. 完全不同的布局
   → 使用底層 hooks 構建自定義組件

5. 品牌化
   → CSS 變量 + 自定義 logo

下一步：
- 查看 08_多Agent.py 學習複雜協作
- 查看 10_最佳實踐.py 了解最佳實踐
- 參考官方文檔了解更多自定義選項
"""
