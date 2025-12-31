"""
Agent-S 經驗學習模組

此模組展示 Agent-S 如何從執行經驗中學習和改進：
1. 經驗收集 - 記錄任務執行的詳細信息
2. 模式識別 - 識別成功和失敗的模式
3. 策略優化 - 基於經驗優化執行策略
4. 知識累積 - 構建和更新知識庫

Agent-S 使用經驗回放和元學習技術來提升性能。
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import json
import random
from collections import defaultdict, Counter


class ExperienceType(Enum):
    """經驗類型"""
    SUCCESS = "成功"
    FAILURE = "失敗"
    PARTIAL = "部分成功"


class LearningStrategy(Enum):
    """學習策略"""
    REINFORCEMENT = "強化學習"
    IMITATION = "模仿學習"
    CASE_BASED = "案例學習"
    META_LEARNING = "元學習"


@dataclass
class ActionRecord:
    """操作記錄"""
    action_type: str
    parameters: Dict[str, Any]
    timestamp: datetime
    success: bool
    duration: float  # 執行時長（秒）
    error_message: Optional[str] = None


@dataclass
class Experience:
    """
    經驗記錄

    包含一次任務執行的完整信息
    """
    experience_id: str
    task_type: str
    task_description: str
    context: Dict[str, Any]  # 執行上下文（環境狀態、輸入等）
    actions: List[ActionRecord]  # 執行的操作序列
    result: ExperienceType
    outcome: Dict[str, Any]  # 執行結果
    metrics: Dict[str, float]  # 性能指標
    timestamp: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """轉換為字典"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['result'] = self.result.value
        for i, action in enumerate(data['actions']):
            action['timestamp'] = self.actions[i].timestamp.isoformat()
        return data

    def get_success_rate(self) -> float:
        """計算操作成功率"""
        if not self.actions:
            return 0.0
        successful = sum(1 for a in self.actions if a.success)
        return successful / len(self.actions)


@dataclass
class Pattern:
    """
    識別出的模式

    表示一種常見的成功或失敗模式
    """
    pattern_id: str
    pattern_type: str  # "success" 或 "failure"
    task_type: str
    conditions: Dict[str, Any]  # 觸發條件
    action_sequence: List[Dict[str, Any]]  # 操作序列模式
    confidence: float  # 置信度
    occurrences: int = 0  # 出現次數

    def matches(self, experience: Experience) -> bool:
        """檢查經驗是否匹配此模式"""
        # 簡化的模式匹配
        if experience.task_type != self.task_type:
            return False

        # 檢查條件匹配
        for key, value in self.conditions.items():
            if key not in experience.context:
                return False
            if experience.context[key] != value:
                return False

        return True


@dataclass
class Strategy:
    """執行策略"""
    strategy_id: str
    name: str
    description: str
    task_type: str
    steps: List[Dict[str, Any]]
    success_count: int = 0
    failure_count: int = 0
    avg_execution_time: float = 0.0

    def get_success_rate(self) -> float:
        """獲取成功率"""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total

    def update_metrics(self, success: bool, execution_time: float):
        """更新指標"""
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        # 更新平均執行時間
        total = self.success_count + self.failure_count
        self.avg_execution_time = (
            (self.avg_execution_time * (total - 1) + execution_time) / total
        )


