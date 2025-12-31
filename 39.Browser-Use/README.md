# Browser-Use - 讓 AI Agent 自動控制瀏覽器

Browser-Use 是一個創新的開源框架，專門為 LLM (大型語言模型) 與瀏覽器之間建立無縫連接橋樑，使 AI Agent 能夠智能化地自動執行各種網頁操作任務。

## 框架簡介

Browser-Use 為開發者提供了一個強大且易於使用的解決方案，讓 AI Agent 能夠像人類一樣與網頁互動。它支援複雜的網頁操作場景，包括表單填寫、數據提取、多標籤頁管理、登錄驗證等，並在 WebVoyager 基準測試中展現出超越 OpenAI Operator 的卓越性能。

## 核心特點

### 1. 卓越的性能表現
- **WebVoyager 基準測試領先**：在標準化測試中超越 OpenAI Operator
- **高效的任務執行**：優化的操作邏輯，減少不必要的等待時間
- **穩定可靠**：內建重試機制和錯誤處理

### 2. 多模型支援
Browser-Use 支援多種主流 LLM 模型：
- **OpenAI GPT**：GPT-4、GPT-3.5-turbo
- **Anthropic Claude**：Claude 3.5 Sonnet、Claude 3 Opus
- **Google Gemini**：Gemini Pro、Gemini Ultra
- **本地模型**：支援 Ollama 等本地部署方案

### 3. 真實瀏覽器環境
- **完整瀏覽器配置**：可使用現有的瀏覽器配置文件
- **Cookie 和會話保持**：支援已登錄的瀏覽器狀態
- **擴展程序支援**：相容各種瀏覽器擴展
- **多瀏覽器支援**：Chrome、Firefox、Edge 等

### 4. 靈活的操作能力
- **智能元素定位**：自動識別和操作頁面元素
- **視覺理解**：支援截圖分析和視覺反饋
- **多標籤頁管理**：並行處理多個網頁任務
- **自定義動作**：可擴展的動作系統

## 與其他方案的對比

### Browser-Use vs Computer Use (Anthropic)

| 特性 | Browser-Use | Computer Use |
|------|-------------|--------------|
| 專注領域 | 瀏覽器操作 | 完整桌面控制 |
| 性能開銷 | 低 | 高 |
| 易用性 | 簡單直接 | 需要更多設置 |
| 適用場景 | 網頁自動化 | 通用桌面任務 |
| API 複雜度 | 低 | 中等 |

**優勢**：Browser-Use 專注於瀏覽器操作，提供更輕量級和專業化的解決方案。

### Browser-Use vs OpenAI Operator

| 特性 | Browser-Use | OpenAI Operator |
|------|-------------|-----------------|
| 開源程度 | 完全開源 | 閉源 |
| 模型選擇 | 多模型支援 | 僅 OpenAI |
| WebVoyager 測試 | 領先 | 落後 |
| 定制化 | 高度可定制 | 受限 |
| 成本控制 | 靈活 | 固定 |

**優勢**：Browser-Use 提供更好的性能、完全的透明度和靈活的模型選擇。

## 技術架構

```
Browser-Use 架構
├── LLM 集成層
│   ├── OpenAI 適配器
│   ├── Claude 適配器
│   ├── Gemini 適配器
│   └── 自定義模型適配器
├── 瀏覽器控制層
│   ├── Playwright 引擎
│   ├── 元素定位系統
│   ├── 動作執行器
│   └── 狀態管理器
├── 視覺理解層
│   ├── 截圖處理
│   ├── 元素識別
│   └── 視覺反饋
└── 任務協調層
    ├── 任務規劃
    ├── 錯誤處理
    └── 結果驗證
```

## 安裝與配置

### 環境要求
- Python 3.9+
- 支援的作業系統：Windows、macOS、Linux

### 安裝步驟

1. **安裝 Browser-Use**
```bash
pip install browser-use
```

2. **安裝 Playwright 瀏覽器**
```bash
playwright install
```

3. **安裝其他依賴**
```bash
pip install -r requirements.txt
```

### 配置 API 金鑰

#### OpenAI
```bash
export OPENAI_API_KEY="your-api-key-here"
```

#### Anthropic Claude
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

#### Google Gemini
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

## 快速開始

### 基礎範例

```python
from browser_use import Agent
import asyncio

async def main():
    # 創建瀏覽器 Agent
    agent = Agent(
        task="在 Google 上搜尋 'Python 教程' 並提取前三個結果",
        llm_model="gpt-4"
    )

    # 執行任務
    result = await agent.run()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### 使用現有瀏覽器配置

```python
from browser_use import Agent, BrowserConfig

config = BrowserConfig(
    headless=False,  # 顯示瀏覽器窗口
    user_data_dir="/path/to/chrome/profile",  # 使用現有配置
    disable_security=False
)

