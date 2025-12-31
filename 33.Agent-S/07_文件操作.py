"""
Agent-S 文件操作模組

此模組展示 Agent-S 的文件管理和編輯能力：
1. 文件搜索 - 在文件系統中定位文件
2. 文件操作 - 打開、編輯、保存、移動、刪除
3. 內容編輯 - 使用各種編輯器編輯文件內容
4. 批量處理 - 批量文件操作

Agent-S 能夠理解文件結構並執行複雜的文件管理任務。
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from pathlib import Path
from datetime import datetime
import time


class FileType(Enum):
    """文件類型"""
    TEXT = "文本文件"
    CODE = "代碼文件"
    DOCUMENT = "文檔"
    SPREADSHEET = "電子表格"
    IMAGE = "圖片"
    VIDEO = "視頻"
    AUDIO = "音頻"
    ARCHIVE = "壓縮包"
    UNKNOWN = "未知"


class EditorType(Enum):
    """編輯器類型"""
    NOTEPAD = "記事本"
    VSCODE = "VS Code"
    WORD = "Microsoft Word"
    EXCEL = "Microsoft Excel"
    PYCHARM = "PyCharm"
    SUBLIME = "Sublime Text"


@dataclass
class FileInfo:
    """文件信息"""
    path: Path
    name: str
    extension: str
    size: int  # 字節
    created: datetime
    modified: datetime
    file_type: FileType

    @property
    def size_human(self) -> str:
        """人類可讀的文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.size < 1024:
                return f"{self.size:.2f} {unit}"
            self.size /= 1024
        return f"{self.size:.2f} TB"

    def __str__(self):
        return f"{self.name} ({self.size_human})"


@dataclass
class EditOperation:
    """編輯操作"""
    operation_type: str  # insert, delete, replace, format
    position: int  # 行號或字符位置
    content: str
    timestamp: datetime = field(default_factory=datetime.now)


class FileExplorer:
    """
    文件瀏覽器

    模擬文件系統瀏覽和搜索
    """

    def __init__(self, root_path: str = "/"):
        self.root_path = Path(root_path)
        self.current_path = self.root_path
        # 模擬文件系統
        self.mock_files = self._create_mock_filesystem()

    def _create_mock_filesystem(self) -> List[FileInfo]:
        """創建模擬文件系統"""
        now = datetime.now()

        return [
            FileInfo(
                Path("/Documents/報告.docx"),
                "報告.docx",
                ".docx",
                102400,
                now,
                now,
                FileType.DOCUMENT
            ),
            FileInfo(
                Path("/Documents/數據分析.xlsx"),
                "數據分析.xlsx",
                ".xlsx",
                51200,
                now,
                now,
                FileType.SPREADSHEET
            ),
            FileInfo(
                Path("/Code/main.py"),
                "main.py",
                ".py",
                4096,
                now,
                now,
                FileType.CODE
            ),
            FileInfo(
                Path("/Code/utils.py"),
                "utils.py",
                ".py",
                2048,
                now,
                now,
                FileType.CODE
            ),
            FileInfo(
                Path("/Downloads/圖片1.png"),
                "圖片1.png",
                ".png",
                1048576,
                now,
                now,
                FileType.IMAGE
            ),
            FileInfo(
                Path("/Notes/筆記.txt"),
                "筆記.txt",
                ".txt",
                1024,
                now,
                now,
                FileType.TEXT
            ),
        ]

    def search(self, filename: str, search_path: Optional[Path] = None) -> List[FileInfo]:
        """搜索文件"""
        search_path = search_path or self.current_path

        print(f"\n在 {search_path} 中搜索: {filename}")

        results = []
        for file in self.mock_files:
            if filename.lower() in file.name.lower():
                # 檢查路徑是否匹配
                if str(search_path) == "/" or str(file.path).startswith(str(search_path)):
                    results.append(file)

        print(f"找到 {len(results)} 個結果:")
        for i, file in enumerate(results, 1):
            print(f"  {i}. {file.path}")

        return results

    def search_by_type(self, file_type: FileType) -> List[FileInfo]:
        """按類型搜索文件"""
        print(f"\n搜索 {file_type.value} 類型的文件")

        results = [f for f in self.mock_files if f.file_type == file_type]

        print(f"找到 {len(results)} 個文件:")
        for i, file in enumerate(results, 1):
            print(f"  {i}. {file}")

        return results

    def search_by_extension(self, extension: str) -> List[FileInfo]:
        """按擴展名搜索"""
        if not extension.startswith('.'):
            extension = '.' + extension

        print(f"\n搜索 {extension} 文件")

        results = [f for f in self.mock_files if f.extension == extension]

        print(f"找到 {len(results)} 個文件")
        return results

    def list_directory(self, path: Optional[Path] = None) -> List[FileInfo]:
        """列出目錄內容"""
        path = path or self.current_path

        print(f"\n列出目錄: {path}")

        # 模擬列出目錄
        files = [f for f in self.mock_files if str(f.path.parent) == str(path)]

        for i, file in enumerate(files, 1):
            print(f"  {i}. {file}")

        return files


