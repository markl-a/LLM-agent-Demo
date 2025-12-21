"""
Flowise 文檔處理範例
==================

本範例展示如何在 Flowise 中處理各種文檔。

支持的文檔類型：
1. PDF
2. Word (docx)
3. 文本文件
4. CSV/Excel
5. 網頁

安裝依賴：
pip install requests pypdf python-docx pandas
"""

import os
import json
from typing import Dict, Any, List

# ============================================================
# 配置
# ============================================================

FLOWISE_API_URL = os.getenv("FLOWISE_API_URL", "http://localhost:3000")


# ============================================================
# 文檔加載器配置
# ============================================================

PDF_LOADER_CONFIG = '''
{
    "nodes": [
        {
            "id": "pdfFile_0",
            "type": "PDFFile",
            "data": {
                "label": "PDF File",
                "inputs": {
                    "pdfFile": "",
                    "usage": "perPage"
                }
            }
        }
    ]
}
'''

TEXT_LOADER_CONFIG = '''
{
    "nodes": [
        {
            "id": "textFile_0",
            "type": "TextFile",
            "data": {
                "label": "Text File",
                "inputs": {
                    "txtFile": ""
                }
            }
        }
    ]
}
'''

DOCX_LOADER_CONFIG = '''
{
    "nodes": [
        {
            "id": "docxFile_0",
            "type": "DocxFile",
            "data": {
                "label": "Docx File",
                "inputs": {
                    "docxFile": ""
                }
            }
        }
    ]
}
'''

CSV_LOADER_CONFIG = '''
{
    "nodes": [
        {
            "id": "csvFile_0",
            "type": "CSVFile",
            "data": {
                "label": "CSV File",
                "inputs": {
                    "csvFile": "",
                    "columnName": ""
                }
            }
        }
    ]
}
'''

WEB_LOADER_CONFIG = '''
{
    "nodes": [
        {
            "id": "cheerioWebScraper_0",
            "type": "CheerioWebScraper",
            "data": {
                "label": "Web Scraper",
                "inputs": {
                    "url": "",
                    "selector": "body"
                }
            }
        }
    ]
}
'''


# ============================================================
# 文本分割配置
# ============================================================

TEXT_SPLITTER_CONFIG = '''
{
    "nodes": [
        {
            "id": "recursiveCharacterTextSplitter_0",
            "type": "RecursiveCharacterTextSplitter",
            "data": {
                "label": "Recursive Text Splitter",
                "inputs": {
                    "chunkSize": 1000,
                    "chunkOverlap": 200
                }
            }
        }
    ]
}
'''

MARKDOWN_SPLITTER_CONFIG = '''
{
    "nodes": [
        {
            "id": "markdownTextSplitter_0",
            "type": "MarkdownTextSplitter",
            "data": {
                "label": "Markdown Splitter",
                "inputs": {
                    "chunkSize": 1000,
                    "chunkOverlap": 0
                }
            }
        }
    ]
}
'''


# ============================================================
# 完整文檔處理流程
# ============================================================

DOCUMENT_QA_FLOW = '''
{
    "nodes": [
        {
            "id": "pdfFile_0",
            "type": "PDFFile",
            "data": {
                "label": "PDF Document"
            }
        },
        {
            "id": "recursiveCharacterTextSplitter_0",
            "type": "RecursiveCharacterTextSplitter",
            "data": {
                "inputs": {
                    "chunkSize": 1000,
                    "chunkOverlap": 200
                }
            }
        },
        {
            "id": "openAIEmbeddings_0",
            "type": "OpenAIEmbeddings"
        },
        {
            "id": "faiss_0",
            "type": "Faiss",
            "data": {
                "inputs": {
                    "basePath": "./document_store"
                }
            }
        },
        {
            "id": "chatOpenAI_0",
            "type": "ChatOpenAI",
            "data": {
                "inputs": {
                    "modelName": "gpt-4"
                }
            }
        },
        {
            "id": "conversationalRetrievalQA_0",
            "type": "ConversationalRetrievalQAChain"
        }
    ],
    "edges": [
        {"source": "pdfFile_0", "target": "recursiveCharacterTextSplitter_0"},
        {"source": "recursiveCharacterTextSplitter_0", "target": "faiss_0", "targetHandle": "document"},
        {"source": "openAIEmbeddings_0", "target": "faiss_0"},
        {"source": "faiss_0", "target": "conversationalRetrievalQA_0", "targetHandle": "vectorStoreRetriever"},
        {"source": "chatOpenAI_0", "target": "conversationalRetrievalQA_0", "targetHandle": "model"}
    ]
}
'''


# ============================================================
# 使用範例
# ============================================================

def example_pdf_loader():
    """範例 1: PDF 加載器"""
    print("=" * 50)
    print("範例 1: PDF 加載器")
    print("=" * 50)
    print(PDF_LOADER_CONFIG)


def example_text_splitter():
    """範例 2: 文本分割器"""
    print("\n" + "=" * 50)
    print("範例 2: 文本分割器")
    print("=" * 50)
    print(TEXT_SPLITTER_CONFIG)


def example_web_scraper():
    """範例 3: 網頁抓取器"""
    print("\n" + "=" * 50)
    print("範例 3: 網頁抓取器")
    print("=" * 50)
    print(WEB_LOADER_CONFIG)


def example_document_qa():
    """範例 4: 文檔問答流程"""
    print("\n" + "=" * 50)
    print("範例 4: 文檔問答流程")
    print("=" * 50)
    print(DOCUMENT_QA_FLOW[:1000] + "...")


def example_upload_api():
    """範例 5: 文檔上傳 API"""
    print("\n" + "=" * 50)
    print("範例 5: 文檔上傳 API")
    print("=" * 50)
    print("""
# 上傳文檔到 Flowise
curl -X POST http://localhost:3000/api/v1/vector/upsert/{chatflowId} \\
    -F "files=@document.pdf" \\
    -H "Authorization: Bearer YOUR_API_KEY"

# 使用 Python
import requests

files = {'files': open('document.pdf', 'rb')}
response = requests.post(
    f"{FLOWISE_API_URL}/api/v1/vector/upsert/{chatflow_id}",
    files=files,
    headers={"Authorization": f"Bearer {api_key}"}
)
""")


def example_batch_processing():
    """範例 6: 批量處理"""
    print("\n" + "=" * 50)
    print("範例 6: 批量處理文檔")
    print("=" * 50)
    print("""
# 批量上傳多個文檔
import os
import requests

def upload_documents(folder_path, chatflow_id, api_key):
    for filename in os.listdir(folder_path):
        if filename.endswith(('.pdf', '.docx', '.txt')):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'rb') as f:
                files = {'files': f}
                response = requests.post(
                    f"{api_url}/api/v1/vector/upsert/{chatflow_id}",
                    files=files,
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                print(f"上傳 {filename}: {response.status_code}")
""")


def example_metadata():
    """範例 7: 文檔元數據"""
    print("\n" + "=" * 50)
    print("範例 7: 文檔元數據處理")
    print("=" * 50)
    print("""
{
    "nodes": [
        {
            "id": "metadata_0",
            "type": "JsonTransformator",
            "data": {
                "inputs": {
                    "transformFunction": "return { ...doc, metadata: { source: doc.metadata.source, page: doc.metadata.page, timestamp: new Date().toISOString() } }"
                }
            }
        }
    ]
}
""")


if __name__ == "__main__":
    print("Flowise 文檔處理範例\\n")
    example_pdf_loader()
    example_text_splitter()
    example_web_scraper()
    example_document_qa()
    example_upload_api()
    example_batch_processing()
    example_metadata()
