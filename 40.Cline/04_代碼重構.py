"""
Cline 代碼重構示例

展示如何使用 Cline 進行代碼重構：
1. 提取函數和類
2. 重命名和移動代碼
3. 簡化複雜邏輯
4. 消除代碼重複
5. 優化性能
6. 改進可讀性

代碼重構是提高代碼質量的關鍵步驟。
"""

import os
from typing import Dict, List, Any, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class ClineRefactoring:
    """Cline 代碼重構工具"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化重構工具"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("需要提供 ANTHROPIC_API_KEY")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def _call_claude(self, prompt: str, system: str = None) -> str:
        """調用 Claude API"""
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages
        }

        if system:
            kwargs["system"] = system

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def extract_function(self, code: str, target: str) -> str:
        """
        提取函數

        Args:
            code: 原始代碼
            target: 要提取的代碼段描述

        Returns:
            重構後的代碼
        """
        prompt = f"""
        請從以下代碼中提取 "{target}" 為獨立函數：

        ```
        {code}
        ```

        要求:
        1. 提取的函數應該職責單一
        2. 使用清晰的函數名
        3. 添加適當的參數和返回值
        4. 包含文檔字符串
        5. 保持原有功能不變

        請返回重構後的完整代碼。
        """

        system = "你是一個專業的代碼重構專家，擅長改進代碼結構和可讀性。"

        return self._call_claude(prompt, system)

    def extract_class(self, code: str, class_name: str, responsibilities: List[str]) -> str:
        """
        提取類

        Args:
            code: 原始代碼
            class_name: 新類的名稱
            responsibilities: 類的職責列表

        Returns:
            重構後的代碼
        """
        responsibilities_str = "\n".join(f"- {r}" for r in responsibilities)

        prompt = f"""
        請從以下代碼中提取一個名為 {class_name} 的類：

        ```
        {code}
        ```

        類的職責:
        {responsibilities_str}

        要求:
        1. 遵循單一職責原則
        2. 使用清晰的方法名
        3. 添加類和方法的文檔
        4. 保持封裝性
        5. 保持原有功能不變

        請返回重構後的完整代碼。
        """

        return self._call_claude(prompt)

    def simplify_logic(self, code: str) -> str:
        """
        簡化複雜邏輯

        Args:
            code: 原始代碼

        Returns:
            簡化後的代碼
        """
        prompt = f"""
        請簡化以下代碼的邏輯：

        ```
        {code}
        ```

        要求:
        1. 減少嵌套層級
        2. 使用早返回模式
        3. 提取複雜條件為變量
        4. 消除魔法數字
        5. 保持功能完全一致

        請返回簡化後的代碼。
        """

        return self._call_claude(prompt)

    def remove_duplication(self, code: str) -> str:
        """
        消除重複代碼

        Args:
            code: 原始代碼

        Returns:
            消除重複後的代碼
        """
        prompt = f"""
        請消除以下代碼中的重複部分：

        ```
        {code}
        ```

        要求:
        1. 識別重複的邏輯
        2. 提取為可重用的函數或方法
        3. 使用參數化處理差異
        4. 保持代碼的可讀性
        5. 遵循 DRY 原則

        請返回重構後的代碼。
        """

        return self._call_claude(prompt)

    def optimize_performance(self, code: str, bottleneck: str = None) -> str:
        """
        優化性能

        Args:
            code: 原始代碼
            bottleneck: 性能瓶頸描述（可選）

        Returns:
            優化後的代碼
        """
        bottleneck_info = f"\n已知瓶頸: {bottleneck}" if bottleneck else ""

        prompt = f"""
        請優化以下代碼的性能：

        ```
        {code}
        ```
        {bottleneck_info}

        要求:
        1. 識別性能問題
        2. 使用更高效的算法或數據結構
        3. 減少不必要的計算
        4. 考慮緩存策略
        5. 保持代碼可讀性

        請返回優化後的代碼，並說明優化點。
        """

        return self._call_claude(prompt)

    def improve_readability(self, code: str) -> str:
        """
        改進可讀性

        Args:
            code: 原始代碼

        Returns:
            改進後的代碼
        """
        prompt = f"""
        請改進以下代碼的可讀性：

        ```
        {code}
        ```

        要求:
        1. 使用更清晰的變量名
        2. 添加適當的註釋
        3. 改進代碼組織
        4. 使用更直觀的邏輯結構
        5. 遵循編碼規範

        請返回改進後的代碼。
        """

        return self._call_claude(prompt)

    def modernize_code(self, code: str, language: str, target_version: str) -> str:
        """
        現代化代碼

        Args:
            code: 原始代碼
            language: 編程語言
            target_version: 目標版本

        Returns:
            現代化後的代碼
        """
        prompt = f"""
        請將以下 {language} 代碼現代化到 {target_version} 版本：

        ```
        {code}
        ```

        要求:
        1. 使用新版本的特性
        2. 替換已棄用的 API
        3. 使用更好的語法糖
        4. 改進類型提示（如果適用）
        5. 保持向後兼容性（如果可能）

        請返回現代化後的代碼。
        """

        return self._call_claude(prompt)

    def apply_design_pattern(self, code: str, pattern: str) -> str:
        """
        應用設計模式

        Args:
            code: 原始代碼
            pattern: 設計模式名稱

        Returns:
            應用設計模式後的代碼
        """
        prompt = f"""
        請將以下代碼重構為使用 {pattern} 設計模式：

        ```
        {code}
        ```

        要求:
        1. 正確實現設計模式
        2. 保持代碼的靈活性
        3. 添加模式說明文檔
        4. 保持原有功能
        5. 提高可擴展性

        請返回重構後的代碼。
        """

        return self._call_claude(prompt)


def example_extract_function():
    """示例 1: 提取函數"""
    print("=" * 60)
    print("示例 1: 提取函數重構")
    print("=" * 60)

    refactoring = ClineRefactoring()

    # 原始代碼（包含重複邏輯）
    original_code = """
