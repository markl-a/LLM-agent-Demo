#!/usr/bin/env python3
"""Haystack - 文檔處理與預處理示例"""

from haystack import Document
from haystack.components.preprocessors import DocumentSplitter, DocumentCleaner
from haystack.components.converters import TextFileToDocument, PDFToDocument

# 示例 1: 文檔清理
cleaner = DocumentCleaner(
    remove_empty_lines=True,
    remove_extra_whitespaces=True,
    remove_repeated_substrings=True
)

docs = [Document(content="這是  重複的  文本\n\n\n多餘空行")]
cleaned = cleaner.run(documents=docs)
print("✅ 文檔清理:", cleaned["documents"][0].content)

# 示例 2: 文檔分割
splitter = DocumentSplitter(
    split_by="sentence",
    split_length=3,
    split_overlap=1
)

long_doc = Document(content="句子一。句子二。句子三。句子四。句子五。")
chunks = splitter.run(documents=[long_doc])
print(f"✅ 分割成 {len(chunks['documents'])} 個塊")

# 示例 3: PDF 轉換
converter = PDFToDocument()
# pdf_docs = converter.run(sources=["document.pdf"])

print("\n📄 Haystack 文檔處理完成")
