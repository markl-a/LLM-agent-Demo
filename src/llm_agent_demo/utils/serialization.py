"""序列化工具模組 - 提供數據序列化和反序列化功能

此模組提供了類型安全的序列化功能，支援：
- JSON 序列化（支援 datetime, Enum, UUID, bytes 等）
- YAML 序列化
- 數據壓縮（gzip）
- 類型安全的序列化/反序列化

Example:
    基本 JSON 序列化：
    >>> data = {"timestamp": datetime.now(), "status": Status.ACTIVE}
    >>> json_str = serialize_json(data)
    >>> restored = deserialize_json(json_str)

    帶壓縮的序列化：
    >>> compressed = serialize_json(data, compress=True)
    >>> restored = deserialize_json(compressed, decompress=True)

    YAML 序列化：
    >>> yaml_str = serialize_yaml(data)
    >>> restored = deserialize_yaml(yaml_str)

    類型安全的序列化：
    >>> typed_data = serialize_with_type(MyClass(name="test"))
    >>> restored: MyClass = deserialize_with_type(typed_data, MyClass)
"""

import base64
import gzip
import json
import pickle
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from .exceptions import DataError, InvalidDataError, handle_exception
from .logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

# ============================================================================
# JSON 編碼器和解碼器
# ============================================================================


class EnhancedJSONEncoder(json.JSONEncoder):
    """增強的 JSON 編碼器，支援更多 Python 類型

    支援的類型：
    - datetime, date, time: 轉換為 ISO 格式字符串
    - timedelta: 轉換為總秒數
    - Enum: 轉換為枚舉值
    - UUID: 轉換為字符串
    - bytes: 轉換為 base64 字符串
    - Decimal: 轉換為浮點數
    - set, frozenset: 轉換為列表
    - Path: 轉換為字符串
    """

    def default(self, obj: Any) -> Any:
        """轉換不支援的類型"""
        # 日期時間類型
        if isinstance(obj, datetime):
            return {
                "__type__": "datetime",
                "value": obj.isoformat(),
            }
        if isinstance(obj, date):
            return {
                "__type__": "date",
                "value": obj.isoformat(),
            }
        if isinstance(obj, time):
            return {
                "__type__": "time",
                "value": obj.isoformat(),
            }
        if isinstance(obj, timedelta):
            return {
                "__type__": "timedelta",
                "value": obj.total_seconds(),
            }

        # 枚舉類型
        if isinstance(obj, Enum):
            return {
                "__type__": "enum",
                "class": f"{obj.__class__.__module__}.{obj.__class__.__name__}",
                "value": obj.value,
            }

        # UUID 類型
        if isinstance(obj, UUID):
            return {
                "__type__": "uuid",
                "value": str(obj),
            }

        # bytes 類型
        if isinstance(obj, bytes):
            return {
                "__type__": "bytes",
                "value": base64.b64encode(obj).decode('ascii'),
            }

        # Decimal 類型
        if isinstance(obj, Decimal):
            return {
                "__type__": "decimal",
                "value": str(obj),
            }

        # 集合類型
        if isinstance(obj, (set, frozenset)):
            return {
                "__type__": "set" if isinstance(obj, set) else "frozenset",
                "value": list(obj),
            }

        # Path 類型
        if isinstance(obj, Path):
            return {
                "__type__": "path",
                "value": str(obj),
            }

        # 如果有 __dict__ 屬性，嘗試序列化為字典
        if hasattr(obj, '__dict__'):
            return {
                "__type__": "object",
                "class": f"{obj.__class__.__module__}.{obj.__class__.__name__}",
                "value": obj.__dict__,
            }

        # 調用父類的默認處理
        return super().default(obj)


