"""
Letta 自定義 Persona 系統

本模組展示如何為 Letta Agent 創建自定義人格：
1. Persona 模板設計
2. 動態人格調整
3. 情境感知的人格
4. 多人格 Agent
5. 人格一致性維護
6. 個性化對話風格

讓 Agent 具有獨特的個性和對話風格。

作者：Letta 框架示例
日期：2025-01
"""

import os
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import random


class PersonalityTrait(Enum):
    """性格特質"""
    FRIENDLY = "友善"
    PROFESSIONAL = "專業"
    HUMOROUS = "幽默"
    EMPATHETIC = "同理心"
    ANALYTICAL = "分析型"
    CREATIVE = "創造性"
    PATIENT = "耐心"
    ENTHUSIASTIC = "熱情"


class CommunicationStyle(Enum):
    """溝通風格"""
    FORMAL = "正式"
    CASUAL = "隨意"
    TECHNICAL = "技術性"
    SIMPLE = "簡單"
    DETAILED = "詳細"
    CONCISE = "簡潔"


@dataclass
class PersonaTemplate:
    """Persona 模板"""
    name: str
    description: str
    traits: List[PersonalityTrait]
    communication_style: CommunicationStyle
    background: str
    expertise: List[str]
    language_patterns: Dict[str, List[str]]
    values: List[str]
    goals: List[str]
    constraints: List[str] = field(default_factory=list)


@dataclass
class PersonaState:
    """Persona 狀態"""
    current_mood: str = "中性"
    energy_level: int = 5  # 1-10
    engagement_level: int = 5  # 1-10
    context_awareness: Dict[str, Any] = field(default_factory=dict)
    interaction_count: int = 0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class PersonaBuilder:
    """
    Persona 構建器

    幫助創建和自定義 Agent Persona。
    """

    def __init__(self):
        """初始化 Persona 構建器"""
        self.template = None
        print("Persona 構建器初始化完成")

    def create_template(self, name: str, description: str) -> 'PersonaBuilder':
        """
        創建 Persona 模板

        參數:
            name: Persona 名稱
            description: 描述

        返回:
            self（鏈式調用）
        """
        self.template = PersonaTemplate(
            name=name,
            description=description,
            traits=[],
            communication_style=CommunicationStyle.CASUAL,
            background="",
            expertise=[],
            language_patterns={},
            values=[],
            goals=[]
        )

        print(f"\n[Persona 模板] 創建: {name}")

        return self

    def add_trait(self, trait: PersonalityTrait) -> 'PersonaBuilder':
        """添加性格特質"""
        if self.template:
            self.template.traits.append(trait)
            print(f"  添加特質: {trait.value}")
        return self

    def set_communication_style(self, style: CommunicationStyle) -> 'PersonaBuilder':
        """設置溝通風格"""
        if self.template:
            self.template.communication_style = style
            print(f"  溝通風格: {style.value}")
        return self

    def set_background(self, background: str) -> 'PersonaBuilder':
        """設置背景"""
        if self.template:
            self.template.background = background
            print(f"  背景: {background[:50]}...")
        return self

    def add_expertise(self, expertise: str) -> 'PersonaBuilder':
        """添加專業領域"""
        if self.template:
            self.template.expertise.append(expertise)
            print(f"  專長: {expertise}")
        return self

    def add_language_pattern(self, pattern_type: str, patterns: List[str]) -> 'PersonaBuilder':
        """添加語言模式"""
        if self.template:
            self.template.language_patterns[pattern_type] = patterns
            print(f"  語言模式 ({pattern_type}): {len(patterns)} 個")
        return self

    def add_value(self, value: str) -> 'PersonaBuilder':
        """添加價值觀"""
        if self.template:
            self.template.values.append(value)
            print(f"  價值觀: {value}")
        return self

    def add_goal(self, goal: str) -> 'PersonaBuilder':
        """添加目標"""
        if self.template:
            self.template.goals.append(goal)
            print(f"  目標: {goal}")
        return self

    def add_constraint(self, constraint: str) -> 'PersonaBuilder':
        """添加約束"""
        if self.template:
            self.template.constraints.append(constraint)
            print(f"  約束: {constraint}")
        return self

    def build(self) -> PersonaTemplate:
        """構建並返回 Persona 模板"""
        if self.template:
            print(f"\n✓ Persona '{self.template.name}' 構建完成")
            return self.template
        raise ValueError("未創建模板")