class ExperienceMemory:
    """
    經驗記憶庫

    存儲和檢索過去的執行經驗
    """

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.experiences: List[Experience] = []
        self.index_by_type: Dict[str, List[str]] = defaultdict(list)
        self.index_by_result: Dict[ExperienceType, List[str]] = defaultdict(list)

    def add(self, experience: Experience):
        """添加經驗"""
        # 如果超過容量，移除最舊的經驗
        if len(self.experiences) >= self.max_size:
            old_exp = self.experiences.pop(0)
            self._remove_from_index(old_exp)

        self.experiences.append(experience)

        # 更新索引
        self.index_by_type[experience.task_type].append(experience.experience_id)
        self.index_by_result[experience.result].append(experience.experience_id)

    def _remove_from_index(self, experience: Experience):
        """從索引中移除"""
        self.index_by_type[experience.task_type].remove(experience.experience_id)
        self.index_by_result[experience.result].remove(experience.experience_id)

    def get_by_type(self, task_type: str) -> List[Experience]:
        """按任務類型檢索"""
        ids = self.index_by_type.get(task_type, [])
        return [exp for exp in self.experiences if exp.experience_id in ids]

    def get_successful(self, task_type: Optional[str] = None) -> List[Experience]:
        """獲取成功的經驗"""
        exps = [exp for exp in self.experiences if exp.result == ExperienceType.SUCCESS]
        if task_type:
            exps = [exp for exp in exps if exp.task_type == task_type]
        return exps

    def get_failed(self, task_type: Optional[str] = None) -> List[Experience]:
        """獲取失敗的經驗"""
        exps = [exp for exp in self.experiences if exp.result == ExperienceType.FAILURE]
        if task_type:
            exps = [exp for exp in exps if exp.task_type == task_type]
        return exps

    def get_similar(self, context: Dict[str, Any], task_type: str, k: int = 5) -> List[Experience]:
        """找到相似的經驗"""
        candidates = self.get_by_type(task_type)

        # 計算相似度（簡化版本）
        similarities = []
        for exp in candidates:
            similarity = self._calculate_similarity(context, exp.context)
            similarities.append((exp, similarity))

        # 排序並返回前 k 個
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [exp for exp, _ in similarities[:k]]

    def _calculate_similarity(self, ctx1: Dict, ctx2: Dict) -> float:
        """計算上下文相似度"""
        common_keys = set(ctx1.keys()) & set(ctx2.keys())
        if not common_keys:
            return 0.0

        matches = sum(1 for key in common_keys if ctx1[key] == ctx2[key])
        return matches / len(common_keys)


class PatternRecognizer:
    """
    模式識別器

    從經驗中識別成功和失敗的模式
    """

    def __init__(self):
        self.patterns: List[Pattern] = []

    def analyze_experiences(self, experiences: List[Experience]) -> List[Pattern]:
        """分析經驗並識別模式"""
        print(f"\n分析 {len(experiences)} 條經驗...")

        # 按任務類型和結果分組
        groups = defaultdict(list)
        for exp in experiences:
            key = (exp.task_type, exp.result)
            groups[key].append(exp)

        new_patterns = []

        for (task_type, result), exps in groups.items():
            if len(exps) < 2:  # 至少需要 2 個樣本
                continue

            print(f"\n分析 {task_type} - {result.value} ({len(exps)} 個樣本)")

            # 尋找共同的上下文特徵
            common_conditions = self._find_common_conditions(exps)

            # 尋找共同的操作序列
            common_sequence = self._find_common_sequence(exps)

            if common_conditions or common_sequence:
                pattern = Pattern(
                    pattern_id=f"P_{len(self.patterns) + len(new_patterns) + 1}",
                    pattern_type="success" if result == ExperienceType.SUCCESS else "failure",
                    task_type=task_type,
                    conditions=common_conditions,
                    action_sequence=common_sequence,
                    confidence=len(exps) / len(experiences),
                    occurrences=len(exps)
                )
                new_patterns.append(pattern)

                print(f"  發現模式: {pattern.pattern_id}")
                print(f"  條件: {common_conditions}")
                print(f"  置信度: {pattern.confidence:.2%}")

        self.patterns.extend(new_patterns)
        return new_patterns

    def _find_common_conditions(self, experiences: List[Experience]) -> Dict[str, Any]:
        """找到共同的上下文條件"""
        if not experiences:
            return {}

        # 統計每個 key-value 對的出現次數
        condition_counts = defaultdict(int)

        for exp in experiences:
            for key, value in exp.context.items():
                # 只考慮簡單類型
                if isinstance(value, (str, int, bool, float)):
                    condition_counts[(key, value)] += 1

        # 選擇出現在大多數經驗中的條件
        threshold = len(experiences) * 0.7  # 70% 的經驗中出現
        common = {}

        for (key, value), count in condition_counts.items():
            if count >= threshold:
                common[key] = value

        return common

    def _find_common_sequence(self, experiences: List[Experience]) -> List[Dict[str, Any]]:
        """找到共同的操作序列"""
        if not experiences:
            return []

        # 提取所有操作序列
        sequences = []
        for exp in experiences:
            sequence = [{"type": a.action_type, "params": a.parameters} for a in exp.actions]
            sequences.append(sequence)

        # 找到最長公共子序列（簡化版）
        if not sequences:
            return []

        # 這裡使用簡化方法：找出現最頻繁的操作類型序列
        action_type_sequences = [
            tuple(a["type"] for a in seq) for seq in sequences
        ]

        most_common = Counter(action_type_sequences).most_common(1)
        if not most_common:
            return []

        common_types = most_common[0][0]

        # 構建操作序列
        return [{"type": t, "params": {}} for t in common_types]

    def match_pattern(self, experience: Experience) -> Optional[Pattern]:
        """匹配經驗到已知模式"""
        for pattern in self.patterns:
            if pattern.matches(experience):
                return pattern
        return None


