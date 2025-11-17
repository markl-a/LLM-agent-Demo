# 🔧 故障排除指南

本文檔幫助你快速診斷和解決銷售外展自動化系統的常見問題。

## 📋 目錄

- [快速診斷](#快速診斷)
- [設置和配置問題](#設置和配置問題)
- [API 相關問題](#api-相關問題)
- [認證和授權問題](#認證和授權問題)
- [運行時錯誤](#運行時錯誤)
- [性能問題](#性能問題)
- [數據問題](#數據問題)
- [獲取幫助](#獲取幫助)

---

## 快速診斷

### 🚨 系統健康檢查

運行以下命令進行快速診斷：

```bash
# 1. 檢查 Python 版本
python --version  # 應該 >= 3.9

# 2. 檢查虛擬環境
which python  # 應該指向 venv/bin/python

# 3. 檢查依賴安裝
pip list | grep -i "langgraph\|langchain\|google"

# 4. 檢查環境變數
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Gemini:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"

# 5. 檢查文件權限
ls -la credentials.json .env
```

### 常見症狀對照表

| 症狀 | 可能原因 | 快速解決方案 |
|------|---------|------------|
| `ModuleNotFoundError` | 依賴未安裝或虛擬環境未啟動 | 啟動 venv，運行 `pip install -r requirements.txt` |
| `401 Unauthorized` | API 金鑰無效或過期 | 檢查 .env 中的 API 金鑰 |
| `FileNotFoundError: credentials.json` | Google 憑證文件缺失 | 下載並放置 credentials.json |
| `quota_exceeded` | API 配額用盡 | 等待配額重置或升級方案 |
| `Field 'status' not found` | Airtable 缺少必要欄位 | 添加 'status' 欄位 |
| 程式運行但無輸出 | 沒有待處理的客戶 | 檢查 CRM 中是否有 status='pending' 的記錄 |

---

## 設置和配置問題

### 問題 1：虛擬環境無法創建

**症狀**：
```bash
python -m venv venv
# 錯誤: No module named venv
```

**解決方案**：

```bash
# Ubuntu/Debian
sudo apt-get install python3-venv

# CentOS/RHEL
sudo yum install python3-venv

# macOS (使用 Homebrew)
brew install python@3.9

# Windows
# 重新安裝 Python，確保勾選 "pip" 和 "venv"
```

---

### 問題 2：依賴安裝失敗

**症狀**：
```bash
pip install -r requirements.txt
# 錯誤: Could not find a version that satisfies the requirement...
```

**解決方案**：

```bash
# 1. 升級 pip
pip install --upgrade pip setuptools wheel

# 2. 使用國內鏡像（中國用戶）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 逐個安裝排查
pip install langchain
pip install langgraph
pip install google-generativeai
# ...

# 4. 檢查 Python 版本
python --version  # 必須 >= 3.9
```

---

### 問題 3：.env 文件不生效

**症狀**：
```python
print(os.getenv('GEMINI_API_KEY'))  # 輸出: None
```

**解決方案**：

```bash
# 1. 確認文件名正確（不是 .env.txt）
ls -la .env

# 2. 確認文件在正確的目錄
pwd  # 應該在 sales-outreach-automation-langgraph/

# 3. 確認文件格式（無 BOM，使用 UTF-8）
file .env  # 應該顯示 ASCII text

# 4. 檢查語法
cat .env  # 確保格式為 KEY=value（沒有空格）

# 正確格式
GEMINI_API_KEY=abc123

# 錯誤格式
GEMINI_API_KEY = abc123  # ✗ 有空格
GEMINI_API_KEY="abc123"  # ✗ 不需要引號（除非值中包含空格）
```

---

## API 相關問題

### 問題 4：Gemini API 返回 401

**症狀**：
```
google.api_core.exceptions.Unauthenticated: 401 API key not valid
```

**解決方案**：

```bash
# 1. 驗證 API 金鑰
echo $GEMINI_API_KEY  # 確認已設置

# 2. 測試 API 金鑰
curl "https://generativelanguage.googleapis.com/v1/models?key=YOUR_API_KEY"

# 3. 重新生成金鑰
# 訪問 https://makersuite.google.com/app/apikey
# 刪除舊金鑰，創建新金鑰

# 4. 檢查金鑰格式
# Gemini API 金鑰格式: AIzaSy...（39 字符）
```

---

### 問題 5：OpenAI API 配額超限

**症狀**：
```
openai.error.RateLimitError: You exceeded your current quota
```

**解決方案**：

```python
# 1. 檢查用量
# 訪問 https://platform.openai.com/usage

# 2. 添加付費方式
# Settings → Billing → Add payment method

# 3. 設置用量限制
# Settings → Limits → Set monthly budget

# 4. 切換到 Gemini（免費額度更多）
# 在 .env 中配置 GEMINI_API_KEY
```

---

### 問題 6：Serper API 搜索失敗

**症狀**：
```
requests.exceptions.HTTPError: 403 Forbidden
```

**解決方案**：

```bash
# 1. 檢查 API 金鑰
curl -X POST "https://google.serper.dev/search" \
  -H "X-API-KEY: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q": "test"}'

# 2. 檢查配額
# 訪問 https://serper.dev/dashboard

# 3. 確認金鑰格式
# Serper API 金鑰格式: 字母數字組合（約 32 字符）
```

---

### 問題 7：RapidAPI LinkedIn 抓取失敗

**症狀**：
```
RapidAPIError: You are not subscribed to this API
```

**解決方案**：

```bash
# 1. 確認已訂閱 API
# 訪問 https://rapidapi.com/dashboard

# 2. 檢查訂閱狀態
# Dashboard → My Subscriptions

# 3. 訂閱免費方案
# 搜索 "LinkedIn Scraper" → Subscribe to Free plan

# 4. 使用正確的端點
# 確保使用的 endpoint 與訂閱的 API 一致
```

---

## 認證和授權問題

### 問題 8：Gmail API OAuth 失敗

**症狀**：
```
google.auth.exceptions.RefreshError: invalid_grant
```

**解決方案**：

```bash
# 1. 刪除 token.json
rm token.json

# 2. 重新運行程式進行授權
python main.py

# 3. 如果瀏覽器未打開
# 手動訪問終端顯示的 URL

# 4. 檢查 credentials.json 格式
cat credentials.json | python -m json.tool  # 應該是有效的 JSON
```

---

### 問題 9：Google OAuth「應用未經驗證」

**症狀**：
瀏覽器顯示「此應用程式未經 Google 驗證」

**解決方案**：

```
這是正常的，因為你的應用在「測試」模式。

操作步驟：
1. 點擊「進階」或「Advanced」
2. 點擊「前往 [你的專案名稱]（不安全）」
3. 點擊「允許」授予權限

如果需要添加其他測試使用者：
1. Google Cloud Console → OAuth 同意畫面
2. 測試使用者 → 添加使用者
3. 輸入郵箱地址
```

---

### 問題 10：Airtable 權限錯誤

**症狀**：
```
AirtableError: 403 FORBIDDEN - Insufficient permissions
```

**解決方案**：

```bash
# 1. 檢查 Token 權限
# 訪問 https://airtable.com/create/tokens
# 編輯 Token，確保有以下權限：
#   - data.records:read ✓
#   - data.records:write ✓
#   - schema.bases:read ✓

# 2. 確認 Base 授權
# Token 設置 → Access → 確認授權了正確的 Base

# 3. 重新生成 Token
# 刪除舊 Token，創建新 Token

# 4. 更新 .env
AIRTABLE_ACCESS_TOKEN=pat新的token
```

---

## 運行時錯誤

### 問題 11：找不到 'status' 欄位

**症狀**：
```
KeyError: 'status'
或
AirtableError: Field 'status' not found
```

**解決方案**：

```
在 Airtable 中添加 'status' 欄位：

1. 打開你的 Airtable Base
2. 點擊表格最右側的 "+"
3. 選擇「Single select」
4. 欄位名稱輸入：status（全小寫）
5. 添加選項：
   - pending（待處理）
   - sent（已發送）
   - replied（已回覆）
   - failed（失敗）
6. 點擊「Create field」

⚠️ 確保欄位名稱完全匹配（區分大小寫）
```

---

### 問題 12：郵件發送失敗

**症狀**：
```
HttpError 403: Insufficient Permission
```

**解決方案**：

```bash
# 1. 檢查 OAuth 範圍
# credentials.json 應該包含：
#   - https://www.googleapis.com/auth/gmail.send
#   - https://www.googleapis.com/auth/gmail.readonly

# 2. 重新授權
rm token.json
python main.py

# 3. 檢查 Gmail 設置
# 確保沒有啟用「安全性較低的應用程式存取權」限制

# 4. 測試發送
python -c "
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json')
service = build('gmail', 'v1', credentials=creds)
print('Gmail API 連接成功')
"
```

---

### 問題 13：程式運行但無輸出

**症狀**：
程式運行完成，但沒有發送任何郵件

**診斷步驟**：

```python
# 1. 檢查是否有待處理的客戶
# 在 Airtable/HubSpot/Google Sheets 中確認：
#   - 是否有記錄
#   - status 欄位是否為 "pending"

# 2. 添加調試輸出
# 修改 main.py，添加：
print(f"找到 {len(leads)} 個待處理客戶")
for lead in leads:
    print(f"處理: {lead['name']} - {lead['email']}")

# 3. 檢查過濾條件
# 確認 CRM Agent 的過濾邏輯正確
```

---

### 問題 14：編碼錯誤

**症狀**：
```
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**解決方案**：

```python
# 1. 確保 .env 使用 UTF-8 編碼
# 使用支持編碼設置的編輯器（VS Code, Sublime Text 等）

# 2. 檢查 Python 文件編碼
# 在文件開頭添加：
# -*- coding: utf-8 -*-

# 3. 處理文件讀取
with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()

# 4. Windows 用戶特別注意
# 使用 UTF-8（無 BOM）保存文件
```

---

## 性能問題

### 問題 15：程式運行緩慢

**症狀**：
處理每個客戶需要超過 30 秒

**優化方案**：

```python
# 1. 啟用並行處理
from concurrent.futures import ThreadPoolExecutor

def process_leads_parallel(leads, max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_lead, leads))
    return results

# 2. 減少 API 調用
# 緩存搜索結果
from functools import lru_cache

@lru_cache(maxsize=100)
def search_company(company_name):
    return api.search(company_name)

# 3. 使用更快的 LLM
# 在 .env 中切換到 Groq 或 GPT-4o-mini
GROQ_API_KEY=your-groq-key

# 4. 批量 CRM 操作
# 收集所有更新，一次性提交
table.batch_update(all_updates)
```

---

### 問題 16：內存使用過高

**症狀**：
```
MemoryError
```

**解決方案**：

```python
# 1. 分批處理
def process_in_batches(leads, batch_size=10):
    for i in range(0, len(leads), batch_size):
        batch = leads[i:i+batch_size]
        process_batch(batch)
        # 清理內存
        gc.collect()

# 2. 使用生成器
def get_leads_generator():
    for lead in crm.get_all_leads():
        yield lead

# 3. 限制緩存大小
@lru_cache(maxsize=50)  # 減小緩存
def cached_function():
    ...

# 4. 定期清理
import gc
gc.collect()
```

---

## 數據問題

### 問題 17：客戶數據格式錯誤

**症狀**：
```
KeyError: 'email'
或數據驗證失敗
```

**解決方案**：

```python
# 1. 添加數據驗證
def validate_lead(lead):
    required_fields = ['name', 'email', 'company']

    for field in required_fields:
        if field not in lead or not lead[field]:
            print(f"警告: {lead.get('name', 'Unknown')} 缺少 {field}")
            return False

    # 驗證郵箱格式
    import re
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_pattern, lead['email']):
        print(f"警告: {lead['email']} 格式不正確")
        return False

    return True

# 2. 過濾無效數據
valid_leads = [lead for lead in leads if validate_lead(lead)]

# 3. 提供默認值
lead_name = lead.get('name', 'Unknown')
lead_position = lead.get('position', '')
```

---

### 問題 18：重複發送郵件

**症狀**：
同一個客戶收到多封郵件

**解決方案**：

```python
# 1. 檢查 status 更新邏輯
# 確保發送後立即更新狀態
def send_and_update(lead):
    try:
        send_email(lead)
        # 立即更新，防止重複
        crm.update_status(lead['id'], 'sent')
    except Exception as e:
        crm.update_status(lead['id'], 'failed')

# 2. 添加發送記錄
sent_emails = set()

def should_send(lead):
    email = lead['email']
    if email in sent_emails:
        print(f"跳過重複: {email}")
        return False
    sent_emails.add(email)
    return True

# 3. 使用數據庫鎖（進階）
# 防止並發處理時的競爭條件
```

---

## 調試技巧

### 啟用詳細日誌

```python
import logging

# 設置日誌級別
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 查看 HTTP 請求
import http.client as http_client
http_client.HTTPConnection.debuglevel = 1
```

### 使用斷點調試

```python
# 在關鍵位置添加斷點
import pdb; pdb.set_trace()

# 或使用 VS Code 的圖形化調試器
# 設置斷點，按 F5 啟動調試
```

### 測試單個組件

```python
# 測試 LLM Agent
from agents.llm_agent import LLMAgent

agent = LLMAgent()
result = agent.generate_email(
    lead_info={'name': 'Test', 'company': 'ABC Corp'},
    research_data={}
)
print(result)
```

---

## 獲取幫助

如果上述方法都無法解決問題：

### 1. 查看日誌

```bash
# 運行時保存日誌
python main.py 2>&1 | tee output.log

# 查看錯誤行
grep -i "error" output.log
```

### 2. 搜索 Issues

- 原專案 Issues：https://github.com/kaymen99/sales-outreach-automation-langgraph/issues
- LangChain Issues：https://github.com/langchain-ai/langchain/issues

### 3. 社群支持

- LangChain Discord：https://discord.gg/langchain
- Stack Overflow：搜索相關錯誤信息

### 4. 提交 Issue

提交 Issue 時請包含：

```markdown
## 環境信息
- OS: [e.g., Ubuntu 22.04]
- Python版本: [e.g., 3.10.5]
- 依賴版本: [運行 pip freeze]

## 問題描述
[清晰描述問題]

## 重現步驟
1. ...
2. ...

## 錯誤信息
```
[粘貼完整錯誤堆棧]
```

## 已嘗試的解決方案
- [ ] 檢查了 API 金鑰
- [ ] 重新安裝依賴
- [ ] ...
```

---

## 預防性維護

### 定期檢查清單

- [ ] 每月檢查 API 用量
- [ ] 每季度更新依賴套件
- [ ] 每半年輪換 API 金鑰
- [ ] 定期備份 .env 和 credentials.json（加密存儲）
- [ ] 監控郵件發送成功率

### 更新依賴

```bash
# 檢查過時的套件
pip list --outdated

# 更新特定套件
pip install --upgrade langchain langgraph

# 重新生成 requirements.txt
pip freeze > requirements.txt
```

---

**祝你排障順利！** 🎉

如仍有問題，請參考 [config-guide.md](./config-guide.md) 或聯繫社群支持。
