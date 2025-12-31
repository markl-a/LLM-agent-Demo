"""
Txtai - API 服務範例

本範例展示：
1. RESTful API 構建
2. FastAPI 整合
3. 服務部署
4. API 端點設計
5. 性能優化

安裝：pip install txtai sentence-transformers fastapi uvicorn
"""

from txtai import Embeddings
from typing import List, Optional
import asyncio


# ============================================================================
# 範例 1: 基本 API 服務結構
# ============================================================================

def example_1_basic_api():
    """基本 API 服務結構"""
    print("\n" + "="*60)
    print("範例 1: 基本 API 服務結構")
    print("="*60)

    print("✓ API 服務組件:")
    print("  - FastAPI 應用")
    print("  - Embeddings 索引")
    print("  - RESTful 端點")
    print("  - 請求/響應模型")


# ============================================================================
# 範例 2: 搜索 API 端點
# ============================================================================

def example_2_search_endpoint():
    """搜索 API 端點設計"""
    print("\n" + "="*60)
    print("範例 2: 搜索 API 端點")
    print("="*60)

    # 模擬 API 端點邏輯
    embeddings = Embeddings({"content": True})

    documents = [
        "Python programming tutorial",
        "JavaScript web development",
        "Machine learning basics",
    ]

    embeddings.index([(i, doc, None) for i, doc in enumerate(documents)])

    # 模擬搜索請求
    query = "programming"
    results = embeddings.search(query, limit=2)

    print(f"模擬 API 響應:")
    print(f"  查詢: {query}")
    print(f"  結果數: {len(results)}")
    for result in results:
        print(f"    - {result['text']}")


# ============================================================================
# 範例 3: 索引管理 API
# ============================================================================

def example_3_index_management():
    """索引管理 API"""
    print("\n" + "="*60)
    print("範例 3: 索引管理 API")
    print("="*60)

    print("✓ 索引管理端點:")
    print("  POST   /index     - 創建/更新索引")
    print("  DELETE /index/:id - 刪除文檔")
    print("  GET    /index/stats - 獲取索引統計")


# ============================================================================
# 範例 4: 批量操作 API
# ============================================================================

def example_4_batch_api():
    """批量操作 API"""
    print("\n" + "="*60)
    print("範例 4: 批量操作 API")
    print("="*60)

    embeddings = Embeddings()

    # 模擬批量索引
    batch = [
        {"id": i, "text": f"Document {i}"}
        for i in range(5)
    ]

    documents = [(item["id"], item["text"], None) for item in batch]
    embeddings.index(documents)

    print(f"✓ 批量索引 {len(batch)} 個文檔")


# ============================================================================
# 範例 5: 異步 API 處理
# ============================================================================

async def example_5_async_api():
    """異步 API 處理"""
    print("\n" + "="*60)
    print("範例 5: 異步 API 處理")
    print("="*60)

    print("✓ 異步處理優勢:")
    print("  - 更高的併發性")
    print("  - 更好的資源利用")
    print("  - 非阻塞 I/O")

    # 模擬異步操作
    await asyncio.sleep(0.1)
    print("  異步操作完成")


# ============================================================================
# 範例 6-10: 更多 API 功能
# ============================================================================

def example_6_error_handling():
    """API 錯誤處理"""
    print("\n" + "="*60)
    print("範例 6: API 錯誤處理")
    print("="*60)

    print("✓ 錯誤處理策略:")
    print("  - 400: 無效請求")
    print("  - 404: 資源未找到")
    print("  - 500: 服務器錯誤")
    print("  - 統一的錯誤響應格式")


def example_7_authentication():
    """API 認證"""
    print("\n" + "="*60)
    print("範例 7: API 認證")
    print("="*60)

    print("✓ 認證方法:")
    print("  - API Key")
    print("  - JWT Token")
    print("  - OAuth 2.0")


def example_8_rate_limiting():
    """API 速率限制"""
    print("\n" + "="*60)
    print("範例 8: 速率限制")
    print("="*60)

    print("✓ 速率限制:")
    print("  - 每分鐘請求限制")
    print("  - IP 基礎限制")
    print("  - 用戶級別限制")


def example_9_caching():
    """API 緩存"""
    print("\n" + "="*60)
    print("範例 9: API 緩存")
    print("="*60)

    print("✓ 緩存策略:")
    print("  - 查詢結果緩存")
    print("  - Redis 整合")
    print("  - TTL 配置")


def example_10_deployment():
    """API 部署"""
    print("\n" + "="*60)
    print("範例 10: API 部署")
    print("="*60)

    print("✓ 部署選項:")
    print("  - Docker 容器化")
    print("  - Kubernetes 編排")
    print("  - 雲平台部署 (AWS, GCP, Azure)")
    print("\n啟動命令示例:")
    print("  uvicorn api:app --host 0.0.0.0 --port 8000")


# ============================================================================
# 主程式
# ============================================================================

def main():
    """運行所有範例"""
    print("\n" + "="*60)
    print("🌐 Txtai - API 服務範例")
    print("="*60)

    example_1_basic_api()
    example_2_search_endpoint()
    example_3_index_management()
    example_4_batch_api()
    asyncio.run(example_5_async_api())
    example_6_error_handling()
    example_7_authentication()
    example_8_rate_limiting()
    example_9_caching()
    example_10_deployment()

    print("\n" + "="*60)
    print("✓ 所有 API 服務範例完成！")
    print("="*60)
    print("\n提示: 查看 FastAPI 文檔了解更多細節")
    print("     https://fastapi.tiangolo.com/\n")


if __name__ == '__main__':
    main()
