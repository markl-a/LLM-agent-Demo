"""
DSPy 簽名定義進階教學

本模組深入講解 DSPy 的簽名（Signature）系統，包括：
1. 簽名的核心概念和設計原則
2. 輸入輸出欄位的定義和配置
3. 複雜簽名的設計模式
4. 簽名的繼承和組合
5. 類型提示和驗證
6. 最佳實踐和常見陷阱

作者：DSPy 教學團隊
日期：2025-01
"""

import dspy
from typing import List, Dict, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
import json


# ==================== 基礎簽名定義 ====================

class SimpleSignature(dspy.Signature):
    """
    最簡單的簽名定義

    簽名是 DSPy 的核心抽象，定義了：
    - 任務的輸入是什麼
    - 任務的輸出是什麼
    - 任務的描述（docstring）
    """
    input_text = dspy.InputField()
    output_text = dspy.OutputField()


class DetailedSignature(dspy.Signature):
    """
    詳細的簽名定義

    使用 desc 參數提供欄位描述可以：
    - 幫助 LLM 更好地理解任務
    - 提高輸出質量
    - 讓程式碼更易讀
    """
    question = dspy.InputField(desc="用戶提出的問題，可能是任何主題")
    context = dspy.InputField(desc="相關的背景資訊或上下文")
    answer = dspy.OutputField(desc="基於上下文的準確、簡潔的答案")


# ==================== 專業領域簽名 ====================

class MedicalDiagnosis(dspy.Signature):
    """醫療診斷助手簽名"""
    symptoms = dspy.InputField(
        desc="患者的症狀描述，包括持續時間、嚴重程度等"
    )
    medical_history = dspy.InputField(
        desc="患者的病史，包括過往疾病、用藥情況、過敏史等"
    )
    age = dspy.InputField(desc="患者年齡")
    gender = dspy.InputField(desc="患者性別")

    possible_conditions = dspy.OutputField(
        desc="可能的疾病診斷，按可能性排序"
    )
    recommended_tests = dspy.OutputField(
        desc="建議進行的醫學檢查"
    )
    urgency_level = dspy.OutputField(
        desc="緊急程度：low（低）、medium（中）、high（高）、critical（危急）"
    )


class LegalAnalysis(dspy.Signature):
    """法律分析簽名"""
    case_description = dspy.InputField(
        desc="案件的詳細描述，包括事實、爭議點等"
    )
    jurisdiction = dspy.InputField(
        desc="適用的法律管轄區域"
    )
    case_type = dspy.InputField(
        desc="案件類型：民事、刑事、行政等"
    )

    legal_analysis = dspy.OutputField(
        desc="法律分析，包括適用法律條文、判例引用等"
    )
    potential_outcomes = dspy.OutputField(
        desc="可能的判決結果及其可能性"
    )
    recommended_strategy = dspy.OutputField(
        desc="建議的訴訟或辯護策略"
    )


class FinancialAnalysis(dspy.Signature):
    """財務分析簽名"""
    company_name = dspy.InputField(desc="公司名稱")
    financial_statements = dspy.InputField(
        desc="財務報表數據，包括資產負債表、損益表等"
    )
    industry = dspy.InputField(desc="所屬行業")
    time_period = dspy.InputField(desc="分析時間段")

    profitability_analysis = dspy.OutputField(
        desc="獲利能力分析，包括毛利率、淨利率等指標"
    )
    liquidity_analysis = dspy.OutputField(
        desc="流動性分析，包括流動比率、速動比率等"
    )
    solvency_analysis = dspy.OutputField(
        desc="償債能力分析，包括負債比率、利息保障倍數等"
    )
    investment_recommendation = dspy.OutputField(
        desc="投資建議：買入、持有、賣出"
    )


# ==================== 多輸入多輸出簽名 ====================

class MultiInputAnalysis(dspy.Signature):
    """
    多輸入分析簽名

    展示如何處理多個輸入欄位的複雜場景
    """
    # 多個輸入欄位
    text_input = dspy.InputField(desc="文本內容")
    numerical_data = dspy.InputField(desc="數值數據")
    categorical_data = dspy.InputField(desc="分類數據")
    metadata = dspy.InputField(desc="元數據資訊")

    # 單一輸出
    comprehensive_analysis = dspy.OutputField(
        desc="綜合分析結果，整合所有輸入的見解"
    )


