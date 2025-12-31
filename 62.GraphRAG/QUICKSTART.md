# GraphRAG 快速開始指南

## 安裝依賴

```bash
# 安裝基礎依賴
pip install -r requirements.txt

# 安裝可選依賴（用於可視化）
pip install matplotlib plotly
```

## 環境配置

創建 `.env` 文件並添加您的 API 密鑰：

```env
GRAPHRAG_API_KEY=your_openai_api_key_here
# 或者
OPENAI_API_KEY=your_openai_api_key_here
```

## 學習路徑

建議按以下順序學習示例：

### 1. 基礎入門
- **01_快速開始.py** - 了解 GraphRAG 的基本概念和工作流程
- **02_知識圖譜構建.py** - 學習如何構建知識圖譜

### 2. 核心技術
- **03_實體抽取.py** - 深入理解實體識別技術
- **04_關係發現.py** - 學習關係提取方法
- **05_社區檢測.py** - 掌握社區發現算法

### 3. 查詢應用
- **06_本地搜索.py** - 了解 Local Search 的原理和應用
- **07_全局搜索.py** - 掌握 Global Search 技術
- **08_混合查詢.py** - 學習如何結合兩種搜索方式

### 4. 高級主題
- **09_可視化.py** - 學習圖譜可視化技術
- **10_企業應用.py** - 了解企業級部署方案

## 運行示例

```bash
# 進入項目目錄
cd /home/user/LLM-agent-Demo/62.GraphRAG

# 運行任何示例
python 01_快速開始.py
python 02_知識圖譜構建.py
# ... 以此類推
```

## 目錄結構

```
62.GraphRAG/
├── README.md              # 框架介紹（中文）
├── QUICKSTART.md          # 快速開始指南
├── requirements.txt       # 依賴文件
├── .gitignore            # Git 忽略文件
│
├── 01_快速開始.py        # 基本使用示例
├── 02_知識圖譜構建.py    # 圖譜構建
├── 03_實體抽取.py        # 實體識別
├── 04_關係發現.py        # 關係提取
├── 05_社區檢測.py        # 社區發現
├── 06_本地搜索.py        # Local Search
├── 07_全局搜索.py        # Global Search
├── 08_混合查詢.py        # 混合搜索
├── 09_可視化.py          # 圖譜可視化
└── 10_企業應用.py        # 企業級部署
```

## 常見問題

### Q: 運行示例時提示 "No module named 'dotenv'"
**A:** 請先安裝依賴：`pip install -r requirements.txt`

### Q: 示例使用的是模擬數據嗎？
**A:** 是的，為了方便演示，大部分示例使用模擬數據。實際應用時，請參考代碼注釋中的說明，使用真實的 LLM API。

### Q: 如何在實際項目中使用？
**A:**
1. 安裝 GraphRAG：`pip install graphrag`
2. 參考 01_快速開始.py 進行項目初始化
3. 根據您的需求修改配置文件
4. 參考各個示例文件實現具體功能

### Q: GraphRAG 和傳統 RAG 有什麼區別？
**A:** 請查看 README.md 中的詳細對比表格。簡單來說，GraphRAG 通過知識圖譜提供更好的全局理解能力。

## 進階學習

- 官方文檔：https://microsoft.github.io/graphrag/
- GitHub：https://github.com/microsoft/graphrag
- 論文：[From Local to Global: A Graph RAG Approach](https://arxiv.org/abs/2404.16130)

## 技術支持

如有問題，請查看：
1. README.md 中的詳細說明
2. 各示例文件中的註釋
3. GraphRAG 官方文檔
4. GitHub Issues

## 許可證

本示例代碼僅供學習參考使用。GraphRAG 框架本身採用 MIT 許可證。

---

**最後更新**：2025-12-31
