#!/usr/bin/env python3
"""Haystack - 部署與監控示例"""

print("🚀 Haystack 部署與監控\n")

print("=" * 60)
print("部署方式")
print("=" * 60)
print("""
1. REST API 部署
   from haystack import Pipeline
   pipeline.serve(host="0.0.0.0", port=8000)

2. Docker 部署
   docker run -p 8000:8000 haystack-app

3. Kubernetes 部署
   kubectl apply -f haystack-deployment.yaml
""")

print("=" * 60)
print("監控指標")
print("=" * 60)
print("""
- 請求延遲 (Latency)
- 吞吐量 (Throughput)
- 錯誤率 (Error Rate)
- Token 使用量
- 緩存命中率
""")

print("=" * 60)
print("日誌與追蹤")
print("=" * 60)
print("""
import logging
logging.basicConfig(level=logging.INFO)

# 啟用追蹤
pipeline.enable_tracing()
""")

print("\n✅ Haystack 20個示例全部完成！")