class MultiOutputGeneration(dspy.Signature):
    """
    多輸出生成簽名

    展示如何生成多個相關但不同的輸出
    """
    # 單一輸入
    topic = dspy.InputField(desc="要分析的主題")

    # 多個輸出欄位
    summary = dspy.OutputField(desc="主題摘要（50字以內）")
    key_points = dspy.OutputField(desc="關鍵要點（5-7個要點）")
    detailed_explanation = dspy.OutputField(desc="詳細解釋（200字以上）")
    related_topics = dspy.OutputField(desc="相關主題列表")
    references = dspy.OutputField(desc="參考資料來源")


class ComplexTransformation(dspy.Signature):
    """
    複雜轉換簽名

    多輸入多輸出的完整範例
    """
    # 輸入組
    source_text = dspy.InputField(desc="原始文本")
    target_format = dspy.InputField(desc="目標格式")
    style_guide = dspy.InputField(desc="風格指南")
    constraints = dspy.InputField(desc="限制條件")

    # 輸出組
    transformed_text = dspy.OutputField(desc="轉換後的文本")
    change_summary = dspy.OutputField(desc="變更摘要")
    quality_score = dspy.OutputField(desc="質量評分（0-100）")
    suggestions = dspy.OutputField(desc="進一步改進建議")


# ==================== 結構化輸出簽名 ====================

class JSONOutputSignature(dspy.Signature):
    """
    JSON 結構化輸出簽名

    確保輸出是有效的 JSON 格式
    """
    query = dspy.InputField(desc="用戶查詢")

    json_result = dspy.OutputField(
        desc="JSON 格式的結果，必須是有效的 JSON 字符串，"
             "包含 'data', 'metadata', 'timestamp' 欄位"
    )


class StructuredDataExtraction(dspy.Signature):
    """
    結構化數據提取簽名

    從非結構化文本中提取結構化資訊
    """
    unstructured_text = dspy.InputField(
        desc="非結構化的文本內容"
    )

    entities = dspy.OutputField(
        desc="提取的實體列表，JSON 格式：[{'type': '類型', 'value': '值', 'confidence': 置信度}]"
    )
    relationships = dspy.OutputField(
        desc="實體之間的關係，JSON 格式：[{'entity1': '實體1', 'relation': '關係', 'entity2': '實體2'}]"
    )
    key_facts = dspy.OutputField(
        desc="關鍵事實列表"
    )


class TableGeneration(dspy.Signature):
    """表格生成簽名"""
    description = dspy.InputField(desc="表格需求描述")
    data_points = dspy.InputField(desc="數據點或範例")

    table_markdown = dspy.OutputField(
        desc="Markdown 格式的表格"
    )
    table_caption = dspy.OutputField(desc="表格標題")
    column_descriptions = dspy.OutputField(
        desc="各列的描述說明"
    )


# ==================== 任務鏈簽名 ====================

class ResearchQuestion(dspy.Signature):
    """研究問題分解"""
    research_topic = dspy.InputField(desc="研究主題")

    sub_questions = dspy.OutputField(
        desc="分解後的子問題列表，每個都可以獨立研究"
    )
    search_keywords = dspy.OutputField(desc="搜索關鍵詞")
    research_method = dspy.OutputField(desc="建議的研究方法")


class InformationSynthesis(dspy.Signature):
    """資訊綜合"""
    sub_questions = dspy.InputField(desc="子問題列表")
    findings = dspy.InputField(desc="各個子問題的研究發現")

    synthesized_answer = dspy.OutputField(
        desc="綜合所有發現後的完整答案"
    )
    confidence_level = dspy.OutputField(desc="答案的可信度")
    gaps = dspy.OutputField(desc="尚未解決的問題或資訊缺口")


class QualityCheck(dspy.Signature):
    """質量檢查"""
    original_question = dspy.InputField(desc="原始問題")
    generated_answer = dspy.InputField(desc="生成的答案")

    is_accurate = dspy.OutputField(desc="答案是否準確（yes/no）")
    is_complete = dspy.OutputField(desc="答案是否完整（yes/no）")
    is_relevant = dspy.OutputField(desc="答案是否相關（yes/no）")
    improvement_suggestions = dspy.OutputField(
        desc="改進建議"
    )


# ==================== 條件式簽名 ====================

class ConditionalProcessing(dspy.Signature):
    """
    條件式處理簽名

    根據輸入的類型決定處理方式
    """
    input_data = dspy.InputField(desc="輸入數據")
    data_type = dspy.InputField(
        desc="數據類型：text, number, json, xml, csv"
    )

    processed_output = dspy.OutputField(desc="處理後的輸出")
    processing_method = dspy.OutputField(desc="使用的處理方法")


