# 安全政策

## 我們對安全的承諾

LLM Agent Demo 專案團隊非常重視安全性。我們致力於確保本專案的安全性，並鼓勵社區成員負責任地披露任何安全漏洞。

## 支持的版本

目前正在接受安全更新的版本：

| 版本 | 支持狀態 |
| --- | --- |
| main (最新) | ✅ 支持 |
| 舊版本 | ❌ 不支持 |

**建議**: 請始終使用最新版本以獲得最佳安全性。

## 報告安全漏洞

### 🔒 私密報告（推薦）

如果您發現了安全漏洞，請**不要**在公開的 GitHub Issues 中報告。

請通過以下方式私密報告：

1. **GitHub Security Advisories**（推薦）
   - 訪問: https://github.com/markl-a/LLM-agent-Demo/security/advisories
   - 點擊 "New draft security advisory"
   - 填寫詳細信息並提交

2. **電子郵件**
   - 發送至: security@example.com（請替換為實際郵箱）
   - 主題: [SECURITY] LLM-agent-Demo 安全漏洞報告
   - 包含詳細的漏洞描述（見下方模板）

### 📝 漏洞報告模板

請在報告中包含以下信息：

```markdown
## 漏洞概述
[簡短描述漏洞]

## 漏洞類型
- [ ] 注入漏洞（SQL、命令、提示注入等）
- [ ] 敏感信息泄露
- [ ] 權限提升
- [ ] 跨站腳本（XSS）
- [ ] 不安全的依賴項
- [ ] 其他（請說明）

## 影響範圍
- **嚴重程度**: Critical / High / Medium / Low
- **受影響版本**:
- **受影響組件**:

## 重現步驟
1.
2.
3.

## 概念驗證（PoC）
[如果有的話，提供 PoC 代碼或截圖]

## 建議的修復方案
[如果有想法的話]

## 其他信息
[任何其他相關信息]
```

### ⏱️ 響應時間

我們承諾：

- **初步響應**: 48 小時內確認收到報告
- **嚴重漏洞**: 7 天內提供初步評估
- **一般漏洞**: 14 天內提供初步評估
- **修復時間**: 根據嚴重程度，30-90 天內發布修復

### 🎁 致謝

我們感謝所有負責任地披露安全漏洞的研究人員。我們會在修復後：

- 在 CHANGELOG 中公開感謝您（除非您選擇匿名）
- 在 Security Advisories 中列出您的貢獻
- 根據漏洞嚴重程度考慮提供獎勵（待定）

## 安全最佳實踐

### 對於用戶

#### 1. API Key 管理

**❌ 不要這樣做**：

```python
# 不要硬編碼 API Key
api_key = "sk-abc123..."
client = OpenAI(api_key=api_key)

# 不要提交包含 API Key 的文件
.env
config.json
```

**✅ 正確做法**：

```python
# 使用環境變量
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
```

```bash
# .gitignore 中添加
.env
.env.*
!.env.example
*.key
*_credentials.json
```

#### 2. 提示注入防護

**風險示例**：

```python
# ❌ 直接使用用戶輸入可能導致提示注入
user_input = request.get("query")
prompt = f"Translate the following to French: {user_input}"
```

**防護措施**：

```python
# ✅ 驗證和清理用戶輸入
def sanitize_input(text: str, max_length: int = 1000) -> str:
    """清理用戶輸入"""
    # 限制長度
    text = text[:max_length]

    # 移除潛在危險字符
    dangerous_patterns = [
        "Ignore previous instructions",
        "You are now",
        "System:",
        "Human:",
    ]

    for pattern in dangerous_patterns:
        if pattern.lower() in text.lower():
            raise ValueError("檢測到潛在的提示注入攻擊")

    return text.strip()

# 使用
user_input = sanitize_input(request.get("query"))
prompt = f"Translate the following to French: {user_input}"
```

#### 3. 輸出驗證

```python
# ✅ 驗證 LLM 輸出
def validate_output(output: str) -> bool:
    """驗證 LLM 輸出的安全性"""
    # 檢查是否包含敏感信息
    sensitive_patterns = [
        r"api[_-]?key",
        r"password",
        r"secret",
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # 郵箱
    ]

    for pattern in sensitive_patterns:
        if re.search(pattern, output, re.IGNORECASE):
            logger.warning(f"輸出包含敏感信息: {pattern}")
            return False

    return True
```

#### 4. 依賴項安全

