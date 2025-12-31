"""
Gradio 認證系統示例

本示例展示：
1. 用戶認證
2. 密碼保護
3. 多用戶管理
4. 權限控制

運行方式：
    python 08_認證系統.py
"""

import gradio as gr
from typing import Tuple, Optional
import hashlib
import time
from datetime import datetime


# ==================== 用戶數據庫（示例） ====================

# 實際應用中應使用真正的數據庫
USER_DATABASE = {
    "admin": {
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "permissions": ["read", "write", "delete", "manage_users"]
    },
    "user1": {
        "password": hashlib.sha256("user123".encode()).hexdigest(),
        "role": "user",
        "permissions": ["read", "write"]
    },
    "guest": {
        "password": hashlib.sha256("guest123".encode()).hexdigest(),
        "role": "guest",
        "permissions": ["read"]
    }
}


# ==================== 認證函數 ====================

def authenticate(username: str, password: str) -> bool:
    """
    驗證用戶身份

    Args:
        username: 用戶名
        password: 密碼

    Returns:
        是否驗證成功
    """
    if username in USER_DATABASE:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return USER_DATABASE[username]["password"] == hashed_password
    return False


def get_user_info(username: str) -> dict:
    """獲取用戶信息"""
    return USER_DATABASE.get(username, {})


def check_permission(username: str, permission: str) -> bool:
    """檢查用戶權限"""
    user_info = get_user_info(username)
    return permission in user_info.get("permissions", [])


# ==================== 業務函數 ====================

def protected_function(username: str, action: str) -> str:
    """
    受保護的功能

    Args:
        username: 當前用戶名
        action: 要執行的動作

    Returns:
        執行結果
    """
    user_info = get_user_info(username)
    role = user_info.get("role", "unknown")

    # 檢查權限
    permission_map = {
        "讀取數據": "read",
        "寫入數據": "write",
        "刪除數據": "delete",
        "管理用戶": "manage_users"
    }

    required_permission = permission_map.get(action)

    if not required_permission:
        return f"❌ 未知操作：{action}"

    if not check_permission(username, required_permission):
        return f"""
❌ **權限不足**

用戶：{username}
角色：{role}
操作：{action}
所需權限：{required_permission}

你沒有執行此操作的權限！
        """

    # 執行操作
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""
✅ **操作成功**

用戶：{username}
角色：{role}
操作：{action}
時間：{timestamp}

操作已成功執行！
    """


def get_user_dashboard(username: str) -> str:
    """獲取用戶儀表板"""
    user_info = get_user_info(username)

    if not user_info:
        return "用戶不存在"

    permissions_list = "\n".join([f"• {p}" for p in user_info.get("permissions", [])])

    return f"""
👤 **用戶信息儀表板**

**基本信息：**
• 用戶名：{username}
• 角色：{user_info.get('role', 'unknown')}
• 登錄時間：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**權限列表：**
{permissions_list}

**系統狀態：**
✅ 在線
    """


def list_users(current_user: str) -> str:
    """列出所有用戶（僅管理員）"""
    if not check_permission(current_user, "manage_users"):
        return "❌ 權限不足：僅管理員可查看用戶列表"

    result = "👥 **用戶列表**\n\n"
    result += "用戶名 | 角色 | 權限數量\n"
    result += "-" * 50 + "\n"

    for username, info in USER_DATABASE.items():
        result += f"{username:10s} | {info['role']:10s} | {len(info['permissions'])}\n"

    return result


# ==================== Gradio 界面 ====================

def create_protected_demo():
    """創建受保護的演示界面"""

    with gr.Blocks(theme=gr.themes.Soft(), title="🔐 受保護的應用") as demo:

        gr.Markdown("# 🔐 受保護的 Gradio 應用")

        # 存儲當前登錄用戶
        current_user = gr.State(value="")

        with gr.Tabs():

            # Tab 1: 用戶儀表板
            with gr.TabItem("📊 儀表板"):
                gr.Markdown("### 用戶信息和權限")

                dashboard_output = gr.Textbox(
                    label="儀表板",
                    lines=15
                )

                refresh_btn = gr.Button("🔄 刷新")

                def show_dashboard(username):
                    if not username:
                        return "請先登錄！"
                    return get_user_dashboard(username)

                refresh_btn.click(
                    fn=show_dashboard,
                    inputs=current_user,
                    outputs=dashboard_output
                )

            # Tab 2: 受保護的操作
            with gr.TabItem("🛡️ 受保護操作"):
                gr.Markdown("### 需要權限的操作")

                with gr.Row():
                    with gr.Column():
                        action_select = gr.Radio(
                            choices=["讀取數據", "寫入數據", "刪除數據", "管理用戶"],
                            label="選擇操作",
                            value="讀取數據"
                        )
                        action_btn = gr.Button("🚀 執行操作", variant="primary")

                    with gr.Column():
                        action_output = gr.Textbox(
                            label="執行結果",
                            lines=12
                        )

                def execute_action(username, action):
                    if not username:
                        return "❌ 請先登錄！"
                    return protected_function(username, action)

                action_btn.click(
                    fn=execute_action,
                    inputs=[current_user, action_select],
                    outputs=action_output
                )

            # Tab 3: 用戶管理
            with gr.TabItem("👥 用戶管理"):
                gr.Markdown("### 管理用戶（僅管理員）")

                users_output = gr.Textbox(
                    label="用戶列表",
                    lines=15
                )

                list_users_btn = gr.Button("📋 查看用戶列表")

                list_users_btn.click(
                    fn=list_users,
                    inputs=current_user,
                    outputs=users_output
                )

            # Tab 4: 登錄信息
            with gr.TabItem("ℹ️ 登錄信息"):
                gr.Markdown("""
