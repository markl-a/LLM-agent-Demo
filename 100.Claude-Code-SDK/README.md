# Claude Code SDK - Anthropic 官方 Agent 開發框架

## 簡介

Claude Code SDK 是 Anthropic 官方推出的 Agent 開發框架，專為構建智能、可靠的 AI Agent 應用而設計。該框架提供了完整的工具集，讓開發者能夠輕鬆利用 Claude 的強大能力構建生產級的 Agent 系統。

Claude Code SDK 不僅僅是一個 API 封裝，它提供了完整的 Agent 開發生態系統，包括對話管理、工具調用、流式輸出、多輪對話、文件處理、代碼執行等核心功能。框架特別強調類型安全、錯誤處理和生產環境的可靠性。

## 核心特點

### 1. 原生 Claude 支持
- **官方支持**: Anthropic 官方維護，與 Claude 完美整合
- **最新特性**: 第一時間支持 Claude 的新功能
- **性能優化**: 針對 Claude 優化的請求處理
- **最佳實踐**: 內建 Claude 使用最佳實踐

### 2. 強大的工具系統
- **工具定義**: 簡潔的工具定義 API
- **自動驗證**: 自動參數驗證和類型檢查
- **並行調用**: 支持並行工具調用優化性能
- **錯誤處理**: 完善的工具執行錯誤處理
- **工具鏈**: 支持複雜的工具調用鏈

### 3. 流式處理
- **實時響應**: 支持流式文本輸出
- **工具流式**: 流式工具調用和結果返回
- **事件驅動**: 基於事件的流式處理架構
- **取消支持**: 支持中斷長時間運行的請求

### 4. 多輪對話管理
- **對話歷史**: 自動管理對話上下文
- **狀態持久化**: 支持對話狀態保存和恢復
- **上下文優化**: 智能壓縮長對話上下文
- **分支對話**: 支持對話分支和回溯

### 5. 文件處理能力
- **多模態**: 支持文本、圖像、PDF 等多種格式
- **文件上傳**: 簡化的文件上傳 API
- **視覺分析**: 圖像理解和分析
- **文檔解析**: 自動文檔內容提取

### 6. 代碼執行環境
- **安全沙箱**: 安全的代碼執行環境
- **多語言**: 支持 Python、JavaScript 等語言
- **實時輸出**: 實時捕獲代碼執行輸出
- **依賴管理**: 自動處理代碼依賴

### 7. MCP 整合
- **MCP 協議**: 原生支持 Model Context Protocol
- **擴展性**: 輕鬆整合第三方 MCP 服務器
- **標準化**: 標準化的工具和數據源接口
- **生態系統**: 接入豐富的 MCP 生態

### 8. 生產就緒
- **可靠性**: 內建重試、超時、錯誤處理
- **監控**: 完整的日誌和監控支持
- **配置管理**: 靈活的配置系統
- **部署友好**: 支持各種部署環境

## 安裝

### 基本安裝

```bash
pip install anthropic
```

### 完整安裝（包含所有依賴）

```bash
pip install -r requirements.txt
```

### 從源碼安裝

```bash
git clone https://github.com/anthropics/anthropic-sdk-python
cd anthropic-sdk-python
pip install -e .
```

## 系統要求

### 最小配置
- **Python**: 3.8+
- **內存**: 2GB RAM
- **網絡**: 穩定的互聯網連接

### 推薦配置
- **Python**: 3.10+
- **內存**: 4GB+ RAM
- **CPU**: 多核心處理器

## 核心概念

### 1. Client 初始化

```python
from anthropic import Anthropic

# 使用環境變量中的 API Key
client = Anthropic()

# 或明確指定 API Key
client = Anthropic(api_key="your-api-key")
```

### 2. 基本對話

```python
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "你好，Claude！"}
    ]
)

print(message.content[0].text)
```

### 3. 工具定義

```python
tools = [
    {
        "name": "get_weather",
        "description": "獲取指定城市的天氣信息",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名稱"
                }
            },
            "required": ["city"]
        }
    }
]
```

### 4. 流式輸出

```python
with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "講個故事"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### 5. 多模態輸入

```python
import base64

