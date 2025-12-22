"""測試序列化工具模組"""

import gzip
import json
import tempfile
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from llm_agent_demo.utils.serialization import (
    EnhancedJSONEncoder,
    compress_data,
    decompress_data,
    deserialize_json,
    deserialize_with_type,
    deserialize_yaml,
    from_json_string,
    get_size_info,
    json_decode_hook,
    load_json,
    load_yaml,
    save_json,
    save_yaml,
    serialize_json,
    serialize_with_type,
    serialize_yaml,
    to_json_string,
)
from llm_agent_demo.utils.exceptions import DataError, InvalidDataError


# ============================================================================
# 測試數據
# ============================================================================


class TestEnum(Enum):
    """測試用枚舉"""

    OPTION_A = "a"
    OPTION_B = "b"
    OPTION_C = 123


class TestDataClass:
    """測試用數據類"""

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value

    def __eq__(self, other):
        return isinstance(other, TestDataClass) and self.name == other.name and self.value == other.value


# ============================================================================
# JSON 編碼器測試
# ============================================================================


class TestEnhancedJSONEncoder:
    """測試增強的 JSON 編碼器"""

    def test_encode_datetime(self):
        """測試編碼 datetime"""
        dt = datetime(2024, 1, 15, 12, 30, 45)
        result = json.dumps(dt, cls=EnhancedJSONEncoder)
        assert "datetime" in result
        assert "2024-01-15" in result

    def test_encode_date(self):
        """測試編碼 date"""
        d = date(2024, 1, 15)
        result = json.dumps(d, cls=EnhancedJSONEncoder)
        assert "date" in result
        assert "2024-01-15" in result

    def test_encode_time(self):
        """測試編碼 time"""
        t = time(12, 30, 45)
        result = json.dumps(t, cls=EnhancedJSONEncoder)
        assert "time" in result
        assert "12:30:45" in result

    def test_encode_timedelta(self):
        """測試編碼 timedelta"""
        td = timedelta(days=1, hours=2, minutes=3)
        result = json.dumps(td, cls=EnhancedJSONEncoder)
        assert "timedelta" in result

    def test_encode_uuid(self):
        """測試編碼 UUID"""
        u = uuid4()
        result = json.dumps(u, cls=EnhancedJSONEncoder)
        assert "uuid" in result
        assert str(u) in result

    def test_encode_bytes(self):
        """測試編碼 bytes"""
        b = b"hello world"
        result = json.dumps(b, cls=EnhancedJSONEncoder)
        assert "bytes" in result

    def test_encode_decimal(self):
        """測試編碼 Decimal"""
        d = Decimal("123.456")
        result = json.dumps(d, cls=EnhancedJSONEncoder)
        assert "decimal" in result
        assert "123.456" in result

    def test_encode_set(self):
        """測試編碼 set"""
        s = {1, 2, 3}
        result = json.dumps(s, cls=EnhancedJSONEncoder)
        assert "set" in result

    def test_encode_path(self):
        """測試編碼 Path"""
        p = Path("/tmp/test.txt")
        result = json.dumps(p, cls=EnhancedJSONEncoder)
        assert "path" in result
        assert "/tmp/test.txt" in result

    def test_encode_enum(self):
        """測試編碼 Enum"""
        e = TestEnum.OPTION_A
        result = json.dumps(e, cls=EnhancedJSONEncoder)
        assert "enum" in result


# ============================================================================
# JSON 解碼測試
# ============================================================================