class PersonaEngine:
    """
    Persona 引擎

    管理 Agent 的人格表現。
    """

    def __init__(self, template: PersonaTemplate):
        """
        初始化 Persona 引擎

        參數:
            template: Persona 模板
        """
        self.template = template
        self.state = PersonaState()

        print(f"\nPersona 引擎初始化: {template.name}")

    def generate_system_prompt(self) -> str:
        """
        生成系統提示詞

        返回:
            系統提示詞
        """
        prompt_parts = [
            f"你是 {self.template.name}。",
            f"{self.template.description}",
            f"\n背景：{self.template.background}",
        ]

        # 性格特質
        if self.template.traits:
            traits_str = "、".join([t.value for t in self.template.traits])
            prompt_parts.append(f"\n你的性格特質：{traits_str}。")

        # 專業領域
        if self.template.expertise:
            expertise_str = "、".join(self.template.expertise)
            prompt_parts.append(f"\n你的專業領域：{expertise_str}。")

        # 溝通風格
        prompt_parts.append(f"\n你的溝通風格是{self.template.communication_style.value}的。")

        # 價值觀
        if self.template.values:
            values_str = "、".join(self.template.values)
            prompt_parts.append(f"\n你重視：{values_str}。")

        # 目標
        if self.template.goals:
            goals_str = "\n- ".join(self.template.goals)
            prompt_parts.append(f"\n你的目標：\n- {goals_str}")

        # 約束
        if self.template.constraints:
            constraints_str = "\n- ".join(self.template.constraints)
            prompt_parts.append(f"\n你的行為約束：\n- {constraints_str}")

        prompt = "".join(prompt_parts)

        print("\n[系統提示詞生成]")
        print("-" * 60)
        print(prompt)
        print("-" * 60)

        return prompt

    def adjust_response(self, base_response: str) -> str:
        """
        根據 Persona 調整響應

        參數:
            base_response: 基礎響應

        返回:
            調整後的響應
        """
        response = base_response

        # 根據溝通風格調整
        if self.template.communication_style == CommunicationStyle.FORMAL:
            response = self._formalize_response(response)
        elif self.template.communication_style == CommunicationStyle.CASUAL:
            response = self._casualize_response(response)

        # 根據特質添加語言模式
        response = self._apply_language_patterns(response)

        # 更新狀態
        self.state.interaction_count += 1

        return response

    def _formalize_response(self, response: str) -> str:
        """正式化響應"""
        # 添加正式的開場和結束
        if "您" not in response:
            response = response.replace("你", "您")
        return response

    def _casualize_response(self, response: str) -> str:
        """隨意化響應"""
        # 添加隨意的語氣詞
        casual_additions = ["呢", "哦", "啦"]
        if random.random() > 0.5:
            response += random.choice(casual_additions)
        return response

    def _apply_language_patterns(self, response: str) -> str:
        """應用語言模式"""
        # 根據特質添加特定的語言模式
        if PersonalityTrait.FRIENDLY in self.template.traits:
            if "greetings" in self.template.language_patterns:
                # 可能添加友善的問候
                pass

        if PersonalityTrait.ENTHUSIASTIC in self.template.traits:
            # 添加感嘆號
            if random.random() > 0.5:
                response = response.rstrip("。") + "！"

        return response

    def update_state(self, context: Dict[str, Any]) -> None:
        """
        更新 Persona 狀態

        參數:
            context: 上下文信息
        """
        self.state.context_awareness.update(context)

        # 根據交互次數調整參與度
        if self.state.interaction_count > 10:
            self.state.engagement_level = min(10, self.state.engagement_level + 1)

        self.state.last_updated = datetime.now().isoformat()


class MultiPersonaAgent:
    """
    多人格 Agent

    支持在不同情境下切換人格。
    """

    def __init__(self, agent_id: str):
        """
        初始化多人格 Agent

        參數:
            agent_id: Agent ID
        """
        self.agent_id = agent_id
        self.personas: Dict[str, PersonaEngine] = {}
        self.current_persona: Optional[str] = None
        self.context_rules: Dict[str, str] = {}

        print(f"\n多人格 Agent 創建: {agent_id}")

    def add_persona(self, persona_name: str, engine: PersonaEngine) -> None:
        """
        添加人格

        參數:
            persona_name: 人格名稱
            engine: Persona 引擎
        """
        self.personas[persona_name] = engine
        if self.current_persona is None:
            self.current_persona = persona_name

        print(f"[{self.agent_id}] 添加人格: {persona_name}")

    def switch_persona(self, persona_name: str) -> None:
        """
        切換人格

        參數:
            persona_name: 人格名稱
        """
        if persona_name in self.personas:
            old_persona = self.current_persona
            self.current_persona = persona_name
            print(f"\n[{self.agent_id}] 人格切換: {old_persona} -> {persona_name}")
        else:
            print(f"[錯誤] 人格 '{persona_name}' 不存在")

    def add_context_rule(self, context_key: str, persona_name: str) -> None:
        """
        添加上下文規則

        當檢測到特定上下文時，自動切換人格。

        參數:
            context_key: 上下文關鍵詞
            persona_name: 對應的人格名稱
        """
        self.context_rules[context_key] = persona_name
        print(f"[{self.agent_id}] 上下文規則: '{context_key}' -> {persona_name}")

    def auto_switch_persona(self, message: str) -> None:
        """
        根據消息內容自動切換人格

        參數:
            message: 用戶消息
        """
        for context_key, persona_name in self.context_rules.items():
            if context_key.lower() in message.lower():
                self.switch_persona(persona_name)
                return

    def respond(self, message: str) -> str:
        """
        響應消息

        參數:
            message: 用戶消息

        返回:
            Agent 響應
        """
        # 自動切換人格
        self.auto_switch_persona(message)

        # 使用當前人格響應
        if self.current_persona and self.current_persona in self.personas:
            engine = self.personas[self.current_persona]

            # 生成基礎響應（簡化版）
            base_response = f"收到你的消息：{message}"

            # 根據人格調整響應
            response = engine.adjust_response(base_response)

            print(f"\n[{self.agent_id}] ({self.current_persona}): {response}")

            return response

        return "無法響應"


