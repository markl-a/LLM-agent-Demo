"""
Mirascope 驗證器示例
運行方式：python 08_驗證器.py
"""
import os
from mirascope.openai import OpenAICall
from pydantic import validator, BaseModel, Field

class ValidatedInput(OpenAICall):
    prompt_template = "分析：{text}"
    text: str
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v.strip():
            raise ValueError("文本不能為空")
        if len(v) < 5:
            raise ValueError("文本太短")
        return v

class ValidatedOutput(BaseModel):
    title: str = Field(min_length=5, max_length=100)
    score: int = Field(ge=0, le=100)

class OutputValidator(OpenAICall):
    prompt_template = "評估：{content}"
    content: str
    call_params = {"response_model": ValidatedOutput}

def main():
    print("\\nMirascope 驗證器示例\\n")
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY")
        return
    
    print("示例 1: 輸入驗證")
    try:
        response = ValidatedInput(text="這是一段足夠長的測試文本").call()
        print(f"  ✅ 驗證通過")
    except ValueError as e:
        print(f"  ❌ 驗證失敗: {e}")
    
    print("\\n示例 2: 輸出驗證")
    try:
        result = OutputValidator(content="評估這個項目").call()
        print(f"  標題: {result.title}, 分數: {result.score}")
    except Exception as e:
        print(f"  ❌ 錯誤: {e}")
    
    print("\\n✅ 示例完成")

if __name__ == "__main__":
    main()