class FileEditor:
    """
    文件編輯器

    管理文件的打開、編輯和保存
    """

    def __init__(self):
        self.open_files: Dict[str, Dict[str, Any]] = {}
        self.edit_history: Dict[str, List[EditOperation]] = {}

    def open_file(self, file_info: FileInfo, editor: EditorType) -> bool:
        """打開文件"""
        print(f"\n使用 {editor.value} 打開: {file_info.name}")

        # 檢查編輯器是否適合文件類型
        if not self._is_compatible(file_info.file_type, editor):
            print(f"警告: {editor.value} 可能不適合編輯 {file_info.file_type.value}")

        # 模擬讀取文件內容
        content = self._load_content(file_info)

        self.open_files[str(file_info.path)] = {
            "file_info": file_info,
            "editor": editor,
            "content": content,
            "modified": False
        }

        self.edit_history[str(file_info.path)] = []

        print(f"文件已打開 ✓")
        return True

    def _is_compatible(self, file_type: FileType, editor: EditorType) -> bool:
        """檢查編輯器和文件類型兼容性"""
        compatibility = {
            EditorType.NOTEPAD: [FileType.TEXT, FileType.CODE],
            EditorType.VSCODE: [FileType.TEXT, FileType.CODE],
            EditorType.WORD: [FileType.DOCUMENT, FileType.TEXT],
            EditorType.EXCEL: [FileType.SPREADSHEET],
            EditorType.PYCHARM: [FileType.CODE],
            EditorType.SUBLIME: [FileType.TEXT, FileType.CODE],
        }

        return file_type in compatibility.get(editor, [])

    def _load_content(self, file_info: FileInfo) -> str:
        """加載文件內容（模擬）"""
        if file_info.file_type == FileType.TEXT:
            return "這是文本文件的內容...\n第二行\n第三行"
        elif file_info.file_type == FileType.CODE:
            return "# Python 代碼\ndef main():\n    print('Hello')\n"
        elif file_info.file_type == FileType.DOCUMENT:
            return "文檔內容\n標題\n正文..."
        else:
            return "[二進制內容]"

    def edit(self, file_path: str, operation: EditOperation) -> bool:
        """編輯文件"""
        if file_path not in self.open_files:
            print(f"錯誤: 文件未打開 {file_path}")
            return False

        print(f"\n執行編輯操作: {operation.operation_type}")
        print(f"  位置: 第 {operation.position} 行")
        print(f"  內容: {operation.content[:50]}...")

        # 記錄操作
        self.edit_history[file_path].append(operation)
        self.open_files[file_path]["modified"] = True

        # 模擬應用編輯
        time.sleep(0.1)

        print("編輯完成 ✓")
        return True

    def save(self, file_path: str) -> bool:
        """保存文件"""
        if file_path not in self.open_files:
            print(f"錯誤: 文件未打開 {file_path}")
            return False

        file_data = self.open_files[file_path]

        if not file_data["modified"]:
            print("文件未修改，無需保存")
            return True

        print(f"\n保存文件: {file_data['file_info'].name}")

        # 模擬保存
        time.sleep(0.2)

        file_data["modified"] = False
        file_data["file_info"].modified = datetime.now()

        print("文件已保存 ✓")
        return True

    def close(self, file_path: str, save_if_modified: bool = True) -> bool:
        """關閉文件"""
        if file_path not in self.open_files:
            return True

        file_data = self.open_files[file_path]

        if file_data["modified"] and save_if_modified:
            self.save(file_path)

        print(f"\n關閉文件: {file_data['file_info'].name}")
        del self.open_files[file_path]

        return True

    def get_edit_history(self, file_path: str) -> List[EditOperation]:
        """獲取編輯歷史"""
        return self.edit_history.get(file_path, [])


