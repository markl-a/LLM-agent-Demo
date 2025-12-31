# Browserbase - 雲端無頭瀏覽器基礎設施

## 框架介紹

Browserbase 是一個專為 AI Agent 設計的雲端無頭瀏覽器基礎設施平台。它提供了完整的瀏覽器自動化解決方案，讓開發者能夠輕鬆構建可擴展的網頁爬蟲、自動化測試和 AI 瀏覽器代理。

Browserbase 解決了傳統瀏覽器自動化的諸多痛點：
- 複雜的環境配置和依賴管理
- 瀏覽器指紋識別和反爬蟲檢測
- 資源管理和並行處理
- Session 持久化和狀態管理

通過 Browserbase，您可以專注於業務邏輯，而無需擔心底層的瀏覽器運維問題。

## 核心特性

### 1. 隱身模式 (Stealth Mode)
- **反指紋識別**: 自動處理瀏覽器指紋，避免被網站檢測
- **真實瀏覽器環境**: 使用真實的 Chrome/Firefox 瀏覽器，而非 headless 檢測特徵
- **Canvas 指紋隨機化**: 防止基於 Canvas 的追蹤技術
- **WebGL 保護**: 隱藏或偽造 WebGL 參數
- **時區和語言模擬**: 模擬真實用戶的地理位置和語言設置

### 2. Session 管理
- **持久化 Session**: 保存並復用瀏覽器 Session，包括 Cookie 和本地存儲
- **Session 共享**: 在多個請求間共享 Session 狀態
- **自動清理**: 智能管理 Session 生命週期，避免資源洩漏
- **Session 快照**: 保存和恢復瀏覽器狀態
- **並行 Session**: 支持同時運行多個獨立 Session

### 3. 代理輪換 (Proxy Rotation)
- **自動代理池**: 內置代理池管理，自動輪換 IP
- **地理位置選擇**: 指定代理的國家和城市
- **住宅代理支持**: 支持住宅代理、數據中心代理等
- **失敗重試**: 代理失敗時自動切換
- **代理健康檢查**: 實時監控代理可用性

### 4. 反檢測技術
- **User-Agent 輪換**: 智能 UA 生成和輪換
- **請求頭優化**: 模擬真實瀏覽器的請求頭
- **行為模擬**: 模擬人類操作行為（鼠標移動、滾動等）
- **驗證碼處理**: 集成驗證碼識別服務
- **速率限制**: 智能請求速率控制

### 5. 雲端基礎設施
- **零配置部署**: 無需管理服務器和瀏覽器環境
- **自動擴展**: 根據負載自動調整資源
- **全球分佈**: 多個數據中心可選
- **高可用性**: 99.9% 的服務可用性保證
- **實時監控**: 完整的性能和錯誤監控

### 6. 開發者友好
- **多語言 SDK**: 支持 Python、JavaScript、Go 等
- **豐富的 API**: 完整的 RESTful API 和 WebSocket 支持
- **調試工具**: 實時查看瀏覽器畫面和日誌
- **截圖和錄影**: 自動捕獲執行過程
- **詳細文檔**: 完善的文檔和示例代碼

## 安裝指南

### 環境要求
- Python 3.8+
- pip 包管理器
- Browserbase API Key（註冊獲取：https://browserbase.com）

### 安裝步驟

1. **安裝依賴包**
```bash
pip install -r requirements.txt
```

2. **配置環境變量**

創建 `.env` 文件並添加您的 API Key：
```env
BROWSERBASE_API_KEY=your_api_key_here
BROWSERBASE_PROJECT_ID=your_project_id_here
```

3. **驗證安裝**
```python
from browserbase import Browserbase

client = Browserbase(api_key="your_api_key")
print("Browserbase 連接成功！")
```

## 快速開始

### 基礎示例

```python
import os
from browserbase import Browserbase
from playwright.sync_api import sync_playwright

# 初始化 Browserbase 客戶端
client = Browserbase(api_key=os.getenv("BROWSERBASE_API_KEY"))

# 創建瀏覽器 Session
session = client.sessions.create(
    project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
    stealth=True,  # 啟用隱身模式
    proxy=True     # 啟用代理
)

# 使用 Playwright 連接到遠程瀏覽器
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(session.connect_url)
    page = browser.new_page()

    # 訪問網頁
    page.goto("https://example.com")

    # 提取數據
    title = page.title()
    print(f"頁面標題: {title}")

    # 截圖
    page.screenshot(path="screenshot.png")

    browser.close()

# 清理 Session
client.sessions.delete(session.id)
```

### 使用 Session 持久化

```python
# 創建持久化 Session
session = client.sessions.create(
    project_id=os.getenv("BROWSERBASE_PROJECT_ID"),
    keep_alive=True,  # Session 不會自動過期
    timeout=3600      # 1小時超時
)

# 第一次使用
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(session.connect_url)
    page = browser.new_page()
    page.goto("https://example.com/login")
    # 執行登錄操作...
    browser.close()

# 稍後重用同一個 Session（保持登錄狀態）
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(session.connect_url)
    page = browser.new_page()
    page.goto("https://example.com/dashboard")
    # 已經是登錄狀態
    browser.close()
```

