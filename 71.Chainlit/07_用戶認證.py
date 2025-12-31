"""
Chainlit 用戶認證示例

本示例展示：
1. 認證系統配置
2. 用戶登入/登出
3. 自定義認證邏輯
4. 用戶權限管理
5. 會話管理

運行方式：
    chainlit run 07_用戶認證.py -w

注意：
    需要創建 .chainlit/config.toml 配置文件
"""

import chainlit as cl
from typing import Optional
import hashlib
from datetime import datetime


# ==================== 用戶數據庫（演示用）====================

# 在實際應用中，應該使用真實的數據庫
USERS_DB = {
    "admin": {
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "name": "管理員",
        "email": "admin@example.com"
    },
    "user1": {
        "password_hash": hashlib.sha256("user123".encode()).hexdigest(),
        "role": "user",
        "name": "張三",
        "email": "user1@example.com"
    },
    "user2": {
        "password_hash": hashlib.sha256("user456".encode()).hexdigest(),
        "role": "user",
        "name": "李四",
        "email": "user2@example.com"
    },
}


# ==================== 認證回調 ====================

@cl.password_auth_callback
async def auth_callback(username: str, password: str) -> Optional[cl.User]:
    """
    密碼認證回調函數

    Args:
        username: 用戶名
        password: 密碼

    Returns:
        認證成功返回 User 對象，失敗返回 None
    """
    try:
        print(f"🔐 認證嘗試: {username}")

        # 檢查用戶是否存在
        if username not in USERS_DB:
            print(f"❌ 用戶不存在: {username}")
            return None

        # 獲取用戶數據
        user_data = USERS_DB[username]

        # 驗證密碼
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != user_data["password_hash"]:
            print(f"❌ 密碼錯誤: {username}")
            return None

        # 認證成功，創建用戶對象
        print(f"✅ 認證成功: {username}")

        return cl.User(
            identifier=username,
            metadata={
                "role": user_data["role"],
                "name": user_data["name"],
                "email": user_data["email"],
                "login_time": datetime.now().isoformat()
            }
        )

    except Exception as e:
        print(f"❌ 認證錯誤: {str(e)}")
        return None


# ==================== OAuth 回調（可選）====================

@cl.oauth_callback
async def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: dict,
    default_user: cl.User,
) -> Optional[cl.User]:
    """
    OAuth 認證回調函數

    Args:
        provider_id: OAuth 提供商 ID
        token: 訪問令牌
        raw_user_data: 原始用戶數據
        default_user: 默認用戶對象

    Returns:
        用戶對象
    """
    try:
        print(f"🔐 OAuth 認證: {provider_id}")

        # 這裡可以自定義用戶數據處理邏輯
        # 例如：保存到數據庫、添加元數據等

        return default_user

    except Exception as e:
        print(f"❌ OAuth 錯誤: {str(e)}")
        return None


# ==================== 會話初始化 ====================

@cl.on_chat_start
async def on_chat_start():
    """
    當用戶開始聊天時調用
    此時用戶已經通過認證
    """
    try:
        # 獲取當前用戶
        user = cl.user_session.get("user")

        if user:
            # 從元數據中獲取用戶信息
            user_name = user.metadata.get("name", user.identifier)
            user_role = user.metadata.get("role", "user")
            user_email = user.metadata.get("email", "未設置")
            login_time = user.metadata.get("login_time", "未知")

            # 根據角色設置不同的歡迎消息
            if user_role == "admin":
                welcome_msg = f"""
# 👑 歡迎，{user_name}！（管理員）

你已成功登入系統。

## 👤 用戶信息

- **用戶名**: {user.identifier}
- **姓名**: {user_name}
- **角色**: 管理員 🔑
- **郵箱**: {user_email}
- **登入時間**: {login_time}

## 🔐 管理員權限

作為管理員，你可以：
- ✅ 訪問所有功能
- ✅ 查看系統統計
- ✅ 管理用戶
- ✅ 查看日誌

## 🎮 試試這些命令

- `個人資料` - 查看你的個人資料
- `權限` - 查看你的權限
- `統計` - 查看系統統計（僅管理員）
- `用戶列表` - 查看所有用戶（僅管理員）
- `幫助` - 查看幫助信息
                """
            else:
                welcome_msg = f"""
# 👋 歡迎，{user_name}！

你已成功登入系統。

## 👤 用戶信息

- **用戶名**: {user.identifier}
- **姓名**: {user_name}
- **角色**: 普通用戶
- **郵箱**: {user_email}
- **登入時間**: {login_time}

## 🎮 可用功能

- 💬 聊天對話
- 📊 查看個人數據
- ⚙️ 設置偏好

## 💡 試試這些命令

- `個人資料` - 查看你的個人資料
- `權限` - 查看你的權限
- `幫助` - 查看幫助信息

開始聊天吧！
                """

            await cl.Message(
                content=welcome_msg,
                author="系統"
            ).send()

            # 初始化用戶會話數據
            cl.user_session.set("message_count", 0)
            cl.user_session.set("start_time", datetime.now())

            print(f"✅ 用戶會話已初始化: {user.identifier}")

        else:
            # 理論上不應該到這裡（認證應該已經處理）
            await cl.Message(
                content="❌ 無法獲取用戶信息，請重新登入。"
            ).send()

    except Exception as e:
        error_msg = f"❌ 初始化失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 消息處理 ====================

