# RPA + LLM 工具與框架比較指南

## 目錄

1. [瀏覽器自動化工具](#瀏覽器自動化工具)
2. [桌面自動化工具](#桌面自動化工具)
3. [LLM 服務提供商](#llm-服務提供商)
4. [RPA 框架](#rpa-框架)
5. [選擇指南](#選擇指南)

---

## 瀏覽器自動化工具

### Playwright vs Selenium vs Puppeteer

| 特性 | Playwright | Selenium | Puppeteer |
|------|-----------|----------|-----------|
| **語言支援** | Python, JS, Java, C# | 多種語言 | JavaScript/Node.js |
| **速度** | ⭐⭐⭐⭐⭐ 最快 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ 快 |
| **穩定性** | ⭐⭐⭐⭐⭐ 最穩定 | ⭐⭐⭐ 一般 | ⭐⭐⭐⭐ 穩定 |
| **瀏覽器支援** | Chrome, Firefox, Safari | 全部瀏覽器 | 僅 Chrome |
| **學習曲線** | 低 | 中 | 低 |
| **文檔質量** | ⭐⭐⭐⭐⭐ 優秀 | ⭐⭐⭐⭐ 好 | ⭐⭐⭐⭐ 好 |
| **自動等待** | ✅ 內建 | ❌ 需手動 | ✅ 內建 |
| **截圖/PDF** | ✅ 完整支援 | ✅ 基本支援 | ✅ 完整支援 |
| **移動端模擬** | ✅ 優秀 | ⚠️ 有限 | ✅ 優秀 |
| **適合場景** | 現代化 RPA 專案 | 跨瀏覽器測試 | Chrome 專案 |

### 詳細比較

#### Playwright 🏆 推薦

**優點**：
- 速度最快，自動等待機制完善
- API 設計現代化，使用簡單
- 內建錄製功能（codegen）
- 優秀的除錯工具
- 多瀏覽器支援且一致性好

**缺點**：
- 相對較新，社群資源較少
- 某些舊瀏覽器不支援

**適合場景**：
- 新專案首選
- 需要穩定性的生產環境
- 多瀏覽器測試

**範例**：
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")
    page.click("text=Login")
    browser.close()
```

#### Selenium

**優點**：
- 最成熟，社群資源豐富
- 支援所有主流瀏覽器
- 大量第三方工具和擴展

**缺點**：
- 速度較慢
- 需要手動配置等待
- API 較為繁瑣

**適合場景**：
- 需要廣泛瀏覽器支援
- 現有專案已使用 Selenium
- 團隊熟悉 Selenium

#### Puppeteer

**優點**：
- Google 官方維護
- Chrome DevTools Protocol 直接控制
- 性能優異

**缺點**：
- 僅支援 Chrome/Chromium
- 僅 JavaScript

**適合場景**：
- Node.js 專案
- 只需 Chrome 支援
- 需要深度 Chrome 整合

---

## 桌面自動化工具

### PyAutoGUI vs AutoHotkey vs UIAutomation

| 特性 | PyAutoGUI | AutoHotkey | pywinauto |
|------|-----------|-----------|-----------|
| **平台支援** | Windows, macOS, Linux | 僅 Windows | 僅 Windows |
| **語言** | Python | 專用腳本語言 | Python |
| **易用性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **功能豐富度** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **圖像識別** | ✅ 內建 | ⚠️ 需插件 | ❌ 無 |
| **元素識別** | ❌ 無 | ⚠️ 有限 | ✅ 優秀 |
| **熱鍵支援** | ✅ 基本 | ✅ 強大 | ❌ 無 |
| **適合場景** | 跨平台簡單自動化 | Windows 高級腳本 | Windows UI 自動化 |

### 詳細比較

#### PyAutoGUI

**優點**：
- 跨平台，一套代碼多平台運行
- Python 生態整合好
- 簡單易學

**缺點**：
- 功能相對基礎
- 依賴坐標，不夠可靠

**範例**：
```python
import pyautogui

# 移動並點擊
pyautogui.moveTo(100, 100, duration=1)
pyautogui.click()

# 圖像識別點擊
location = pyautogui.locateOnScreen('button.png')
if location:
    pyautogui.click(location)
```

#### pywinauto (Windows 推薦)

**優點**：
- 精確的 UI 元素識別
- 不依賴坐標
- 支援各種 Windows 應用

**缺點**：
- 僅限 Windows
- 學習曲線較陡

**範例**：
```python
from pywinauto import Application

app = Application().start("notepad.exe")
app.UntitledNotepad.menu_select("File->Save As")
app.SaveAs.FileNameEdit.set_text("test.txt")
app.SaveAs.Save.click()
```

---

## LLM 服務提供商

### OpenAI vs Anthropic vs 本地 LLM

| 特性 | OpenAI GPT-4 | Anthropic Claude | 本地 LLM (Ollama) |
|------|-------------|------------------|-------------------|
| **性能** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **成本** | $$ 較高 | $$ 中等 | ✅ 免費 |
| **隱私性** | ⚠️ 雲端 | ⚠️ 雲端 | ✅ 本地 |
| **延遲** | 中 | 低 | ⭐ 最低 |
| **上下文長度** | 128K tokens | 200K tokens | 取決於模型 |
| **結構化輸出** | ✅ Function Calling | ⚠️ 需 Prompt | ⚠️ 需 Prompt |
| **多語言** | ✅ 優秀 | ✅ 優秀 | ⭐⭐⭐ 一般 |
| **適合場景** | 生產環境 | 長文檔處理 | 隱私敏感場景 |

### 詳細比較

#### OpenAI GPT-4 🏆 功能最強

**優點**：
- 性能頂尖，理解能力強
- Function Calling 支援完善
- 生態系統豐富
- 文檔完善

**缺點**：
- 成本較高
- 數據隱私考量
- API 限流

**定價**（2024）：
- GPT-4 Turbo: $10/1M input tokens, $30/1M output tokens
- GPT-3.5 Turbo: $0.50/1M input tokens, $1.50/1M output tokens

**適合場景**：
- 複雜推理任務
- 需要結構化輸出
- 預算充足的生產環境

#### Anthropic Claude 🎯 長文檔專家

**優點**：
- 超長上下文（200K tokens）
- 安全性高，減少有害輸出
- 價格相對合理
- 優秀的指令遵循能力

**缺點**：
- Function Calling 支援較弱
- 生態相對較小

**定價**（2024）：
- Claude 3 Sonnet: $3/1M input tokens, $15/1M output tokens
- Claude 3 Haiku: $0.25/1M input tokens, $1.25/1M output tokens

**適合場景**：
- 長文檔處理
- 需要高度安全性
- 成本敏感的專案

#### 本地 LLM (Ollama/LM Studio) 💰 零成本

**優點**：
- 完全免費
- 數據完全本地化
- 無 API 限流
- 低延遲

**缺點**：
- 性能不如商業模型
- 需要硬體資源（GPU）
- 設置較複雜

**推薦模型**：
- llama2 (7B/13B): 通用任務
- mistral (7B): 性能平衡
- codellama (7B): 代碼生成

**適合場景**：
- 開發測試環境
- 隱私敏感數據
- 高頻調用場景
- 預算有限

---

## RPA 框架

### Skyvern vs RPA-Python vs UIPath

| 特性 | Skyvern | RPA-Python | UiPath |
|------|---------|-----------|--------|
| **類型** | AI 驅動 | 傳統 RPA | 企業級平台 |
| **開源** | ✅ 開源 | ✅ 開源 | ❌ 商業 |
| **成本** | 免費 | 免費 | $$$ 昂貴 |
| **LLM 整合** | ✅ 深度整合 | ❌ 無 | ⚠️ 部分 |
| **學習曲線** | 中 | 低 | 高 |
| **適應性** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **適合規模** | 中小型 | 小型 | 企業級 |

### 詳細比較

#### Skyvern - AI 驅動的未來 🚀

**優點**：
- 無需預定義選擇器，適應性強
- LLM 驅動，能理解頁面語義
- 處理動態網頁能力強

**缺點**：
- 依賴 LLM，有 API 成本
- 相對較新，生態待完善

**適合場景**：
- 頻繁變動的網站
- 複雜的網頁自動化
- 需要智能決策

#### RPA-Python - 輕量快速 ⚡

**優點**：
- 極簡 API，上手快
- 輕量級，無依賴
- 適合快速原型

**缺點**：
- 功能基礎
- 無 LLM 整合
- 維護不活躍

**適合場景**：
- 簡單重複任務
- 快速驗證概念
- 學習 RPA 基礎

#### UiPath - 企業級完整方案 🏢

**優點**：
- 功能最完整
- 企業級支援
- 視覺化設計器
- 豐富的活動庫

**缺點**：
- 成本高昂
- 學習曲線陡峭
- 過度工程化

**適合場景**：
- 大型企業
- 複雜業務流程
- 需要長期支援

---

## 選擇指南

### 按場景選擇

#### 1. 網頁數據採集

**推薦組合**：Playwright + OpenAI GPT-4
- **原因**：Playwright 穩定快速，GPT-4 智能提取

**替代方案**：Skyvern
- **原因**：一體化解決方案，無需編碼選擇器

#### 2. 發票/文檔處理

**推薦組合**：pdfplumber + Claude 3
- **原因**：Claude 長文檔處理能力強

**替代方案**：Ollama + 本地 OCR
- **原因**：隱私敏感，本地化處理

#### 3. 桌面應用自動化

**推薦組合**：
- **Windows**: pywinauto + OpenAI
- **跨平台**: PyAutoGUI + OpenAI

#### 4. 郵件處理

**推薦組合**：IMAP + GPT-3.5 Turbo
- **原因**：成本低，性能足夠

#### 5. 測試自動化

**推薦組合**：Playwright + pytest
- **原因**：穩定性高，測試框架整合好

### 按預算選擇

#### 零預算方案

```python
# 組合：開源工具 + 本地 LLM
- Playwright (免費)
- PyAutoGUI (免費)
- Ollama (免費)
- 總成本：$0/月
```

#### 小預算方案 ($50-200/月)

```python
# 組合：開源工具 + GPT-3.5
- Playwright (免費)
- OpenAI GPT-3.5 (~$50-100/月)
- 適合：中小型專案
```

#### 中等預算方案 ($500-2000/月)

```python
# 組合：開源工具 + GPT-4
- Playwright (免費)
- OpenAI GPT-4 (~$500-1500/月)
- Claude 3 Sonnet (備用)
- 適合：生產環境
```

#### 企業級方案 ($5000+/月)

```python
# 組合：商業平台 + 企業 LLM
- UiPath ($$$)
- OpenAI Enterprise
- 專用基礎設施
- 適合：大型企業
```

### 按技術能力選擇

#### 初學者

**推薦**：
1. RPA-Python（學習基礎）
2. PyAutoGUI（桌面自動化）
3. OpenAI GPT-3.5（LLM 入門）

**學習路徑**：
1. 完成 tutorial-part1
2. 嘗試簡單專案
3. 逐步引入 LLM

#### 中級開發者

**推薦**：
1. Playwright（網頁自動化）
2. OpenAI GPT-4（智能處理）
3. LangChain（框架整合）

**學習路徑**：
1. 掌握全部教程
2. 實現複雜專案
3. 探索架構模式

#### 高級開發者

**推薦**：
1. 自定義框架
2. 多 LLM 整合
3. 分佈式部署

**學習路徑**：
1. 研究源碼
2. 貢獻開源
3. 設計架構

---

## 快速決策樹

```
開始
  │
  ├─ 需要網頁自動化？
  │   ├─ 是 → 網頁經常變動？
  │   │   ├─ 是 → Skyvern
  │   │   └─ 否 → Playwright
  │   │
  │   └─ 否 → 需要桌面自動化？
  │       ├─ 是 → Windows 專用？
  │       │   ├─ 是 → pywinauto
  │       │   └─ 否 → PyAutoGUI
  │       │
  │       └─ 否 → 需要文檔處理？
  │           └─ 是 → pdfplumber + LLM
  │
  └─ 選擇 LLM：
      ├─ 預算充足 → GPT-4
      ├─ 長文檔 → Claude 3
      ├─ 成本優先 → GPT-3.5
      └─ 隱私優先 → Ollama
```

---

## 總結

### 通用推薦組合

**最佳實踐組合**（適合 80% 場景）：
```
- 網頁自動化: Playwright
- 桌面自動化: PyAutoGUI (跨平台) / pywinauto (Windows)
- LLM: OpenAI GPT-4 (生產) + GPT-3.5 (開發)
- 數據處理: Pandas
- 文檔處理: pdfplumber
```

### 記住三個原則

1. **從簡單開始**：先用基礎工具驗證可行性
2. **按需升級**：根據實際需求選擇工具
3. **成本可控**：優先考慮開源方案，LLM 從低成本開始

---

下一步建議閱讀：
- [best-practices.md](./best-practices.md) - 學習最佳實踐
- [use-cases.md](./use-cases.md) - 查看實際案例
- [tutorial-part1-basic-rpa.md](./tutorial-part1-basic-rpa.md) - 開始實戰