### AI Agent 整合示例

```python
from browserbase import Browserbase
from openai import OpenAI

# 初始化客戶端
bb_client = Browserbase(api_key=os.getenv("BROWSERBASE_API_KEY"))
ai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 創建瀏覽器 Session
session = bb_client.sessions.create(
    project_id=os.getenv("BROWSERBASE_PROJECT_ID")
)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(session.connect_url)
    page = browser.new_page()
    page.goto("https://news.ycombinator.com")

    # 提取頁面內容
    content = page.inner_text("body")

    # 使用 AI 分析內容
    response = ai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "你是一個新聞分析助手"},
            {"role": "user", "content": f"總結以下新聞內容：\n{content[:2000]}"}
        ]
    )

    print(response.choices[0].message.content)
    browser.close()
```

## 使用場景

### 1. 網頁爬蟲
- 電商價格監控
- 新聞內容聚合
- 社交媒體數據採集
- 競品分析
- SEO 數據收集

### 2. 自動化測試
- E2E 測試
- 跨瀏覽器測試
- 性能測試
- 截圖對比測試
- 回歸測試

### 3. AI Agent 瀏覽
- 智能網頁助手
- 自動化客戶服務
- 數據研究助手
- 內容生成器
- 自動化報告生成

### 4. 業務流程自動化
- 表單自動填寫
- 報表自動生成
- 數據同步
- 定時任務執行
- 批量操作處理

### 5. 監控和告警
- 網站可用性監控
- 價格變動告警
- 內容更新檢測
- 競品動態追蹤
- SLA 監控

## 項目結構

```
43.Browserbase/
├── README.md                 # 項目說明文檔
├── requirements.txt          # 依賴包列表
├── 01_快速開始.py           # 基礎設置和連接
├── 02_Session管理.py        # Session 管理示例
├── 03_隱身瀏覽.py           # 隱身模式示例
├── 04_代理輪換.py           # 代理管理示例
├── 05_截圖錄影.py           # 媒體捕獲示例
├── 06_表單自動化.py         # 表單處理示例
├── 07_數據提取.py           # 數據爬取示例
├── 08_並行瀏覽.py           # 並行處理示例
├── 09_AI整合.py             # AI 集成示例
└── 10_生產部署.py           # 生產環境示例
```

## 最佳實踐

### 1. Session 管理
- 使用完畢後及時關閉 Session
- 對於需要登錄的場景，使用持久化 Session
- 設置合理的超時時間
- 定期清理過期 Session

### 2. 性能優化
- 使用並行處理提高效率
- 合理設置頁面加載超時
- 禁用不必要的資源加載（圖片、CSS）
- 使用 Session 池復用連接

### 3. 錯誤處理
- 實現重試機制
- 記錄詳細的錯誤日誌
- 使用截圖保存錯誤現場
- 設置告警通知

### 4. 安全性
- 妥善保管 API Key
- 使用環境變量存儲敏感信息
- 定期輪換憑證
- 限制 API 訪問權限

### 5. 成本控制
- 監控 Session 使用時長
- 及時釋放閒置資源
- 使用批量操作減少請求次數
- 選擇合適的定價方案

## 常見問題

### Q: Browserbase 和傳統 Selenium/Playwright 有什麼區別？
A: Browserbase 提供了完全託管的瀏覽器基礎設施，無需自己管理瀏覽器環境、代理、反檢測等。它在 Selenium/Playwright 的基礎上提供了更多企業級功能。

### Q: 如何處理驗證碼？
A: Browserbase 支持集成第三方驗證碼識別服務，也可以使用持久化 Session 在首次手動完成驗證後復用。

### Q: 支持哪些瀏覽器？
A: 目前支持 Chrome 和 Firefox，計劃支持更多瀏覽器。

### Q: 如何處理動態內容？
A: 使用 Playwright 的等待機制（wait_for_selector, wait_for_load_state）確保內容完全加載。

### Q: 價格如何計算？
A: 基於 Session 運行時間計費，具體請參考官方定價頁面。

## 資源鏈接

- **官方網站**: https://browserbase.com
- **文檔中心**: https://docs.browserbase.com
- **API 參考**: https://docs.browserbase.com/api-reference
- **GitHub**: https://github.com/browserbase
- **Discord 社群**: https://discord.gg/browserbase
- **狀態頁面**: https://status.browserbase.com

## 技術支持

- 郵件: support@browserbase.com
- Discord: https://discord.gg/browserbase
- GitHub Issues: https://github.com/browserbase/sdk-python/issues

## 授權協議

本示例代碼採用 MIT 協議開源。Browserbase 服務本身遵循其服務條款。

---

最後更新: 2025年12月