def create_professional_persona() -> PersonaTemplate:
    """創建專業型 Persona"""
    print("\n" + "=" * 60)
    print("創建專業型 Persona")
    print("=" * 60)

    builder = PersonaBuilder()

    persona = (builder
               .create_template(
                   "專業顧問",
                   "一位經驗豐富的技術顧問，專注於提供準確、專業的建議"
               )
               .add_trait(PersonalityTrait.PROFESSIONAL)
               .add_trait(PersonalityTrait.ANALYTICAL)
               .add_trait(PersonalityTrait.PATIENT)
               .set_communication_style(CommunicationStyle.FORMAL)
               .set_background(
                   "擁有 15 年的軟件開發和架構設計經驗，曾在多家頂級科技公司工作"
               )
               .add_expertise("軟件架構")
               .add_expertise("系統設計")
               .add_expertise("技術諮詢")
               .add_value("準確性")
               .add_value("專業性")
               .add_value("客戶滿意度")
               .add_goal("提供精確的技術解決方案")
               .add_goal("幫助客戶做出明智的技術決策")
               .add_constraint("始終保持專業態度")
               .add_constraint("避免過度承諾")
               .build())

    return persona


def create_friendly_assistant_persona() -> PersonaTemplate:
    """創建友善助手 Persona"""
    print("\n" + "=" * 60)
    print("創建友善助手 Persona")
    print("=" * 60)

    builder = PersonaBuilder()

    persona = (builder
               .create_template(
                   "友善助手",
                   "一位親切友好的 AI 助手，總是樂於幫助"
               )
               .add_trait(PersonalityTrait.FRIENDLY)
               .add_trait(PersonalityTrait.EMPATHETIC)
               .add_trait(PersonalityTrait.ENTHUSIASTIC)
               .set_communication_style(CommunicationStyle.CASUAL)
               .set_background(
                   "訓練有素的 AI 助手，擅長理解用戶需求並提供貼心幫助"
               )
               .add_expertise("日常協助")
               .add_expertise("問題解答")
               .add_expertise("情感支持")
               .add_language_pattern("greetings", [
                   "你好呀！",
                   "嗨！很高興見到你！",
                   "歡迎回來！"
               ])
               .add_language_pattern("encouragement", [
                   "你做得很好！",
                   "繼續加油！",
                   "我相信你！"
               ])
               .add_value("同理心")
               .add_value("友善")
               .add_value("可靠性")
               .add_goal("讓用戶感到被理解和支持")
               .add_goal("提供溫暖的互動體驗")
               .build())

    return persona


def create_creative_persona() -> PersonaTemplate:
    """創建創意型 Persona"""
    print("\n" + "=" * 60)
    print("創建創意型 Persona")
    print("=" * 60)

    builder = PersonaBuilder()

    persona = (builder
               .create_template(
                   "創意大師",
                   "充滿創造力的思想家，總能提供獨特的視角"
               )
               .add_trait(PersonalityTrait.CREATIVE)
               .add_trait(PersonalityTrait.ENTHUSIASTIC)
               .add_trait(PersonalityTrait.HUMOROUS)
               .set_communication_style(CommunicationStyle.CASUAL)
               .set_background(
                   "跨領域創新者，擅長將不同領域的想法結合產生新穎解決方案"
               )
               .add_expertise("創意思維")
               .add_expertise("腦力激盪")
               .add_expertise("創新方法")
               .add_value("創新")
               .add_value("開放思維")
               .add_value("勇於嘗試")
               .add_goal("激發用戶的創造力")
               .add_goal("提供非常規的解決方案")
               .add_constraint("保持想法的可行性")
               .build())

    return persona


