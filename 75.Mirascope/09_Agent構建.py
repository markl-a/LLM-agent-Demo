"""
Mirascope Agent 構建示例
運行方式：python 09_Agent構建.py
"""
import os
from mirascope.openai import OpenAICall
from typing import List, Dict

class AgentPlanner(OpenAICall):
    prompt_template = """
    任務：{task}
    
    請制定執行計劃，分解成具體步驟。
    """
    task: str

class AgentExecutor(OpenAICall):
    prompt_template = """
    執行步驟：{step}
    
    之前的結果：{previous_results}
    
    請執行這一步並報告結果。
    """
    step: str
    previous_results: str = ""

class SimpleAgent:
    """簡單的 Agent 實現"""
    
    def __init__(self, task: str):
        self.task = task
        self.results: List[str] = []
    
    def run(self):
        # 步驟 1: 制定計劃
        print("📋 制定計劃...")
        plan_response = AgentPlanner(task=self.task).call()
        print(f"   計劃: {plan_response.content[:100]}...\\n")
        
        # 步驟 2: 執行（簡化版本）
        print("⚙️ 執行任務...")
        steps = ["分析需求", "設計方案", "實施方案"]
        
        for i, step in enumerate(steps, 1):
            print(f"   {i}. {step}...")
            try:
                response = AgentExecutor(
                    step=step,
                    previous_results="\\n".join(self.results)
                ).call()
                result = response.content[:50]
                self.results.append(f"{step}: {result}")
                print(f"      完成: {result}...\\n")
            except Exception as e:
                print(f"      ❌ 失敗: {e}\\n")
                break
        
        # 步驟 3: 總結
        print("📊 任務完成總結:")
        for result in self.results:
            print(f"   ✅ {result[:80]}...")

def main():
    print("\\nMirascope Agent 構建示例\\n")
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY")
        return
    
    print("示例: 構建簡單 Agent")
    try:
        agent = SimpleAgent(task="創建一個網站")
        agent.run()
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    
    print("\\n✅ 示例完成")

if __name__ == "__main__":
    main()