def json_decode_hook(dct: Dict[str, Any]) -> Any:
    """JSON 解碼鉤子，還原特殊類型

    Args:
        dct: 字典對象

    Returns:
        還原的 Python 對象
    """
    if "__type__" not in dct:
        return dct

    obj_type = dct["__type__"]
    value = dct["value"]

    try:
        # 日期時間類型
        if obj_type == "datetime":
            return datetime.fromisoformat(value)
        if obj_type == "date":
            return date.fromisoformat(value)
        if obj_type == "time":
            return time.fromisoformat(value)
        if obj_type == "timedelta":
            return timedelta(seconds=value)

        # UUID 類型
        if obj_type == "uuid":
            return UUID(value)

        # bytes 類型
        if obj_type == "bytes":
            return base64.b64decode(value.encode('ascii'))

        # Decimal 類型
        if obj_type == "decimal":
            return Decimal(value)

        # 集合類型
        if obj_type == "set":
            return set(value)
        if obj_type == "frozenset":
            return frozenset(value)

        # Path 類型
        if obj_type == "path":
            return Path(value)

        # 枚舉類型（需要導入相應的類）
        if obj_type == "enum":
            # 這裡無法自動還原枚舉，返回值即可
            logger.warning(f"Cannot automatically restore enum {dct['class']}, returning value")
            return value

        # 自定義對象（需要手動處理）
        if obj_type == "object":
            logger.warning(f"Cannot automatically restore object {dct['class']}, returning dict")
            return value

    except Exception as e:
        logger.error(f"Error decoding {obj_type}: {e}")
        return dct

    return dct


# ============================================================================
# JSON 序列化函數
# ============================================================================


def serialize_json(
    data: Any,
    *,
    compress: bool = False,
    indent: Optional[int] = None,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
) -> Union[str, bytes]:
    """將數據序列化為 JSON 字符串

    Args:
        data: 要序列化的數據
        compress: 是否壓縮（返回 bytes）
        indent: 縮進空格數（美化輸出）
        ensure_ascii: 是否確保 ASCII 編碼
        sort_keys: 是否排序鍵

    Returns:
        JSON 字符串或壓縮的 bytes

    Raises:
        DataError: 序列化失敗
    """
    try:
        json_str = json.dumps(
            data,
            cls=EnhancedJSONEncoder,
            indent=indent,
            ensure_ascii=ensure_ascii,
            sort_keys=sort_keys,
        )

        if compress:
            return gzip.compress(json_str.encode('utf-8'))

        return json_str

    except Exception as e:
        raise DataError(f"JSON serialization failed: {e}") from e


def deserialize_json(
    data: Union[str, bytes],
    *,
    decompress: bool = False,
) -> Any:
    """從 JSON 字符串反序列化數據

    Args:
        data: JSON 字符串或壓縮的 bytes
        decompress: 是否解壓縮

    Returns:
        反序列化的 Python 對象

    Raises:
        DataError: 反序列化失敗
    """
    try:
        if decompress:
            if isinstance(data, str):
                data = data.encode('utf-8')
            data = gzip.decompress(data).decode('utf-8')

        if isinstance(data, bytes):
            data = data.decode('utf-8')

        return json.loads(data, object_hook=json_decode_hook)

    except Exception as e:
        raise DataError(f"JSON deserialization failed: {e}") from e


def save_json(
    data: Any,
    file_path: Union[str, Path],
    *,
    compress: bool = False,
    indent: int = 2,
    ensure_ascii: bool = False,
    sort_keys: bool = False,
) -> None:
    """將數據保存為 JSON 文件

    Args:
        data: 要保存的數據
        file_path: 文件路徑
        compress: 是否壓縮
        indent: 縮進空格數
        ensure_ascii: 是否確保 ASCII 編碼
        sort_keys: 是否排序鍵

    Raises:
        DataError: 保存失敗
    """
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        serialized = serialize_json(
            data,
            compress=compress,
            indent=indent,
            ensure_ascii=ensure_ascii,
            sort_keys=sort_keys,
        )

        if compress:
            file_path.write_bytes(serialized)  # type: ignore
        else:
            file_path.write_text(serialized, encoding='utf-8')  # type: ignore

        logger.debug(f"Saved JSON to {file_path}")

    except Exception as e:
        raise DataError(f"Failed to save JSON to {file_path}: {e}") from e


def load_json(
    file_path: Union[str, Path],
    *,
    decompress: bool = False,
) -> Any:
    """從 JSON 文件加載數據

    Args:
        file_path: 文件路徑
        decompress: 是否解壓縮

    Returns:
        加載的 Python 對象

    Raises:
        DataError: 加載失敗
    """
    try:
        file_path = Path(file_path)

        if not file_path.exists():
            raise InvalidDataError(f"File not found: {file_path}")

        if decompress:
            data = file_path.read_bytes()
        else:
            data = file_path.read_text(encoding='utf-8')

        result = deserialize_json(data, decompress=decompress)
        logger.debug(f"Loaded JSON from {file_path}")

        return result

    except Exception as e:
        raise DataError(f"Failed to load JSON from {file_path}: {e}") from e


