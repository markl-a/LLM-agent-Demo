#!/usr/bin/env python3
"""
LangFlow - 測試與部署示例

展示如何測試和部署 LangFlow 應用
"""

import requests
import json


LANGFLOW_URL = "http://localhost:7860"


def test_flow(flow_id: str, test_cases: list):
    """測試 Flow"""
    print(f"\n🧪 測試 Flow: {flow_id}\n")

    for i, test_case in enumerate(test_cases, 1):
        print(f"測試案例 {i}: {test_case['input']}")

        try:
            response = requests.post(
                f"{LANGFLOW_URL}/api/v1/process/{flow_id}",
                json={"inputs": test_case["input"]},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                output = result.get("outputs", {}).get("output", "")
                expected = test_case.get("expected")

                if expected:
                    match = expected.lower() in output.lower()
                    status = "✅ PASS" if match else "❌ FAIL"
                else:
                    status = "✅ DONE"

                print(f"  {status} - {output[:100]}...")
            else:
                print(f"  ❌ ERROR - Status {response.status_code}")

        except Exception as e:
            print(f"  ❌ EXCEPTION - {e}")

        print()


def deploy_flow_to_production():
    """部署 Flow 到生產環境"""
    print("\n" + "=" * 60)
    print("🚀 部署 LangFlow 到生產環境")
    print("=" * 60)

    print("""
📋 部署步驟：

1. 導出 Flow
   - 在 LangFlow 界面點擊 'Export'
   - 保存 JSON 配置文件

2. 配置環境變量
   export OPENAI_API_KEY=your_key
   export LANGFLOW_PORT=7860

3. 使用 Docker 部署
   ```bash
   docker run -d \\
     -p 7860:7860 \\
     -e OPENAI_API_KEY=$OPENAI_API_KEY \\
     -v $(pwd)/flows:/app/flows \\
     langflowai/langflow:latest
   ```

4. 使用 Kubernetes 部署
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: langflow
   spec:
     replicas: 3
     template:
       spec:
         containers:
         - name: langflow
           image: langflowai/langflow:latest
           ports:
           - containerPort: 7860
           env:
           - name: OPENAI_API_KEY
             valueFrom:
               secretKeyRef:
                 name: langflow-secrets
                 key: openai-key
   ```

5. 配置負載均衡
   - 使用 Nginx 或 HAProxy
   - 配置健康檢查
   - 設置速率限制

6. 監控和日誌
   - 使用 Prometheus 監控
   - 配置 Grafana 儀表板
   - 集成 ELK/Loki 日誌系統

🔒 生產環境最佳實踐：
- 使用 HTTPS
- 配置 API 密鑰認證
- 設置請求速率限制
- 啟用日誌記錄
- 實施備份策略
- 配置告警
- 使用 CDN 加速
""")


def performance_testing():
    """性能測試"""
    print("\n" + "=" * 60)
    print("⚡ 性能測試")
    print("=" * 60)

    print("""
📊 性能測試指標：

1. 響應時間
   - P50: 中位數響應時間
   - P95: 95% 請求的響應時間
   - P99: 99% 請求的響應時間

2. 吞吐量
   - 每秒請求數 (RPS)
   - 並發用戶數
   - 成功率

3. 資源使用
   - CPU 使用率
   - 內存使用率
   - 網絡帶寬

🔧 使用 Locust 進行壓力測試：

```python
from locust import HttpUser, task, between

class LangFlowUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def query_flow(self):
        self.client.post(
            "/api/v1/process/your-flow-id",
            json={"inputs": {"question": "測試問題"}},
            headers={"Authorization": "Bearer your-token"}
        )
```

運行壓力測試：
```bash
locust -f locustfile.py --host=http://localhost:7860 --users=100 --spawn-rate=10
```
""")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🧪 LangFlow - 測試與部署示例")
    print("=" * 60)

    # 測試案例示例
    test_cases = [
        {
            "input": {"question": "什麼是 AI？"},
            "expected": "artificial intelligence",
        },
        {
            "input": {"question": "Python 是什麼？"},
            "expected": "programming",
        },
    ]

    # 注意：需要替換為實際的 flow_id
    # test_flow("your-flow-id", test_cases)

    print("\n💡 提示：將上面的 'your-flow-id' 替換為實際的 Flow ID 以運行測試\n")

    deploy_flow_to_production()
    performance_testing()

    print("\n" + "=" * 60)
    print("✅ 測試與部署示例完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