class LearningAgent:
    """
    學習代理

    整合經驗記憶、模式識別和策略優化
    """

    def __init__(self):
        self.memory = ExperienceMemory()
        self.recognizer = PatternRecognizer()
        self.strategies: Dict[str, List[Strategy]] = defaultdict(list)
        self.learning_stats = {
            "total_experiences": 0,
            "patterns_learned": 0,
            "strategies_created": 0,
            "strategies_improved": 0
        }

    def record_experience(self, experience: Experience):
        """記錄新經驗"""
        self.memory.add(experience)
        self.learning_stats["total_experiences"] += 1

        print(f"\n記錄經驗: {experience.experience_id}")
        print(f"  任務類型: {experience.task_type}")
        print(f"  結果: {experience.result.value}")
        print(f"  成功率: {experience.get_success_rate():.2%}")

        # 定期分析和學習
        if self.learning_stats["total_experiences"] % 10 == 0:
            self.learn_from_experiences()

    def learn_from_experiences(self):
        """從經驗中學習"""
        print("\n" + "="*60)
        print("開始學習...")
        print("="*60)

        # 分析所有經驗
        all_experiences = self.memory.experiences

        # 識別模式
        new_patterns = self.recognizer.analyze_experiences(all_experiences)
        self.learning_stats["patterns_learned"] += len(new_patterns)

        # 從成功模式生成或改進策略
        for pattern in new_patterns:
            if pattern.pattern_type == "success":
                self._create_or_update_strategy(pattern)

        print(f"\n學習完成！")
        print(f"  新模式: {len(new_patterns)}")
        print(f"  總模式: {len(self.recognizer.patterns)}")
        print(f"  總策略: {sum(len(s) for s in self.strategies.values())}")

    def _create_or_update_strategy(self, pattern: Pattern):
        """從模式創建或更新策略"""
        # 檢查是否已有類似策略
        existing = self.strategies.get(pattern.task_type, [])

        for strategy in existing:
            # 簡化比較：檢查步驟是否相似
            if len(strategy.steps) == len(pattern.action_sequence):
                # 更新現有策略
                strategy.success_count += pattern.occurrences
                self.learning_stats["strategies_improved"] += 1
                print(f"  更新策略: {strategy.name}")
                return

        # 創建新策略
        strategy = Strategy(
            strategy_id=f"S_{pattern.task_type}_{len(existing) + 1}",
            name=f"{pattern.task_type} 策略 {len(existing) + 1}",
            description=f"基於模式 {pattern.pattern_id} 的策略",
            task_type=pattern.task_type,
            steps=pattern.action_sequence,
            success_count=pattern.occurrences
        )

        self.strategies[pattern.task_type].append(strategy)
        self.learning_stats["strategies_created"] += 1

        print(f"  創建新策略: {strategy.name}")

    def recommend_strategy(self, task_type: str, context: Dict[str, Any]) -> Optional[Strategy]:
        """為任務推薦最佳策略"""
        candidates = self.strategies.get(task_type, [])

        if not candidates:
            print(f"沒有找到 {task_type} 的策略")
            return None

        # 選擇成功率最高的策略
        best = max(candidates, key=lambda s: s.get_success_rate())

        print(f"\n推薦策略: {best.name}")
        print(f"  成功率: {best.get_success_rate():.2%}")
        print(f"  平均執行時間: {best.avg_execution_time:.2f}秒")

        return best

    def get_learning_insights(self) -> Dict[str, Any]:
        """獲取學習洞察"""
        insights = {
            "統計": self.learning_stats,
            "經驗庫大小": len(self.memory.experiences),
            "已識別模式": len(self.recognizer.patterns),
            "策略數量": {
                task_type: len(strategies)
                for task_type, strategies in self.strategies.items()
            },
            "最佳策略": {}
        }

        # 找出每種任務類型的最佳策略
        for task_type, strategies in self.strategies.items():
            if strategies:
                best = max(strategies, key=lambda s: s.get_success_rate())
                insights["最佳策略"][task_type] = {
                    "名稱": best.name,
                    "成功率": best.get_success_rate(),
                    "使用次數": best.success_count + best.failure_count
                }

        return insights


