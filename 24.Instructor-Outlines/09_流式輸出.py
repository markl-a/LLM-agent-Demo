"""
Instructor/Outlines 流式輸出範例
================================

本範例展示如何處理結構化數據的流式輸出。

功能：
1. 流式 JSON 生成
2. 部分對象更新
3. 流式列表生成
4. 實時進度顯示

安裝依賴：
pip install instructor openai pydantic
"""

import instructor
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Iterator
from instructor import Partial
import json
import sys
import time

# ============================================================
# 1. 基本流式輸出
# ============================================================

BASIC_STREAM_EXAMPLE = '''
import instructor
from openai import OpenAI
from pydantic import BaseModel
from instructor import Partial

client = instructor.from_openai(OpenAI())

class StoryPart(BaseModel):
    title: str
    content: str
    characters: List[str]

# 流式生成
for partial_story in client.chat.completions.create_partial(
    model="gpt-3.5-turbo",
    response_model=StoryPart,
    messages=[
        {"role": "user", "content": "寫一個短故事"}
    ],
    stream=True
):
    # partial_story 是部分填充的對象
    print(f"標題: {partial_story.title or '生成中...'}")
    print(f"內容: {partial_story.content or '生成中...'}")
'''


# ============================================================
# 2. 定義流式模型
# ============================================================

class Article(BaseModel):
    """文章模型"""
    title: str = Field(description="標題")
    summary: str = Field(description="摘要")
    sections: List[str] = Field(default_factory=list, description="章節")
    keywords: List[str] = Field(default_factory=list, description="關鍵詞")
    word_count: int = Field(default=0, description="字數")


class AnalysisReport(BaseModel):
    """分析報告"""
    topic: str
    findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    conclusion: str = ""
    confidence: float = 0.0


class ExtractedData(BaseModel):
    """提取的數據"""
    entities: List[Dict[str, str]] = Field(default_factory=list)
    relationships: List[Dict[str, str]] = Field(default_factory=list)
    summary: str = ""


# ============================================================
# 3. 流式處理器
# ============================================================

class StreamProcessor:
    """流式處理器"""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.client = instructor.from_openai(OpenAI())
        self.model = model

    def stream_generate(
        self,
        response_model: type,
        prompt: str,
        system_prompt: str = None,
        on_update: callable = None
    ):
        """流式生成"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        final_result = None

        for partial in self.client.chat.completions.create_partial(
            model=self.model,
            response_model=response_model,
            messages=messages,
            stream=True
        ):
            final_result = partial
            if on_update:
                on_update(partial)

        return final_result


STREAM_PROCESSOR_EXAMPLE = '''
# 流式處理器使用範例

def on_update(partial):
    # 清除當前行並打印更新
    sys.stdout.write("\\r" + " " * 80 + "\\r")
    if partial.title:
        sys.stdout.write(f"標題: {partial.title[:50]}...")
    sys.stdout.flush()

processor = StreamProcessor()

result = processor.stream_generate(
    response_model=Article,
    prompt="寫一篇關於 AI 的文章",
    on_update=on_update
)

print(f"\\n完成! 標題: {result.title}")
'''


# ============================================================
# 4. 流式列表生成
# ============================================================

class ListItem(BaseModel):
    """列表項"""
    id: int
    content: str
    completed: bool = False


class StreamingList(BaseModel):
    """流式列表"""
    items: List[ListItem] = Field(default_factory=list)


class StreamingListGenerator:
    """流式列表生成器"""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.client = instructor.from_openai(OpenAI())
        self.model = model

    def generate_list(
        self,
        prompt: str,
        on_item_added: callable = None
    ) -> List[ListItem]:
        """生成列表，每增加一項時觸發回調"""
        messages = [{"role": "user", "content": prompt}]
        previous_count = 0

        final_result = None

        for partial in self.client.chat.completions.create_partial(
            model=self.model,
            response_model=StreamingList,
            messages=messages,
            stream=True
        ):
            final_result = partial
            current_count = len(partial.items) if partial.items else 0

            # 檢測新項目
            if current_count > previous_count and on_item_added:
                new_items = partial.items[previous_count:]
                for item in new_items:
                    on_item_added(item)
                previous_count = current_count

        return final_result.items if final_result else []


STREAMING_LIST_EXAMPLE = '''
# 流式列表生成範例

def on_item_added(item):
    print(f"新項目: [{item.id}] {item.content}")

generator = StreamingListGenerator()

items = generator.generate_list(
    prompt="列出 5 個學習 Python 的步驟",
    on_item_added=on_item_added
)

print(f"\\n總共 {len(items)} 個項目")
'''


# ============================================================
# 5. 實時進度顯示
# ============================================================

class ProgressiveOutput:
    """漸進式輸出"""

    def __init__(self):
        self.buffer = ""
        self.field_status = {}

    def update(self, partial: BaseModel, fields: List[str] = None):
        """更新輸出"""
        if fields is None:
            fields = list(partial.model_fields.keys())

        output_lines = []
        for field in fields:
            value = getattr(partial, field, None)
            status = self._get_status(field, value)

            if isinstance(value, list):
                display = f"{len(value)} 項"
            elif isinstance(value, str):
                display = value[:50] + "..." if len(value or "") > 50 else value
            else:
                display = str(value) if value is not None else "等待中..."

            output_lines.append(f"  {field}: {display} [{status}]")

        # 清屏並顯示
        self._clear_and_print(output_lines)

    def _get_status(self, field: str, value: Any) -> str:
        """獲取字段狀態"""
        if value is None or (isinstance(value, list) and len(value) == 0):
            return "⏳"
        elif isinstance(value, str) and len(value) < 10:
            return "🔄"
        else:
            return "✓"

    def _clear_and_print(self, lines: List[str]):
        """清除並打印"""
        # 簡化版本：直接打印
        print("\033[H\033[J", end="")  # 清屏
        print("生成進度:")
        for line in lines:
            print(line)


PROGRESS_DISPLAY_EXAMPLE = '''
# 實時進度顯示範例

progress = ProgressiveOutput()

for partial in client.chat.completions.create_partial(
    model="gpt-3.5-turbo",
    response_model=Article,
    messages=[{"role": "user", "content": "寫一篇文章"}],
    stream=True
):
    progress.update(partial, ["title", "summary", "sections", "keywords"])
    time.sleep(0.1)  # 控制刷新頻率

print("\\n生成完成!")
'''


# ============================================================
# 6. 流式錯誤處理
# ============================================================

class StreamError(Exception):
    """流式處理錯誤"""
    pass


class RobustStreamProcessor:
    """健壯的流式處理器"""

    def __init__(self, model: str = "gpt-3.5-turbo", max_retries: int = 3):
        self.client = instructor.from_openai(OpenAI())
        self.model = model
        self.max_retries = max_retries

    def stream_with_retry(
        self,
        response_model: type,
        prompt: str,
        on_update: callable = None,
        on_error: callable = None
    ):
        """帶重試的流式生成"""
        last_partial = None
        attempt = 0

        while attempt < self.max_retries:
            try:
                for partial in self.client.chat.completions.create_partial(
                    model=self.model,
                    response_model=response_model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True
                ):
                    last_partial = partial
                    if on_update:
                        on_update(partial)

                return last_partial

            except Exception as e:
                attempt += 1
                if on_error:
                    on_error(e, attempt)

                if attempt >= self.max_retries:
                    raise StreamError(f"流式處理失敗: {e}")

                time.sleep(1 * attempt)

        return last_partial


ROBUST_STREAM_EXAMPLE = '''
# 健壯的流式處理範例

def on_error(error, attempt):
    print(f"錯誤 (嘗試 {attempt}): {error}")

processor = RobustStreamProcessor(max_retries=3)

try:
    result = processor.stream_with_retry(
        response_model=Article,
        prompt="寫一篇文章",
        on_update=lambda p: print(f"標題: {p.title}"),
        on_error=on_error
    )
except StreamError as e:
    print(f"最終失敗: {e}")
'''


# ============================================================
# 7. 流式到文件
# ============================================================

class StreamToFile:
    """流式輸出到文件"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.updates = []

    def on_update(self, partial: BaseModel):
        """每次更新時記錄"""
        self.updates.append({
            "timestamp": time.time(),
            "data": partial.model_dump() if hasattr(partial, 'model_dump') else dict(partial)
        })

    def save(self):
        """保存到文件"""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.updates, f, ensure_ascii=False, indent=2)