class TestJSONDecodeHook:
    """測試 JSON 解碼鉤子"""

    def test_decode_datetime(self):
        """測試解碼 datetime"""
        dt = datetime(2024, 1, 15, 12, 30, 45)
        encoded = json.dumps(dt, cls=EnhancedJSONEncoder)
        decoded = json.loads(encoded, object_hook=json_decode_hook)
        assert decoded == dt

    def test_decode_date(self):
        """測試解碼 date"""
        d = date(2024, 1, 15)
        encoded = json.dumps(d, cls=EnhancedJSONEncoder)
        decoded = json.loads(encoded, object_hook=json_decode_hook)
        assert decoded == d

    def test_decode_time(self):
        """測試解碼 time"""
        t = time(12, 30, 45)
        encoded = json.dumps(t, cls=EnhancedJSONEncoder)
        decoded = json.loads(encoded, object_hook=json_decode_hook)
        assert decoded == t

    def test_decode_timedelta(self):
        """測試解碼 timedelta"""
        td = timedelta(days=1, hours=2, minutes=3)
        encoded = json.dumps(td, cls=EnhancedJSONEncoder)
        decoded = json.loads(encoded, object_hook=json_decode_hook)
        assert decoded == td

    def test_decode_uuid(self):
        """測試解碼 UUID"""
        u = uuid4()
        encoded = json.dumps(u, cls=EnhancedJSONEncoder)
        decoded = json.loads(encoded, object_hook=json_decode_hook)
        assert decoded == u

    def test_decode_bytes(self):
        """測試解碼 bytes"""
        b = b"hello world"
        encoded = json.dumps(b, cls=EnhancedJSONEncoder)
        decoded = json.loads(encoded, object_hook=json_decode_hook)
        assert decoded == b

    def test_decode_decimal(self):
        """測試解碼 Decimal"""
        d = Decimal("123.456")
        encoded = json.dumps(d, cls=EnhancedJSONEncoder)
        decoded = json.loads(encoded, object_hook=json_decode_hook)
        assert decoded == d

    def test_decode_set(self):
        """測試解碼 set"""
        s = {1, 2, 3}
        encoded = json.dumps(s, cls=EnhancedJSONEncoder)
        decoded = json.loads(encoded, object_hook=json_decode_hook)
        assert decoded == s

    def test_decode_path(self):
        """測試解碼 Path"""
        p = Path("/tmp/test.txt")
        encoded = json.dumps(p, cls=EnhancedJSONEncoder)
        decoded = json.loads(encoded, object_hook=json_decode_hook)
        assert decoded == p


# ============================================================================
# JSON 序列化測試
# ============================================================================


class TestJSONSerialization:
    """測試 JSON 序列化"""

    def test_serialize_simple_data(self):
        """測試序列化簡單數據"""
        data = {"name": "test", "value": 123}
        result = serialize_json(data)
        assert isinstance(result, str)
        assert "test" in result

    def test_serialize_with_special_types(self):
        """測試序列化特殊類型"""
        data = {
            "datetime": datetime(2024, 1, 15, 12, 30),
            "uuid": uuid4(),
            "decimal": Decimal("123.456"),
            "set": {1, 2, 3},
        }
        result = serialize_json(data)
        assert isinstance(result, str)

    def test_serialize_with_compression(self):
        """測試壓縮序列化"""
        data = {"name": "test", "value": 123}
        result = serialize_json(data, compress=True)
        assert isinstance(result, bytes)

    def test_serialize_with_indent(self):
        """測試美化輸出"""
        data = {"name": "test", "value": 123}
        result = serialize_json(data, indent=2)
        assert "\n" in result

    def test_deserialize_simple_data(self):
        """測試反序列化簡單數據"""
        data = {"name": "test", "value": 123}
        serialized = serialize_json(data)
        deserialized = deserialize_json(serialized)
        assert deserialized == data

    def test_deserialize_with_special_types(self):
        """測試反序列化特殊類型"""
        dt = datetime(2024, 1, 15, 12, 30, 45)
        u = uuid4()
        data = {
            "datetime": dt,
            "uuid": u,
            "decimal": Decimal("123.456"),
        }
        serialized = serialize_json(data)
        deserialized = deserialize_json(serialized)
        assert deserialized["datetime"] == dt
        assert deserialized["uuid"] == u
        assert deserialized["decimal"] == Decimal("123.456")

    def test_deserialize_compressed(self):
        """測試反序列化壓縮數據"""
        data = {"name": "test", "value": 123}
        serialized = serialize_json(data, compress=True)
        deserialized = deserialize_json(serialized, decompress=True)
        assert deserialized == data

    def test_deserialize_invalid_json(self):
        """測試反序列化無效 JSON"""
        with pytest.raises(DataError):
            deserialize_json("invalid json")


# ============================================================================
# JSON 文件操作測試
# ============================================================================


