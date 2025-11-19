# 🚀 快速開始指南

歡迎來到 LLM Agent Demo 項目！本指南將幫助您在 5 分鐘內開始運行第一個示例。

## 📋 前置要求

- Python 3.8 或更高版本
- Git
- （可選）CUDA GPU 用於本地模型

## ⚡ 5 分鐘快速開始

### 步驟 1: 克隆項目

```bash
git clone https://github.com/markl-a/LLM-agent-Demo.git
cd LLM-agent-Demo
```

### 步驟 2: 創建虛擬環境

```bash
# 創建虛擬環境
python -m venv venv

# 激活虛擬環境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 步驟 3: 安裝基礎依賴

```bash
# 安裝所有框架的依賴
pip install -r requirements.txt

# 或者只安裝特定框架的依賴
pip install -r "12.Semantic Kernel/requirements.txt"
```

### 步驟 4: 配置 API Keys

創建 `.env` 文件：

```bash
cat > .env << EOF
# OpenAI (必需 - 大多數示例使用)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Claude (可選)
ANTHROPIC_API_KEY=your_anthropic_key_here

# Google Gemini (可選)
GOOGLE_API_KEY=your_google_key_here
EOF
```

### 步驟 5: 運行第一個示例

選擇任一框架開始：

#### 選項 A: OpenAI Swarm (推薦初學者 - 最簡單)

```bash
cd "16.OpenAI Swarm"
python 01_多Agent協作.py
```

#### 選項 B: Semantic Kernel (推薦企業應用)

```bash
cd "12.Semantic Kernel"
python 01_快速開始.py
```

#### 選項 C: LangGraph (推薦工作流應用)

```bash
cd "17.LangGraph"
python 01_狀態圖基礎.py
```

#### 選項 D: Haystack (推薦 RAG 應用)

```bash
cd "14.Haystack"
python 01_RAG基礎.py
```

## 🎯 選擇您的學習路徑

### 🌱 初學者路徑 (第 1 週)

**目標**: 理解基本概念，運行簡單示例

1. **OpenAI Swarm** - 輕量級，易於理解
   ```bash
   cd "16.OpenAI Swarm"
   python 01_多Agent協作.py  # Agent 基礎
   python 02_Agent切換.py     # Agent 切換
   python 04_函數工具.py      # 函數調用
   ```

2. **LangGraph** - 狀態管理與工作流
   ```bash
   cd "17.LangGraph"
   python 01_狀態圖基礎.py
   python 02_節點與邊.py
   python 03_條件路由.py
   ```

3. **Semantic Kernel** - 企業級框架
   ```bash
   cd "12.Semantic Kernel"
   python 01_快速開始.py
   python 02_多LLM提供商.py
   python 05_記憶管理.py
   ```

### 🚀 進階路徑 (第 2-3 週)

**目標**: 掌握 RAG、多 Agent、複雜應用

1. **Haystack** - RAG 專家
   ```bash
   cd "14.Haystack"
   python 01_RAG基礎.py
   python 03_多種檢索器.py
   python 04_Pipeline構建.py
   ```

2. **LangGraph** - 複雜工作流
   ```bash
   cd "17.LangGraph"
   python 06_並行執行.py
   python 11_人機協作.py
   python 16_客服機器人.py
   ```

3. **AutoGPT** - 自主 Agent
   ```bash
   cd "15.AutoGPT"
   python 01_自主Agent.py
   python 02_目標規劃.py
   python 06_自我反思.py
   ```

### 💼 專家路徑 (第 4-8 週)

**目標**: 構建生產級應用

1. 完成所有 120 個示例
2. 研究框架源碼
3. 構建自己的項目

## 📚 框架快速選擇

### 我應該從哪個框架開始？

| 你的目標 | 推薦框架 | 原因 |
|---------|---------|------|
| **學習 AI Agent 概念** | OpenAI Swarm | 代碼最簡單，核心概念清晰 |
| **構建企業應用** | Semantic Kernel | Microsoft 支持，功能完整 |
| **實現 RAG 系統** | Haystack | RAG 專注，性能優秀 |
| **複雜工作流編排** | LangGraph | 狀態管理，支持循環和條件 |
| **可視化設計** | LangFlow | 低代碼，拖放式界面 |
| **自動化任務** | AutoGPT | 自主決策，持續執行 |

### 框架難度排序

```
簡單 → 中等 → 進階 → 困難
   ↓      ↓      ↓      ↓