with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": "這張圖片裡有什麼？"
                }
            ]
        }
    ]
)
```

## 使用案例

### 1. 智能客服 Agent
- **多輪對話**: 處理複雜的客戶查詢
- **知識檢索**: 整合企業知識庫
- **工單處理**: 自動創建和更新工單
- **情感分析**: 理解客戶情緒並適當響應

### 2. 代碼助手
- **代碼生成**: 根據需求生成代碼
- **代碼審查**: 自動代碼審查和建議
- **Bug 修復**: 智能定位和修復問題
- **文檔生成**: 自動生成代碼文檔

### 3. 數據分析 Agent
- **數據處理**: 自動化數據清洗和轉換
- **可視化**: 生成數據可視化圖表
- **洞察提取**: 從數據中提取關鍵洞察
- **報告生成**: 自動生成分析報告

### 4. 內容創作助手
- **文章撰寫**: 協助撰寫各類文章
- **內容優化**: 改進和優化現有內容
- **SEO 優化**: 提供 SEO 建議
- **多語言**: 支持多語言內容創作

### 5. 研究助手
- **文獻檢索**: 智能搜索相關文獻
- **摘要生成**: 自動生成文獻摘要
- **知識圖譜**: 構建研究主題知識圖譜
- **論文寫作**: 協助論文寫作和修改

### 6. 自動化運維
- **系統監控**: 智能監控系統狀態
- **故障診斷**: 自動診斷和修復問題
- **日誌分析**: 分析系統日誌找出問題
- **容量規劃**: 預測資源需求

## 示例文件說明

本目錄包含 10 個完整的示例文件，涵蓋 Claude Code SDK 的各個方面：

1. **01_快速開始.py** - SDK 初始化、基本對話、錯誤處理
2. **02_對話管理.py** - 多輪對話、上下文管理、對話歷史
3. **03_工具使用.py** - 工具定義、工具調用、工具鏈
4. **04_流式輸出.py** - 流式文本、流式工具調用、事件處理
5. **05_多輪對話.py** - 複雜對話流程、狀態管理、對話分支
6. **06_文件處理.py** - 圖像分析、PDF 解析、多模態處理
7. **07_代碼執行.py** - 代碼生成、安全執行、結果處理
8. **08_Agent構建.py** - 完整 Agent 系統、任務規劃、執行
9. **09_MCP整合.py** - MCP 服務器整合、工具擴展
10. **10_生產部署.py** - 錯誤處理、監控、日誌、部署配置

## 最佳實踐

### 1. API Key 管理
- 使用環境變量存儲 API Key
- 不要在代碼中硬編碼 API Key
- 使用 .env 文件管理開發環境配置
- 生產環境使用密鑰管理服務

### 2. 錯誤處理
```python
from anthropic import APIError, APIConnectionError, RateLimitError

try:
    message = client.messages.create(...)
except RateLimitError:
    # 處理速率限制
    pass
except APIConnectionError:
    # 處理網絡錯誤
    pass
except APIError as e:
    # 處理其他 API 錯誤
    print(f"API Error: {e}")
