#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AutoGPT 自主 Agent 示例
演示如何構建一個自主決策的 AI Agent
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai


class AutonomousAgent:
    """自主 AI Agent"""

    def __init__(
        self,
        name: str,
        role: str,
        goals: List[str],
        max_iterations: int = 25,
        max_cost: float = 5.0
    ):
        """
        初始化自主 Agent

        Args:
            name: Agent 名稱
            role: Agent 角色
            goals: 目標列表
            max_iterations: 最大迭代次數
            max_cost: 最大成本（美元）
        """
        self.name = name
        self.role = role
        self.goals = goals
        self.max_iterations = max_iterations
        self.max_cost = max_cost

        # 初始化狀態
        self.iteration = 0
        self.current_cost = 0.0
        self.completed_tasks = []
        self.memory = []

        # 配置 OpenAI
        self.setup_openai()

        # 可用工具
        self.tools = {
            "search": self.tool_search,
            "write_file": self.tool_write_file,
            "read_file": self.tool_read_file,
            "analyze": self.tool_analyze,
        }

    def setup_openai(self):
        """配置 OpenAI API"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("請設置 OPENAI_API_KEY 環境變量")

        openai.api_key = api_key
        self.model = "gpt-3.5-turbo"  # 使用低成本模型

    def think(self) -> Dict[str, Any]:
        """
        思考下一步行動

        Returns:
            包含思考結果的字典
        """
        # 構建 prompt
        prompt = self._build_thinking_prompt()

        # 調用 LLM
        response = self._call_llm(prompt)

        # 解析響應
        thought = self._parse_thought(response)

        # 記錄到記憶
        self.memory.append({
            "type": "thought",
            "content": thought,
            "timestamp": datetime.now().isoformat()
        })

        return thought

    def _build_thinking_prompt(self) -> str:
        """構建思考 prompt"""
        prompt = f"""
你是 {self.name}，一個 {self.role}。

你的目標：
{self._format_goals()}

已完成的任務：
{self._format_completed_tasks()}

當前狀態：
- 迭代次數：{self.iteration}/{self.max_iterations}
- 已使用成本：${self.current_cost:.4f}/${self.max_cost}

可用工具：
{self._format_tools()}

請分析當前情況，決定下一步行動。