Swarm → SK → LangGraph → Haystack → AutoGPT
  ↓      ↓      ↓         ↓          ↓
 1天    2-3天  3-4天    4-5天      1-2週
```

## 🛠️ 常見問題

### Q: 沒有 GPU 可以運行嗎？

**A**: 可以！所有示例默認使用 OpenAI API，不需要本地 GPU。

### Q: API 調用會花費很多錢嗎？

**A**: 不會。大多數示例使用 `gpt-3.5-turbo`，成本很低。一個示例通常只需 $0.001-0.01。

### Q: 需要安裝所有框架的依賴嗎？

**A**: 不需要。你可以只安裝你要學習的框架：

```bash
# 只安裝 Semantic Kernel
pip install -r "12.Semantic Kernel/requirements.txt"

# 只安裝 OpenAI Swarm
pip install -r "16.OpenAI Swarm/requirements.txt"
```

### Q: 遇到 ImportError 怎麼辦？

**A**: 確保：
1. 虛擬環境已激活
2. 依賴已安裝：`pip install -r requirements.txt`
3. Python 版本 >= 3.8

### Q: API Key 不工作？

**A**: 檢查：
1. `.env` 文件在項目根目錄
2. API Key 格式正確（無多餘空格）
3. API Key 有效且有餘額
4. 使用 `python-dotenv` 加載環境變量

## 🎓 學習資源

### 官方文檔

- [Semantic Kernel](https://learn.microsoft.com/semantic-kernel/)
- [LangFlow](https://docs.langflow.org/)
- [Haystack](https://haystack.deepset.ai/)
- [OpenAI Swarm](https://github.com/openai/swarm)
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT)
- [LangGraph](https://langchain-ai.github.io/langgraph/)

### 項目文檔

- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - 完整項目總結
- [12.Semantic Kernel/README.md](12.Semantic%20Kernel/README.md) - SK 教程
- [16.OpenAI Swarm/README.md](16.OpenAI%20Swarm/README.md) - Swarm 教程
- [17.LangGraph/README.md](17.LangGraph/README.md) - LangGraph 教程
- [14.Haystack/README.md](14.Haystack/README.md) - Haystack 教程

## 🔧 開發工具

### 推薦的編輯器

- **VS Code** (推薦)
  - 安裝 Python 擴展
  - 安裝 Pylance
  - 安裝 Jupyter

- **PyCharm** (專業)
- **Jupyter Lab** (交互式)

### 有用的命令

```bash
# 查看已安裝的包
pip list

# 更新 pip
pip install --upgrade pip

# 重新安裝依賴
pip install -r requirements.txt --force-reinstall

# 清理緩存
pip cache purge
```

## 📊 進度追蹤

使用以下 checklist 追蹤你的學習進度：

### Week 1: 基礎
- [ ] 運行第一個 Swarm 示例
- [ ] 運行第一個 Semantic Kernel 示例
- [ ] 理解 Agent 和函數調用概念
- [ ] 配置好開發環境

### Week 2: 進階
- [ ] 完成 Swarm 基礎示例 (1-5)
- [ ] 完成 SK 基礎示例 (1-5)
- [ ] 學習 RAG 基礎
- [ ] 運行 Haystack 示例

### Week 3-4: 深入
- [ ] 完成至少一個框架的所有示例
- [ ] 理解多 Agent 協作
- [ ] 實現自己的小項目
- [ ] 閱讀框架源碼

## 🎯 下一步

1. **運行更多示例**
   - 每個框架都有 20 個示例
   - 從簡單到複雜遞進

2. **閱讀文檔**
   - 每個框架目錄下都有詳細的 README
   - 查看 PROJECT_SUMMARY.md 了解全局

3. **構建項目**
   - 選擇一個實際問題
   - 使用學到的知識解決它
   - 分享你的成果

4. **加入社區**
   - GitHub Issues: 提問和討論
   - Pull Requests: 貢獻代碼
   - Star 項目: 支持開發

## 💬 需要幫助？

- **GitHub Issues**: [提交問題](https://github.com/markl-a/LLM-agent-Demo/issues)
- **文檔**: 查看各框架的 README.md
- **示例代碼**: 所有代碼都有詳細註釋

---

<div align="center">

**準備好了嗎？選擇一個框架開始你的 AI Agent 之旅！** 🚀

[查看完整項目總結](PROJECT_SUMMARY.md) | [返回主頁](README.md)

</div>
