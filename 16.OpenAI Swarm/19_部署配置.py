#!/usr/bin/env python3
"""OpenAI Swarm - 部署配置"""

print("""
🚀 OpenAI Swarm 部署指南
================================================================================

1. 環境準備
   export OPENAI_API_KEY="your-api-key"
   pip install openai-swarm

2. Docker 部署
   docker build -t swarm-app .
   docker run -p 8000:8000 swarm-app

3. 配置文件 (config.yaml)
   agents:
     - name: router
       model: gpt-4o-mini
     - name: sales
       model: gpt-4o-mini

4. 負載均衡
   - 使用 Nginx 反向代理
   - 配置健康檢查
   - 設置請求限流

5. 監控告警
   - Prometheus + Grafana
   - 日誌聚合 (ELK Stack)
   - 錯誤追蹤 (Sentry)

================================================================================
✅ 部署配置示例
""")