def 示例1_記錄和學習經驗():
    """示例：記錄執行經驗並學習"""
    print("\n" + "="*60)
    print("示例 1: 記錄和學習經驗")
    print("="*60)

    agent = LearningAgent()

    # 模擬記錄多次網頁瀏覽任務
    for i in range(5):
        # 成功的經驗
        exp = Experience(
            experience_id=f"EXP_{i+1}",
            task_type="網頁瀏覽",
            task_description="訪問新聞網站並閱讀文章",
            context={
                "browser": "Chrome",
                "url": "https://news.example.com",
                "network": "WiFi"
            },
            actions=[
                ActionRecord("open_browser", {"browser": "Chrome"}, datetime.now(), True, 1.5),
                ActionRecord("navigate", {"url": "https://news.example.com"}, datetime.now(), True, 2.0),
                ActionRecord("click", {"element": "article_link"}, datetime.now(), True, 0.5),
                ActionRecord("read", {}, datetime.now(), True, 10.0),
            ],
            result=ExperienceType.SUCCESS,
            outcome={"articles_read": 1},
            metrics={"total_time": 14.0, "success_rate": 1.0}
        )
        agent.record_experience(exp)

    # 一些失敗的經驗
    for i in range(3):
        exp = Experience(
            experience_id=f"EXP_FAIL_{i+1}",
            task_type="網頁瀏覽",
            task_description="訪問新聞網站但失敗",
            context={
                "browser": "Firefox",
                "url": "https://news.example.com",
                "network": "Mobile Data"
            },
            actions=[
                ActionRecord("open_browser", {"browser": "Firefox"}, datetime.now(), True, 2.0),
                ActionRecord("navigate", {"url": "https://news.example.com"}, datetime.now(), False, 0.5,
                           "Timeout"),
            ],
            result=ExperienceType.FAILURE,
            outcome={},
            metrics={"total_time": 2.5, "success_rate": 0.5}
        )
        agent.record_experience(exp)

    # 觸發學習
    agent.learn_from_experiences()

    # 顯示學習成果
    insights = agent.get_learning_insights()
    print("\n學習洞察:")
    print(json.dumps(insights, indent=2, ensure_ascii=False))

    return agent


def 示例2_策略推薦():
    """示例：基於學習推薦執行策略"""
    print("\n" + "="*60)
    print("示例 2: 策略推薦")
    print("="*60)

    # 使用示例1的 agent
    agent = 示例1_記錄和學習經驗()

    # 為新任務請求策略推薦
    print("\n請求策略推薦...")
    strategy = agent.recommend_strategy(
        task_type="網頁瀏覽",
        context={
            "browser": "Chrome",
            "url": "https://news.example.com"
        }
    )

    if strategy:
        print("\n推薦的執行步驟:")
        for i, step in enumerate(strategy.steps, 1):
            print(f"  {i}. {step['type']}")

    return strategy