@cl.on_message
async def on_message(message: cl.Message):
    """處理用戶消息"""
    try:
        # 獲取當前用戶
        user = cl.user_session.get("user")

        if not user:
            await cl.Message(
                content="❌ 請先登入。"
            ).send()
            return

        # 更新消息計數
        count = cl.user_session.get("message_count", 0)
        count += 1
        cl.user_session.set("message_count", count)

        user_message = message.content.strip().lower()

        # 處理命令
        if "個人資料" in user_message or "profile" in user_message:
            await show_profile(user)

        elif "權限" in user_message or "permission" in user_message:
            await show_permissions(user)

        elif "統計" in user_message or "stats" in user_message:
            await show_statistics(user)

        elif "用戶列表" in user_message or "users" in user_message:
            await show_users(user)

        elif "幫助" in user_message or "help" in user_message:
            await show_help(user)

        else:
            # 普通對話
            user_name = user.metadata.get("name", user.identifier)
            response = f"""
你好，{user_name}！

我收到了你的消息：「{message.content}」

這是第 {count} 條消息。

💡 **提示**: 輸入「幫助」查看可用命令。
            """
            await cl.Message(content=response).send()

    except Exception as e:
        error_msg = f"❌ 處理失敗: {str(e)}"
        print(error_msg)
        await cl.Message(content=error_msg).send()


# ==================== 功能函數 ====================

async def show_profile(user: cl.User):
    """顯示用戶個人資料"""
    try:
        user_name = user.metadata.get("name", user.identifier)
        user_role = user.metadata.get("role", "user")
        user_email = user.metadata.get("email", "未設置")
        login_time = user.metadata.get("login_time", "未知")

        # 會話統計
        message_count = cl.user_session.get("message_count", 0)
        start_time = cl.user_session.get("start_time")

        if start_time:
            duration = (datetime.now() - start_time).total_seconds() / 60
            duration_str = f"{duration:.1f} 分鐘"
        else:
            duration_str = "未知"

        profile = f"""
## 👤 個人資料

### 基本信息
- **用戶名**: {user.identifier}
- **姓名**: {user_name}
- **角色**: {user_role}
- **郵箱**: {user_email}

### 會話信息
- **登入時間**: {login_time}
- **會話時長**: {duration_str}
- **消息數量**: {message_count} 條

### 🎯 狀態
✅ 在線
        """

        await cl.Message(content=profile, author="個人資料").send()

    except Exception as e:
        await cl.Message(content=f"❌ 獲取資料失敗: {str(e)}").send()