### 測試賬戶信息

**管理員賬戶：**
- 用戶名：`admin`
- 密碼：`admin123`
- 權限：全部權限

**普通用戶：**
- 用戶名：`user1`
- 密碼：`user123`
- 權限：讀取、寫入

**訪客賬戶：**
- 用戶名：`guest`
- 密碼：`guest123`
- 權限：僅讀取

### 權限說明

- **read**：讀取數據
- **write**：寫入數據
- **delete**：刪除數據
- **manage_users**：管理用戶

### 安全提示

⚠️ **重要：**
- 這只是演示示例
- 實際應用中應使用：
  - 真實的數據庫
  - 更強的密碼加密（如 bcrypt）
  - Session 管理
  - HTTPS 加密
  - 防暴力破解機制
  - 日誌記錄
                """)

        # 自動顯示儀表板
        demo.load(
            fn=show_dashboard,
            inputs=current_user,
            outputs=dashboard_output
        )

    return demo


def create_simple_auth_demo():
    """創建簡單認證演示"""

    def simple_auth(username: str, password: str) -> bool:
        """簡單的認證函數"""
        return authenticate(username, password)

    # 創建需要認證的界面
    demo = gr.Interface(
        fn=lambda x: f"✅ 歡迎，{x}！你已成功訪問受保護的內容。",
        inputs=gr.Textbox(label="受保護的內容", placeholder="輸入任何內容..."),
        outputs=gr.Textbox(label="響應"),
        title="🔐 簡單認證示例",
        description="此界面需要登錄才能訪問"
    )

    return demo


# ==================== 主函數 ====================

def create_demo():
    """創建主演示"""

    with gr.Blocks(theme=gr.themes.Soft(), title="🔐 Gradio 認證系統") as demo:

        gr.Markdown("# 🔐 Gradio 認證系統示例")
        gr.Markdown("展示用戶認證和權限管理")

        with gr.Tabs():

            # Tab 1: 基礎認證
            with gr.TabItem("🔑 基礎認證"):
                gr.Markdown("### 使用 auth 參數的簡單認證")

                gr.Markdown("""
Gradio 支持內建的基礎認證：

```python
gr.Interface(
    fn=my_function,
    inputs="text",
    outputs="text",
    auth=("username", "password")  # 單用戶
)

# 或多用戶
gr.Interface(
    fn=my_function,
    inputs="text",
    outputs="text",
    auth=[
        ("user1", "pass1"),
        ("user2", "pass2")
    ]
)

# 或使用自定義函數
def auth_function(username, password):
    return username == "admin" and password == "secret"

gr.Interface(
    fn=my_function,
    inputs="text",
    outputs="text",
    auth=auth_function
)
```

**特點：**
- ✅ 簡單易用
- ✅ HTTP 基本認證
- ❌ 無會話管理
- ❌ 無權限控制
                """)

            # Tab 2: 高級權限管理
            with gr.TabItem("🛡️ 高級權限"):
                gr.Markdown("### 基於角色的權限控制")

                # 嵌入受保護的演示
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("""
**模擬登錄：**

選擇一個測試賬戶查看不同權限效果
                        """)

                        login_user = gr.Dropdown(
                            choices=list(USER_DATABASE.keys()),
                            label="選擇用戶",
                            value="admin"
                        )

                        login_btn = gr.Button("🔓 登錄", variant="primary")

                    with gr.Column():
                        login_status = gr.Textbox(
                            label="登錄狀態",
                            lines=5
                        )

                # 用戶操作區
                gr.Markdown("---")

                user_state = gr.State(value="")

                with gr.Row():
                    with gr.Column():
                        gr.Markdown("**執行操作：**")

                        operation = gr.Radio(
                            choices=["讀取數據", "寫入數據", "刪除數據", "管理用戶"],
                            label="選擇操作",
                            value="讀取數據"
                        )

                        execute_btn = gr.Button("▶️ 執行", variant="primary")

                    with gr.Column():
                        result_output = gr.Textbox(
                            label="操作結果",
                            lines=12
                        )

                def do_login(username):
                    user_info = get_user_info(username)
                    perms = ", ".join(user_info.get("permissions", []))

                    status = f"""
