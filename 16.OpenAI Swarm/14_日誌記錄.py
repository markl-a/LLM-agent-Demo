#!/usr/bin/env python3
"""OpenAI Swarm - 日誌記錄"""
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class AgentLogger:
    def log_transfer(self, from_agent: str, to_agent: str):
        logging.info(f"Agent 轉接: {from_agent} → {to_agent}")

    def log_action(self, agent: str, action: str):
        logging.info(f"{agent} 執行: {action}")

logger = AgentLogger()
logger.log_transfer("路由員", "銷售專員")
logger.log_action("銷售專員", "提供產品信息")

print("\n✅ 完整日誌記錄")
