"""
工具函數單元測試

測試專案中的工具函數。
"""

import pytest


@pytest.mark.unit
class TestStringUtils:
    """字串工具測試類"""

    def test_uppercase_conversion(self):
        """測試大寫轉換"""
        assert "hello".upper() == "HELLO"
        assert "WORLD".upper() == "WORLD"

    def test_lowercase_conversion(self):
        """測試小寫轉換"""
        assert "HELLO".lower() == "hello"
        assert "world".lower() == "world"

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("hello world", "Hello World"),
            ("HELLO WORLD", "Hello World"),
            ("hello", "Hello"),
        ],
    )
    def test_title_case(self, input_str, expected):
        """測試標題格式轉換"""
        assert input_str.title() == expected


@pytest.mark.unit
class TestListUtils:
    """列表工具測試類"""

    def test_list_creation(self):
        """測試列表創建"""
        test_list = [1, 2, 3, 4, 5]
        assert len(test_list) == 5
        assert test_list[0] == 1
        assert test_list[-1] == 5

    def test_list_append(self):
        """測試列表添加元素"""
        test_list = []
        test_list.append(1)
        test_list.append(2)
        assert len(test_list) == 2
        assert test_list == [1, 2]

    def test_list_comprehension(self):
        """測試列表推導式"""
        numbers = [1, 2, 3, 4, 5]
        squares = [n**2 for n in numbers]
        assert squares == [1, 4, 9, 16, 25]


@pytest.mark.unit
class TestDictUtils:
    """字典工具測試類"""

    def test_dict_creation(self):
        """測試字典創建"""
        test_dict = {"name": "LLM Agent", "version": "1.0"}
        assert len(test_dict) == 2
        assert test_dict["name"] == "LLM Agent"

    def test_dict_update(self):
        """測試字典更新"""
        test_dict = {"a": 1}
        test_dict["b"] = 2
        assert len(test_dict) == 2
        assert test_dict["b"] == 2

    def test_dict_get_with_default(self):
        """測試字典的 get 方法帶默認值"""
        test_dict = {"a": 1}
        assert test_dict.get("a") == 1
        assert test_dict.get("b", "default") == "default"
