#!/usr/bin/env python3
"""Haystack - Web 檢索示例"""
from haystack.components.fetchers import LinkContentFetcher
from haystack.components.converters import HTMLToDocument

fetcher = LinkContentFetcher()
converter = HTMLToDocument()

print("✅ Web 內容抓取器已創建")
print("🌐 可抓取網頁並轉換為文檔")
