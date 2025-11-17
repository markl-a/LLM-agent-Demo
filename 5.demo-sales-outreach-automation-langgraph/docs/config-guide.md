# 📘 詳細配置指南

本文檔提供所有 API 服務的詳細配置說明，幫助你順利設置銷售外展自動化系統。

## 📋 目錄

- [環境變數概覽](#環境變數概覽)
- [LLM API 配置](#llm-api-配置)
- [Google API 配置](#google-api-配置)
- [搜索和數據 API](#搜索和數據-api)
- [CRM 系統配置](#crm-系統配置)
- [配置驗證](#配置驗證)
- [安全最佳實踐](#安全最佳實踐)

---

## 環境變數概覽

所有配置都通過 `.env` 文件管理。以下是完整的環境變數列表：

```env
# ============================================
# LLM API 配置
# ============================================
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key

# ============================================
# 搜索和數據 API
# ============================================
SERPER_API_KEY=your-serper-api-key
RAPIDAPI_KEY=your-rapidapi-key

# ============================================
# CRM 配置（選擇其中一個）
# ============================================

## Airtable
AIRTABLE_ACCESS_TOKEN=your-airtable-token
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
AIRTABLE_TABLE_NAME=Databases

## HubSpot
HUBSPOT_API_KEY=your-hubspot-key

## Google Sheets
SHEET_ID=your-google-sheet-id
```

---

## LLM API 配置

### 選項 1：Google Gemini（推薦）

**為什麼選擇 Gemini？**
- 免費額度充足（每日 1,500 次請求）
- 性價比高
- 支持繁體中文
- 回應速度快

#### 獲取 Gemini API Key

1. **訪問 Google AI Studio**
   - 網址：https://ai.google.dev/
   - 或：https://makersuite.google.com/app/apikey

2. **創建 API Key**
   ```
   1. 使用 Google 帳號登入
   2. 點擊「Get API Key」
   3. 選擇或創建 Google Cloud 專案
   4. 點擊「Create API Key」
   5. 複製生成的 API Key
   ```

3. **配置到 .env**
   ```env
   GEMINI_API_KEY=AIzaSy...（你的 API Key）
   GOOGLE_API_KEY=AIzaSy...（同上，保持一致）
   ```

#### 配額限制

免費版限制：
- **每分鐘請求數**：60 次
- **每日請求數**：1,500 次
- **Token 限制**：30,000 tokens/min

如需更高配額，可升級到付費方案。

---

### 選項 2：OpenAI GPT

**為什麼選擇 OpenAI？**
- 成熟穩定
- 文檔豐富
- 社群支持好

#### 獲取 OpenAI API Key

1. **訪問 OpenAI Platform**
   - 網址：https://platform.openai.com/

2. **創建 API Key**
   ```
   1. 註冊並登入 OpenAI 帳號
   2. 前往 API Keys 頁面
   3. 點擊「Create new secret key」
   4. 給金鑰命名（如：sales-automation）
   5. 複製並保存金鑰（只顯示一次！）
   ```

3. **配置到 .env**
   ```env
   OPENAI_API_KEY=sk-proj-...（你的 API Key）
   ```

#### 定價參考（截至 2025）

- **GPT-4o**：輸入 $2.50/1M tokens，輸出 $10/1M tokens
- **GPT-4o-mini**：輸入 $0.15/1M tokens，輸出 $0.60/1M tokens
- **GPT-3.5 Turbo**：輸入 $0.50/1M tokens，輸出 $1.50/1M tokens

**建議**：開發測試使用 GPT-4o-mini，生產環境可考慮 GPT-4o。

#### 設置用量警報

為避免意外費用，建議設置用量警報：

```
1. 前往 Settings → Billing
2. 設置 Usage limits
3. 設定每月預算上限（如：$10）
4. 啟用郵件通知
```

---

### 選項 3：Groq（高速推理）

**特點**：
- 推理速度極快（LPU 架構）
- 免費額度慷慨
- 適合需要快速回應的場景

#### 獲取 Groq API Key

1. 訪問：https://console.groq.com/
2. 註冊並創建 API Key
3. 配置到 .env：
   ```env
   GROQ_API_KEY=gsk_...
   ```

---

## Google API 配置

### Gmail API（必須）

用於發送銷售郵件。

#### 步驟 1：創建 Google Cloud 專案

1. **前往 Google Cloud Console**
   - 網址：https://console.cloud.google.com/

2. **創建新專案**
   ```
   1. 點擊專案選擇器
   2. 點擊「新增專案」
   3. 輸入專案名稱（如：Sales Automation）
   4. 點擊「建立」
   ```

#### 步驟 2：啟用 Gmail API

```
1. 在 Console 中搜索「Gmail API」
2. 點擊「Gmail API」
3. 點擊「啟用」
```

#### 步驟 3：配置 OAuth 同意畫面

```
1. 前往「API 和服務」→「OAuth 同意畫面」
2. 選擇「外部」（External）
3. 填寫應用程式資訊：
   - 應用程式名稱：Sales Outreach Automation
   - 使用者支援電子郵件：你的郵箱
   - 開發人員聯絡資訊：你的郵箱
4. 點擊「儲存並繼續」
```

#### 步驟 4：添加範圍（Scopes）

```
1. 點擊「新增或移除範圍」
2. 手動輸入以下範圍：
   - https://www.googleapis.com/auth/gmail.send
   - https://www.googleapis.com/auth/gmail.readonly
3. 點擊「更新」
4. 點擊「儲存並繼續」
```

#### 步驟 5：添加測試使用者

```
1. 點擊「新增使用者」
2. 輸入你的 Gmail 地址
3. 點擊「儲存並繼續」
```

#### 步驟 6：創建 OAuth 2.0 憑證

```
1. 前往「API 和服務」→「憑證」
2. 點擊「建立憑證」→「OAuth 用戶端 ID」
3. 應用程式類型：選擇「電腦版應用程式」
4. 名稱：Sales Automation Desktop
5. 點擊「建立」
6. 下載 JSON 檔案
7. 將檔案重命名為 credentials.json
8. 移動到專案根目錄（與 main.py 同級）
```

#### 步驟 7：首次授權

當你第一次運行 `python main.py` 時：

```
1. 會自動打開瀏覽器
2. 選擇你的 Google 帳號
3. 點擊「繼續」（可能顯示「這個應用程式未經驗證」警告）
4. 點擊「前往 Sales Automation（不安全）」
5. 允許所有權限
6. 授權完成後，會在專案目錄生成 token.json
```

⚠️ **安全提示**：`token.json` 包含訪問權限，請勿分享或提交到版本控制！

---

## 搜索和數據 API

### Serper API（網路搜索）

用於搜索公司信息和行業資訊。

#### 獲取 Serper API Key

1. **訪問 Serper**
   - 網址：https://serper.dev/

2. **註冊並獲取 API Key**
   ```
   1. 使用 Google 或 GitHub 帳號註冊
   2. 前往 Dashboard
   3. 複製 API Key
   ```

3. **配置到 .env**
   ```env
   SERPER_API_KEY=abc123...
   ```

#### 免費額度

- **2,500 次搜索/月**（免費）
- 之後 $5/1,000 次搜索

**優化建議**：
- 只在必要時進行搜索
- 緩存搜索結果
- 對同一公司避免重複搜索

---

### RapidAPI（LinkedIn 數據）

用於抓取潛在客戶的 LinkedIn 資料。

#### 獲取 RapidAPI Key

1. **訪問 RapidAPI**
   - 網址：https://rapidapi.com/

2. **註冊帳號**
   ```
   1. 註冊 RapidAPI 帳號
   2. 前往 Dashboard
   3. 找到你的 API Key（在右上角）
   ```

3. **訂閱 LinkedIn API**
   ```
   1. 搜索「LinkedIn」
   2. 選擇適合的 LinkedIn API（如：LinkedIn Profile Scraper）
   3. 選擇免費或付費方案
   4. 點擊「Subscribe」
   ```

4. **配置到 .env**
   ```env
   RAPIDAPI_KEY=your-rapidapi-key
   ```

#### 常用 LinkedIn API

推薦以下 API（視需求選擇）：

1. **LinkedIn Data Scraper**
   - 免費額度：100 次/月
   - 適合：獲取基本檔案信息

2. **Fresh LinkedIn Profile Data**
   - 免費額度：500 次/月
   - 適合：獲取詳細資料

⚠️ **法律提醒**：請遵守 LinkedIn 使用條款和數據保護法規。

---

## CRM 系統配置

選擇以下其中一個 CRM 系統進行整合。

### 選項 1：Airtable（推薦用於小型團隊）

**優點**：
- 使用簡單
- 視覺化介面
- 免費版功能充足

#### 步驟 1：創建 Airtable Base

```
1. 前往 https://airtable.com/
2. 創建新的 Base（或使用現有的）
3. 創建表格（預設名稱：Databases）
```

#### 步驟 2：設計表格結構

建議的欄位：

| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| Name | Single line text | 潛在客戶姓名 |
| Email | Email | 郵箱地址 |
| Company | Single line text | 公司名稱 |
| Position | Single line text | 職位 |
| LinkedIn | URL | LinkedIn 連結 |
| status | Single select | 狀態（pending, sent, replied） |
| Notes | Long text | 備註 |
| Created | Created time | 創建時間 |

⚠️ **重要**：必須添加 `status` 欄位，否則程式會報錯！

#### 步驟 3：獲取 Access Token

```
1. 前往 https://airtable.com/create/tokens
2. 點擊「Create new token」
3. 輸入 Token 名稱（如：Sales Automation）
4. 添加權限：
   - data.records:read ✓
   - data.records:write ✓
   - schema.bases:read ✓
5. 選擇 Base：
   - 選擇「Specific bases」
   - 勾選你的 Base
6. 點擊「Create token」
7. 複製 Token（只顯示一次！）
```

#### 步驟 4：獲取 Base ID

Base ID 在 Airtable URL 中：

```
https://airtable.com/appABC123/tblXYZ456
                      ^^^^^^^^^^^
                      這就是 Base ID
```

或者：

```
1. 前往 https://airtable.com/api
2. 選擇你的 Base
3. Base ID 顯示在文檔中
```

#### 步驟 5：配置到 .env

```env
AIRTABLE_ACCESS_TOKEN=pat...（你的 Token）
AIRTABLE_BASE_ID=appABC123
AIRTABLE_TABLE_NAME=Databases
```

---

### 選項 2：HubSpot（企業級）

**優點**：
- 功能強大
- 適合大型團隊
- 整合生態完善

#### 獲取 HubSpot API Key

1. **訪問 HubSpot**
   - 網址：https://developers.hubspot.com/

2. **創建私人應用程式**
   ```
   1. 登入 HubSpot 帳號
   2. 前往 Settings → Integrations → Private Apps
   3. 點擊「Create a private app」
   4. 設置權限：
      - Contacts: Read, Write
      - Companies: Read, Write
   5. 點擊「Create app」
   6. 複製 Access Token
   ```

3. **配置到 .env**
   ```env
   HUBSPOT_API_KEY=pat-na1-...
   ```

---

### 選項 3：Google Sheets（簡易方案）

**優點**：
- 零成本
- 操作簡單
- 適合個人或小型測試

#### 設置步驟

1. **創建 Google Sheet**
   ```
   1. 訪問 Google Sheets
   2. 創建新試算表
   3. 添加欄位：Name, Email, Company, Status
   ```

2. **獲取 Sheet ID**

   Sheet ID 在 URL 中：
   ```
   https://docs.google.com/spreadsheets/d/1ABC...XYZ/edit
                                          ^^^^^^^^^^^
                                          這就是 Sheet ID
   ```

3. **配置到 .env**
   ```env
   SHEET_ID=1ABC...XYZ
   ```

4. **設置 Google Sheets API**

   類似 Gmail API 的設置流程：
   ```
   1. 在 Google Cloud Console 中啟用「Google Sheets API」
   2. 使用相同的 credentials.json
   ```

---

## 配置驗證

創建一個簡單的驗證腳本來檢查配置：

### verify_config.py

```python
#!/usr/bin/env python3
"""驗證 API 配置"""

import os
from dotenv import load_dotenv

load_dotenv()

def check_env_var(var_name, required=True):
    """檢查環境變數"""
    value = os.getenv(var_name)
    if value:
        print(f"✓ {var_name}: 已設置")
        return True
    elif required:
        print(f"✗ {var_name}: 未設置（必須）")
        return False
    else:
        print(f"⚠ {var_name}: 未設置（選填）")
        return True

print("=" * 50)
print("環境變數配置檢查")
print("=" * 50)

# LLM APIs
print("\n[LLM APIs]")
has_gemini = check_env_var("GEMINI_API_KEY", required=False)
has_openai = check_env_var("OPENAI_API_KEY", required=False)

if not (has_gemini or has_openai):
    print("✗ 至少需要配置一個 LLM API（Gemini 或 OpenAI）")

# Search APIs
print("\n[搜索和數據 APIs]")
check_env_var("SERPER_API_KEY")
check_env_var("RAPIDAPI_KEY")

# CRM
print("\n[CRM 配置]")
has_airtable = check_env_var("AIRTABLE_ACCESS_TOKEN", required=False)
has_hubspot = check_env_var("HUBSPOT_API_KEY", required=False)
has_sheets = check_env_var("SHEET_ID", required=False)

if has_airtable:
    check_env_var("AIRTABLE_BASE_ID")
    check_env_var("AIRTABLE_TABLE_NAME")

if not (has_airtable or has_hubspot or has_sheets):
    print("✗ 至少需要配置一個 CRM 系統")

# Google Credentials
print("\n[Google API 憑證]")
if os.path.exists("credentials.json"):
    print("✓ credentials.json: 存在")
else:
    print("✗ credentials.json: 不存在")

print("\n" + "=" * 50)
```

使用方法：

```bash
cd sales-outreach-automation-langgraph
python verify_config.py
```

---

## 安全最佳實踐

### 1. 保護 API 金鑰

```bash
# 永遠不要將 .env 提交到版本控制
echo ".env" >> .gitignore
echo "credentials.json" >> .gitignore
echo "token.json" >> .gitignore
```

### 2. 使用環境變數

```python
# 好的做法
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
```

```python
# 壞的做法 - 不要這樣做！
api_key = "AIzaSy..."  # 硬編碼在代碼中
```

### 3. 定期輪換金鑰

建議每 3-6 個月更換一次 API 金鑰。

### 4. 最小權限原則

只授予必要的權限。例如：
- Gmail API：只需要 `gmail.send`，不需要 `gmail.modify`
- Airtable：只授權特定 Base，不要「All bases」

### 5. 監控 API 使用量

定期檢查：
- Google Cloud Console → API Dashboard
- OpenAI Platform → Usage
- Airtable → API Usage

---

## 常見配置錯誤

### 錯誤 1：API Key 無效

**症狀**：`401 Unauthorized` 或 `403 Forbidden`

**解決方案**：
1. 檢查 API Key 是否正確複製（沒有多餘空格）
2. 確認 API Key 沒有過期
3. 檢查 API 服務是否啟用

### 錯誤 2：Google OAuth 權限不足

**症狀**：`insufficient_scope` 錯誤

**解決方案**：
1. 刪除 `token.json`
2. 重新運行程式進行授權
3. 確認 OAuth 同意畫面中添加了正確的範圍

### 錯誤 3：Airtable 找不到欄位

**症狀**：`Field 'status' not found`

**解決方案**：
1. 在 Airtable 表格中添加 `status` 欄位
2. 確認欄位名稱完全匹配（區分大小寫）

### 錯誤 4：配額超限

**症狀**：`429 Too Many Requests` 或 `quota_exceeded`

**解決方案**：
1. 等待配額重置（通常是每分鐘或每日）
2. 升級到付費方案
3. 優化代碼減少 API 調用

---

## 下一步

配置完成後：

1. **運行驗證腳本**：確保所有配置正確
2. **測試基本功能**：發送測試郵件
3. **查看最佳實踐**：[best-practices.md](./best-practices.md)
4. **遇到問題？**：[troubleshooting.md](./troubleshooting.md)

---

**祝配置順利！** 🎉

如有疑問，歡迎查閱原專案文檔或提出 Issue。