# ============================================================================
# YAML 序列化函數
# ============================================================================


def serialize_yaml(
    data: Any,
    *,
    compress: bool = False,
    default_flow_style: bool = False,
) -> Union[str, bytes]:
    """將數據序列化為 YAML 字符串

    Args:
        data: 要序列化的數據
        compress: 是否壓縮（返回 bytes）
        default_flow_style: 是否使用流式風格

    Returns:
        YAML 字符串或壓縮的 bytes

    Raises:
        DataError: 序列化失敗或 YAML 不可用
    """
    if not YAML_AVAILABLE:
        raise DataError("PyYAML is not installed. Install it with: pip install pyyaml")

    try:
        # 將特殊類型轉換為可序列化的格式
        json_compatible = json.loads(
            json.dumps(data, cls=EnhancedJSONEncoder)
        )

        yaml_str = yaml.dump(
            json_compatible,
            default_flow_style=default_flow_style,
            allow_unicode=True,
        )

        if compress:
            return gzip.compress(yaml_str.encode('utf-8'))

        return yaml_str

    except Exception as e:
        raise DataError(f"YAML serialization failed: {e}") from e


def deserialize_yaml(
    data: Union[str, bytes],
    *,
    decompress: bool = False,
) -> Any:
    """從 YAML 字符串反序列化數據

    Args:
        data: YAML 字符串或壓縮的 bytes
        decompress: 是否解壓縮

    Returns:
        反序列化的 Python 對象

    Raises:
        DataError: 反序列化失敗或 YAML 不可用
    """
    if not YAML_AVAILABLE:
        raise DataError("PyYAML is not installed. Install it with: pip install pyyaml")

    try:
        if decompress:
            if isinstance(data, str):
                data = data.encode('utf-8')
            data = gzip.decompress(data).decode('utf-8')

        if isinstance(data, bytes):
            data = data.decode('utf-8')

        return yaml.safe_load(data)

    except Exception as e:
        raise DataError(f"YAML deserialization failed: {e}") from e


def save_yaml(
    data: Any,
    file_path: Union[str, Path],
    *,
    compress: bool = False,
    default_flow_style: bool = False,
) -> None:
    """將數據保存為 YAML 文件

    Args:
        data: 要保存的數據
        file_path: 文件路徑
        compress: 是否壓縮
        default_flow_style: 是否使用流式風格

    Raises:
        DataError: 保存失敗
    """
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        serialized = serialize_yaml(
            data,
            compress=compress,
            default_flow_style=default_flow_style,
        )

        if compress:
            file_path.write_bytes(serialized)  # type: ignore
        else:
            file_path.write_text(serialized, encoding='utf-8')  # type: ignore

        logger.debug(f"Saved YAML to {file_path}")

    except Exception as e:
        raise DataError(f"Failed to save YAML to {file_path}: {e}") from e


def load_yaml(
    file_path: Union[str, Path],
    *,
    decompress: bool = False,
) -> Any:
    """從 YAML 文件加載數據

    Args:
        file_path: 文件路徑
        decompress: 是否解壓縮

    Returns:
        加載的 Python 對象

    Raises:
        DataError: 加載失敗
    """
    try:
        file_path = Path(file_path)

        if not file_path.exists():
            raise InvalidDataError(f"File not found: {file_path}")

        if decompress:
            data = file_path.read_bytes()
        else:
            data = file_path.read_text(encoding='utf-8')

        result = deserialize_yaml(data, decompress=decompress)
        logger.debug(f"Loaded YAML from {file_path}")

        return result

    except Exception as e:
        raise DataError(f"Failed to load YAML from {file_path}: {e}") from e


# ============================================================================
# 壓縮工具函數
# ============================================================================


def compress_data(data: bytes, level: int = 9) -> bytes:
    """壓縮數據

    Args:
        data: 要壓縮的數據
        level: 壓縮級別（0-9，9 為最高壓縮）

    Returns:
        壓縮後的數據

    Raises:
        DataError: 壓縮失敗
    """
    try:
        return gzip.compress(data, compresslevel=level)
    except Exception as e:
        raise DataError(f"Compression failed: {e}") from e


def decompress_data(data: bytes) -> bytes:
    """解壓縮數據

    Args:
        data: 壓縮的數據

    Returns:
        解壓縮後的數據

    Raises:
        DataError: 解壓縮失敗
    """
    try:
        return gzip.decompress(data)
    except Exception as e:
        raise DataError(f"Decompression failed: {e}") from e