class FileManager:
    """
    文件管理器

    提供高級文件管理功能
    """

    def __init__(self):
        self.explorer = FileExplorer()
        self.editor = FileEditor()

    def find_and_open(self, filename: str, editor: EditorType) -> Optional[FileInfo]:
        """查找並打開文件"""
        print("\n" + "="*60)
        print(f"查找並打開: {filename}")
        print("="*60)

        # 搜索文件
        results = self.explorer.search(filename)

        if not results:
            print("未找到文件")
            return None

        # 打開第一個結果
        file_info = results[0]
        self.editor.open_file(file_info, editor)

        return file_info

    def batch_rename(self, pattern: str, new_pattern: str) -> int:
        """批量重命名文件"""
        print("\n" + "="*60)
        print(f"批量重命名: {pattern} -> {new_pattern}")
        print("="*60)

        # 查找匹配的文件
        matching_files = [
            f for f in self.explorer.mock_files
            if pattern in f.name
        ]

        print(f"找到 {len(matching_files)} 個匹配的文件")

        renamed_count = 0
        for file in matching_files:
            old_name = file.name
            new_name = file.name.replace(pattern, new_pattern)

            print(f"  重命名: {old_name} -> {new_name}")
            file.name = new_name

            renamed_count += 1
            time.sleep(0.05)

        print(f"\n✓ 成功重命名 {renamed_count} 個文件")
        return renamed_count

    def organize_by_type(self) -> Dict[FileType, List[FileInfo]]:
        """按類型整理文件"""
        print("\n" + "="*60)
        print("按類型整理文件")
        print("="*60)

        organized = {}

        for file in self.explorer.mock_files:
            if file.file_type not in organized:
                organized[file.file_type] = []
            organized[file.file_type].append(file)

        for file_type, files in organized.items():
            print(f"\n{file_type.value} ({len(files)} 個):")
            for file in files:
                print(f"  - {file.name}")

        return organized

    def bulk_edit(self, file_pattern: str, search_text: str, replace_text: str) -> int:
        """批量編輯文件內容"""
        print("\n" + "="*60)
        print(f"批量替換: '{search_text}' -> '{replace_text}'")
        print("="*60)

        # 查找匹配的文件
        files = [
            f for f in self.explorer.mock_files
            if file_pattern in f.name and f.file_type in [FileType.TEXT, FileType.CODE]
        ]

        print(f"找到 {len(files)} 個文件需要處理")

        edited_count = 0

        for file in files:
            print(f"\n處理: {file.name}")

            # 打開文件
            editor_type = EditorType.VSCODE if file.file_type == FileType.CODE else EditorType.NOTEPAD
            self.editor.open_file(file, editor_type)

            # 執行替換
            operation = EditOperation(
                operation_type="replace",
                position=0,
                content=f"Replace '{search_text}' with '{replace_text}'"
            )

            self.editor.edit(str(file.path), operation)

            # 保存並關閉
            self.editor.save(str(file.path))
            self.editor.close(str(file.path))

            edited_count += 1

        print(f"\n✓ 成功編輯 {edited_count} 個文件")
        return edited_count