✅ **登錄成功**

用戶：{username}
角色：{user_info.get('role')}
權限：{perms}

可以開始執行操作了！
                    """
                    return status, username

                login_btn.click(
                    fn=do_login,
                    inputs=login_user,
                    outputs=[login_status, user_state]
                )

                execute_btn.click(
                    fn=lambda u, o: protected_function(u, o) if u else "❌ 請先登錄！",
                    inputs=[user_state, operation],
                    outputs=result_output
                )

            # Tab 3: 實現指南
            with gr.TabItem("📖 實現指南"):
                gr.Markdown("""
### 完整的認證系統實現

#### 1. 數據庫設計

```python
# 使用 SQLite/PostgreSQL 等
class User:
    id: int
    username: str
    password_hash: str  # 使用 bcrypt
    role: str
    created_at: datetime
    last_login: datetime

class Permission:
    id: int
    name: str
    description: str

class UserPermission:
    user_id: int
    permission_id: int
```

#### 2. 密碼加密

```python
import bcrypt

# 加密密碼
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

# 驗證密碼
def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)
```

#### 3. Session 管理

```python
from datetime import datetime, timedelta
import secrets

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, username: str) -> str:
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            'username': username,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=24)
        }
        return session_id

    def validate_session(self, session_id: str) -> bool:
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        if datetime.now() > session['expires_at']:
            del self.sessions[session_id]
            return False

        return True
```

#### 4. 權限裝飾器

```python
from functools import wraps

def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            username = get_current_user()
            if not check_permission(username, permission):
                return "權限不足"
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 使用
@require_permission("admin")
def admin_function():
    return "管理員操作"
```

#### 5. 日誌記錄

```python
import logging

def log_action(username: str, action: str, result: str):
    logging.info(
        f"User: {username}, "
        f"Action: {action}, "
        f"Result: {result}, "
        f"Time: {datetime.now()}"
    )
```

#### 6. 防暴力破解

```python
from collections import defaultdict
from datetime import datetime, timedelta

class LoginAttemptTracker:
    def __init__(self, max_attempts=5, lockout_time=300):
        self.attempts = defaultdict(list)
        self.max_attempts = max_attempts
        self.lockout_time = lockout_time

    def is_locked(self, username: str) -> bool:
        attempts = self.attempts[username]
        if len(attempts) < self.max_attempts:
            return False

        # 檢查最近的嘗試
        recent_attempts = [
            t for t in attempts
            if datetime.now() - t < timedelta(seconds=self.lockout_time)
        ]

        return len(recent_attempts) >= self.max_attempts

    def record_attempt(self, username: str):
        self.attempts[username].append(datetime.now())
```

### 最佳實踐

✅ **DO：**
- 使用 HTTPS
- 密碼加密存儲（bcrypt、argon2）
- 實現 Session 過期
- 記錄審計日誌
- 實現速率限制
- 使用環境變量存儲秘密
- 定期更新依賴

❌ **DON'T：**
- 明文存儲密碼
- 在代碼中硬編碼密碼
- 忽略 SQL 注入防護
- 不驗證用戶輸入
- 暴露敏感錯誤信息

### 相關資源

- [OWASP 認證備忘錄](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Python bcrypt](https://pypi.org/project/bcrypt/)
- [Flask-Login](https://flask-login.readthedocs.io/)
                """)

        gr.Markdown("""
---
### 💡 認證方式總結

1. **HTTP 基本認證**（Gradio 內建）
   - 簡單快速
   - 適合原型和內部工具

2. **自定義認證函數**
   - 更靈活的驗證邏輯
   - 可集成現有用戶系統

3. **基於角色的訪問控制（RBAC）**
   - 細粒度權限管理
   - 適合複雜應用

4. **OAuth/SSO**
   - 企業級集成
   - 第三方登錄

選擇合適的認證方式取決於你的應用需求！
        """)

    return demo


def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║      Gradio 認證系統示例                 ║
╚══════════════════════════════════════════╝

測試賬戶：
👤 admin / admin123（管理員）
👤 user1 / user123（普通用戶）
👤 guest / guest123（訪客）

功能特點：
✅ HTTP 基本認證
✅ 自定義認證函數
✅ 基於角色的權限控制
✅ 操作權限驗證
✅ 用戶管理

啟動應用...
    """)

    demo = create_demo()

    # 如果要啟用基本認證，取消註釋：
    # demo.launch(
    #     server_name="0.0.0.0",
    #     server_port=7860,
    #     share=False,
    #     auth=authenticate  # 啟用認證
    # )

    # 演示模式（無認證要求）
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )


if __name__ == "__main__":
    main()
