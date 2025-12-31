"""
Aider 最佳實踐
==============

本範例總結使用 Aider 的最佳實踐和專家技巧，包括：
- 提示詞技巧
- 工作流程優化
- 團隊協作
- 安全和隱私
- 性能優化
- 常見陷阱

作者：AI Agent Demo
日期：2025-12-31
"""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class BestPracticeCategory(Enum):
    """最佳實踐分類"""
    PROMPTING = "提示詞技巧"
    WORKFLOW = "工作流程"
    COLLABORATION = "團隊協作"
    SECURITY = "安全隱私"
    PERFORMANCE = "性能優化"
    TROUBLESHOOTING = "問題排查"


@dataclass
class BestPractice:
    """
    最佳實踐

    描述一個具體的最佳實踐。
    """
    category: BestPracticeCategory
    title: str
    description: str
    do_example: str
    dont_example: str
    rationale: str

    def __str__(self) -> str:
        return f"{self.category.value}: {self.title}"


class AiderBestPractices:
    """
    Aider 最佳實踐集合

    提供全面的最佳實踐指南。
    """

    @staticmethod
    def demonstrate_prompting_techniques():
        """
        演示提示詞技巧

        如何編寫有效的 Aider 提示詞。
        """
        print("\n" + "=" * 80)
        print("提示詞技巧")
        print("=" * 80)

        print("""
## 1. 明確具體

### ✓ 好的提示詞

```
請在 User 類中添加一個 validate_email 方法，
使用正則表達式驗證郵箱格式，
如果格式無效則拋出 ValueError 異常。
```

### ✗ 不好的提示詞

```
添加郵箱驗證
```

**原因**：
- 具體說明要做什麼
- 指定位置（User 類）
- 說明實現方式（正則表達式）
- 明確錯誤處理

## 2. 提供上下文

### ✓ 好的提示詞

```
這個專案使用 SQLAlchemy 作為 ORM。
請在 User 模型中添加一個 created_at 字段，
類型為 DateTime，默認值為當前時間。
```

### ✗ 不好的提示詞

```
添加時間戳字段
```

**原因**：
- 說明技術棧
- 提供實現約束
- 明確默認行為

## 3. 分步驟請求

### ✓ 好的提示詞

```
請按以下步驟重構 UserService：

1. 將數據庫操作提取到 UserRepository 類
2. 將驗證邏輯提取到 UserValidator 類
3. UserService 只保留業務邏輯
4. 更新所有相關的測試
```

### ✗ 不好的提示詞

```
重構 UserService
```

**原因**：
- 清晰的步驟
- 明確的職責分離
- 包括測試更新

## 4. 指定代碼風格

### ✓ 好的提示詞

```
請實現一個分頁功能，要求：

1. 使用 Google Python 風格的 docstring
2. 參數使用類型註解
3. 遵循 PEP 8 命名規範
4. 添加防禦性編程檢查
```

### ✗ 不好的提示詞

```
實現分頁
```

**原因**：
- 指定文檔風格
- 要求類型安全
- 遵循規範
- 提高代碼質量

## 5. 包括示例

### ✓ 好的提示詞

```
請實現一個緩存裝飾器，使用方式如下：

@cache(ttl=300)
def expensive_operation(user_id: int):
    return database.query(user_id)

功能要求：
- 支援 TTL（生存時間）
- LRU 淘汰策略
- 線程安全
```

### ✗ 不好的提示詞

```
實現緩存
```

**原因**：
- 提供使用示例
- 明確接口設計
- 列出功能需求

## 6. 說明約束條件

### ✓ 好的提示詞

```
請優化這個查詢函數，要求：

1. 性能提升至少 50%
2. 不改變返回值格式
3. 保持向後兼容
4. 不增加外部依賴
```

### ✗ 不好的提示詞

```
優化這個函數
```

**原因**：
- 明確性能目標
- 保證兼容性
- 限制依賴範圍

## 7. 錯誤修復提示

### ✓ 好的提示詞

```
測試 test_user_login 失敗，錯誤訊息：
"KeyError: 'password'"

這是因為當 password 字段不存在時沒有處理。
請添加適當的錯誤處理，並確保測試通過。
```

### ✗ 不好的提示詞

```
修復測試
```

**原因**：
- 提供錯誤訊息
- 分析原因
- 明確修復目標

## 8. 使用技術術語

### ✓ 好的提示詞

```
請實現一個單例模式的配置管理器：

1. 使用 __new__ 方法實現單例
2. 線程安全（使用 threading.Lock）
3. 支援惰性初始化
4. 實現 context manager 協議
```

### ✗ 不好的提示詞

```
創建一個全局配置
```

**原因**：
- 使用正確的設計模式名稱
- 指定實現細節
- 明確技術要求

## 9. 測試相關提示

### ✓ 好的提示詞

```
為 calculate_discount 函數生成測試，要求：

1. 測試正常情況（有效折扣）
2. 測試邊界條件（0%, 100%）
3. 測試異常情況（負數、超過100%）
4. 測試浮點數精度
5. 使用 pytest 參數化測試
```

### ✗ 不好的提示詞

```
生成測試
```

**原因**：
- 覆蓋所有情況
- 指定測試框架
- 使用進階功能

## 10. 重構提示

### ✓ 好的提示詞

```
請重構 process_order 方法，應用以下重構模式：

1. Extract Method - 將驗證邏輯提取為 _validate_order
2. Replace Conditional with Polymorphism - 不同訂單類型使用子類
3. Introduce Parameter Object - 創建 OrderRequest 類
4. 確保所有測試仍然通過
```

### ✗ 不好的提示詞

```
重構這個方法
```

**原因**：
- 指定重構模式
- 明確目標結構
- 要求測試保護
        """)

    @staticmethod
    def demonstrate_workflow_optimization():
        """
        演示工作流程優化
        """
        print("\n" + "=" * 80)
        print("工作流程優化")
        print("=" * 80)

        print("""
## 1. 漸進式開發

### 推薦流程

```bash
# 步驟 1: 創建基本結構
$ aider models.py
> 創建一個基本的 User 類，包含 id、username、email 屬性

# 步驟 2: 添加驗證
> 添加郵箱和用戶名驗證方法

# 步驟 3: 添加持久化
> 添加 SQLAlchemy 映射

# 步驟 4: 生成測試
$ aider models.py tests/test_models.py
> 為 User 類生成完整的測試

# 步驟 5: 審查和提交
> /diff
> /commit 實現 User 模型和驗證
```

**優勢**：
- 每步都可審查
- 容易回滾
- 清晰的提交歷史

## 2. 使用分支策略

### Feature 分支工作流

```bash
# 創建功能分支
$ git checkout -b feature/user-auth

# 使用 Aider 開發
$ aider --auto-commits src/auth/*.py

# 完成後合併
$ git checkout main
$ git merge feature/user-auth
```

### 實驗性變更

```bash
# 創建實驗分支
$ git checkout -b experiment/new-approach

# 嘗試新方法
$ aider --model gpt-4-turbo
> 嘗試使用策略模式重構

# 如果成功
$ git checkout main
$ git merge experiment/new-approach

# 如果失敗
$ git checkout main
$ git branch -D experiment/new-approach
```

## 3. 會話管理

### 保持會話專注

```bash
# ✓ 好的做法
$ aider auth.py  # 只處理認證相關

# ✗ 不好的做法
$ aider src/**/*.py  # 太多文件，失去焦點
```

### 定期重啟會話

```bash
# 長時間會話可能導致上下文混亂
# 建議：每完成一個功能重啟

$ aider feature1.py
> 實現功能 1
> /commit

$ exit

$ aider feature2.py  # 新會話
> 實現功能 2
```

## 4. 文件組織

### 相關文件一起處理

```bash
# ✓ 好的做法
$ aider models.py schemas.py repositories.py
> 這些文件相互關聯，一起處理

# ✓ 也好
$ aider auth.py tests/test_auth.py
> 源碼和測試一起
```

## 5. 利用 Git 歷史

### 參考提交歷史

```bash
$ aider
> /git log

# 查看最近的提交風格
> 請生成類似格式的提交訊息
```

### 使用 Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash

# 使用 Aider 自動格式化
aider --message "格式化代碼" --yes --read src/*.py

# 運行測試
pytest
```

## 6. 模型選擇策略

### 根據任務複雜度

```bash
# 簡單任務
$ aider --model gpt-3.5-turbo
> 添加類型註解

# 中等任務
$ aider --model claude-3-5-sonnet-20241022
> 實現業務邏輯

# 複雜任務
$ aider --model gpt-4-turbo
> 設計系統架構
```

## 7. 測試驅動開發

### TDD 工作流

```bash
# 1. 先寫測試
$ aider tests/test_feature.py
> 為新功能編寫測試（會失敗）

# 2. 實現功能
$ aider src/feature.py tests/test_feature.py
> 實現功能讓測試通過

# 3. 重構
> 重構代碼改善結構

# 4. 確認
> /test
```

## 8. 代碼審查流程

### Pull Request 工作流

```bash
# 1. 創建 PR
$ git push origin feature-branch

# 2. 使用 Aider 處理審查意見
$ aider
> 根據審查意見修改：
> 1. 添加錯誤處理
> 2. 改善變數命名
> 3. 添加文檔

# 3. 推送更新
> /commit 根據審查意見改進代碼
$ git push
```

## 9. 文檔維護

### 保持文檔同步

```bash
# 代碼變更後
$ aider src/api.py README.md
> 代碼已更新，請同步更新 README 中的 API 文檔
```

## 10. 持續優化

### 定期重構

```bash
# 每週或每兩週
$ aider src/**/*.py
> 請審查代碼並提出重構建議

# 根據建議執行重構
> 執行建議的重構
```
        """)

    @staticmethod
    def demonstrate_team_collaboration():
        """
        演示團隊協作最佳實踐
        """
        print("\n" + "=" * 80)
        print("團隊協作")
        print("=" * 80)

        print("""
## 1. 團隊配置標準化

### 創建共享配置

```yaml
# .aider.team.yml (提交到 Git)

# 團隊默認模型
model: gpt-4-turbo

# 代碼風格
style:
  docstring: google
  line_length: 88
  imports: isort

# 自動化
auto-commits: false  # 團隊決定手動提交
dirty-commits: false  # 不允許在髒工作區提交

# 測試
auto-test: true
```

### 團隊指南文檔

```markdown
# Aider 使用指南

## 提交訊息規範

使用 Aider 時，提交訊息應遵循：

- feat: 新功能
- fix: Bug 修復
- refactor: 重構
- test: 測試
- docs: 文檔

示例：
> /commit feat: 實現用戶認證功能
```

## 2. 代碼審查協作

### 審查者使用 Aider

```bash
# 審查 Pull Request
$ gh pr checkout 123
$ aider --read src/**/*.py

> 請審查這些變更，檢查：
> 1. 代碼品質
> 2. 潛在問題
> 3. 測試覆蓋

# 提供具體的改進建議
> 生成具體的改進建議清單
```

### 開發者回應審查

```bash
$ aider src/feature.py
> 根據審查意見：
> 1. [審查意見 1]
> 2. [審查意見 2]
```

## 3. 知識分享

### 創建範例庫

```bash
# 團隊範例倉庫
examples/
├── authentication/
│   ├── prompt.txt
│   └── result.py
├── database/
│   ├── prompt.txt
│   └── result.py
└── testing/
    ├── prompt.txt
    └── result.py
```

### 分享成功模式

```markdown
# 團隊 Wiki: Aider 成功案例

## 案例 1: API 端點實現

**提示詞**：
> 創建一個 RESTful API 端點 /api/users，
> 支援 CRUD 操作，使用 Flask-RESTful

**結果**：完美實現，無需修改

**學習**：提供具體框架名稱效果更好
```

## 4. 配對編程

### 遠程配對使用 Aider

```bash
# 開發者 A 分享屏幕
$ aider feature.py

# 兩人討論後
> [討論的實現方案]

# 開發者 B 也可以本地跟進
$ aider feature.py --read
```

## 5. 新人培訓

### Aider 培訓檢查清單

```markdown
- [ ] 安裝和配置
- [ ] 基本命令
- [ ] 提示詞技巧
- [ ] Git 整合
- [ ] 團隊規範
- [ ] 成本意識
- [ ] 常見問題
```

### 實踐練習

```bash
# 練習 1: 簡單功能
$ aider tutorial/exercise1.py
> 實現一個計算器類

# 練習 2: 測試生成
$ aider tutorial/exercise2.py tests/test_exercise2.py
> 為現有代碼生成測試

# 練習 3: 重構
$ aider tutorial/exercise3.py
> 重構這個類遵循 SOLID 原則
```

## 6. 成本管理

### 團隊預算

```yaml
# 團隊配置
budget:
  monthly_limit: 500  # USD
  per_developer: 50
  alert_threshold: 0.8

tracking:
  enabled: true
  report_to: tech-lead@example.com
```

### 成本優化策略

```markdown
# 團隊成本指南

1. 簡單任務用 GPT-3.5
2. 複雜任務用 GPT-4
3. 大型重構用 Claude（大上下文）
4. 實驗性任務用本地模型
```

## 7. 代碼所有權

### 歸屬標記

```python
# 使用 Aider 生成的代碼應標記
# Generated with Aider on 2025-12-31
# Reviewed by: @developer_name

class UserService:
    # Aider 生成的實現
    pass
```

### 審查要求

```markdown
# Aider 生成代碼的審查清單

- [ ] 功能正確性
- [ ] 代碼品質
- [ ] 安全性
- [ ] 性能
- [ ] 測試覆蓋
- [ ] 文檔完整
```
        """)

    @staticmethod
    def demonstrate_security_practices():
        """
        演示安全和隱私最佳實踐
        """
        print("\n" + "=" * 80)
        print("安全和隱私")
        print("=" * 80)

        print("""
## 1. API 金鑰管理

### ✓ 安全做法

```bash
# 使用環境變數
export OPENAI_API_KEY="sk-..."

# 或使用 .env 文件（不要提交到 Git）
echo "OPENAI_API_KEY=sk-..." > .env
echo ".env" >> .gitignore

# 使用密鑰管理工具
$ aider --api-key-from-vault
```

### ✗ 不安全做法

```bash
# 不要硬編碼
aider --api-key sk-xxx  # 會出現在 shell 歷史

# 不要提交到 Git
.env  # 確保在 .gitignore 中
```

## 2. 敏感資料處理

### 避免提交敏感資料

```bash
# 在 .aiderignore 中排除敏感文件
echo "secrets.py" >> .aiderignore
echo "config/production.yml" >> .aiderignore
echo ".env" >> .aiderignore
echo "*.key" >> .aiderignore
```

### 審查提交內容

```bash
# 提交前檢查
$ aider
> /diff  # 仔細審查變更

# 確認沒有敏感資料
> /commit
```

## 3. 私有代碼保護

### 本地模型選項

```bash
# 對於敏感代碼，使用本地模型
$ ollama pull codellama
$ aider --model ollama/codellama sensitive_code.py

# 完全離線，保護隱私
```

### 企業部署

```bash
# 使用私有 API 端點
export OPENAI_API_BASE="https://private.api.company.com"
aider --model custom/internal-model
```

## 4. 代碼審查安全

### 審查 AI 生成的代碼

```python
# 檢查點：

# 1. SQL 注入
# ✗ 危險
query = f"SELECT * FROM users WHERE id = {user_id}"

# ✓ 安全
query = "SELECT * FROM users WHERE id = ?"

# 2. XSS 漏洞
# ✗ 危險
html = f"<div>{user_input}</div>"

# ✓ 安全
html = f"<div>{escape(user_input)}</div>"

# 3. 路徑遍歷
# ✗ 危險
file_path = f"/uploads/{filename}"

# ✓ 安全
file_path = safe_join("/uploads", secure_filename(filename))
```

## 5. 依賴安全

### 檢查新增依賴

```bash
# Aider 可能建議安裝新包
> /commit 添加了依賴：some-package

# 在接受前檢查
$ pip index versions some-package
$ safety check  # 檢查已知漏洞
```

## 6. 訪問控制

### 團隊權限管理

```yaml
# .aider.permissions.yml

roles:
  junior:
    models: [gpt-3.5-turbo]
    max_daily_cost: 5
    requires_review: true

  senior:
    models: [gpt-4-turbo, claude-3-5-sonnet-20241022]
    max_daily_cost: 50
    requires_review: false

  admin:
    models: all
    max_daily_cost: unlimited
```

## 7. 審計日誌

### 記錄使用情況

```bash
# 啟用審計日誌
aider --audit-log audit.json

# 日誌包含：
# - 時間戳
# - 用戶
# - 文件
# - 提示詞
# - 模型
# - 成本
```

## 8. 合規性

### GDPR / 數據保護

```markdown
# 數據處理聲明

使用 Aider 時：

1. 不要處理個人身份資訊（PII）
2. 生產數據不要用於開發
3. 使用匿名化測試數據
4. 定期審查和清理聊天歷史
```

## 9. 網路安全

### 防火牆配置

```bash
# 限制 API 訪問
# 只允許特定 IP 訪問 OpenAI API

# 使用代理
export HTTPS_PROXY="http://proxy.company.com:8080"
aider
```

## 10. 事件響應

### 安全事件處理

```markdown
# 如果 API 金鑰洩露：

1. 立即撤銷金鑰
2. 生成新金鑰
3. 審查最近的使用記錄
4. 檢查是否有未授權使用
5. 更新所有使用該金鑰的地方
6. 報告給安全團隊
```
        """)

    @staticmethod
    def demonstrate_common_pitfalls():
        """
        演示常見陷阱和解決方案
        """
        print("\n" + "=" * 80)
        print("常見陷阱")
        print("=" * 80)

        print("""
## 1. Token 限制問題

### 問題
```
Error: Context length exceeded
```

### 解決方案
```bash
# 減少文件數量
aider specific_file.py  # 而不是 src/**/*.py

# 使用更大上下文的模型
aider --model claude-3-5-sonnet-20241022  # 200K context

# 調整 repository map
aider --map-tokens 512  # 減少 map 使用
```

## 2. 模型不理解需求

### 問題
Aider 生成的代碼不符合預期

### 解決方案
```bash
# 提供更多上下文
> 這個專案使用 Flask 和 SQLAlchemy
> 請實現一個用戶模型，遵循項目現有的模式
> 參考 Product 模型的實現方式

# 提供示例
> 類似於這樣的結構：
> [粘貼示例代碼]
```

## 3. 測試失敗

### 問題
Aider 的變更破壞了現有測試

### 解決方案
```bash
# 包含測試文件
$ aider src/feature.py tests/test_feature.py

> 修改功能，確保所有測試仍然通過

# 或使用 /test 命令
> /test
# 如果失敗
> 修復導致測試失敗的問題
```

## 4. Git 衝突

### 問題
自動提交導致合併衝突

### 解決方案
```bash
# 不使用 auto-commits
aider  # 默認手動提交

# 定期同步
$ git pull
$ aider
> 繼續工作...

# 使用功能分支
$ git checkout -b feature-x
$ aider --auto-commits
```

## 5. 成本超支

### 問題
意外的高額 API 費用

### 解決方案
```bash
# 設置成本限制
# .aider.yml
costs:
  daily_limit: 10.0
  warn_at: 0.8

# 使用便宜的模型
aider --model gpt-3.5-turbo

# 監控使用
> /costs
```

## 6. 代碼品質下降

### 問題
AI 生成的代碼不符合團隊標準

### 解決方案
```bash
# 明確指定標準
> 請遵循以下標準：
> 1. PEP 8
> 2. Google docstring
> 3. 類型註解
> 4. 最大行長度 88

# 使用 linter 檢查
$ black src/
$ pylint src/
```

## 7. 依賴地獄

### 問題
Aider 添加了不必要的依賴

### 解決方案
```bash
# 明確限制依賴
> 請不要添加新的外部依賴
> 使用標準庫實現

# 審查依賴變更
> /diff requirements.txt
```

## 8. 過度依賴 AI

### 問題
開發者不理解生成的代碼

### 解決方案
```bash
# 要求解釋
> 請解釋這段代碼是如何工作的

# 要求添加註釋
> 請添加詳細的註釋解釋每個步驟

# 學習和理解
# 不要盲目接受，要理解代碼邏輯
```

## 9. 會話上下文混亂

### 問題
長時間會話後 Aider 開始產生不相關的建議

### 解決方案
```bash
# 定期重啟會話
$ exit
$ aider feature.py  # 新會話

# 使用 /clear 清除歷史
> /clear

# 重新添加必要文件
> /drop old_file.py
> /add relevant_file.py
```

## 10. 版本控制混亂

### 問題
太多小的自動提交

### 解決方案
```bash
# 關閉自動提交
aider  # 默認手動

# 合併提交
$ git rebase -i HEAD~10

# 或使用 squash
$ git reset --soft HEAD~10
$ git commit -m "實現功能 X"
```
        """)


