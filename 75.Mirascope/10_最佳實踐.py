"""
Mirascope 最佳實踐示例
運行方式：python 10_最佳實踐.py
"""
import os
import logging
from mirascope.openai import OpenAICall
from pydantic import BaseModel, Field
from typing import Optional

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== 1. 配置管理 ====================

class AppConfig:
    """應用配置"""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEFAULT_MODEL = "gpt-3.5-turbo"
    DEFAULT_TEMPERATURE = 0.7

# ==================== 2. 結構化代碼 ====================

class ProductReview(BaseModel):
    """產品評論結構"""
    rating: int = Field(ge=1, le=5, description="評分1-5")
    summary: str = Field(min_length=10, description="評論摘要")
    sentiment: str = Field(description="情感：positive/negative/neutral")

class ReviewAnalyzer(OpenAICall):
    """評論分析器"""
    prompt_template = """
    分析以下產品評論：
    
    {review_text}
    
    請提供評分（1-5）、摘要和情感分析。
    """
    
    review_text: str
    call_params = {
        "model": AppConfig.DEFAULT_MODEL,
        "temperature": 0.3,  # 低溫度提高準確性
        "response_model": ProductReview
    }

# ==================== 3. 錯誤處理 ====================

class SafeCall(OpenAICall):
    """安全的調用包裝"""
    prompt_template = "處理：{data}"
    data: str
    
    def safe_call(self):
        """帶錯誤處理的調用"""
        try:
            logger.info(f"開始處理：{self.data[:30]}...")
            response = self.call()
            logger.info("處理成功")
            return response
        except Exception as e:
            logger.error(f"處理失敗：{e}")
            return None

# ==================== 4. 性能優化 ====================

class OptimizedCall(OpenAICall):
    """優化的調用"""
    prompt_template = "簡短回答：{question}"
    question: str
    call_params = {
        "model": "gpt-3.5-turbo",  # 使用更快的模型
        "max_tokens": 100,  # 限制輸出長度
        "temperature": 0.3  # 降低隨機性
    }

# ==================== 5. 測試友好 ====================

class TestableCall(OpenAICall):
    """可測試的調用"""
    prompt_template = "總結：{text}"
    text: str
    
    def validate_input(self) -> bool:
        """驗證輸入"""
        if not self.text or len(self.text) < 10:
            logger.warning("輸入文本太短")
            return False
        return True
    
    def process(self):
        """處理流程"""
        if not self.validate_input():
            return None
        return self.call()

# ==================== 主函數 ====================

def main():
    """主函數"""
    print("""
╔══════════════════════════════════════════╗
║      Mirascope 最佳實踐示例               ║
╚══════════════════════════════════════════╝

最佳實踐清單:
✅ 1. 統一配置管理
✅ 2. 結構化代碼組織
✅ 3. 完善的錯誤處理
✅ 4. 性能優化策略
✅ 5. 測試友好設計
✅ 6. 日誌記錄
✅ 7. 類型提示
    """)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 請設置 OPENAI_API_KEY")
        return
    
    # 示例 1: 結構化輸出
    print("\\n示例 1: 結構化評論分析")
    try:
        review = ReviewAnalyzer(
            review_text="這個產品很好用，質量不錯，值得推薦！"
        ).call()
        print(f"  評分: {review.rating}/5")
        print(f"  摘要: {review.summary}")
        print(f"  情感: {review.sentiment}")
    except Exception as e:
        logger.error(f"分析失敗: {e}")
    
    # 示例 2: 安全調用
    print("\\n示例 2: 安全調用")
    result = SafeCall(data="測試數據").safe_call()
    if result:
        print(f"  ✅ 成功: {result.content[:50]}...")
    else:
        print("  ❌ 調用失敗")
    
    # 示例 3: 性能優化
    print("\\n示例 3: 優化的調用")
    try:
        response = OptimizedCall(question="什麼是AI？").call()
        print(f"  快速回答: {response.content[:50]}...")
    except Exception as e:
        logger.error(f"調用失敗: {e}")
    
    # 示例 4: 可測試的調用
    print("\\n示例 4: 可測試的調用")
    testable = TestableCall(text="這是一段測試文本，用於演示可測試性")
    result = testable.process()
    if result:
        print(f"  ✅ 處理成功: {result.content[:50]}...")
    else:
        print("  ❌ 驗證失敗")
    
    print("\\n" + "="*60)
    print("✅ 所有示例完成！")
    print("="*60)
    print("\\n💡 生產環境建議:")
    print("   1. 使用環境變量管理配置")
    print("   2. 實施完善的錯誤處理")
    print("   3. 添加日誌記錄")
    print("   4. 編寫單元測試")
    print("   5. 監控API使用量")
    print("   6. 使用緩存減少調用")

if __name__ == "__main__":
    main()
