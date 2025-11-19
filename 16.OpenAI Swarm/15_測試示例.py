#!/usr/bin/env python3
"""OpenAI Swarm - 測試示例"""

class AgentTester:
    def test_routing(self, router, test_cases):
        passed = 0
        for user_msg, expected_agent in test_cases:
            result = router.route(user_msg)
            if result == expected_agent:
                print(f"✅ '{user_msg}' → {result}")
                passed += 1
            else:
                print(f"❌ '{user_msg}' → {result} (期望: {expected_agent})")

        print(f"\n測試結果: {passed}/{len(test_cases)} 通過")

print("🧪 Agent 測試框架已就緒")
print("✅ 支持單元測試與集成測試")