agent = Agent(
    task="檢查我的 Gmail 收件箱",
    llm_model="claude-3-5-sonnet-20241022",
    browser_config=config
)
```

## 核心功能

### 1. 網頁導航
- 自動訪問 URL
- 智能點擊連結
- 頁面前進/後退
- 等待頁面載入

### 2. 表單操作
- 輸入文字
- 選擇下拉選單
- 勾選核取方塊
- 上傳文件
- 提交表單

### 3. 數據提取
- 提取文字內容
- 抓取表格數據
- 下載文件
- 截取螢幕截圖

### 4. 複雜互動
- 處理彈出視窗
- 管理多個標籤頁
- 執行 JavaScript
- 處理 iframe

### 5. 視覺分析
- 頁面截圖
- 元素截圖
- 視覺驗證
- OCR 文字識別

## 進階特性

### 自定義動作
```python
from browser_use import Agent, CustomAction

class ClickWithRetry(CustomAction):
    async def execute(self, page, selector, max_retries=3):
        for i in range(max_retries):
            try:
                await page.click(selector)
                return True
            except:
                if i == max_retries - 1:
                    raise
                await page.wait_for_timeout(1000)
        return False

agent = Agent(
    task="點擊登錄按鈕",
    custom_actions=[ClickWithRetry()]
)
```

### 多步驟工作流
```python
workflow = [
    "打開 example.com",
    "點擊登錄按鈕",
    "輸入用戶名和密碼",
    "點擊提交",
    "等待儀表板載入",
    "提取用戶資料"
]

agent = Agent(
    task=workflow,
    llm_model="gpt-4-turbo"
)
```

### 錯誤處理和重試
```python
from browser_use import Agent, RetryConfig

retry_config = RetryConfig(
    max_retries=3,
    retry_delay=2,
    exponential_backoff=True
)

agent = Agent(
    task="複雜的網頁操作任務",
    retry_config=retry_config
)
```

## 使用案例

### 1. 自動化測試
- 端到端測試
- 回歸測試
- 視覺回歸測試

### 2. 數據採集
- 網頁爬蟲
- 競品分析
- 價格監控

### 3. 業務流程自動化
- 表單批量填寫
- 訂單處理
- 報告生成

### 4. 監控和告警
- 網站可用性監控
- 內容變更檢測
- 異常告警

## 範例文件說明

本目錄包含 10 個完整的 Python 範例：

1. **01_快速開始.py** - 基礎瀏覽器控制和簡單任務
2. **02_網頁導航.py** - 複雜頁面導航和元素操作
3. **03_表單填寫.py** - 自動化表單填寫流程
4. **04_數據提取.py** - 網頁數據抓取和處理
5. **05_多標籤頁.py** - 多標籤頁並行管理
6. **06_登錄操作.py** - 網站登錄自動化
7. **07_購物流程.py** - 電商購物完整流程
8. **08_截圖分析.py** - 視覺分析和 OCR 功能
9. **09_自定義動作.py** - 擴展自定義瀏覽器動作
10. **10_生產部署.py** - 生產環境配置和最佳實踐

## 最佳實踐

### 1. 性能優化
- 合理設置超時時間
- 使用無頭模式提高速度
- 關閉不必要的功能（圖片、CSS）
- 複用瀏覽器實例

### 2. 穩定性提升
- 實現完善的錯誤處理
- 使用智能等待而非固定延遲
- 驗證操作結果
- 記錄詳細日誌

### 3. 安全考量
- 安全存儲憑證
- 使用環境變數
- 避免在代碼中硬編碼敏感訊息
- 定期更新依賴

### 4. 可維護性
- 模組化任務定義
- 使用配置文件
- 編寫清晰的註解
- 建立測試覆蓋

## 故障排除

### 常見問題

**問題 1：瀏覽器無法啟動**
```bash
# 重新安裝 Playwright 瀏覽器
playwright install --force
```

**問題 2：元素定位失敗**
- 增加等待時間
- 使用更具體的選擇器
- 檢查 iframe 嵌套

**問題 3：記憶體佔用過高**
- 使用無頭模式
- 及時關閉不需要的標籤頁
- 限制並發瀏覽器實例數量

## 社群與支援

- **GitHub**: [browser-use repository](https://github.com/browser-use/browser-use)
- **文檔**: [官方文檔](https://docs.browser-use.com)
- **Discord**: 加入社群討論
- **問題反饋**: GitHub Issues

## 授權協議

Browser-Use 採用 MIT 授權協議，可自由用於商業和個人專案。

## 更新日誌

### v1.0.0 (2024-12)
- 初始發布
- 支援主流 LLM 模型
- 完整的瀏覽器控制功能
- WebVoyager 基準測試驗證

### v1.1.0 (2025-01)
- 新增視覺理解能力
- 優化性能和穩定性
- 擴展自定義動作 API
- 改進錯誤處理機制

## 貢獻指南

我們歡迎社群貢獻！請參考以下步驟：

1. Fork 專案
2. 創建特性分支
3. 提交變更
4. 推送到分支
5. 創建 Pull Request

## 致謝

感謝所有為 Browser-Use 做出貢獻的開發者和社群成員。

---

**立即開始使用 Browser-Use，讓您的 AI Agent 自動化網頁操作！**
