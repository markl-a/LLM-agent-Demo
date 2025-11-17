# 🌟 最佳實踐指南

本文檔提供使用銷售外展自動化系統的最佳實踐，幫助你最大化效果並避免常見陷阱。

## 📋 目錄

- [郵件撰寫最佳實踐](#郵件撰寫最佳實踐)
- [API 使用優化](#api-使用優化)
- [數據管理](#數據管理)
- [安全和隱私](#安全和隱私)
- [性能優化](#性能優化)
- [合規性和道德](#合規性和道德)
- [監控和維護](#監控和維護)

---

## 郵件撰寫最佳實踐

### ✅ 個性化是關鍵

**不好的做法**：
```
嗨 [姓名]，

我們有很棒的產品，你應該試試。

謝謝，
銷售團隊
```

**好的做法**：
```
嗨 John，

我注意到 TechCorp 最近發布了新的 AI 平台。恭喜這個里程碑！

作為數據分析領域的領導者，你可能對我們的 [具體產品] 感興趣，
它幫助類似 [競爭對手] 的公司提升了 40% 的效率。

方便的話，我們可以安排一個 15 分鐘的通話討論你們在 [具體痛點]
方面的挑戰。

最好的祝福，
Mark
```

### Prompt 工程最佳實踐

優化你的郵件生成 prompt：

```python
# ❌ 模糊的 prompt
prompt = "寫一封銷售郵件"

# ✅ 清晰、結構化的 prompt
prompt = """
請撰寫一封專業的銷售郵件，遵循以下要求：

潛在客戶信息：
- 姓名：{name}
- 職位：{position}（強調他們在該領域的專業性）
- 公司：{company}（提及最近的公司動態：{recent_news}）

產品/服務：
{product_description}

語氣和風格：
- 專業但友好
- 避免使用過度行銷語言
- 突出價值而非功能

郵件結構：
1. 個性化開場（提及具體的公司或個人成就）
2. 簡要說明你的產品如何解決他們的具體問題
3. 提供社會證明（案例或數據）
4. 明確且低壓力的行動呼籲（CTA）

字數：150-200 字
"""
```

### 郵件元素清單

每封郵件應包含：

- [ ] **個性化開場**：提及收件人或公司的具體信息
- [ ] **價值主張**：清晰說明能解決什麼問題
- [ ] **社會證明**：案例研究、數據或推薦
- [ ] **明確的 CTA**：具體的下一步行動
- [ ] **簽名**：包含你的完整信息和聯繫方式

### A/B 測試建議

測試不同的郵件元素：

```python
# 主旨行測試
subjects_to_test = [
    "關於 {company} 的 {solution}",  # 直接型
    "快速問題：{company} 如何處理 {pain_point}？",  # 問題型
    "我們如何幫助 {competitor} 提升 40%",  # 案例型
]

# 開場白測試
openings_to_test = [
    "恭喜 {company} 最近的 {achievement}！",  # 恭喜型
    "我注意到您在 LinkedIn 上分享的關於 {topic} 的見解...",  # 共鳴型
    "作為 {industry} 的領導者...",  # 認可型
]

# CTA 測試
ctas_to_test = [
    "方便安排一個 15 分鐘的通話嗎？",  # 直接型
    "如果感興趣，請回覆我...",  # 低壓型
    "點擊這裡查看案例研究",  # 鏈接型
]
```

---

## API 使用優化

### 成本控制

#### 1. 選擇性價比高的 LLM

```python
# 根據任務複雜度選擇模型

# 簡單任務（數據提取、分類）
model = "gemini-1.5-flash"  # 快速且便宜

# 中等任務（郵件生成、摘要）
model = "gemini-1.5-pro"  # 平衡質量和成本

# 複雜任務（深度分析、多步推理）
model = "gpt-4o"  # 高質量但較貴
```

#### 2. 使用緩存減少調用

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def generate_email_cached(lead_hash, research_hash):
    """緩存郵件生成結果"""
    return llm.generate_email(lead_data, research_data)

# 使用哈希避免大對象作為緩存鍵
def get_hash(data):
    return hashlib.md5(str(data).encode()).hexdigest()

lead_hash = get_hash(lead_info)
research_hash = get_hash(research_data)

email = generate_email_cached(lead_hash, research_hash)
```

#### 3. 批量處理

```python
# ❌ 逐個處理（效率低）
for lead in leads:
    result = process_lead(lead)

# ✅ 批量處理
batch_size = 10
for i in range(0, len(leads), batch_size):
    batch = leads[i:i+batch_size]
    results = process_batch(batch)  # 並行處理
```

### API 配額管理

#### 監控用量

```python
import time
from collections import defaultdict

class APIUsageTracker:
    def __init__(self):
        self.usage = defaultdict(int)
        self.costs = defaultdict(float)

    def track_call(self, api_name, tokens=0, cost=0):
        self.usage[api_name] += 1
        self.costs[api_name] += cost

    def report(self):
        print("API 用量報告:")
        for api, calls in self.usage.items():
            print(f"  {api}: {calls} 次調用, ${self.costs[api]:.4f}")

# 使用
tracker = APIUsageTracker()

def make_llm_call(prompt):
    response = llm.invoke(prompt)
    tokens = len(prompt.split()) + len(response.content.split())
    cost = tokens * 0.00001  # 估算成本

    tracker.track_call("gemini", tokens, cost)
    return response
```

#### 速率限制

```python
from ratelimit import limits, sleep_and_retry
import time

# Gemini 免費版：60 次/分鐘
@sleep_and_retry
@limits(calls=60, period=60)
def call_gemini_api(prompt):
    return gemini.invoke(prompt)

# Serper：2500 次/月
@sleep_and_retry
@limits(calls=80, period=86400)  # ~2400/月，留點餘地
def call_serper_api(query):
    return serper.search(query)
```

---

## 數據管理

### CRM 數據質量

#### 數據驗證

```python
import re
from typing import Optional

def validate_email(email: str) -> bool:
    """驗證郵箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_lead(lead: dict) -> tuple[bool, Optional[str]]:
    """
    驗證潛在客戶數據

    Returns:
        (is_valid, error_message)
    """
    # 必填字段
    required_fields = ['name', 'email', 'company']
    for field in required_fields:
        if not lead.get(field):
            return False, f"缺少必填字段: {field}"

    # 郵箱格式
    if not validate_email(lead['email']):
        return False, f"郵箱格式不正確: {lead['email']}"

    # 公司名稱長度
    if len(lead['company']) < 2:
        return False, "公司名稱太短"

    return True, None

# 使用
valid_leads = []
for lead in all_leads:
    is_valid, error = validate_lead(lead)
    if is_valid:
        valid_leads.append(lead)
    else:
        logger.warning(f"跳過無效數據: {lead.get('name', 'Unknown')} - {error}")
```

#### 數據清理

```python
def clean_lead_data(lead: dict) -> dict:
    """清理和標準化數據"""

    # 去除空白
    for key in ['name', 'email', 'company']:
        if key in lead:
            lead[key] = lead[key].strip()

    # 統一郵箱格式（小寫）
    if 'email' in lead:
        lead['email'] = lead['email'].lower()

    # 統一公司名稱（移除 Inc., Ltd. 等）
    if 'company' in lead:
        lead['company'] = re.sub(r'\s+(Inc\.|Ltd\.|LLC|Corp\.)?\s*$', '', lead['company'])

    # 處理缺失字段
    lead.setdefault('position', '')
    lead.setdefault('linkedin_url', '')

    return lead
```

### 去重邏輯

```python
class LeadDeduplicator:
    def __init__(self):
        self.seen_emails = set()
        self.seen_combinations = set()

    def is_duplicate(self, lead: dict) -> bool:
        """檢查是否重複"""

        email = lead.get('email', '').lower()

        # 郵箱重複
        if email in self.seen_emails:
            return True

        # 姓名+公司組合重複（處理郵箱不同但同一人的情況）
        combo = (lead.get('name', '').lower(), lead.get('company', '').lower())
        if combo in self.seen_combinations:
            return True

        # 記錄
        self.seen_emails.add(email)
        self.seen_combinations.add(combo)

        return False

# 使用
dedup = LeadDeduplicator()
unique_leads = [lead for lead in leads if not dedup.is_duplicate(lead)]
```

---

## 安全和隱私

### 保護敏感信息

#### 1. 環境變數管理

```bash
# ✅ 使用 .env 文件
GEMINI_API_KEY=abc123

# ❌ 硬編碼
# config.py:
API_KEY = "abc123"  # 不要這樣做！
```

#### 2. Git 忽略規則

```bash
# .gitignore
.env
.env.local
credentials.json
token.json
*.log
__pycache__/
*.pyc
```

#### 3. 加密敏感數據

```python
from cryptography.fernet import Fernet

class SecureConfig:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)

    def encrypt(self, data: str) -> bytes:
        return self.cipher.encrypt(data.encode())

    def decrypt(self, encrypted: bytes) -> str:
        return self.cipher.decrypt(encrypted).decode()

# 使用
key = Fernet.generate_key()  # 保存在安全的地方
config = SecureConfig(key)

encrypted_api_key = config.encrypt("abc123")
# 使用時解密
api_key = config.decrypt(encrypted_api_key)
```

### GDPR 和數據保護合規

#### 數據最小化

```python
# 只收集必要的數據
necessary_fields = [
    'name',
    'email',
    'company',
    'position',  # 用於個性化
]

# 不要收集
avoid_fields = [
    'personal_address',  # 非必要個人信息
    'phone_home',
    'birthdate',
]
```

#### 數據保留政策

```python
from datetime import datetime, timedelta

def cleanup_old_data(days_to_keep=90):
    """清理舊數據"""

    cutoff_date = datetime.now() - timedelta(days=days_to_keep)

    # 刪除舊的互動記錄
    old_records = crm.get_records(
        filter=f"created_time < '{cutoff_date.isoformat()}'"
    )

    for record in old_records:
        crm.delete_record(record['id'])
        logger.info(f"刪除舊記錄: {record['id']}")
```

#### 選擇退出機制

```python
class OptOutManager:
    def __init__(self, storage_path="opt_out.json"):
        self.storage_path = storage_path
        self.opt_out_emails = self.load_opt_outs()

    def load_opt_outs(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                return set(json.load(f))
        return set()

    def add_opt_out(self, email: str):
        """添加到退出列表"""
        self.opt_out_emails.add(email.lower())
        self.save_opt_outs()

    def is_opted_out(self, email: str) -> bool:
        """檢查是否已退出"""
        return email.lower() in self.opt_out_emails

    def save_opt_outs(self):
        with open(self.storage_path, 'w') as f:
            json.dump(list(self.opt_out_emails), f)

# 使用
opt_out = OptOutManager()

# 過濾已退出的用戶
leads_to_contact = [
    lead for lead in leads
    if not opt_out.is_opted_out(lead['email'])
]
```

---

## 性能優化

### 並行處理

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def process_lead_with_timeout(lead, timeout=30):
    """帶超時的處理函數"""
    try:
        return process_lead(lead)
    except Exception as e:
        logger.error(f"處理失敗: {lead['email']} - {e}")
        return {'status': 'failed', 'error': str(e)}

def process_leads_parallel(leads, max_workers=5):
    """並行處理潛在客戶"""

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任務
        future_to_lead = {
            executor.submit(process_lead_with_timeout, lead): lead
            for lead in leads
        }

        # 收集結果（帶進度顯示）
        for future in as_completed(future_to_lead):
            lead = future_to_lead[future]
            try:
                result = future.result()
                results.append(result)

                # 進度顯示
                progress = len(results) / len(leads) * 100
                print(f"進度: {progress:.1f}% ({len(results)}/{len(leads)})")

            except Exception as e:
                logger.error(f"任務失敗: {lead['email']} - {e}")

    return results
```

### 智能批處理

```python
def smart_batch_processing(leads, initial_batch_size=10):
    """
    動態調整批次大小的智能處理

    根據處理速度自動調整批次大小
    """

    batch_size = initial_batch_size
    processed = 0

    while processed < len(leads):
        batch = leads[processed:processed+batch_size]

        start_time = time.time()
        results = process_batch(batch)
        elapsed = time.time() - start_time

        processed += len(batch)

        # 動態調整批次大小
        if elapsed < 5:  # 太快，增加批次
            batch_size = min(batch_size + 5, 50)
        elif elapsed > 20:  # 太慢，減少批次
            batch_size = max(batch_size - 5, 5)

        logger.info(f"批次大小: {batch_size}, 耗時: {elapsed:.1f}s")
```

---

## 合規性和道德

### 郵件發送最佳實踐

#### 頻率限制

```python
from datetime import datetime, timedelta

class SendingThrottler:
    """發送頻率控制"""

    def __init__(self, min_interval_days=7):
        self.min_interval = timedelta(days=min_interval_days)
        self.last_sent = {}  # {email: datetime}

    def can_send(self, email: str) -> bool:
        """檢查是否可以發送"""

        if email not in self.last_sent:
            return True

        time_since_last = datetime.now() - self.last_sent[email]
        return time_since_last >= self.min_interval

    def record_sent(self, email: str):
        """記錄發送時間"""
        self.last_sent[email] = datetime.now()

# 使用
throttler = SendingThrottler(min_interval_days=7)

for lead in leads:
    if throttler.can_send(lead['email']):
        send_email(lead)
        throttler.record_sent(lead['email'])
    else:
        logger.info(f"跳過（頻率限制）: {lead['email']}")
```

#### 發送時間優化

```python
from datetime import datetime

def get_optimal_send_time():
    """
    獲取最佳發送時間

    研究表明：週二、週三、週四上午 10-11 點
    回覆率最高
    """

    now = datetime.now()

    # 避免週末
    if now.weekday() in [5, 6]:  # 週六、週日
        return False

    # 避免非工作時間
    if now.hour < 9 or now.hour > 17:
        return False

    # 最佳時間段
    optimal_days = [1, 2, 3]  # 週二、週三、週四
    optimal_hours = [10, 11, 14]  # 10-11 點, 14-15 點

    if now.weekday() in optimal_days and now.hour in optimal_hours:
        return True

    return False

# 使用
if get_optimal_send_time():
    send_emails(leads)
else:
    logger.info("當前不是最佳發送時間，延後處理")
    schedule_for_later(leads)
```

### 反垃圾郵件措施

```python
def check_spam_score(email_content: str) -> float:
    """
    簡單的垃圾郵件分數檢查

    Returns:
        0-1 之間的分數，越高越可能是垃圾郵件
    """

    spam_indicators = [
        ('!!!', 0.2),  # 多個驚嘆號
        ('100% FREE', 0.3),  # 全大寫促銷詞
        ('CLICK HERE', 0.3),
        ('立即購買', 0.2),
        ('限時優惠', 0.2),
    ]

    score = 0
    content_upper = email_content.upper()

    for indicator, weight in spam_indicators:
        if indicator in content_upper:
            score += weight

    # 檢查大寫字母比例
    if email_content.isupper():
        score += 0.5

    return min(score, 1.0)

# 使用
email = generate_email(lead, research)

if check_spam_score(email) > 0.5:
    logger.warning("郵件可能被視為垃圾郵件，重新生成")
    email = regenerate_with_lower_spam_score(lead, research)
```

---

## 監控和維護

### 成功率追蹤

```python
class PerformanceTracker:
    def __init__(self):
        self.stats = {
            'sent': 0,
            'failed': 0,
            'bounced': 0,
            'replied': 0,
        }

    def record_event(self, event_type: str):
        if event_type in self.stats:
            self.stats[event_type] += 1

    def get_success_rate(self) -> float:
        total = self.stats['sent'] + self.stats['failed']
        if total == 0:
            return 0
        return self.stats['sent'] / total

    def get_reply_rate(self) -> float:
        if self.stats['sent'] == 0:
            return 0
        return self.stats['replied'] / self.stats['sent']

    def report(self):
        print("=" * 50)
        print("性能報告")
        print("=" * 50)
        print(f"發送成功: {self.stats['sent']}")
        print(f"發送失敗: {self.stats['failed']}")
        print(f"成功率: {self.get_success_rate():.1%}")
        print(f"回覆數: {self.stats['replied']}")
        print(f"回覆率: {self.get_reply_rate():.1%}")
        print("=" * 50)
```

### 定期審計

```python
import schedule

def daily_audit():
    """每日審計任務"""

    # 1. 檢查 API 用量
    api_usage = check_api_usage()
    if api_usage > 0.8:  # 超過 80%
        send_alert("API 用量即將耗盡")

    # 2. 檢查錯誤率
    error_rate = get_error_rate()
    if error_rate > 0.1:  # 超過 10%
        send_alert(f"錯誤率過高: {error_rate:.1%}")

    # 3. 清理舊日誌
    cleanup_old_logs(days=30)

    # 4. 生成報告
    generate_daily_report()

# 計劃每天執行
schedule.every().day.at("23:00").do(daily_audit)
```

### 日誌最佳實踐

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_file='app.log', level=logging.INFO):
    """配置日誌系統"""

    # 創建 logger
    logger = logging.getLogger('sales_automation')
    logger.setLevel(level)

    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 文件處理器（自動輪換）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)

    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 添加處理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# 使用
logger = setup_logging()
logger.info("系統啟動")
logger.debug(f"處理客戶: {lead['email']}")
logger.error(f"發送失敗: {error}")
```

---

## 總結清單

### ✅ 每次運行前

- [ ] 檢查 API 配額
- [ ] 驗證 .env 配置
- [ ] 確認 CRM 數據質量
- [ ] 檢查是否在最佳發送時間

### ✅ 運行過程中

- [ ] 監控錯誤率
- [ ] 追蹤成功率
- [ ] 記錄異常情況

### ✅ 運行後

- [ ] 查看性能報告
- [ ] 更新 CRM 狀態
- [ ] 清理臨時數據
- [ ] 備份重要數據

---

**遵循這些最佳實踐，你的銷售外展系統將更高效、更安全、更成功！** 🎉
