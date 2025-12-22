"""
FileSurfer - 文件操作 Agent
===================================

FileSurfer 是 Magentic-One 的文件系統專家，負責：
1. 文件和目錄的讀寫操作
2. 多種文件格式的解析和處理
3. 批量文件操作
4. 文件搜索和過濾
5. 文檔格式轉換

支持格式：
- 文本：TXT, MD, JSON, XML, YAML
- 文檔：PDF, DOCX, XLSX, PPTX
- 代碼：PY, JS, JAVA, CPP 等
- 數據：CSV, JSON, XML
- 圖像：PNG, JPG（元數據）
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path


class FileSurferAgent:
    """
    文件操作 Agent

    提供全面的文件系統操作能力
    """

    def __init__(
        self,
        llm_config: Dict[str, Any],
        work_dir: str = "./workspace",
        max_file_size: int = 100 * 1024 * 1024  # 100MB
    ):
        """
        初始化 FileSurfer

        Args:
            llm_config: LLM 配置
            work_dir: 工作目錄
            max_file_size: 最大文件大小（字節）
        """
        self.llm_config = llm_config
        self.work_dir = Path(work_dir)
        self.max_file_size = max_file_size

        # 確保工作目錄存在
        self.work_dir.mkdir(parents=True, exist_ok=True)

        # 統計
        self.stats = {
            'files_read': 0,
            'files_written': 0,
            'directories_created': 0,
            'files_deleted': 0,
            'searches_performed': 0
        }

        # 支持的文件類型
        self.supported_formats = {
            'text': ['.txt', '.md', '.json', '.xml', '.yaml', '.yml'],
            'document': ['.pdf', '.docx', '.xlsx', '.pptx'],
            'code': ['.py', '.js', '.java', '.cpp', '.c', '.h', '.ts'],
            'data': ['.csv', '.json', '.xml'],
            'image': ['.png', '.jpg', '.jpeg', '.gif']
        }

    def read_file(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        讀取文件

        Args:
            file_path: 文件路徑
            encoding: 編碼格式

        Returns:
            讀取結果
        """
        print(f"\n📖 讀取文件: {file_path}")

        try:
            full_path = self._resolve_path(file_path)

            # 檢查文件大小
            file_size = self._get_file_size(full_path)
            if file_size > self.max_file_size:
                return {
                    'success': False,
                    'error': f'文件過大: {file_size} bytes (限制: {self.max_file_size})'
                }

            # 根據文件類型讀取
            file_type = self._detect_file_type(full_path)

            if file_type in ['text', 'code']:
                content = self._read_text_file(full_path, encoding)
            elif file_type == 'document':
                content = self._read_document(full_path)
            elif file_type == 'data':
                content = self._read_data_file(full_path)
            else:
                content = f"不支持的文件類型: {file_type}"

            self.stats['files_read'] += 1

            print(f"✓ 讀取成功 ({file_size} bytes)")

            return {
                'success': True,
                'file_path': str(full_path),
                'file_type': file_type,
                'size': file_size,
                'content': content
            }

        except Exception as e:
            print(f"✗ 讀取失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def write_file(
        self,
        file_path: str,
        content: str,
        encoding: str = 'utf-8',
        mode: str = 'w'
    ) -> Dict[str, Any]:
        """
        寫入文件

        Args:
            file_path: 文件路徑
            content: 文件內容
            encoding: 編碼格式
            mode: 寫入模式 (w=覆蓋, a=追加)

        Returns:
            寫入結果
        """
        print(f"\n✏️ 寫入文件: {file_path}")

        try:
            full_path = self._resolve_path(file_path)

            # 確保父目錄存在
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # 根據文件類型寫入
            file_type = self._detect_file_type(full_path)

            if file_type in ['text', 'code']:
                bytes_written = self._write_text_file(full_path, content, encoding, mode)
            elif file_type == 'data' and full_path.suffix == '.json':
                bytes_written = self._write_json_file(full_path, content)
            else:
                bytes_written = self._write_text_file(full_path, content, encoding, mode)

            self.stats['files_written'] += 1

            print(f"✓ 寫入成功 ({bytes_written} bytes)")

            return {
                'success': True,
                'file_path': str(full_path),
                'bytes_written': bytes_written
            }

        except Exception as e:
            print(f"✗ 寫入失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def list_directory(
        self,
        directory: str = ".",
        pattern: str = "*",
        recursive: bool = False
    ) -> Dict[str, Any]:
        """
        列出目錄內容

        Args:
            directory: 目錄路徑
            pattern: 文件模式（如 *.py）
            recursive: 是否遞歸

        Returns:
            目錄內容
        """
        print(f"\n📁 列出目錄: {directory}")

        try:
            dir_path = self._resolve_path(directory)

            if recursive:
                files = list(dir_path.rglob(pattern))
            else:
                files = list(dir_path.glob(pattern))

            # 分類文件和目錄
            result = {
                'directories': [],
                'files': []
            }

            for item in sorted(files):
                item_info = {
                    'name': item.name,
                    'path': str(item),
                    'size': item.stat().st_size if item.is_file() else 0,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }

                if item.is_dir():
                    result['directories'].append(item_info)
                else:
                    result['files'].append(item_info)

            print(f"✓ 找到 {len(result['directories'])} 個目錄, {len(result['files'])} 個文件")

            return {
                'success': True,
                'directory': str(dir_path),
                'pattern': pattern,
                'recursive': recursive,
                'result': result
            }

        except Exception as e:
            print(f"✗ 列出失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def search_files(
        self,
        directory: str,
        search_term: str,
        file_pattern: str = "*",
        case_sensitive: bool = False
    ) -> Dict[str, Any]:
        """
        搜索文件內容

        Args:
            directory: 搜索目錄
            search_term: 搜索詞
            file_pattern: 文件模式
            case_sensitive: 是否區分大小寫

        Returns:
            搜索結果
        """
        print(f"\n🔍 搜索文件: '{search_term}' in {directory}")

        try:
            dir_path = self._resolve_path(directory)
            matches = []

            # 獲取所有匹配的文件
            files = dir_path.rglob(file_pattern)

            for file_path in files:
                if not file_path.is_file():
                    continue

                # 讀取文件並搜索
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # 搜索
                    if not case_sensitive:
                        content_search = content.lower()
                        term_search = search_term.lower()
                    else:
                        content_search = content
                        term_search = search_term

                    if term_search in content_search:
                        # 找到匹配的行
                        lines = content.split('\n')
                        matched_lines = []

                        for i, line in enumerate(lines, 1):
                            line_search = line if case_sensitive else line.lower()
                            if term_search in line_search:
                                matched_lines.append({
                                    'line_number': i,
                                    'content': line.strip()
                                })

                        matches.append({
                            'file': str(file_path),
                            'total_matches': len(matched_lines),
                            'matched_lines': matched_lines[:10]  # 最多顯示 10 行
                        })

                except Exception as e:
                    print(f"  跳過文件 {file_path}: {e}")

            self.stats['searches_performed'] += 1

            print(f"✓ 在 {len(matches)} 個文件中找到匹配")

            return {
                'success': True,
                'search_term': search_term,
                'files_searched': len(list(dir_path.rglob(file_pattern))),
                'files_matched': len(matches),
                'matches': matches
            }

        except Exception as e:
            print(f"✗ 搜索失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_directory(self, directory: str) -> Dict[str, Any]:
        """
        創建目錄

        Args:
            directory: 目錄路徑

        Returns:
            創建結果
        """
        print(f"\n📂 創建目錄: {directory}")

        try:
            dir_path = self._resolve_path(directory)
            dir_path.mkdir(parents=True, exist_ok=True)

            self.stats['directories_created'] += 1

            print(f"✓ 目錄已創建")

            return {
                'success': True,
                'directory': str(dir_path)
            }

        except Exception as e:
            print(f"✗ 創建失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        刪除文件

        Args:
            file_path: 文件路徑

        Returns:
            刪除結果
        """
        print(f"\n🗑️ 刪除文件: {file_path}")

        try:
            full_path = self._resolve_path(file_path)

            if full_path.is_file():
                full_path.unlink()
                self.stats['files_deleted'] += 1
                print(f"✓ 文件已刪除")
            else:
                return {
                    'success': False,
                    'error': '文件不存在'
                }

            return {
                'success': True,
                'file_path': str(full_path)
            }

        except Exception as e:
            print(f"✗ 刪除失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def copy_file(self, source: str, destination: str) -> Dict[str, Any]:
        """
        複製文件

        Args:
            source: 源文件路徑
            destination: 目標路徑

        Returns:
            複製結果
        """
        print(f"\n📋 複製文件: {source} → {destination}")

        try:
            src_path = self._resolve_path(source)
            dst_path = self._resolve_path(destination)

            # 確保目標目錄存在
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            # 讀取並寫入
            content = src_path.read_bytes()
            dst_path.write_bytes(content)

            print(f"✓ 文件已複製 ({len(content)} bytes)")

            return {
                'success': True,
                'source': str(src_path),
                'destination': str(dst_path),
                'bytes_copied': len(content)
            }

        except Exception as e:
            print(f"✗ 複製失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        獲取文件信息

        Args:
            file_path: 文件路徑

        Returns:
            文件信息
        """
        print(f"\nℹ️ 獲取文件信息: {file_path}")

        try:
            full_path = self._resolve_path(file_path)
            stat = full_path.stat()

            info = {
                'name': full_path.name,
                'path': str(full_path),
                'size': stat.st_size,
                'size_human': self._format_size(stat.st_size),
                'is_file': full_path.is_file(),
                'is_directory': full_path.is_dir(),
                'extension': full_path.suffix,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'file_type': self._detect_file_type(full_path)
            }

            print(f"✓ 文件信息已獲取")

            return {
                'success': True,
                'info': info
            }

        except Exception as e:
            print(f"✗ 獲取失敗: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # 內部輔助方法

    def _resolve_path(self, path: str) -> Path:
        """解析路徑"""
        p = Path(path)
        if not p.is_absolute():
            p = self.work_dir / p
        return p

    def _get_file_size(self, path: Path) -> int:
        """獲取文件大小"""
        if path.exists() and path.is_file():
            return path.stat().st_size
        return 0

    def _detect_file_type(self, path: Path) -> str:
        """檢測文件類型"""
        ext = path.suffix.lower()

        for type_name, extensions in self.supported_formats.items():
            if ext in extensions:
                return type_name

        return 'unknown'

    def _read_text_file(self, path: Path, encoding: str) -> str:
        """讀取文本文件"""
        with open(path, 'r', encoding=encoding) as f:
            return f.read()

    def _read_document(self, path: Path) -> str:
        """讀取文檔文件（模擬）"""
        return f"這是從 {path.name} 提取的文檔內容"

    def _read_data_file(self, path: Path) -> Any:
        """讀取數據文件"""
        if path.suffix == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif path.suffix == '.csv':
            return "CSV 數據（需要 pandas 庫）"
        else:
            return self._read_text_file(path, 'utf-8')

    def _write_text_file(self, path: Path, content: str, encoding: str, mode: str) -> int:
        """寫入文本文件"""
        with open(path, mode, encoding=encoding) as f:
            f.write(content)
        return len(content.encode(encoding))

    def _write_json_file(self, path: Path, content: Any) -> int:
        """寫入 JSON 文件"""
        if isinstance(content, str):
            content = json.loads(content)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

        return path.stat().st_size

    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def get_statistics(self) -> Dict[str, Any]:
        """獲取統計數據"""
        return self.stats.copy()


def demo_file_operations():
    """文件操作示範"""
    print("=" * 60)
    print("範例 1: 基本文件操作")
    print("=" * 60)

    file_surfer = FileSurferAgent(
        llm_config={"model": "gpt-4"},
        work_dir="./test_workspace"
    )

    # 寫入文件
    content = """# 測試文件

這是一個測試文件的內容。

## 功能列表
- 功能 1
- 功能 2
- 功能 3
"""

    result = file_surfer.write_file("test.md", content)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 讀取文件
    result = file_surfer.read_file("test.md")
    print("\n讀取的內容:")
    print(result['content'])


def demo_directory_operations():
    """目錄操作示範"""
    print("\n" + "=" * 60)
    print("範例 2: 目錄操作")
    print("=" * 60)

    file_surfer = FileSurferAgent(llm_config={"model": "gpt-4"})

    # 創建目錄
    file_surfer.create_directory("test_dir/subdir")

    # 列出目錄
    result = file_surfer.list_directory(".", pattern="*", recursive=False)

    print("\n目錄內容:")
    print(f"目錄: {len(result['result']['directories'])}")
    print(f"文件: {len(result['result']['files'])}")


def demo_file_search():
    """文件搜索示範"""
    print("\n" + "=" * 60)
    print("範例 3: 文件搜索")
    print("=" * 60)

    file_surfer = FileSurferAgent(llm_config={"model": "gpt-4"})

    # 創建測試文件
    file_surfer.write_file("file1.txt", "這是包含 Python 關鍵字的文件")
    file_surfer.write_file("file2.txt", "這是另一個包含 Python 的文件")

    # 搜索
    result = file_surfer.search_files(".", "Python", file_pattern="*.txt")

    print("\n搜索結果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def demo_file_info():
    """文件信息示範"""
    print("\n" + "=" * 60)
    print("範例 4: 文件信息")
    print("=" * 60)

    file_surfer = FileSurferAgent(llm_config={"model": "gpt-4"})

    # 創建文件
    file_surfer.write_file("example.json", '{"key": "value"}')

    # 獲取信息
    result = file_surfer.get_file_info("example.json")

    print("\n文件信息:")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


def demo_batch_operations():
    """批量操作示範"""
    print("\n" + "=" * 60)
    print("範例 5: 批量文件操作")
    print("=" * 60)

    file_surfer = FileSurferAgent(llm_config={"model": "gpt-4"})

    # 批量創建文件
    for i in range(5):
        file_surfer.write_file(
            f"batch_file_{i}.txt",
            f"這是批量文件 {i}\n內容示例"
        )

    # 列出所有批量文件
    result = file_surfer.list_directory(".", pattern="batch_file_*")

    print(f"\n創建了 {len(result['result']['files'])} 個文件")

    # 獲取統計
    stats = file_surfer.get_statistics()
    print("\n統計數據:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    demo_file_operations()
    demo_directory_operations()
    demo_file_search()
    demo_file_info()
    demo_batch_operations()

    print("\n" + "=" * 60)
    print("FileSurfer 示範完成！")
    print("=" * 60)