def demonstrate_persona_engine():
    """演示 Persona 引擎"""
    print("\n" + "=" * 60)
    print("Persona 引擎演示")
    print("=" * 60)

    # 創建並使用專業顧問
    professional_template = create_professional_persona()
    professional_engine = PersonaEngine(professional_template)
    professional_engine.generate_system_prompt()

    # 調整響應
    base_response = "這個問題很有深度，讓我來分析一下"
    adjusted = professional_engine.adjust_response(base_response)
    print(f"\n原始響應: {base_response}")
    print(f"調整後: {adjusted}")


def demonstrate_multi_persona():
    """演示多人格 Agent"""
    print("\n" + "=" * 60)
    print("多人格 Agent 演示")
    print("=" * 60)

    # 創建多人格 Agent
    agent = MultiPersonaAgent("multi_agent_001")

    # 添加不同的人格
    professional = create_professional_persona()
    friendly = create_friendly_assistant_persona()
    creative = create_creative_persona()

    agent.add_persona("專業模式", PersonaEngine(professional))
    agent.add_persona("友善模式", PersonaEngine(friendly))
    agent.add_persona("創意模式", PersonaEngine(creative))

    # 設置上下文規則
    agent.add_context_rule("技術", "專業模式")
    agent.add_context_rule("聊天", "友善模式")
    agent.add_context_rule("創意", "創意模式")
    agent.add_context_rule("想法", "創意模式")

    # 測試不同情境
    print("\n" + "=" * 40)
    print("情境測試")
    print("=" * 40)

    test_messages = [
        "你好，很高興認識你！",
        "我遇到了一個技術問題，需要你的建議",
        "能幫我想一些創意的營銷策略嗎？",
        "我們來聊聊天吧",
        "關於系統架構設計，你有什麼建議？"
    ]

    for msg in test_messages:
        print(f"\n[用戶] {msg}")
        agent.respond(msg)
        time.sleep(0.5)


def demonstrate_dynamic_persona():
    """演示動態調整 Persona"""
    print("\n" + "=" * 60)
    print("動態 Persona 調整演示")
    print("=" * 60)

    # 創建基礎 Persona
    builder = PersonaBuilder()
    template = (builder
                .create_template("適應性助手", "根據用戶需求調整行為的助手")
                .add_trait(PersonalityTrait.EMPATHETIC)
                .add_trait(PersonalityTrait.PATIENT)
                .set_communication_style(CommunicationStyle.CASUAL)
                .build())

    engine = PersonaEngine(template)

    # 模擬交互並動態調整
    contexts = [
        {"user_mood": "frustrated", "topic": "technical"},
        {"user_mood": "happy", "topic": "general"},
        {"user_mood": "curious", "topic": "learning"}
    ]

    for context in contexts:
        print(f"\n[上下文] {context}")
        engine.update_state(context)

        # 根據上下文調整響應策略
        if context.get("user_mood") == "frustrated":
            print("  → Persona 調整：增加耐心和同理心")
        elif context.get("user_mood") == "happy":
            print("  → Persona 調整：保持輕鬆友好")
        elif context.get("user_mood") == "curious":
            print("  → Persona 調整：提供詳細解釋")


def demonstrate_persona_consistency():
    """演示 Persona 一致性"""
    print("\n" + "=" * 60)
    print("Persona 一致性演示")
    print("=" * 60)

    professional = create_professional_persona()
    engine = PersonaEngine(professional)

    print("\n測試多次響應的一致性：")

    test_scenarios = [
        "如何優化數據庫性能？",
        "能給我一些建議嗎？",
        "謝謝你的幫助！"
    ]

    for scenario in test_scenarios:
        print(f"\n[場景] {scenario}")
        response = engine.adjust_response(f"關於{scenario}，我建議...")
        print(f"[響應] {response}")
        time.sleep(0.5)

    # 檢查狀態
    print(f"\n[統計] 總交互次數: {engine.state.interaction_count}")
    print(f"[統計] 參與度: {engine.state.engagement_level}/10")


def main():
    """主函數：運行所有演示"""
    print("\n" + "=" * 70)
    print(" " * 20 + "Letta 自定義 Persona 系統")
    print("=" * 70)

    # Persona 引擎演示
    demonstrate_persona_engine()

    # 多人格 Agent 演示
    demonstrate_multi_persona()

    # 動態 Persona 調整
    demonstrate_dynamic_persona()

    # Persona 一致性
    demonstrate_persona_consistency()

    print("\n" + "=" * 70)
    print("自定義 Persona 演示完成！")
    print("=" * 70)
    print("\n關鍵要點：")
    print("  1. Persona 定義了 Agent 的性格和行為方式")
    print("  2. 使用構建器模式創建複雜的 Persona")
    print("  3. Persona 引擎調整響應以匹配人格")
    print("  4. 多人格 Agent 可根據情境切換")
    print("  5. 維護 Persona 一致性很重要")
    print("\n下一步：查看 08_記憶檢索.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