def main():
    """
    主函數

    展示所有最佳實踐。
    """
    print("=" * 80)
    print("Aider 最佳實踐指南")
    print("=" * 80)

    practices = AiderBestPractices()

    # 展示各類最佳實踐
    practices.demonstrate_prompting_techniques()
    practices.demonstrate_workflow_optimization()
    practices.demonstrate_team_collaboration()
    practices.demonstrate_security_practices()
    practices.demonstrate_common_pitfalls()

    print("\n" + "=" * 80)
    print("總結")
    print("=" * 80)

    print("""
# Aider 使用金科玉律

## 1. 明確溝通
   提供清晰、具體、完整的指示

## 2. 小步前進
   將大任務分解為小步驟

## 3. 頻繁審查
   定期檢查生成的代碼

## 4. 保持上下文
   只添加相關文件到會話

## 5. 測試保護
   始終運行測試確保正確性

## 6. Git 最佳實踐
   使用分支、有意義的提交訊息

## 7. 成本意識
   根據任務選擇合適的模型

## 8. 安全第一
   保護敏感數據和 API 金鑰

## 9. 團隊協作
   建立共同的標準和流程

## 10. 持續學習
    不斷改進提示詞和工作流程

---

記住：Aider 是工具，不是替代品。
它增強您的能力，但不替代您的判斷。

最佳實踐是持續演進的，
隨著工具更新和經驗積累而改進。

祝編程愉快！ 🚀
    """)


if __name__ == "__main__":
    main()