def process_order(order_data):
    # 驗證訂單
    if not order_data.get('customer_id'):
        return {'error': '缺少客戶 ID'}
    if not order_data.get('items'):
        return {'error': '訂單中沒有商品'}
    for item in order_data['items']:
        if item['quantity'] <= 0:
            return {'error': '商品數量必須大於 0'}
        if item['price'] < 0:
            return {'error': '商品價格不能為負數'}

    # 計算總價
    total = 0
    for item in order_data['items']:
        item_total = item['quantity'] * item['price']
        if item.get('discount'):
            item_total = item_total * (1 - item['discount'] / 100)
        total += item_total

    # 應用優惠券
    if order_data.get('coupon_code'):
        if order_data['coupon_code'] == 'SAVE10':
            total = total * 0.9
        elif order_data['coupon_code'] == 'SAVE20':
            total = total * 0.8

    return {'total': total, 'status': 'success'}
    """

    print("\n原始代碼:")
    print(original_code)

    refactored_code = refactoring.extract_function(
        code=original_code,
        target="訂單驗證、總價計算和優惠券應用邏輯"
    )

    print("\n重構後的代碼:")
    print(refactored_code)


def example_simplify_logic():
    """示例 2: 簡化複雜邏輯"""
    print("\n" + "=" * 60)
    print("示例 2: 簡化複雜邏輯")
    print("=" * 60)

    refactoring = ClineRefactoring()

    # 複雜的嵌套邏輯
    complex_code = """
def get_user_discount(user):
    if user:
        if user.is_active:
            if user.membership:
                if user.membership.level == 'gold':
                    if user.membership.years >= 5:
                        return 0.3
                    else:
                        return 0.2
                elif user.membership.level == 'silver':
                    if user.membership.years >= 3:
                        return 0.15
                    else:
                        return 0.1
                else:
                    return 0.05
            else:
                return 0
        else:
            return 0
    else:
        return 0
    """

    print("\n原始代碼（複雜嵌套）:")
    print(complex_code)

    simplified_code = refactoring.simplify_logic(complex_code)

    print("\n簡化後的代碼:")
    print(simplified_code)


def example_remove_duplication():
    """示例 3: 消除重複代碼"""
    print("\n" + "=" * 60)
    print("示例 3: 消除重複代碼")
    print("=" * 60)

    refactoring = ClineRefactoring()

    # 包含重複邏輯的代碼
    duplicated_code = """
def save_user(user_data):
    # 驗證用戶名
    if not user_data.get('username'):
        raise ValueError('用戶名不能為空')
    if len(user_data['username']) < 3:
        raise ValueError('用戶名至少 3 個字符')
    if len(user_data['username']) > 50:
        raise ValueError('用戶名最多 50 個字符')

    # 驗證郵箱
    if not user_data.get('email'):
        raise ValueError('郵箱不能為空')
    if len(user_data['email']) < 5:
        raise ValueError('郵箱格式錯誤')
    if '@' not in user_data['email']:
        raise ValueError('郵箱必須包含 @')

    # 驗證密碼
    if not user_data.get('password'):
        raise ValueError('密碼不能為空')
    if len(user_data['password']) < 8:
        raise ValueError('密碼至少 8 個字符')
    if len(user_data['password']) > 100:
        raise ValueError('密碼最多 100 個字符')

    # 保存用戶...
    """

    print("\n原始代碼（重複驗證邏輯）:")
    print(duplicated_code)

    deduplicated_code = refactoring.remove_duplication(duplicated_code)

    print("\n消除重複後的代碼:")
    print(deduplicated_code)


def example_optimize_performance():
    """示例 4: 性能優化"""
    print("\n" + "=" * 60)
    print("示例 4: 性能優化")
    print("=" * 60)

    refactoring = ClineRefactoring()

    # 性能較差的代碼
    slow_code = """