請以 JSON 格式回答，包含：
{{
    "reasoning": "你的推理過程",
    "action": "要執行的動作名稱",
    "parameters": {{"參數名": "參數值"}},
    "expected_outcome": "預期結果"
}}
"""
        return prompt

    def _format_goals(self) -> str:
        """格式化目標"""
        return "\n".join([f"{i+1}. {goal}" for i, goal in enumerate(self.goals)])

    def _format_completed_tasks(self) -> str:
        """格式化已完成任務"""
        if not self.completed_tasks:
            return "無"
        return "\n".join([f"- {task}" for task in self.completed_tasks])

    def _format_tools(self) -> str:
        """格式化工具列表"""
        tools_desc = {
            "search": "搜索信息（參數：query）",
            "write_file": "寫入文件（參數：filename, content）",
            "read_file": "讀取文件（參數：filename）",
            "analyze": "分析數據（參數：data）",
        }
        return "\n".join([f"- {name}: {desc}" for name, desc in tools_desc.items()])

    def _call_llm(self, prompt: str) -> str:
        """調用 LLM"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"你是一個自主 AI Agent，名為 {self.name}"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            # 估算成本
            usage = response["usage"]
            cost = (usage["prompt_tokens"] * 0.0015 + usage["completion_tokens"] * 0.002) / 1000
            self.current_cost += cost

            return response.choices[0].message.content

        except Exception as e:
            print(f"LLM 調用錯誤：{e}")
            return "{}"

    def _parse_thought(self, response: str) -> Dict[str, Any]:
        """解析思考結果"""
        try:
            # 提取 JSON
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end]

            thought = json.loads(json_str)
            return thought
        except:
            # 解析失敗，返回默認
            return {
                "reasoning": "解析失敗",
                "action": "none",
                "parameters": {},
                "expected_outcome": ""
            }

    def execute(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行動作

        Args:
            action: 動作名稱
            parameters: 動作參數

        Returns:
            執行結果
        """
        print(f"\n執行動作：{action}")
        print(f"參數：{parameters}")

        if action == "none" or action not in self.tools:
            return {"success": False, "error": "無效動作"}

        try:
            # 調用工具
            tool = self.tools[action]
            result = tool(**parameters)

            # 記錄到記憶
            self.memory.append({
                "type": "action",
                "action": action,
                "parameters": parameters,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })

            return result

        except Exception as e:
            return {"success": False, "error": str(e)}

    def evaluate(self, result: Dict[str, Any]) -> bool:
        """
        評估結果

        Args:
            result: 執行結果

        Returns:
            是否成功
        """
        if not result.get("success", False):
            print(f"執行失敗：{result.get('error', '未知錯誤')}")
            return False

        print(f"執行成功：{result.get('message', '')}")
        return True

    def reflect(self):
        """自我反思"""
        # 檢查是否陷入循環
        if self._detect_loop():
            print("警告：檢測到重複行為，嘗試調整策略")

        # 評估進度
        progress = len(self.completed_tasks) / len(self.goals) if self.goals else 0
        print(f"當前進度：{progress * 100:.1f}%")

    def _detect_loop(self) -> bool:
        """檢測是否陷入循環"""
        if len(self.memory) < 6:
            return False

        # 檢查最近的動作
        recent = [m for m in self.memory[-6:] if m["type"] == "action"]
        actions = [m["action"] for m in recent]

        # 如果最近 3 個動作相同，可能是循環
        if len(actions) >= 3 and len(set(actions[-3:])) == 1:
            return True

        return False

    def is_goal_achieved(self) -> bool:
        """檢查目標是否達成"""
        # 簡化版：如果完成了所有目標，則達成
        return len(self.completed_tasks) >= len(self.goals)

    def run(self):
        """運行 Agent 主循環"""
        print(f"\n{'='*60}")
        print(f"啟動自主 Agent：{self.name}")
        print(f"角色：{self.role}")
        print(f"{'='*60}\n")

        print("目標：")
        for i, goal in enumerate(self.goals, 1):
            print(f"{i}. {goal}")
        print()

        while self.iteration < self.max_iterations:
            self.iteration += 1
            print(f"\n--- 迭代 {self.iteration} ---")

            # 檢查預算
            if self.current_cost >= self.max_cost:
                print(f"已達成本上限：${self.current_cost:.4f}")
                break

            # 1. 思考
            thought = self.think()
            print(f"推理：{thought.get('reasoning', '')}")

            # 2. 執行
            action = thought.get("action", "none")
            parameters = thought.get("parameters", {})
            result = self.execute(action, parameters)

            # 3. 評估
            success = self.evaluate(result)
            if success and action != "none":
                self.completed_tasks.append(f"{action} 成功")

            # 4. 反思
            self.reflect()

            # 5. 檢查目標
            if self.is_goal_achieved():
                print("\n所有目標已達成！")
                break

        # 生成報告
        self.generate_report()

    def generate_report(self):
        """生成執行報告"""
        print(f"\n{'='*60}")
        print("執行報告")
        print(f"{'='*60}")
        print(f"Agent 名稱：{self.name}")
        print(f"總迭代次數：{self.iteration}")
        print(f"完成任務數：{len(self.completed_tasks)}")
        print(f"總成本：${self.current_cost:.4f}")
        print(f"\n已完成的任務：")
        for task in self.completed_tasks:
            print(f"  - {task}")
        print(f"{'='*60}\n")

    # ===== 工具實現 =====

    def tool_search(self, query: str) -> Dict[str, Any]:
        """搜索工具（模擬）"""
        print(f"搜索：{query}")
        # 實際應用中，這裡會調用真實的搜索 API
        return {
            "success": True,
            "message": f"找到關於 '{query}' 的結果",
            "results": [
                f"{query} 相關資源 1",
                f"{query} 相關資源 2",
            ]
        }

    def tool_write_file(self, filename: str, content: str) -> Dict[str, Any]:
        """寫入文件工具"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            return {
                "success": True,
                "message": f"已寫入文件：{filename}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def tool_read_file(self, filename: str) -> Dict[str, Any]:
        """讀取文件工具"""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "success": True,
                "message": f"已讀取文件：{filename}",
                "content": content
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def tool_analyze(self, data: str) -> Dict[str, Any]:
        """分析工具（模擬）"""
        print(f"分析數據：{data}")
        return {
            "success": True,
            "message": "分析完成",
            "analysis": f"關於 '{data}' 的分析結果"
        }


def main():
    """主函數"""
    print("AutoGPT 自主 Agent 示例\n")

    # 創建自主 Agent
    agent = AutonomousAgent(
        name="研究助手",
        role="AI 研究員",
        goals=[
            "搜索關於 AI Agent 的信息",
            "分析收集到的信息",
            "生成研究報告"
        ],
        max_iterations=10,  # 限制迭代次數以控制成本
        max_cost=1.0        # 限制最大成本
    )

    # 運行 Agent
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n用戶中斷執行")
        agent.generate_report()
    except Exception as e:
        print(f"\n發生錯誤：{e}")
        agent.generate_report()


if __name__ == "__main__":
    main()