def 示例3_相似經驗檢索():
    """示例：檢索相似的歷史經驗"""
    print("\n" + "="*60)
    print("示例 3: 相似經驗檢索")
    print("="*60)

    agent = LearningAgent()

    # 添加各種經驗
    experiences_data = [
        ("文件編輯", {"editor": "VSCode", "file_type": "py"}, ExperienceType.SUCCESS),
        ("文件編輯", {"editor": "VSCode", "file_type": "js"}, ExperienceType.SUCCESS),
        ("文件編輯", {"editor": "Notepad", "file_type": "txt"}, ExperienceType.SUCCESS),
        ("文件編輯", {"editor": "Word", "file_type": "docx"}, ExperienceType.FAILURE),
    ]

    for i, (task_type, context, result) in enumerate(experiences_data):
        exp = Experience(
            experience_id=f"EXP_{i+1}",
            task_type=task_type,
            task_description=f"{task_type} 任務",
            context=context,
            actions=[ActionRecord("edit", {}, datetime.now(), result == ExperienceType.SUCCESS, 5.0)],
            result=result,
            outcome={},
            metrics={}
        )
        agent.memory.add(exp)

    # 查找相似經驗
    query_context = {"editor": "VSCode", "file_type": "py"}
    print(f"\n查詢上下文: {query_context}")

    similar = agent.memory.get_similar(query_context, "文件編輯", k=3)

    print(f"\n找到 {len(similar)} 個相似經驗:")
    for exp in similar:
        print(f"  - {exp.experience_id}: {exp.context} -> {exp.result.value}")

    return similar


def 示例4_性能改進追蹤():
    """示例：追蹤學習帶來的性能改進"""
    print("\n" + "="*60)
    print("示例 4: 性能改進追蹤")
    print("="*60)

    agent = LearningAgent()

    # 模擬多輪學習
    task_type = "數據處理"
    rounds = 5

    for round_num in range(rounds):
        print(f"\n第 {round_num + 1} 輪:")

        # 初期成功率較低，隨著學習逐漸提高
        success_prob = 0.3 + (round_num * 0.15)

        for i in range(10):
            is_success = random.random() < success_prob

            exp = Experience(
                experience_id=f"R{round_num}_EXP_{i}",
                task_type=task_type,
                task_description="處理數據文件",
                context={"format": "csv", "size": "large"},
                actions=[
                    ActionRecord("load", {}, datetime.now(), is_success, 2.0),
                    ActionRecord("process", {}, datetime.now(), is_success, 5.0),
                    ActionRecord("save", {}, datetime.now(), is_success, 1.0),
                ],
                result=ExperienceType.SUCCESS if is_success else ExperienceType.FAILURE,
                outcome={"processed": is_success},
                metrics={"time": 8.0 if is_success else 2.0}
            )
            agent.record_experience(exp)

        # 學習
        agent.learn_from_experiences()

        # 評估當前性能
        recent_exps = agent.memory.experiences[-10:]
        success_count = sum(1 for e in recent_exps if e.result == ExperienceType.SUCCESS)
        print(f"  本輪成功率: {success_count/10:.2%}")

    # 顯示最終學習成果
    print("\n" + "="*60)
    print("最終學習成果:")
    print("="*60)

    insights = agent.get_learning_insights()
    print(f"總經驗數: {insights['統計']['total_experiences']}")
    print(f"識別模式數: {insights['統計']['patterns_learned']}")
    print(f"創建策略數: {insights['統計']['strategies_created']}")

    # 計算整體改進
    first_10 = agent.memory.experiences[:10]
    last_10 = agent.memory.experiences[-10:]

    first_success = sum(1 for e in first_10 if e.result == ExperienceType.SUCCESS) / 10
    last_success = sum(1 for e in last_10 if e.result == ExperienceType.SUCCESS) / 10

    print(f"\n性能改進:")
    print(f"  初期成功率: {first_success:.2%}")
    print(f"  最終成功率: {last_success:.2%}")
    print(f"  提升: {(last_success - first_success):.2%}")

    return agent


if __name__ == "__main__":
    print("Agent-S 經驗學習演示\n")

    示例1_記錄和學習經驗()
    示例2_策略推薦()
    示例3_相似經驗檢索()
    示例4_性能改進追蹤()

    print("\n所有示例執行完成！")