```

### 3. 上下文管理
- 控制對話歷史長度
- 使用系統提示詞設定行為規範
- 定期清理不必要的上下文
- 考慮使用對話摘要壓縮上下文

### 4. 工具設計
- 工具功能單一且明確
- 提供詳細的工具描述和參數說明
- 實現完善的參數驗證
- 處理工具執行錯誤

### 5. 性能優化
- 使用流式輸出提升用戶體驗
- 合理設置 max_tokens 限制
- 並行處理獨立的工具調用
- 緩存常用的響應

### 6. 安全性
- 驗證用戶輸入
- 限制工具的權限範圍
- 使用沙箱執行不可信代碼
- 定期審計 Agent 行為

## 性能指標

### 響應時間
- **非流式**: 1-5 秒（取決於回答長度）
- **流式**: 首字符 <500ms
- **工具調用**: 額外 100-500ms（取決於工具複雜度）

### 吞吐量
- **併發請求**: 支持高併發
- **速率限制**: 根據 API 等級而定
- **批處理**: 支持批量請求優化

### 可靠性
- **成功率**: >99.9%（正常情況下）
- **重試機制**: 自動重試失敗請求
- **超時處理**: 可配置的請求超時

## 與其他框架對比

### Claude Code SDK vs LangChain

| 特性 | Claude Code SDK | LangChain |
|-----|----------------|-----------|
| Claude 支持 | ✅ 官方原生 | ✅ 第三方整合 |
| 學習曲線 | ⭐⭐ 簡單 | ⭐⭐⭐ 中等 |
| 工具系統 | ✅ 原生支持 | ✅ 豐富生態 |
| 流式處理 | ✅ 優秀 | ✅ 支持 |
| MCP 支持 | ✅ 原生 | ❌ 需擴展 |
| 類型安全 | ✅ 強類型 | ⭐ 部分 |
| 文檔質量 | ✅ 優秀 | ✅ 豐富 |
| 生態系統 | ⭐ 成長中 | ✅ 成熟 |

### Claude Code SDK vs OpenAI SDK

| 特性 | Claude Code SDK | OpenAI SDK |
|-----|----------------|-----------|
| 模型支持 | Claude 系列 | GPT 系列 |
| 工具調用 | ✅ 原生支持 | ✅ Function Calling |
| 流式處理 | ✅ 完整支持 | ✅ 支持 |
| 視覺能力 | ✅ 優秀 | ✅ 支持 |
| 代碼執行 | ✅ 內建 | ❌ 需整合 |
| MCP 協議 | ✅ 原生 | ❌ 無 |
| API 設計 | ⭐⭐⭐ 現代 | ⭐⭐⭐ 簡潔 |

## 相關資源

- **官方網站**: https://www.anthropic.com
- **GitHub**: https://github.com/anthropics/anthropic-sdk-python
- **官方文檔**: https://docs.anthropic.com
- **API 參考**: https://docs.anthropic.com/api
- **Claude 模型**: https://www.anthropic.com/claude
- **MCP 協議**: https://modelcontextprotocol.io
- **示例代碼**: https://github.com/anthropics/anthropic-quickstarts
- **社區論壇**: https://community.anthropic.com
- **更新日誌**: https://docs.anthropic.com/changelog

## 模型選擇指南

### Claude 3.5 Sonnet (推薦)
- **用途**: 通用任務，平衡性能和成本
- **強項**: 代碼、分析、複雜推理
- **速度**: 快
- **成本**: 中等

### Claude 3 Opus
- **用途**: 最高質量要求的任務
- **強項**: 深度分析、創意寫作
- **速度**: 較慢
- **成本**: 較高

### Claude 3 Haiku
- **用途**: 簡單任務、高吞吐量場景
- **強項**: 快速響應、成本優化
- **速度**: 最快
- **成本**: 最低

## 系統架構

```
┌─────────────────────────────────────────────────┐
│              應用層                              │
│     你的 Agent 應用                              │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│         Claude Code SDK                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Messages │  │  Tools   │  │ Streaming│      │
│  └──────────┘  └──────────┘  └──────────┘      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   MCP    │  │  Vision  │  │  Context │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└──────────────┬──────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────┐
│         Anthropic API                           │
│           Claude 模型服務                        │
└─────────────────────────────────────────────────┘
```

## 開發路線圖

### 當前版本（v1.x）
- ✅ 基礎對話能力
- ✅ 工具調用系統
- ✅ 流式處理
- ✅ 多模態支持
- ✅ MCP 協議支持

### 計劃中（v2.x）
- 🚧 增強的 Agent 框架
- 🚧 內建對話管理
- 🚧 工具市場
- 🚧 可視化調試工具
- 🚧 性能分析工具

### 未來展望
- 📋 分布式 Agent 系統
- 📋 Agent 協作框架
- 📋 自動優化建議
- 📋 企業級治理工具

## 版本信息

- **當前版本**: 1.0+
- **Python 支持**: 3.8+
- **API 版本**: 2023-06-01
- **更新頻率**: 定期更新

## 社區與支持

### 獲取幫助
- **文檔**: 查閱官方文檔
- **示例**: 參考示例代碼
- **論壇**: 在社區論壇提問
- **Discord**: 加入 Anthropic Discord 社群

### 報告問題
- **Bug 報告**: GitHub Issues
- **功能請求**: GitHub Discussions
- **安全問題**: security@anthropic.com

## 授權

Claude Code SDK 由 Anthropic 提供，使用需遵守 Anthropic 的使用條款。本示例代碼僅供學習參考使用。

---

**注意**: 使用 Claude API 需要有效的 API Key。訪問 https://console.anthropic.com 獲取 API Key。新用戶可獲得免費額度用於測試。