STREAM_TO_FILE_EXAMPLE = '''
# 流式輸出到文件範例

stream_logger = StreamToFile("stream_log.json")

for partial in client.chat.completions.create_partial(
    model="gpt-3.5-turbo",
    response_model=Article,
    messages=[{"role": "user", "content": "寫一篇文章"}],
    stream=True
):
    stream_logger.on_update(partial)

stream_logger.save()
print("流式日誌已保存")
'''


# ============================================================
# 使用範例
# ============================================================

def example_basic_stream():
    """範例 1: 基本流式"""
    print("=" * 50)
    print("範例 1: 基本流式輸出")
    print("=" * 50)
    print(BASIC_STREAM_EXAMPLE)


def example_stream_processor():
    """範例 2: 流式處理器"""
    print("\n" + "=" * 50)
    print("範例 2: 流式處理器")
    print("=" * 50)
    print(STREAM_PROCESSOR_EXAMPLE)


def example_streaming_list():
    """範例 3: 流式列表"""
    print("\n" + "=" * 50)
    print("範例 3: 流式列表生成")
    print("=" * 50)
    print(STREAMING_LIST_EXAMPLE)


def example_progress_display():
    """範例 4: 進度顯示"""
    print("\n" + "=" * 50)
    print("範例 4: 實時進度顯示")
    print("=" * 50)
    print(PROGRESS_DISPLAY_EXAMPLE)


def example_robust_stream():
    """範例 5: 健壯流式"""
    print("\n" + "=" * 50)
    print("範例 5: 健壯的流式處理")
    print("=" * 50)
    print(ROBUST_STREAM_EXAMPLE)


def example_stream_to_file():
    """範例 6: 流式到文件"""
    print("\n" + "=" * 50)
    print("範例 6: 流式輸出到文件")
    print("=" * 50)
    print(STREAM_TO_FILE_EXAMPLE)


def example_models():
    """範例 7: 流式模型"""
    print("\n" + "=" * 50)
    print("範例 7: 流式數據模型")
    print("=" * 50)

    print("\n定義的模型:")
    print(f"  Article: 文章（標題、摘要、章節、關鍵詞）")
    print(f"  AnalysisReport: 分析報告（主題、發現、建議）")
    print(f"  ExtractedData: 提取數據（實體、關係）")


if __name__ == "__main__":
    print("Instructor/Outlines 流式輸出範例\n")
    example_basic_stream()
    example_stream_processor()
    example_streaming_list()
    example_progress_display()
    example_robust_stream()
    example_stream_to_file()
    example_models()
