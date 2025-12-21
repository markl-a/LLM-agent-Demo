# 專案改進執行計劃

> 執行日期：2025-12-21
> 執行方式：10 個 Agent 並行執行

---

## Agent 任務分配

| Agent # | 任務類型 | 任務描述 | 優先級 | 預估時間 |
|---------|---------|---------|--------|---------|
| Agent 1 | 🔴 安全 | 修復 pickle RCE 漏洞 | P0 | 2h |
| Agent 2 | 🔴 安全 | 修復 subprocess shell=True 注入 | P0 | 2h |
| Agent 3 | 🟠 CI/CD | 修復 Mypy 失敗被忽略問題 | P0 | 30min |
| Agent 4 | 🟡 測試 | 創建 test_cli.py | P1 | 3h |
| Agent 5 | 🟡 測試 | 創建 test_async_utils.py | P1 | 3h |
| Agent 6 | 🟡 測試 | 創建 test_events.py | P1 | 3h |
| Agent 7 | 🔵 架構 | 拆分 events.py 大模塊 | P1 | 4h |
| Agent 8 | 🟢 性能 | 優化緩存驅逐算法 | P1 | 3h |
| Agent 9 | 🟣 依賴 | 修復 LangChain 版本問題 | P1 | 1h |
| Agent 10 | ⚪ 開發體驗 | 添加 VS Code 配置 | P2 | 1h |

---

## 詳細任務說明

### Agent 1: 修復 pickle RCE 漏洞

**目標文件：**
- `src/llm_agent_demo/utils/serialization.py:647`
- `src/llm_agent_demo/utils/cache.py:308`

**任務：**
1. 將 `pickle.loads()` 替換為安全的 `json.loads()`
2. 添加適當的類型轉換和錯誤處理
3. 確保向後兼容性

---

### Agent 2: 修復 subprocess 注入

**目標文件：**
- `5.demo-sales-outreach-automation-langgraph/setup_script.py:80-92`
- 其他使用 `shell=True` 的文件

**任務：**
1. 將 `shell=True` 改為使用參數列表
2. 添加命令驗證和錯誤處理

---

### Agent 3: 修復 CI/CD Mypy 問題

**目標文件：**
- `.github/workflows/ci.yml`

**任務：**
1. 移除 mypy 命令後的 `|| true`
2. 確保類型錯誤能正確報告

---

### Agent 4-6: 創建測試文件

**目標：**
- Agent 4: `tests/unit/test_cli.py`
- Agent 5: `tests/unit/test_async_utils.py`
- Agent 6: `tests/unit/test_events.py`

---

### Agent 7: 拆分 events.py

**目標：**
將 1088 行的 `events.py` 拆分為：
- `event_types.py`
- `event_model.py`
- `event_emitter.py`
- `event_stats.py`

---

### Agent 8: 優化緩存算法

**目標文件：**
- `src/llm_agent_demo/utils/cache.py:201-211`

**任務：**
將 O(n) 的驅逐算法優化為 O(1)

---

### Agent 9: 修復依賴版本

**目標文件：**
- `requirements.txt`
- `requirements-lock.txt`

---

### Agent 10: 添加 VS Code 配置

**目標：**
創建 `.vscode/settings.json` 和 `.vscode/launch.json`

---

*計劃生成時間：2025-12-21*
