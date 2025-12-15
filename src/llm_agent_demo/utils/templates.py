"""模板引擎模組 - 提供提示詞模板管理功能"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union

from .exceptions import ValidationError, FileNotFoundError, FileReadError

logger = logging.getLogger(__name__)

# ============================================================================
# 模板語法模式（預編譯正則表達式）
# ============================================================================

# 變數佔位符: {variable} 或 {variable|default}
_VARIABLE_PATTERN = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*(?:\|[^}]*)?)\}")

# 條件語句: {?variable}...{/variable} 或 {?!variable}...{/variable}
_CONDITION_START_PATTERN = re.compile(r"\{\?(!?)([a-zA-Z_][a-zA-Z0-9_]*)\}")
_CONDITION_END_PATTERN = re.compile(r"\{/([a-zA-Z_][a-zA-Z0-9_]*)\}")

# 循環語句: {#items}...{/items}
_LOOP_START_PATTERN = re.compile(r"\{#([a-zA-Z_][a-zA-Z0-9_]*)\}")
_LOOP_END_PATTERN = re.compile(r"\{/([a-zA-Z_][a-zA-Z0-9_]*)\}")

# 註釋: {! 這是註釋 !}
_COMMENT_PATTERN = re.compile(r"\{!.*?!\}", re.DOTALL)

# 過濾器: {variable|filter}
_FILTER_PATTERN = re.compile(r"\|([a-zA-Z_][a-zA-Z0-9_]*)")


# ============================================================================
# 內建過濾器
# ============================================================================

def _filter_upper(value: str) -> str:
    """轉換為大寫"""
    return str(value).upper()


def _filter_lower(value: str) -> str:
    """轉換為小寫"""
    return str(value).lower()


def _filter_capitalize(value: str) -> str:
    """首字母大寫"""
    return str(value).capitalize()


def _filter_title(value: str) -> str:
    """每個單詞首字母大寫"""
    return str(value).title()


def _filter_strip(value: str) -> str:
    """移除首尾空白"""
    return str(value).strip()


def _filter_length(value: Union[str, List, Dict]) -> int:
    """返回長度"""
    return len(value)


def _filter_json(value: Any) -> str:
    """轉換為 JSON 字符串"""
    return json.dumps(value, ensure_ascii=False, indent=2)


def _filter_escape(value: str) -> str:
    """轉義特殊字符"""
    return str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _filter_truncate(value: str, length: int = 50) -> str:
    """截斷字符串"""
    value = str(value)
    if len(value) <= length:
        return value
    return value[:length - 3] + "..."


def _filter_join(value: List[str], separator: str = ", ") -> str:
    """連接列表"""
    return separator.join(str(v) for v in value)


# 內建過濾器字典
_BUILTIN_FILTERS: Dict[str, Callable] = {
    "upper": _filter_upper,
    "lower": _filter_lower,
    "capitalize": _filter_capitalize,
    "title": _filter_title,
    "strip": _filter_strip,
    "length": _filter_length,
    "json": _filter_json,
    "escape": _filter_escape,
    "truncate": _filter_truncate,
    "join": _filter_join,
}


# ============================================================================
# 模板類
# ============================================================================


class PromptTemplate:
    """
    提示詞模板類

    支援功能：
    1. 變數替換: {variable}
    2. 默認值: {variable|default}
    3. 條件語句: {?variable}...{/variable}
    4. 否定條件: {?!variable}...{/variable}
    5. 循環語句: {#items}...{/items}
    6. 註釋: {! 這是註釋 !}
    7. 過濾器: {variable|filter}

    使用範例:
        >>> template = PromptTemplate("你好，{name}！")
        >>> template.render(name="世界")
        '你好，世界！'

        >>> template = PromptTemplate("{?user}歡迎回來，{user}！{/user}")
        >>> template.render(user="Alice")
        '歡迎回來，Alice！'
    """

    def __init__(
        self,
        template: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        required_vars: Optional[List[str]] = None,
        strict: bool = False,
        custom_filters: Optional[Dict[str, Callable]] = None,
    ):
        """
        初始化模板

        Args:
            template: 模板字符串
            name: 模板名稱（可選）
            description: 模板描述（可選）
            required_vars: 必需變數列表（可選）
            strict: 是否嚴格模式（未提供必需變數時拋出異常）
            custom_filters: 自定義過濾器字典
        """
        self.template = template
        self.name = name or "unnamed_template"
        self.description = description or ""
        self.required_vars = set(required_vars) if required_vars else set()
        self.strict = strict

        # 合併內建過濾器和自定義過濾器
        self.filters = _BUILTIN_FILTERS.copy()
        if custom_filters:
            self.filters.update(custom_filters)

        # 提取模板中的變數
        self._extracted_vars = self._extract_variables()

        # 驗證模板
        self._validate_template()

        logger.debug(
            f"模板已創建: {self.name}, "
            f"變數: {self._extracted_vars}, "
            f"必需變數: {self.required_vars}"
        )

    def _extract_variables(self) -> Set[str]:
        """提取模板中的所有變數"""
        variables = set()

        # 移除註釋
        template_without_comments = _COMMENT_PATTERN.sub("", self.template)

        # 提取變數
        for match in _VARIABLE_PATTERN.finditer(template_without_comments):
            var_expr = match.group(1)
            # 處理默認值語法 {var|default}
            var_name = var_expr.split("|")[0].strip()
            variables.add(var_name)

        # 提取條件語句中的變數
        for match in _CONDITION_START_PATTERN.finditer(template_without_comments):
            var_name = match.group(2)
            variables.add(var_name)

        # 提取循環語句中的變數
        for match in _LOOP_START_PATTERN.finditer(template_without_comments):
            var_name = match.group(1)
            variables.add(var_name)

        return variables

    def _validate_template(self) -> None:
        """驗證模板語法"""
        # 檢查括號配對
        self._validate_brackets()

        # 檢查條件語句配對
        self._validate_conditions()

        # 檢查循環語句配對
        self._validate_loops()

    def _validate_brackets(self) -> None:
        """驗證括號配對"""
        stack = []
        for i, char in enumerate(self.template):
            if char == "{":
                stack.append(i)
            elif char == "}":
                if not stack:
                    raise ValidationError(
                        f"模板語法錯誤：在位置 {i} 發現未配對的 '}}'"
                    )
                stack.pop()

        if stack:
            raise ValidationError(
                f"模板語法錯誤：在位置 {stack[0]} 發現未配對的 '{{'"
            )

    def _validate_conditions(self) -> None:
        """驗證條件語句配對"""
        # 移除註釋
        template = _COMMENT_PATTERN.sub("", self.template)

        stack = []
        start_positions = []

        # 查找所有條件開始標記
        for match in _CONDITION_START_PATTERN.finditer(template):
            var_name = match.group(2)
            stack.append(var_name)
            start_positions.append(match.start())

        # 查找所有條件結束標記
        end_positions = []
        for match in _CONDITION_END_PATTERN.finditer(template):
            var_name = match.group(1)

            # 檢查是否是循環結束標記
            if re.match(r"\{#" + var_name + r"\}", template):
                continue

            if not stack:
                raise ValidationError(
                    f"模板語法錯誤：條件 '{{{var_name}}}' 沒有對應的開始標記"
                )

            expected_var = stack.pop()
            if var_name != expected_var:
                raise ValidationError(
                    f"模板語法錯誤：條件標記不匹配，期望 '{expected_var}'，實際 '{var_name}'"
                )
            end_positions.append(match.start())

        if stack:
            raise ValidationError(
                f"模板語法錯誤：條件 '{stack[0]}' 沒有對應的結束標記"
            )

    def _validate_loops(self) -> None:
        """驗證循環語句配對"""
        # 移除註釋
        template = _COMMENT_PATTERN.sub("", self.template)

        stack = []

        # 查找所有循環開始標記
        for match in _LOOP_START_PATTERN.finditer(template):
            var_name = match.group(1)
            stack.append(var_name)

        # 查找所有循環結束標記
        for match in _LOOP_END_PATTERN.finditer(template):
            var_name = match.group(1)

            # 檢查是否是條件結束標記
            if re.match(r"\{\?" + var_name, template):
                continue

            if not stack:
                raise ValidationError(
                    f"模板語法錯誤：循環 '{{{var_name}}}' 沒有對應的開始標記"
                )

            expected_var = stack.pop()
            if var_name != expected_var:
                raise ValidationError(
                    f"模板語法錯誤：循環標記不匹配，期望 '{expected_var}'，實際 '{var_name}'"
                )

        if stack:
            raise ValidationError(
                f"模板語法錯誤：循環 '{stack[0]}' 沒有對應的結束標記"
            )

    def _apply_filter(self, value: Any, filter_name: str) -> Any:
        """應用過濾器"""
        if filter_name not in self.filters:
            logger.warning(f"未知的過濾器: {filter_name}，將返回原始值")
            return value

        try:
            return self.filters[filter_name](value)
        except Exception as e:
            logger.error(f"過濾器 '{filter_name}' 執行失敗: {e}")
            return value

    def _replace_variables(self, text: str, context: Dict[str, Any]) -> str:
        """替換變數"""
        def replace_var(match):
            var_expr = match.group(1)
            parts = var_expr.split("|")
            var_name = parts[0].strip()

            # 獲取變數值
            if var_name in context:
                value = context[var_name]
            elif len(parts) > 1:
                # 使用默認值
                value = parts[1].strip()
            else:
                if self.strict and var_name in self.required_vars:
                    raise ValidationError(
                        f"缺少必需變數: {var_name}",
                        field_name="context",
                    )
                # 保留原始佔位符
                return match.group(0)

            # 應用過濾器
            if len(parts) > 1:
                for filter_name in parts[1:]:
                    filter_name = filter_name.strip()
                    if filter_name and filter_name in self.filters:
                        value = self._apply_filter(value, filter_name)

            return str(value)

        return _VARIABLE_PATTERN.sub(replace_var, text)

    def _process_conditions(self, text: str, context: Dict[str, Any]) -> str:
        """處理條件語句"""
        # 使用遞歸處理嵌套條件
        changed = True
        max_iterations = 100  # 防止無限循環
        iteration = 0

        while changed and iteration < max_iterations:
            changed = False
            iteration += 1

            # 查找最內層的條件語句
            pattern = re.compile(
                r"\{\?(!?)([a-zA-Z_][a-zA-Z0-9_]*)\}(.*?)\{/\2\}",
                re.DOTALL
            )

            def replace_condition(match):
                nonlocal changed
                changed = True

                negation = match.group(1)
                var_name = match.group(2)
                content = match.group(3)

                # 檢查變數是否存在且為真值
                var_exists = var_name in context
                var_value = context.get(var_name, None)

                # 判斷條件
                is_truthy = var_exists and var_value not in (None, False, "", [], {}, 0)

                # 處理否定
                if negation == "!":
                    is_truthy = not is_truthy

                # 返回內容或空字符串
                return content if is_truthy else ""

            text = pattern.sub(replace_condition, text)

        if iteration >= max_iterations:
            logger.warning("條件語句處理達到最大迭代次數，可能存在嵌套過深的問題")

        return text

    def _process_loops(self, text: str, context: Dict[str, Any]) -> str:
        """處理循環語句"""
        # 使用遞歸處理嵌套循環
        changed = True
        max_iterations = 100
        iteration = 0

        while changed and iteration < max_iterations:
            changed = False
            iteration += 1

            # 查找最內層的循環語句
            pattern = re.compile(
                r"\{#([a-zA-Z_][a-zA-Z0-9_]*)\}(.*?)\{/\1\}",
                re.DOTALL
            )

            def replace_loop(match):
                nonlocal changed
                changed = True

                var_name = match.group(1)
                content = match.group(2)

                # 獲取迭代對象
                items = context.get(var_name, [])

                if not isinstance(items, (list, tuple)):
                    logger.warning(f"循環變數 '{var_name}' 不是列表或元組，將被忽略")
                    return ""

                # 渲染每個項目
                results = []
                for index, item in enumerate(items):
                    # 創建循環上下文
                    loop_context = context.copy()

                    # 如果項目是字典，合併到上下文
                    if isinstance(item, dict):
                        loop_context.update(item)
                    else:
                        loop_context["item"] = item

                    # 添加循環變數
                    loop_context["index"] = index
                    loop_context["index1"] = index + 1
                    loop_context["first"] = index == 0
                    loop_context["last"] = index == len(items) - 1

                    # 渲染內容
                    rendered = self._replace_variables(content, loop_context)
                    results.append(rendered)

                return "".join(results)

            text = pattern.sub(replace_loop, text)

        if iteration >= max_iterations:
            logger.warning("循環語句處理達到最大迭代次數，可能存在嵌套過深的問題")

        return text

    def render(self, **context) -> str:
        """
        渲染模板

        Args:
            **context: 模板變數字典

        Returns:
            渲染後的字符串

        Raises:
            ValidationError: 如果缺少必需變數（嚴格模式下）
        """
        # 驗證必需變數
        if self.strict and self.required_vars:
            missing_vars = self.required_vars - set(context.keys())
            if missing_vars:
                raise ValidationError(
                    f"缺少必需變數: {', '.join(missing_vars)}",
                    field_name="context",
                )

        # 1. 移除註釋
        result = _COMMENT_PATTERN.sub("", self.template)

        # 2. 處理條件語句
        result = self._process_conditions(result, context)

        # 3. 處理循環語句
        result = self._process_loops(result, context)

        # 4. 替換變數
        result = self._replace_variables(result, context)

        logger.debug(f"模板 '{self.name}' 渲染完成，長度: {len(result)}")

        return result

    def get_required_vars(self) -> Set[str]:
        """獲取模板所需的所有變數"""
        return self._extracted_vars

    def add_filter(self, name: str, func: Callable) -> None:
        """
        添加自定義過濾器

        Args:
            name: 過濾器名稱
            func: 過濾器函數
        """
        self.filters[name] = func
        logger.debug(f"已添加自定義過濾器: {name}")

    def __str__(self) -> str:
        return f"PromptTemplate(name={self.name}, vars={len(self._extracted_vars)})"

    def __repr__(self) -> str:
        return (
            f"PromptTemplate(name={self.name!r}, "
            f"required_vars={self.required_vars!r}, "
            f"strict={self.strict})"
        )


# ============================================================================
# 模板載入器
# ============================================================================


class TemplateLoader:
    """
    模板載入器類

    支援功能：
    1. 從文件載入模板
    2. 從目錄批量載入
    3. 模板緩存
    4. 熱重載（可選）
    """

    def __init__(
        self,
        template_dir: Optional[Union[str, Path]] = None,
        cache_enabled: bool = True,
        strict: bool = False,
    ):
        """
        初始化模板載入器

        Args:
            template_dir: 模板目錄路徑
            cache_enabled: 是否啟用緩存
            strict: 是否為所有模板啟用嚴格模式
        """
        self.template_dir = Path(template_dir) if template_dir else None
        self.cache_enabled = cache_enabled
        self.strict = strict
        self._cache: Dict[str, PromptTemplate] = {}

        if self.template_dir:
            logger.info(f"模板載入器初始化，模板目錄: {self.template_dir}")

    def load_from_file(
        self,
        file_path: Union[str, Path],
        name: Optional[str] = None,
        required_vars: Optional[List[str]] = None,
    ) -> PromptTemplate:
        """
        從文件載入模板

        Args:
            file_path: 模板文件路徑
            name: 模板名稱（可選，默認使用文件名）
            required_vars: 必需變數列表

        Returns:
            PromptTemplate 對象

        Raises:
            FileNotFoundError: 如果文件不存在
            FileReadError: 如果讀取文件失敗
        """
        file_path = Path(file_path)

        # 如果提供了模板目錄且路徑是相對的，則相對於模板目錄
        if self.template_dir and not file_path.is_absolute():
            file_path = self.template_dir / file_path

        # 檢查緩存
        cache_key = str(file_path)
        if self.cache_enabled and cache_key in self._cache:
            logger.debug(f"從緩存載入模板: {cache_key}")
            return self._cache[cache_key]

        # 檢查文件是否存在
        if not file_path.exists():
            raise FileNotFoundError(
                f"模板文件不存在: {file_path}",
                file_path=str(file_path),
            )

        # 讀取文件
        try:
            template_content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise FileReadError(
                f"讀取模板文件失敗: {file_path}",
                file_path=str(file_path),
                original_error=e,
            )

        # 使用文件名作為默認名稱
        if name is None:
            name = file_path.stem

        # 創建模板
        template = PromptTemplate(
            template=template_content,
            name=name,
            required_vars=required_vars,
            strict=self.strict,
        )

        # 緩存模板
        if self.cache_enabled:
            self._cache[cache_key] = template

        logger.info(f"已載入模板: {name} 從 {file_path}")

        return template

    def load_from_directory(
        self,
        directory: Optional[Union[str, Path]] = None,
        pattern: str = "*.txt",
        recursive: bool = False,
    ) -> Dict[str, PromptTemplate]:
        """
        從目錄批量載入模板

        Args:
            directory: 目錄路徑（可選，默認使用 template_dir）
            pattern: 文件模式（默認 *.txt）
            recursive: 是否遞歸搜索子目錄

        Returns:
            模板名稱到 PromptTemplate 的字典

        Raises:
            FileNotFoundError: 如果目錄不存在
        """
        if directory is None:
            if self.template_dir is None:
                raise ValidationError("未指定模板目錄")
            directory = self.template_dir
        else:
            directory = Path(directory)

        if not directory.exists():
            raise FileNotFoundError(
                f"模板目錄不存在: {directory}",
                file_path=str(directory),
            )

        templates = {}

        # 查找文件
        if recursive:
            files = directory.rglob(pattern)
        else:
            files = directory.glob(pattern)

        # 載入每個文件
        for file_path in files:
            try:
                template = self.load_from_file(file_path)
                templates[template.name] = template
            except Exception as e:
                logger.error(f"載入模板失敗: {file_path}, 錯誤: {e}")

        logger.info(f"從目錄 {directory} 載入了 {len(templates)} 個模板")

        return templates

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        從緩存獲取模板

        Args:
            name: 模板名稱

        Returns:
            PromptTemplate 對象或 None
        """
        for template in self._cache.values():
            if template.name == name:
                return template
        return None

    def clear_cache(self) -> None:
        """清除模板緩存"""
        self._cache.clear()
        logger.info("模板緩存已清除")

    def reload_template(self, file_path: Union[str, Path]) -> PromptTemplate:
        """
        重新載入模板

        Args:
            file_path: 模板文件路徑

        Returns:
            重新載入的 PromptTemplate 對象
        """
        cache_key = str(Path(file_path))
        if cache_key in self._cache:
            del self._cache[cache_key]

        return self.load_from_file(file_path)


# ============================================================================
# 工具函數
# ============================================================================


def create_template(
    template: str,
    name: Optional[str] = None,
    required_vars: Optional[List[str]] = None,
    strict: bool = False,
) -> PromptTemplate:
    """
    創建模板的便捷函數

    Args:
        template: 模板字符串
        name: 模板名稱
        required_vars: 必需變數列表
        strict: 是否嚴格模式

    Returns:
        PromptTemplate 對象
    """
    return PromptTemplate(
        template=template,
        name=name,
        required_vars=required_vars,
        strict=strict,
    )


def load_template(
    file_path: Union[str, Path],
    name: Optional[str] = None,
    required_vars: Optional[List[str]] = None,
    strict: bool = False,
) -> PromptTemplate:
    """
    從文件載入模板的便捷函數

    Args:
        file_path: 模板文件路徑
        name: 模板名稱
        required_vars: 必需變數列表
        strict: 是否嚴格模式

    Returns:
        PromptTemplate 對象
    """
    loader = TemplateLoader(strict=strict)
    return loader.load_from_file(
        file_path=file_path,
        name=name,
        required_vars=required_vars,
    )