class AdaptiveResponse(dspy.Signature):
    """
    自適應回應簽名

    根據用戶的專業程度調整回答
    """
    question = dspy.InputField(desc="用戶問題")
    user_expertise = dspy.InputField(
        desc="用戶專業程度：beginner, intermediate, expert"
    )

    answer = dspy.OutputField(
        desc="根據用戶程度調整的答案，初學者用簡單語言，專家用專業術語"
    )
    additional_resources = dspy.OutputField(
        desc="適合該程度的額外學習資源"
    )


# ==================== 實用函數和範例 ====================

def demonstrate_signature(signature_class, **kwargs):
    """
    演示簽名的使用

    Args:
        signature_class: 簽名類
        **kwargs: 輸入參數
    """
    print(f"\n{'='*60}")
    print(f"簽名：{signature_class.__name__}")
    print(f"描述：{signature_class.__doc__}")
    print(f"{'='*60}")

    # 創建預測模組
    predictor = dspy.Predict(signature_class)

    # 執行預測
    result = predictor(**kwargs)

    # 顯示輸入
    print("\n輸入：")
    for key, value in kwargs.items():
        print(f"  {key}: {value}")

    # 顯示輸出
    print("\n輸出：")
    for key in signature_class.output_fields:
        if hasattr(result, key):
            value = getattr(result, key)
            print(f"  {key}: {value}")


def example_medical_diagnosis():
    """醫療診斷範例"""
    demonstrate_signature(
        MedicalDiagnosis,
        symptoms="持續性頭痛三天，伴隨噁心和畏光",
        medical_history="無重大疾病史，偶爾偏頭痛",
        age="35",
        gender="女性"
    )


def example_legal_analysis():
    """法律分析範例"""
    demonstrate_signature(
        LegalAnalysis,
        case_description="租戶未按時支付租金達三個月，房東要求解除租約並收回房屋",
        jurisdiction="台灣",
        case_type="民事糾紛"
    )


def example_multi_output():
    """多輸出範例"""
    demonstrate_signature(
        MultiOutputGeneration,
        topic="人工智能在醫療領域的應用"
    )


def example_structured_extraction():
    """結構化提取範例"""
    text = """
    蘋果公司（Apple Inc.）於2023年9月發布了iPhone 15系列，
    CEO Tim Cook 在發布會上表示這是有史以來最強大的iPhone。
    新機型採用A17 Pro 晶片，售價從$799美元起。
    """

    demonstrate_signature(
        StructuredDataExtraction,
        unstructured_text=text
    )


def example_conditional_processing():
    """條件處理範例"""
    demonstrate_signature(
        ConditionalProcessing,
        input_data='{"name": "John", "age": 30}',
        data_type="json"
    )


def example_adaptive_response():
    """自適應回應範例"""
    question = "什麼是機器學習？"

    for level in ["beginner", "intermediate", "expert"]:
        print(f"\n\n針對 {level} 的回答：")
        demonstrate_signature(
            AdaptiveResponse,
            question=question,
            user_expertise=level
        )


# ==================== 簽名驗證和測試 ====================

class SignatureValidator:
    """
    簽名驗證器

    用於驗證簽名定義的正確性和完整性
    """

    @staticmethod
    def validate_signature(signature_class):
        """
        驗證簽名定義

        檢查：
        1. 是否有 docstring
        2. 是否有輸入欄位
        3. 是否有輸出欄位
        4. 欄位是否有描述
        """
        issues = []

        # 檢查 docstring
        if not signature_class.__doc__:
            issues.append("缺少 docstring")

        # 檢查輸入欄位
        input_fields = [
            name for name, field in signature_class.__dict__.items()
            if isinstance(field, dspy.InputField)
        ]
        if not input_fields:
            issues.append("沒有定義輸入欄位")

        # 檢查輸出欄位
        output_fields = [
            name for name, field in signature_class.__dict__.items()
            if isinstance(field, dspy.OutputField)
        ]
        if not output_fields:
            issues.append("沒有定義輸出欄位")

        # 檢查欄位描述
        for name, field in signature_class.__dict__.items():
            if isinstance(field, (dspy.InputField, dspy.OutputField)):
                if not hasattr(field, 'desc') or not field.desc:
                    issues.append(f"欄位 '{name}' 缺少描述")

        return issues

    @staticmethod
    def print_signature_info(signature_class):
        """打印簽名資訊"""
        print(f"\n簽名：{signature_class.__name__}")
        print(f"描述：{signature_class.__doc__}")

        print("\n輸入欄位：")
        for name, field in signature_class.__dict__.items():
            if isinstance(field, dspy.InputField):
                desc = getattr(field, 'desc', '無描述')
                print(f"  - {name}: {desc}")

        print("\n輸出欄位：")
        for name, field in signature_class.__dict__.items():
            if isinstance(field, dspy.OutputField):
                desc = getattr(field, 'desc', '無描述')
                print(f"  - {name}: {desc}")

        # 驗證
        issues = SignatureValidator.validate_signature(signature_class)
        if issues:
            print("\n⚠️  發現問題：")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✓ 簽名定義正確")