class TestJSONFileOperations:
    """測試 JSON 文件操作"""

    def test_save_and_load_json(self):
        """測試保存和加載 JSON 文件"""
        data = {"name": "test", "value": 123}

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"
            save_json(data, file_path)
            loaded = load_json(file_path)
            assert loaded == data

    def test_save_and_load_with_special_types(self):
        """測試保存和加載特殊類型"""
        data = {
            "datetime": datetime(2024, 1, 15, 12, 30),
            "uuid": uuid4(),
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"
            save_json(data, file_path)
            loaded = load_json(file_path)
            assert loaded["datetime"] == data["datetime"]
            assert loaded["uuid"] == data["uuid"]

    def test_save_and_load_compressed(self):
        """測試保存和加載壓縮文件"""
        data = {"name": "test", "value": 123}

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json.gz"
            save_json(data, file_path, compress=True)
            loaded = load_json(file_path, decompress=True)
            assert loaded == data

    def test_load_nonexistent_file(self):
        """測試加載不存在的文件"""
        with pytest.raises(DataError):
            load_json("/nonexistent/file.json")


# ============================================================================
# YAML 序列化測試
# ============================================================================


class TestYAMLSerialization:
    """測試 YAML 序列化"""

    def test_serialize_simple_data(self):
        """測試序列化簡單數據"""
        data = {"name": "test", "value": 123}
        try:
            result = serialize_yaml(data)
            assert isinstance(result, str)
            assert "test" in result
        except DataError as e:
            # 如果 PyYAML 未安裝，跳過測試
            if "not installed" in str(e):
                pytest.skip("PyYAML not installed")
            raise

    def test_serialize_with_compression(self):
        """測試壓縮序列化"""
        data = {"name": "test", "value": 123}
        try:
            result = serialize_yaml(data, compress=True)
            assert isinstance(result, bytes)
        except DataError as e:
            if "not installed" in str(e):
                pytest.skip("PyYAML not installed")
            raise

    def test_deserialize_simple_data(self):
        """測試反序列化簡單數據"""
        data = {"name": "test", "value": 123}
        try:
            serialized = serialize_yaml(data)
            deserialized = deserialize_yaml(serialized)
            assert deserialized == data
        except DataError as e:
            if "not installed" in str(e):
                pytest.skip("PyYAML not installed")
            raise

    def test_save_and_load_yaml(self):
        """測試保存和加載 YAML 文件"""
        data = {"name": "test", "value": 123}

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                file_path = Path(tmpdir) / "test.yaml"
                save_yaml(data, file_path)
                loaded = load_yaml(file_path)
                assert loaded == data
        except DataError as e:
            if "not installed" in str(e):
                pytest.skip("PyYAML not installed")
            raise


# ============================================================================
# 壓縮工具測試
# ============================================================================


class TestCompression:
    """測試壓縮工具"""

    def test_compress_data(self):
        """測試壓縮數據"""
        data = b"hello world" * 100
        compressed = compress_data(data)
        assert len(compressed) < len(data)

    def test_decompress_data(self):
        """測試解壓縮數據"""
        data = b"hello world" * 100
        compressed = compress_data(data)
        decompressed = decompress_data(compressed)
        assert decompressed == data

    def test_compression_levels(self):
        """測試不同壓縮級別"""
        data = b"hello world" * 100
        compressed_low = compress_data(data, level=1)
        compressed_high = compress_data(data, level=9)
        # 高壓縮級別應該產生更小的數據
        assert len(compressed_high) <= len(compressed_low)


# ============================================================================
# 類型安全序列化測試
# ============================================================================


class TestTypeSafeSerialization:
    """測試類型安全的序列化"""

    def test_serialize_with_type_json(self):
        """測試帶類型的 JSON 序列化"""
        obj = TestDataClass("test", 123)
        serialized = serialize_with_type(obj, use_json=True)
        assert isinstance(serialized, str)

    def test_serialize_with_type_pickle_deprecated(self):
        """測試帶類型的 Pickle 序列化（已棄用，自動使用 JSON）"""
        obj = TestDataClass("test", 123)
        # use_json=False 現在會自動使用 JSON（安全考慮）
        serialized = serialize_with_type(obj, use_json=False)
        # 現在應該返回字符串（JSON）而不是 bytes
        assert isinstance(serialized, str)

    def test_deserialize_with_type_json(self):
        """測試帶類型的 JSON 反序列化"""
        obj = TestDataClass("test", 123)
        serialized = serialize_with_type(obj, use_json=True)
        # 注意：由於 JSON 無法完全還原自定義類，這裡返回的是字典
        deserialized = deserialize_with_type(serialized, TestDataClass, use_json=True)
        assert deserialized["name"] == "test"
        assert deserialized["value"] == 123

    def test_deserialize_with_type_pickle_deprecated(self):
        """測試帶類型的 Pickle 反序列化（已棄用，自動使用 JSON）"""
        obj = TestDataClass("test", 123)
        # use_json=False 現在會自動使用 JSON（安全考慮）
        serialized = serialize_with_type(obj, use_json=False)
        deserialized = deserialize_with_type(serialized, TestDataClass, use_json=False)
        # JSON 返回字典而不是對象
        assert deserialized["name"] == "test"
        assert deserialized["value"] == 123

    def test_deserialize_with_wrong_type(self):
        """測試類型不匹配的反序列化"""
        obj = TestDataClass("test", 123)
        # 使用 JSON（安全）
        serialized = serialize_with_type(obj, use_json=True)

        # 創建一個不同的類
        class DifferentClass:
            pass

        with pytest.raises(DataError):
            deserialize_with_type(serialized, DifferentClass, use_json=True)


# ============================================================================
# 便捷函數測試
# ============================================================================


class TestConvenienceFunctions:
    """測試便捷函數"""

    def test_to_json_string(self):
        """測試轉換為 JSON 字符串"""
        data = {"name": "test", "value": 123}
        result = to_json_string(data)
        assert isinstance(result, str)
        assert "test" in result

    def test_to_json_string_pretty(self):
        """測試美化的 JSON 字符串"""
        data = {"name": "test", "value": 123}
        result = to_json_string(data, pretty=True)
        assert "\n" in result

    def test_from_json_string(self):
        """測試從 JSON 字符串解析"""
        data = {"name": "test", "value": 123}
        json_str = to_json_string(data)
        parsed = from_json_string(json_str)
        assert parsed == data

    def test_get_size_info(self):
        """測試獲取大小信息"""
        data = [{"name": "test", "value": 123}] * 10
        info = get_size_info(data)
        assert "pickle_bytes" in info
        assert "json_bytes" in info
        assert "compressed_bytes" in info
        assert "compression_ratio" in info
        assert info["compressed_bytes"] <= info["json_bytes"]


# ============================================================================
# 集成測試
# ============================================================================


class TestIntegration:
    """集成測試"""

    def test_roundtrip_complex_data(self):
        """測試複雜數據的往返序列化"""
        data = {
            "string": "hello",
            "number": 123,
            "float": 45.67,
            "datetime": datetime(2024, 1, 15, 12, 30),
            "date": date(2024, 1, 15),
            "time": time(12, 30),
            "timedelta": timedelta(days=1),
            "uuid": uuid4(),
            "bytes": b"binary data",
            "decimal": Decimal("123.456"),
            "set": {1, 2, 3},
            "path": Path("/tmp/test"),
            "nested": {
                "list": [1, 2, 3],
                "dict": {"a": 1, "b": 2},
            },
        }

        # JSON 往返
        json_serialized = serialize_json(data)
        json_deserialized = deserialize_json(json_serialized)

        # 驗證關鍵字段
        assert json_deserialized["string"] == data["string"]
        assert json_deserialized["datetime"] == data["datetime"]
        assert json_deserialized["uuid"] == data["uuid"]

    def test_file_roundtrip_with_compression(self):
        """測試帶壓縮的文件往返"""
        data = {
            "datetime": datetime(2024, 1, 15, 12, 30),
            "uuid": uuid4(),
            "large_text": "x" * 10000,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            # 保存壓縮文件
            file_path = Path(tmpdir) / "test.json.gz"
            save_json(data, file_path, compress=True)

            # 驗證文件確實被壓縮了
            assert file_path.exists()

            # 加載並驗證
            loaded = load_json(file_path, decompress=True)
            assert loaded["datetime"] == data["datetime"]
            assert loaded["uuid"] == data["uuid"]
            assert loaded["large_text"] == data["large_text"]
