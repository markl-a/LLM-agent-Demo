#!/usr/bin/env python3
"""AutoGPT - 安全控制"""

class SafetyController:
    def __init__(self):
        self.whitelist = ["read", "write", "search"]
        self.blacklist = ["delete_all", "format", "rm -rf"]

    def is_safe(self, action: str) -> bool:
        # 檢查黑名單
        for forbidden in self.blacklist:
            if forbidden in action.lower():
                print(f"🚫 危險操作被阻止: {action}")
                return False

        # 檢查白名單
        for allowed in self.whitelist:
            if allowed in action.lower():
                print(f"✅ 安全操作: {action}")
                return True

        print(f"⚠️  未知操作: {action}")
        return False

safety = SafetyController()
safety.is_safe("read file")
safety.is_safe("delete_all data")
print("\n✅ 安全控制已啟用")