# ==================== 最佳實踐範例 ====================

class BestPracticeSignature(dspy.Signature):
    """
    最佳實踐簽名範例

    這個簽名展示了所有最佳實踐：
    1. 清晰的 docstring 說明任務
    2. 所有欄位都有描述性的 desc
    3. 使用有意義的欄位名稱
    4. 輸出欄位指定了期望的格式
    """

    # 輸入欄位 - 使用清晰的名稱和詳細的描述
    user_query = dspy.InputField(
        desc="用戶的自然語言查詢，可能包含多個意圖"
    )

    conversation_history = dspy.InputField(
        desc="對話歷史，JSON 格式的消息列表"
    )

    user_preferences = dspy.InputField(
        desc="用戶偏好設置，如語言、風格、詳細程度等"
    )

    # 輸出欄位 - 明確指定格式和內容要求
    interpreted_intent = dspy.OutputField(
        desc="解析後的用戶意圖，主要意圖和次要意圖"
    )

    response = dspy.OutputField(
        desc="根據意圖和歷史生成的回應，符合用戶偏好"
    )

    suggested_actions = dspy.OutputField(
        desc="建議的後續操作，列表格式"
    )

    confidence_score = dspy.OutputField(
        desc="回應的置信度分數（0-100）"
    )


# ==================== 主程序 ====================

def main():
    """主函數：演示所有簽名範例"""

    print("="*60)
    print("DSPy 簽名定義進階教學")
    print("="*60)

    # 配置 DSPy
    print("\n正在配置 DSPy...")
    try:
        lm = dspy.OpenAI(model="gpt-4", max_tokens=500)
        dspy.settings.configure(lm=lm)
        print("✓ 配置完成")
    except Exception as e:
        print(f"配置失敗：{e}")
        print("某些範例可能無法運行")

    # 1. 基礎簽名驗證
    print("\n" + "="*60)
    print("1. 簽名驗證")
    print("="*60)

    signatures_to_validate = [
        SimpleSignature,
        DetailedSignature,
        MedicalDiagnosis,
        BestPracticeSignature
    ]

    for sig in signatures_to_validate:
        SignatureValidator.print_signature_info(sig)

    # 2. 專業領域簽名範例
    print("\n" + "="*60)
    print("2. 專業領域簽名範例")
    print("="*60)

    try:
        example_medical_diagnosis()
    except Exception as e:
        print(f"醫療診斷範例失敗：{e}")

    try:
        example_legal_analysis()
    except Exception as e:
        print(f"法律分析範例失敗：{e}")

    # 3. 多輸出範例
    print("\n" + "="*60)
    print("3. 多輸出生成範例")
    print("="*60)

    try:
        example_multi_output()
    except Exception as e:
        print(f"多輸出範例失敗：{e}")

    # 4. 結構化提取範例
    print("\n" + "="*60)
    print("4. 結構化數據提取範例")
    print("="*60)

    try:
        example_structured_extraction()
    except Exception as e:
        print(f"結構化提取範例失敗：{e}")

    # 5. 條件處理範例
    print("\n" + "="*60)
    print("5. 條件處理範例")
    print("="*60)

    try:
        example_conditional_processing()
    except Exception as e:
        print(f"條件處理範例失敗：{e}")

    # 6. 自適應回應範例
    print("\n" + "="*60)
    print("6. 自適應回應範例")
    print("="*60)

    try:
        example_adaptive_response()
    except Exception as e:
        print(f"自適應回應範例失敗：{e}")

    # 總結
    print("\n" + "="*60)
    print("教學完成！")
    print("="*60)
    print("""
    你已經學會了：
    1. ✓ 基礎簽名定義
    2. ✓ 專業領域簽名設計
    3. ✓ 多輸入多輸出簽名
    4. ✓ 結構化輸出簽名
    5. ✓ 條件式和自適應簽名
    6. ✓ 簽名驗證和測試
    7. ✓ 最佳實踐

    設計簽名的關鍵原則：
    - 清晰的任務描述（docstring）
    - 詳細的欄位描述（desc）
    - 有意義的欄位名稱
    - 明確的輸出格式要求
    - 適當的輸入輸出數量

    下一步：
    - 學習模組組合（03_模組組合.py）
    - 學習如何優化簽名（04_提示優化.py）
    """)


if __name__ == "__main__":
    main()
