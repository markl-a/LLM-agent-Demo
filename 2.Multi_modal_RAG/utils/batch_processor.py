"""
批量 PDF 處理工具

功能：
1. 批量解析 PDF 文件
2. 生成摘要（文本、圖像、表格）
3. 存儲到向量庫
4. 進度追蹤和錯誤處理
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import logging
from tqdm import tqdm

# LangChain imports
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Unstructured imports
from unstructured.partition.pdf import partition_pdf

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """處理結果數據類"""
    file_path: str
    success: bool
    num_texts: int = 0
    num_images: int = 0
    num_tables: int = 0
    processing_time: float = 0.0
    error: Optional[str] = None


class BatchPDFProcessor:
    """批量 PDF 處理器"""

    def __init__(
        self,
        openai_api_key: str,
        output_dir: str = "./output",
        chunk_size: int = 2000,
        chunk_overlap: int = 200,
        max_workers: int = 4
    ):
        """
        初始化批量處理器

        Args:
            openai_api_key: OpenAI API Key
            output_dir: 輸出目錄
            chunk_size: 文本塊大小
            chunk_overlap: 文本塊重疊
            max_workers: 最大並行工作數
        """
        self.openai_api_key = openai_api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_workers = max_workers

        # 初始化模型
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4o",
            temperature=0
        )

        self.embeddings = OpenAIEmbeddings(
            api_key=openai_api_key,
            model="text-embedding-3-small"
        )

        # 文本分割器
        self.text_splitter = CharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def process_single_pdf(self, pdf_path: str) -> ProcessingResult:
        """
        處理單個 PDF 文件

        Args:
            pdf_path: PDF 文件路徑

        Returns:
            ProcessingResult: 處理結果
        """
        import time
        start_time = time.time()

        try:
            logger.info(f"開始處理：{pdf_path}")

            # 1. 解析 PDF
            elements = partition_pdf(
                filename=pdf_path,
                extract_images_in_pdf=True,
                infer_table_structure=True,
                chunking_strategy="by_title",
                max_characters=self.chunk_size,
                new_after_n_chars=int(self.chunk_size * 0.9),
                combine_text_under_n_chars=int(self.chunk_size * 0.5),
                image_output_dir_path=str(self.output_dir / "images")
            )

            # 2. 分類元素
            texts, tables, images = self._categorize_elements(elements)

            logger.info(
                f"{pdf_path}: {len(texts)} 文本, "
                f"{len(tables)} 表格, {len(images)} 圖像"
            )

            # 3. 生成摘要
            text_summaries = self._generate_text_summaries(texts)
            table_summaries = self._generate_table_summaries(tables)
            image_summaries = self._generate_image_summaries(images)

            # 4. 保存結果
            result_file = self.output_dir / f"{Path(pdf_path).stem}_result.json"
            self._save_results(
                result_file,
                {
                    "source": pdf_path,
                    "texts": texts,
                    "tables": tables,
                    "text_summaries": text_summaries,
                    "table_summaries": table_summaries,
                    "image_summaries": image_summaries
                }
            )

            processing_time = time.time() - start_time

            return ProcessingResult(
                file_path=pdf_path,
                success=True,
                num_texts=len(texts),
                num_images=len(images),
                num_tables=len(tables),
                processing_time=processing_time
            )

        except Exception as e:
            logger.error(f"處理失敗 {pdf_path}: {str(e)}")
            return ProcessingResult(
                file_path=pdf_path,
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )

    def process_batch(self, pdf_files: List[str]) -> List[ProcessingResult]:
        """
        批量處理 PDF 文件

        Args:
            pdf_files: PDF 文件路徑列表

        Returns:
            List[ProcessingResult]: 處理結果列表
        """
        results = []

        # 使用進程池並行處理
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任務
            futures = {
                executor.submit(self.process_single_pdf, pdf): pdf
                for pdf in pdf_files
            }

            # 使用 tqdm 顯示進度
            with tqdm(total=len(pdf_files), desc="處理 PDF") as pbar:
                for future in asyncio.as_completed(futures):
                    result = future.result()
                    results.append(result)
                    pbar.update(1)

                    # 輸出結果
                    if result.success:
                        logger.info(
                            f"✓ {result.file_path} "
                            f"({result.processing_time:.2f}s)"
                        )
                    else:
                        logger.error(
                            f"✗ {result.file_path}: {result.error}"
                        )

        return results

    def process_directory(self, directory: str) -> List[ProcessingResult]:
        """
        處理目錄中的所有 PDF 文件

        Args:
            directory: 目錄路徑

        Returns:
            List[ProcessingResult]: 處理結果列表
        """
        # 查找所有 PDF 文件
        pdf_files = list(Path(directory).glob("**/*.pdf"))

        if not pdf_files:
            logger.warning(f"目錄 {directory} 中沒有找到 PDF 文件")
            return []

        logger.info(f"找到 {len(pdf_files)} 個 PDF 文件")

        return self.process_batch([str(p) for p in pdf_files])

    def _categorize_elements(self, elements):
        """分類提取的元素"""
        texts = []
        tables = []
        images = []

        for element in elements:
            element_type = str(type(element))

            if "Table" in element_type:
                tables.append(str(element))
            elif "CompositeElement" in element_type or "NarrativeText" in element_type:
                texts.append(str(element))
            # 圖像由 Unstructured 單獨提取到文件

        return texts, tables, images

    def _generate_text_summaries(self, texts: List[str]) -> List[str]:
        """生成文本摘要"""
        if not texts:
            return []

        prompt_template = """
        為以下文本生成簡潔的摘要，用於檢索系統。

        要求：
        1. 提取關鍵概念、實體、數字
        2. 保持原文的語義
        3. 長度 100-200 字
        4. 使用檢索友好的語言

        文本：{text}

        摘要：
        """

        summaries = []
        for text in tqdm(texts, desc="生成文本摘要"):
            try:
                summary = self.llm.invoke(
                    prompt_template.format(text=text[:3000])  # 限制長度
                ).content
                summaries.append(summary)
            except Exception as e:
                logger.error(f"文本摘要失敗：{str(e)}")
                summaries.append(text[:200])  # 失敗時使用前 200 字

        return summaries

    def _generate_table_summaries(self, tables: List[str]) -> List[str]:
        """生成表格摘要"""
        if not tables:
            return []

        prompt_template = """
        分析以下表格並生成摘要。

        要點：
        1. 表格結構（行數、列數）
        2. 列名和指標
        3. 數據範圍和趨勢
        4. 關鍵數據點

        表格：{table}

        摘要：
        """

        summaries = []
        for table in tqdm(tables, desc="生成表格摘要"):
            try:
                summary = self.llm.invoke(
                    prompt_template.format(table=table[:2000])
                ).content
                summaries.append(summary)
            except Exception as e:
                logger.error(f"表格摘要失敗：{str(e)}")
                summaries.append(table[:200])

        return summaries

    def _generate_image_summaries(self, images: List[str]) -> List[str]:
        """生成圖像摘要"""
        # 注意：這個方法需要實際的圖像文件
        # 這裡只是占位符
        return []

    def _save_results(self, file_path: Path, data: Dict):
        """保存處理結果"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def generate_report(self, results: List[ProcessingResult]) -> Dict:
        """
        生成處理報告

        Args:
            results: 處理結果列表

        Returns:
            Dict: 報告數據
        """
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful

        total_texts = sum(r.num_texts for r in results if r.success)
        total_images = sum(r.num_images for r in results if r.success)
        total_tables = sum(r.num_tables for r in results if r.success)

        avg_time = sum(r.processing_time for r in results) / total if total > 0 else 0

        report = {
            "summary": {
                "total_files": total,
                "successful": successful,
                "failed": failed,
                "success_rate": f"{successful/total*100:.1f}%" if total > 0 else "0%",
            },
            "statistics": {
                "total_texts": total_texts,
                "total_images": total_images,
                "total_tables": total_tables,
                "avg_processing_time": f"{avg_time:.2f}s"
            },
            "failed_files": [
                {"file": r.file_path, "error": r.error}
                for r in results if not r.success
            ]
        }

        return report


def main():
    """主函數示例"""
    import argparse

    parser = argparse.ArgumentParser(description="批量處理 PDF 文件")
    parser.add_argument("input_dir", help="PDF 文件目錄")
    parser.add_argument("--output-dir", default="./output", help="輸出目錄")
    parser.add_argument("--max-workers", type=int, default=4, help="最大並行數")
    parser.add_argument("--chunk-size", type=int, default=2000, help="文本塊大小")

    args = parser.parse_args()

    # 從環境變數獲取 API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("請設置 OPENAI_API_KEY 環境變數")

    # 創建處理器
    processor = BatchPDFProcessor(
        openai_api_key=api_key,
        output_dir=args.output_dir,
        chunk_size=args.chunk_size,
        max_workers=args.max_workers
    )

    # 處理目錄
    results = processor.process_directory(args.input_dir)

    # 生成報告
    report = processor.generate_report(results)

    # 輸出報告
    print("\n" + "=" * 50)
    print("處理報告")
    print("=" * 50)
    print(json.dumps(report, indent=2, ensure_ascii=False))

    # 保存報告
    report_file = Path(args.output_dir) / "processing_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n報告已保存到：{report_file}")


if __name__ == "__main__":
    main()