# ============================================================================
# 類型安全的序列化
# ============================================================================


def serialize_with_type(
    obj: T,
    *,
    compress: bool = False,
    use_json: bool = True,
) -> Union[str, bytes]:
    """類型安全的序列化，保存類型信息

    Args:
        obj: 要序列化的對象
        compress: 是否壓縮
        use_json: 使用 JSON（建議使用，安全）。pickle 已棄用（安全風險）

    Returns:
        序列化後的字符串或 bytes

    Raises:
        DataError: 序列化失敗
    """
    try:
        data = {
            "type": f"{obj.__class__.__module__}.{obj.__class__.__name__}",
            "value": obj,
        }

        if use_json:
            return serialize_json(data, compress=compress)
        else:
            # 不再支援 pickle 序列化（安全風險）
            logger.warning(
                "pickle serialization is deprecated due to security risks. "
                "Using JSON instead."
            )
            return serialize_json(data, compress=compress)

    except Exception as e:
        raise DataError(f"Type-safe serialization failed: {e}") from e


def deserialize_with_type(
    data: Union[str, bytes],
    expected_type: Type[T],
    *,
    decompress: bool = False,
    use_json: bool = True,
) -> T:
    """類型安全的反序列化，驗證類型

    Args:
        data: 序列化的數據
        expected_type: 期望的類型
        decompress: 是否解壓縮
        use_json: 使用 JSON（建議使用，安全）。pickle 已棄用（安全風險）

    Returns:
        反序列化的對象

    Raises:
        DataError: 反序列化失敗
        InvalidDataError: 類型不匹配
    """
    try:
        if use_json:
            obj_data = deserialize_json(data, decompress=decompress)
        else:
            # 不再支援 pickle 反序列化（RCE 安全風險）
            logger.warning(
                "pickle deserialization is deprecated due to RCE security risks. "
                "Using JSON instead."
            )
            obj_data = deserialize_json(data, decompress=decompress)

        # 驗證類型
        expected_type_name = f"{expected_type.__module__}.{expected_type.__name__}"
        actual_type_name = obj_data.get("type")

        if actual_type_name != expected_type_name:
            raise InvalidDataError(
                f"Type mismatch: expected {expected_type_name}, got {actual_type_name}"
            )

        return obj_data["value"]

    except Exception as e:
        raise DataError(f"Type-safe deserialization failed: {e}") from e


# ============================================================================
# 便捷函數
# ============================================================================


def to_json_string(obj: Any, pretty: bool = False) -> str:
    """將對象轉換為 JSON 字符串（便捷函數）

    Args:
        obj: 要轉換的對象
        pretty: 是否美化輸出

    Returns:
        JSON 字符串
    """
    return serialize_json(obj, indent=2 if pretty else None)  # type: ignore


def from_json_string(json_str: str) -> Any:
    """從 JSON 字符串解析對象（便捷函數）

    Args:
        json_str: JSON 字符串

    Returns:
        解析的 Python 對象
    """
    return deserialize_json(json_str)


def get_size_info(data: Any) -> Dict[str, int]:
    """獲取數據大小信息（JSON、壓縮）

    Args:
        data: 要分析的數據

    Returns:
        包含大小信息的字典
    """
    try:
        # JSON 大小
        json_str = serialize_json(data)
        json_size = len(json_str.encode('utf-8'))  # type: ignore

        # 壓縮後的 JSON 大小
        compressed = serialize_json(data, compress=True)
        compressed_size = len(compressed)  # type: ignore

        return {
            "json_bytes": json_size,
            "compressed_bytes": compressed_size,
            "compression_ratio": round(compressed_size / json_size * 100, 2),
        }
    except Exception as e:
        logger.error(f"Failed to get size info: {e}")
        return {}


__all__ = [
    # JSON 編碼器
    "EnhancedJSONEncoder",
    "json_decode_hook",
    # JSON 序列化
    "serialize_json",
    "deserialize_json",
    "save_json",
    "load_json",
    # YAML 序列化
    "serialize_yaml",
    "deserialize_yaml",
    "save_yaml",
    "load_yaml",
    # 壓縮
    "compress_data",
    "decompress_data",
    # 類型安全序列化
    "serialize_with_type",
    "deserialize_with_type",
    # 便捷函數
    "to_json_string",
    "from_json_string",
    "get_size_info",
]