class DocumentProcessor:
    """
    文檔處理器

    處理特定類型的文檔
    """

    def __init__(self):
        self.manager = FileManager()

    def process_word_document(self, filename: str, edits: List[Dict[str, Any]]) -> bool:
        """處理 Word 文檔"""
        print("\n" + "="*60)
        print(f"處理 Word 文檔: {filename}")
        print("="*60)

        # 查找並打開
        file_info = self.manager.find_and_open(filename, EditorType.WORD)

        if not file_info:
            return False

        # 應用編輯
        for i, edit in enumerate(edits, 1):
            print(f"\n應用編輯 {i}/{len(edits)}")

            operation = EditOperation(
                operation_type=edit.get("type", "replace"),
                position=edit.get("position", 0),
                content=edit.get("content", "")
            )

            self.manager.editor.edit(str(file_info.path), operation)

        # 保存
        self.manager.editor.save(str(file_info.path))

        print("\n✓ 文檔處理完成")
        return True

    def merge_text_files(self, filenames: List[str], output_filename: str) -> bool:
        """合併多個文本文件"""
        print("\n" + "="*60)
        print(f"合併文件到: {output_filename}")
        print("="*60)

        merged_content = []

        for filename in filenames:
            results = self.manager.explorer.search(filename)

            if results:
                file_info = results[0]
                print(f"讀取: {file_info.name}")

                # 模擬讀取內容
                content = f"=== {file_info.name} ===\n內容...\n"
                merged_content.append(content)

        # 創建輸出文件（模擬）
        print(f"\n創建輸出文件: {output_filename}")
        print(f"總內容長度: {sum(len(c) for c in merged_content)} 字符")

        print("\n✓ 文件合併完成")
        return True

    def extract_code_snippets(self, filename: str) -> List[str]:
        """從文檔中提取代碼片段"""
        print("\n" + "="*60)
        print(f"提取代碼片段: {filename}")
        print("="*60)

        # 打開文件
        file_info = self.manager.find_and_open(filename, EditorType.VSCODE)

        if not file_info:
            return []

        # 模擬提取代碼片段
        snippets = [
            "def function1():\n    pass",
            "class MyClass:\n    pass",
            "for i in range(10):\n    print(i)"
        ]

        print(f"\n提取到 {len(snippets)} 個代碼片段:")
        for i, snippet in enumerate(snippets, 1):
            print(f"\n片段 {i}:")
            print(snippet)

        return snippets


def 示例1_文件搜索():
    """示例：搜索文件"""
    print("\n" + "="*60)
    print("示例 1: 文件搜索")
    print("="*60)

    explorer = FileExplorer()

    # 按名稱搜索
    explorer.search("報告")

    # 按類型搜索
    explorer.search_by_type(FileType.CODE)

    # 按擴展名搜索
    explorer.search_by_extension(".py")

    return explorer


def 示例2_編輯文件():
    """示例：編輯文件"""
    print("\n" + "="*60)
    print("示例 2: 編輯文件")
    print("="*60)

    manager = FileManager()

    # 查找並打開文件
    file_info = manager.find_and_open("main.py", EditorType.VSCODE)

    if file_info:
        # 執行編輯操作
        operations = [
            EditOperation("insert", 1, "# 這是新增的註釋"),
            EditOperation("replace", 3, "    print('Hello, World!')"),
            EditOperation("insert", 5, "# 添加新函數"),
        ]

        for op in operations:
            manager.editor.edit(str(file_info.path), op)

        # 查看編輯歷史
        history = manager.editor.get_edit_history(str(file_info.path))
        print(f"\n執行了 {len(history)} 個編輯操作")

        # 保存並關閉
        manager.editor.save(str(file_info.path))
        manager.editor.close(str(file_info.path))

    return manager


def 示例3_批量操作():
    """示例：批量文件操作"""
    print("\n" + "="*60)
    print("示例 3: 批量文件操作")
    print("="*60)

    manager = FileManager()

    # 批量重命名
    manager.batch_rename("報告", "月度報告")

    # 按類型整理
    manager.organize_by_type()

    return manager


def 示例4_批量編輯():
    """示例：批量編輯內容"""
    print("\n" + "="*60)
    print("示例 4: 批量編輯內容")
    print("="*60)

    manager = FileManager()

    # 批量替換內容
    manager.bulk_edit(
        file_pattern=".py",
        search_text="print",
        replace_text="logging.info"
    )

    return manager


def 示例5_文檔處理():
    """示例：處理 Word 文檔"""
    print("\n" + "="*60)
    print("示例 5: 處理 Word 文檔")
    print("="*60)

    processor = DocumentProcessor()

    # 編輯 Word 文檔
    edits = [
        {"type": "replace", "position": 1, "content": "更新標題"},
        {"type": "insert", "position": 5, "content": "新增段落內容"},
        {"type": "replace", "position": 10, "content": "更新結論"},
    ]

    processor.process_word_document("報告.docx", edits)

    return processor


if __name__ == "__main__":
    print("Agent-S 文件操作演示\n")

    示例1_文件搜索()
    示例2_編輯文件()
    示例3_批量操作()
    示例4_批量編輯()
    示例5_文檔處理()

    print("\n所有示例執行完成！")