def find_common_elements(list1, list2, list3):
    result = []
    for item in list1:
        if item in list2 and item in list3:
            if item not in result:
                result.append(item)
    return result

def calculate_statistics(numbers):
    # 多次遍歷列表
    total = 0
    for n in numbers:
        total += n
    average = total / len(numbers)

    variance_sum = 0
    for n in numbers:
        variance_sum += (n - average) ** 2
    variance = variance_sum / len(numbers)

    sorted_numbers = []
    for n in numbers:
        sorted_numbers.append(n)
    sorted_numbers.sort()
    median = sorted_numbers[len(sorted_numbers) // 2]

    return {'average': average, 'variance': variance, 'median': median}
    """

    print("\n原始代碼（性能較差）:")
    print(slow_code)

    optimized_code = refactoring.optimize_performance(
        code=slow_code,
        bottleneck="多次遍歷列表，使用低效的數據結構"
    )

    print("\n優化後的代碼:")
    print(optimized_code)


def example_improve_readability():
    """示例 5: 改進可讀性"""
    print("\n" + "=" * 60)
    print("示例 5: 改進代碼可讀性")
    print("=" * 60)

    refactoring = ClineRefactoring()

    # 可讀性差的代碼
    unclear_code = """
def f(d):
    r = []
    for k, v in d.items():
        if v > 100:
            x = v * 0.9
        else:
            x = v
        if x > 50:
            r.append({'n': k, 'p': x, 't': 'A'})
        else:
            r.append({'n': k, 'p': x, 't': 'B'})
    return r
    """

    print("\n原始代碼（可讀性差）:")
    print(unclear_code)

    readable_code = refactoring.improve_readability(unclear_code)

    print("\n改進後的代碼:")
    print(readable_code)


def example_apply_design_pattern():
    """示例 6: 應用設計模式"""
    print("\n" + "=" * 60)
    print("示例 6: 應用策略模式")
    print("=" * 60)

    refactoring = ClineRefactoring()

    # 使用 if-else 的代碼
    original_code = """
class PaymentProcessor:
    def process_payment(self, amount, method):
        if method == 'credit_card':
            # 信用卡支付邏輯
            print(f"Processing ${amount} via credit card")
            fee = amount * 0.03
            return amount + fee
        elif method == 'paypal':
            # PayPal 支付邏輯
            print(f"Processing ${amount} via PayPal")
            fee = amount * 0.04
            return amount + fee
        elif method == 'bank_transfer':
            # 銀行轉帳邏輯
            print(f"Processing ${amount} via bank transfer")
            fee = 5.0
            return amount + fee
        else:
            raise ValueError("不支持的支付方式")
    """

    print("\n原始代碼:")
    print(original_code)

    refactored_code = refactoring.apply_design_pattern(
        code=original_code,
        pattern="策略模式 (Strategy Pattern)"
    )

    print("\n應用策略模式後的代碼:")
    print(refactored_code)


def example_modernize_code():
    """示例 7: 現代化代碼"""
    print("\n" + "=" * 60)
    print("示例 7: 現代化 Python 代碼")
    print("=" * 60)

    refactoring = ClineRefactoring()

    # 舊式 Python 代碼
    old_code = """
def process_data(data):
    result = []
    for item in data:
        if item['active'] == True:
            new_item = {}
            new_item['id'] = item['id']
            new_item['name'] = item['name']
            new_item['value'] = item['value'] * 2
            result.append(new_item)
    return result

def get_config():
    config = {}
    config['host'] = '127.0.0.1'
    config['port'] = 8000
    config['debug'] = True
    return config
    """

    print("\n原始代碼（Python 2 風格）:")
    print(old_code)

    modern_code = refactoring.modernize_code(
        code=old_code,
        language="Python",
        target_version="Python 3.10+"
    )

    print("\n現代化後的代碼:")
    print(modern_code)


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("Cline 代碼重構示例")
    print("=" * 60)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  警告: 未設置 ANTHROPIC_API_KEY")
        return

    try:
        # 運行示例（注釋以節省 API 調用）
        # example_extract_function()
        # example_simplify_logic()
        # example_remove_duplication()
        # example_optimize_performance()
        # example_improve_readability()
        # example_apply_design_pattern()
        # example_modernize_code()

        print("\n✅ 代碼重構示例已準備就緒")
        print("\n💡 提示:")
        print("1. 使用 extract_function() 提取重複邏輯")
        print("2. 使用 simplify_logic() 減少嵌套")
        print("3. 使用 remove_duplication() 遵循 DRY 原則")
        print("4. 使用 optimize_performance() 提升性能")
        print("5. 使用 apply_design_pattern() 改進架構")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