```bash
# 定期檢查依賴項漏洞
pip install safety
safety check

# 或使用 pip-audit
pip install pip-audit
pip-audit

# 更新依賴項
pip install --upgrade -r requirements.txt
```

#### 5. 速率限制

```python
from ratelimit import limits, sleep_and_retry

# ✅ 實施速率限制
@sleep_and_retry
@limits(calls=10, period=60)  # 每分鐘最多 10 次調用
def call_llm_api(prompt: str):
    """受速率限制保護的 API 調用"""
    return client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
```

### 對於開發者

#### 1. 代碼審查重點

在代碼審查時，特別關注：

- API Key 是否硬編碼
- 用戶輸入是否經過驗證
- 敏感數據是否被記錄
- 錯誤信息是否暴露過多細節
- 依賴項是否有已知漏洞

#### 2. 敏感文件保護

```bash
# 確保這些文件在 .gitignore 中
.env
.env.*
!.env.example
*.key
*.pem
*_credentials.json
*.sqlite
*.db
*.log
secrets/
private/
```

#### 3. 日誌安全

```python
import logging

# ❌ 不要記錄敏感信息
logger.info(f"API Key: {api_key}")
logger.debug(f"User password: {password}")

# ✅ 使用脫敏
def mask_sensitive(text: str) -> str:
    """脫敏敏感信息"""
    if len(text) <= 8:
        return "***"
    return f"{text[:4]}...{text[-4:]}"

logger.info(f"Using API Key: {mask_sensitive(api_key)}")
```

#### 4. 安全的文件操作

```python
import os
from pathlib import Path

# ✅ 驗證文件路徑，防止路徑遍歷
def safe_file_read(filename: str, base_dir: str = "./data") -> str:
    """安全的文件讀取"""
    base_path = Path(base_dir).resolve()
    file_path = (base_path / filename).resolve()

    # 確保文件在允許的目錄內
    if not str(file_path).startswith(str(base_path)):
        raise ValueError("不允許的文件路徑")

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {filename}")

    return file_path.read_text()
```

## 已知的安全考慮

### 1. LLM 相關風險

- **提示注入**: 惡意用戶可能試圖操縱 LLM 行為
- **數據泄露**: LLM 可能無意中輸出訓練數據
- **幻覺**: LLM 可能生成虛假但看似合理的信息

### 2. 依賴項風險

本專案使用多個第三方庫，可能存在已知漏洞。我們建議：

- 定期更新依賴項
- 使用 `safety` 或 `pip-audit` 檢查漏洞
- 關注安全公告

### 3. API Key 泄露風險

- 不要將 API Key 提交到代碼庫
- 使用環境變量或密鑰管理服務
- 定期輪換 API Key
- 為不同環境使用不同的 Key

## 安全更新通知

我們會通過以下渠道發布安全更新：

1. **GitHub Security Advisories**
   - https://github.com/markl-a/LLM-agent-Demo/security/advisories

2. **GitHub Releases**
   - https://github.com/markl-a/LLM-agent-Demo/releases

3. **CHANGELOG.md**
   - 標記為 `[SECURITY]` 的更新

## 安全審計

### 自動化安全檢查

我們的 CI/CD 流程包含：

```yaml
# .github/workflows/security.yml
name: Security Checks

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Safety
        run: |
          pip install safety
          safety check

      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r src/

      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
```

### 定期審計

- **代碼審計**: 每季度進行代碼安全審計
- **依賴項審計**: 每月檢查依賴項漏洞
- **滲透測試**: 根據需要進行（主要針對 Web 應用）

## 合規性

本專案遵循：

- **OWASP Top 10**: 常見 Web 應用安全風險
- **CWE**: 常見弱點枚舉
- **GDPR**: 如果處理歐盟用戶數據
- **CCPA**: 如果處理加州用戶數據

## 參考資源

### LLM 安全

- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [OpenAI Safety Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)
- [Anthropic Responsible Scaling Policy](https://www.anthropic.com/index/responsible-scaling-policy)

### 通用安全

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

## 聯繫方式

- **安全問題**: security@example.com（請替換為實際郵箱）
- **GitHub Security**: https://github.com/markl-a/LLM-agent-Demo/security
- **一般問題**: https://github.com/markl-a/LLM-agent-Demo/issues

---

**最後更新**: 2025-12-31

**版本**: 1.0

感謝您幫助我們保持 LLM Agent Demo 專案的安全！