async def show_permissions(user: cl.User):
    """顯示用戶權限"""
    try:
        user_role = user.metadata.get("role", "user")

        if user_role == "admin":
            permissions = """
## 🔑 權限信息

### 管理員權限

你擁有以下權限：

#### ✅ 完整訪問
- 查看所有功能
- 訪問系統統計
- 管理用戶
- 查看系統日誌
- 修改配置
- 執行管理命令

#### 🎯 特殊功能
- 用戶管理
- 系統監控
- 數據分析
- 權限管理

作為管理員，你可以執行所有操作。
            """
        else:
            permissions = """
## 🔑 權限信息

### 普通用戶權限

你擁有以下權限：

#### ✅ 基本功能
- 發送和接收消息
- 查看個人資料
- 修改個人設置
- 查看對話歷史

#### ❌ 受限功能
- 系統管理（需要管理員權限）
- 用戶管理（需要管理員權限）
- 系統統計（需要管理員權限）

需要更多權限？請聯繫管理員。
            """

        await cl.Message(content=permissions, author="權限管理").send()

    except Exception as e:
        await cl.Message(content=f"❌ 獲取權限失敗: {str(e)}").send()


async def show_statistics(user: cl.User):
    """顯示系統統計（僅管理員）"""
    try:
        user_role = user.metadata.get("role", "user")

        if user_role != "admin":
            await cl.Message(
                content="❌ 權限不足：此功能僅限管理員使用。"
            ).send()
            return

        # 模擬統計數據
        stats = f"""
## 📊 系統統計（管理員專用）

### 用戶統計
- **總用戶數**: {len(USERS_DB)}
- **在線用戶**: 1
- **管理員**: 1
- **普通用戶**: {len(USERS_DB) - 1}

### 會話統計
- **活動會話**: 1
- **今日消息**: 15
- **平均響應時間**: 0.5s

### 系統狀態
- **運行時長**: 2 小時 30 分
- **CPU 使用率**: 25%
- **內存使用**: 512 MB
- **系統狀態**: ✅ 正常

### 📅 更新時間
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        await cl.Message(content=stats, author="系統統計").send()

    except Exception as e:
        await cl.Message(content=f"❌ 獲取統計失敗: {str(e)}").send()


async def show_users(user: cl.User):
    """顯示用戶列表（僅管理員）"""
    try:
        user_role = user.metadata.get("role", "user")

        if user_role != "admin":
            await cl.Message(
                content="❌ 權限不足：此功能僅限管理員使用。"
            ).send()
            return

        # 生成用戶列表
        user_list = "## 👥 用戶列表（管理員專用）\n\n"

        for username, data in USERS_DB.items():
            role_icon = "👑" if data["role"] == "admin" else "👤"
            user_list += f"""
### {role_icon} {data['name']}
- **用戶名**: {username}
- **角色**: {data['role']}
- **郵箱**: {data['email']}

---
            """

        user_list += f"\n**總計**: {len(USERS_DB)} 個用戶"

        await cl.Message(content=user_list, author="用戶管理").send()

    except Exception as e:
        await cl.Message(content=f"❌ 獲取用戶列表失敗: {str(e)}").send()


async def show_help(user: cl.User):
    """顯示幫助信息"""
    try:
        user_role = user.metadata.get("role", "user")

        help_msg = """
## 📚 幫助信息

### 🎮 可用命令

#### 所有用戶
- `個人資料` - 查看個人資料
- `權限` - 查看你的權限
- `幫助` - 顯示此幫助信息
        """

        if user_role == "admin":
            help_msg += """
#### 管理員專用
- `統計` - 查看系統統計
- `用戶列表` - 查看所有用戶
            """

        help_msg += """
### 💡 提示

- 所有命令不區分大小寫
- 可以使用中文或英文命令
- 有問題？直接發送消息給我！

### 🔐 測試賬號

**管理員賬號:**
- 用戶名: admin
- 密碼: admin123

**普通用戶:**
- 用戶名: user1 / user2
- 密碼: user123 / user456
        """

        await cl.Message(content=help_msg, author="幫助").send()

    except Exception as e:
        await cl.Message(content=f"❌ 顯示幫助失敗: {str(e)}").send()


# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║   Chainlit 用戶認證示例                  ║
╚══════════════════════════════════════════╝

運行命令：
    chainlit run 07_用戶認證.py -w

功能特點：
✅ 密碼認證
✅ 用戶角色管理
✅ 權限控制
✅ 會話管理
✅ 用戶資料
✅ OAuth 支持（可選）

測試賬號：
👑 管理員: admin / admin123
👤 用戶1: user1 / user123
👤 用戶2: user2 / user456

配置文件：
需要創建 .chainlit/config.toml 並啟用認證

訪問 http://localhost:8000 開始使用！
    """)


if __name__ == "__main__":
    main()
