"""
Mirascope 結構化輸出示例
運行方式：python 03_結構化輸出.py
"""
import os
from mirascope.openai import OpenAICall
from pydantic import BaseModel, Field
from typing import List

class Person(BaseModel):
    name: str
    age: int
    email: str

class PersonExtractor(OpenAICall):
    prompt_template = "提取人物信息：{text}"
    text: str
    call_params = {"response_model": Person}

class Article(BaseModel):
    title: str = Field(description="文章標題")
    summary: str = Field(description="摘要")
    tags: List[str] = Field(description="標籤")

class ArticleAnalyzer(OpenAICall):
    prompt_template = "分析文章：{content}"
    content: str
    call_params = {"response_model": Article}

def main():
    print("\\nMirascope 結構化輸出示例\\n")
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY")
        return
    
    print("示例 1: 提取人物信息")
    try:
        person = PersonExtractor(text="張三，30歲，zhangsan@example.com").call()
        print(f"  姓名: {person.name}, 年齡: {person.age}, 郵箱: {person.email}")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    
    print("\\n示例 2: 分析文章")
    try:
        article = ArticleAnalyzer(content="AI 技術正在改變世界...").call()
        print(f"  標題: {article.title}")
        print(f"  摘要: {article.summary[:50]}...")
        print(f"  標籤: {', '.join(article.tags)}")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    
    print("\\n✅ 示例完成")

if __name__ == "__main__":
    main()
