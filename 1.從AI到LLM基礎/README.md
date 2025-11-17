# 📖 從 AI 到 LLM 基礎

> 系統化學習人工智慧、機器學習、深度學習到大型語言模型的完整知識體系

## 🎯 學習目標

完成本系列教程後,你將能夠:

- ✅ 理解 AI、ML、DL、LLM 的關係和演進
- ✅ 掌握機器學習的核心概念和經典算法
- ✅ 深入理解深度學習和神經網路原理
- ✅ 完全掌握 Transformer 架構
- ✅ 了解 LLM 的訓練和應用
- ✅ 精通提示工程技巧

## 📚 教程列表

### [0. AI 基礎概念](./0.AI基礎概念.md)

**學習重點**:
- AI 的定義和發展歷史
- AI 的分類 (弱AI、強AI、超AI)
- AI vs 傳統編程
- AI 的應用領域
- 倫理與安全問題

**適合對象**: 完全零基礎的初學者

**預計時間**: 2-3 小時

---

### [1. 機器學習基礎](./1.機器學習基礎.md)

**學習重點**:
- 監督學習、非監督學習、強化學習
- 經典算法 (線性回歸、決策樹、SVM、KNN等)
- 特徵工程
- 模型評估與調優
- 過擬合與欠擬合
- 完整的 Python 實踐流程

**適合對象**: 有基礎 Python 能力的學習者

**預計時間**: 8-10 小時

**實踐項目**:
- MNIST 手寫數字識別
- 房價預測
- 客戶分群

---

### [2. 深度學習基礎](./2.深度學習基礎.md)

**學習重點**:
- 神經網路原理
- 反向傳播算法
- 激活函數、損失函數、優化器
- CNN (卷積神經網路)
- RNN/LSTM (循環神經網路)
- 訓練技巧 (Dropout、Batch Norm等)
- PyTorch 實戰

**適合對象**: 完成機器學習基礎的學習者

**預計時間**: 12-15 小時

**實踐項目**:
- 圖像分類 (CIFAR-10)
- 文本情感分析
- 時間序列預測

---

### [3. Transformer 架構詳解](./3.Transformer架構詳解.md)

**學習重點**:
- Self-Attention 機制
- Multi-Head Attention
- Position Encoding
- Encoder-Decoder 架構
- BERT、GPT、T5 的區別
- Vision Transformer
- 完整代碼實現

**適合對象**: 完成深度學習基礎的學習者

**預計時間**: 10-12 小時

**實踐項目**:
- 機器翻譯
- 文本分類
- 問答系統

---

### [4. LLM 基礎知識](./4.LLM基礎知識.md)

**學習重點**:
- LLM 的定義和特徵
- 主流模型 (GPT、Claude、Gemini、LLaMA)
- 預訓練、SFT、RLHF
- 關鍵技術 (Tokenization、量化、LoRA)
- 應用與限制
- 安全與倫理

**適合對象**: 完成 Transformer 學習的學習者

**預計時間**: 8-10 小時

**實踐項目**:
- 使用 OpenAI API
- 部署開源 LLM
- 模型微調 (Fine-tuning)

---

### [5. 提示工程指南](./5.提示工程指南.md)

**學習重點**:
- 提示工程的基本原則
- Zero-Shot、Few-Shot Prompting
- Chain-of-Thought (CoT)
- 角色扮演與格式化
- 實戰技巧與最佳實踐
- 常見錯誤避免

**適合對象**: 需要使用 LLM 的開發者和研究者

**預計時間**: 6-8 小時

**實踐項目**:
- 代碼生成助手
- 數據分析機器人
- 內容創作工具

---

## 🗺️ 學習路徑

### 初學者路徑 (0 基礎)

```
第 1 週: 0.AI基礎概念
        ↓
第 2-3 週: 1.機器學習基礎
        ↓
第 4-5 週: 2.深度學習基礎
        ↓
第 6-7 週: 3.Transformer架構詳解
        ↓
第 8 週: 4.LLM基礎知識
        ↓
第 9 週: 5.提示工程指南
```

### 進階路徑 (有 ML 基礎)

```
第 1 週: 2.深度學習基礎 (複習)
        ↓
第 2-3 週: 3.Transformer架構詳解
        ↓
第 4 週: 4.LLM基礎知識
        ↓
第 5 週: 5.提示工程指南
```

### 實踐者路徑 (直接應用 LLM)

```
第 1 週: 4.LLM基礎知識
        ↓
第 2 週: 5.提示工程指南
        ↓
實戰: ../1.LangchainDemos/
```

## 💡 學習建議

### 1. 循序漸進

- ✅ 按順序學習,不要跳過基礎內容
- ✅ 每個章節都要動手實踐
- ✅ 完成課後練習

### 2. 理論與實踐結合

```
閱讀理論 (30%) + 動手實踐 (70%) = 深入理解
```

### 3. 建立知識體系

```
AI (人工智慧)
 └── ML (機器學習)
      └── DL (深度學習)
           └── Transformer
                └── LLM
```

### 4. 持續練習

- 📝 記錄學習筆記
- 💻 完成實戰項目
- 🤝 參與社區討論
- 📚 閱讀最新論文

## 🔧 所需工具

### 開發環境

```bash
# Python 環境
Python 3.9+

# 必備庫
pip install numpy pandas matplotlib scikit-learn

# 深度學習
pip install torch torchvision  # PyTorch
pip install transformers       # Hugging Face

# LLM 相關
pip install openai anthropic   # API
pip install langchain          # 框架
```

### 硬體建議

**基礎學習**:
- CPU: 任意現代處理器
- RAM: 8GB+
- GPU: 不必需 (可使用 Google Colab)

**深度學習實踐**:
- GPU: NVIDIA RTX 3060 或更好
- RAM: 16GB+
- VRAM: 6GB+

**LLM 微調**:
- GPU: A100 / H100 (或雲端服務)
- RAM: 32GB+

## 📖 推薦資源

### 在線課程

- [Andrew Ng 機器學習](https://www.coursera.org/learn/machine-learning)
- [Fast.ai 深度學習](https://www.fast.ai/)
- [DeepLearning.AI](https://www.deeplearning.ai/)

### 書籍

- 《機器學習》- 周志華
- 《深度學習》- Ian Goodfellow
- 《動手學深度學習》- 李沐

### 網站

- [Hugging Face](https://huggingface.co/)
- [Papers with Code](https://paperswithcode.com/)
- [Distill](https://distill.pub/)

### 實踐平台

- [Google Colab](https://colab.research.google.com/)
- [Kaggle](https://www.kaggle.com/)
- [GitHub](https://github.com/)

## 🎓 評估標準

完成本系列學習後,你應該能夠:

- [ ] 解釋 AI、ML、DL、LLM 的區別和聯繫
- [ ] 實現經典機器學習算法
- [ ] 使用 PyTorch 構建神經網路
- [ ] 理解並實現 Transformer 架構
- [ ] 使用 LLM API 構建應用
- [ ] 編寫高質量的提示
- [ ] 微調和部署開源 LLM
- [ ] 分析和解決實際 AI 問題

## 🤝 反饋與貢獻

如果你發現任何問題或有改進建議:

- 📧 提交 Issue
- 🔧 提交 Pull Request
- 💬 參與討論區

## 📝 更新日誌

### v2.0 - 深度擴充版 (2025-01-17)

**重大更新**:

#### 0.AI基礎概念.md
- ✨ 新增完整數學基礎章節 (線性代數、微積分、概率統計)
- ✨ 新增可執行的數學示例代碼
- ✨ 新增 2024-2025 最新發展 (多模態、超長上下文、AI Agent)
- ✨ 新增自我測驗和實踐練習
- ✨ 新增 EU AI Act 和監管框架介紹
- ✨ 新增擴展學習資源和工具推薦

#### 1.機器學習基礎.md
- ✨ 新增深入數學推導 (線性回歸、邏輯回歸、決策樹)
- ✨ 新增兩個完整實戰項目 (房價預測、客戶流失預測)
- ✨ 新增學習曲線、特徵重要性分析
- ✨ 新增自我測驗和概念檢查
- ✨ 新增常見陷阱和最佳實踐
- ✨ 擴充實踐代碼示例,包含完整的數據探索和可視化

#### 通用改進
- 📊 所有代碼示例增加詳細注釋
- 🎯 增加交互式測驗 (可折疊答案)
- 📚 更新最新技術和工具
- 🔗 增強文件間的關聯性
- 💡 添加更多實用技巧和建議

### v1.0 - 初始版本 (2025-01-16)
- 創建完整基礎教程系列
- 新增 AI 基礎概念
- 新增機器學習基礎
- 新增深度學習基礎
- 新增 Transformer 架構詳解
- 新增 LLM 基礎知識
- 新增提示工程指南

## 🎓 學習成果檢核表

完成本系列學習後,你應該能夠:

### 理論理解
- [ ] 解釋 AI、ML、DL、LLM 之間的層次關係
- [ ] 理解機器學習的三大類型及其應用場景
- [ ] 掌握深度學習的核心原理 (反向傳播、優化器)
- [ ] 深入理解 Transformer 架構和 Self-Attention 機制
- [ ] 了解 LLM 的訓練流程 (預訓練、SFT、RLHF)
- [ ] 掌握提示工程的基本原則和高級技巧

### 數學基礎
- [ ] 熟悉向量和矩陣運算
- [ ] 理解梯度下降和反向傳播的數學原理
- [ ] 掌握概率分佈和統計推斷
- [ ] 能夠推導常見算法的數學公式

### 實踐能力
- [ ] 使用 Scikit-learn 實現經典機器學習算法
- [ ] 使用 PyTorch/TensorFlow 構建神經網路
- [ ] 完成至少 2-3 個端到端的 ML 項目
- [ ] 能夠評估和優化模型性能
- [ ] 使用 LLM API 構建實用應用
- [ ] 編寫高質量的提示詞

### 工具熟練度
- [ ] Python 數據科學生態 (NumPy, Pandas, Matplotlib)
- [ ] 深度學習框架 (PyTorch 或 TensorFlow)
- [ ] 版本控制和協作 (Git, GitHub)
- [ ] 實驗追蹤和模型管理
- [ ] LangChain/LlamaIndex 等 LLM 框架

## 📖 推薦學習順序

### 🎯 路徑 1: 零基礎入門 (12-16 週)

```
週 1-2:   0.AI基礎概念 + 數學基礎複習
週 3-5:   1.機器學習基礎 + 實戰項目 1
週 6-8:   2.深度學習基礎 + 實戰項目 2
週 9-11:  3.Transformer架構詳解 + 代碼實現
週 12-13: 4.LLM基礎知識 + API 實踐
週 14:    5.提示工程指南
週 15-16: 綜合項目 + 複習鞏固
```

### 🚀 路徑 2: 有 ML 基礎 (6-8 週)

```
週 1-2: 2.深度學習基礎 (快速複習) + 3.Transformer架構詳解
週 3-4: 4.LLM基礎知識 + 開源模型部署
週 5:   5.提示工程指南 + Agent 開發
週 6-8: LangChain/LlamaIndex 實戰項目
```

### ⚡ 路徑 3: 直接應用 LLM (2-3 週)

```
週 1:   4.LLM基礎知識 (跳過技術細節,關注應用)
週 2:   5.提示工程指南 + 大量練習
週 3:   1.LangchainDemos 實戰
```

## 🛠️ 配套資源

### 實踐環境

**雲端平台** (推薦新手):
- [Google Colab](https://colab.research.google.com/) - 免費 GPU, 適合學習
- [Kaggle Notebooks](https://www.kaggle.com/code) - 免費 GPU/TPU
- [Hugging Face Spaces](https://huggingface.co/spaces) - 免費部署

**本地環境**:
```bash
# 創建虛擬環境
python -m venv llm-env
source llm-env/bin/activate  # Linux/Mac
# llm-env\Scripts\activate  # Windows

# 安裝核心庫
pip install numpy pandas matplotlib seaborn
pip install scikit-learn
pip install torch torchvision  # PyTorch
pip install transformers datasets  # Hugging Face
pip install langchain openai anthropic  # LLM 框架
```

### 數據集資源

**機器學習**:
- [Kaggle Datasets](https://www.kaggle.com/datasets)
- [UCI ML Repository](https://archive.ics.uci.edu/ml/)
- [Scikit-learn Datasets](https://scikit-learn.org/stable/datasets.html)

**LLM 相關**:
- [Hugging Face Datasets](https://huggingface.co/datasets)
- [Stanford NLP](https://nlp.stanford.edu/projects/)
- [Common Crawl](https://commoncrawl.org/)

### 社群交流

**中文社群**:
- [機器之心](https://www.jiqizhixin.com/)
- [AI研習社](https://www.yanxishe.com/)
- [知乎 - 機器學習話題](https://www.zhihu.com/topic/19559450)

**國際社群**:
- [r/MachineLearning](https://www.reddit.com/r/MachineLearning/)
- [Hugging Face Discord](https://hf.co/join/discord)
- [AI Alignment Forum](https://www.alignmentforum.org/)

## 🚀 下一步

完成本系列後,繼續探索:

- 📚 [1.LangchainDemos](../1.LangchainDemos/) - LangChain 實戰
- 🖼️ [2.Multi_modal_RAG](../2.Multi_modal_RAG/) - 多模態 RAG
- 🔍 [6.LlamaIndex](../6.LlamaIndex/) - LlamaIndex 教程
- 🤖 [7.AutoGen](../7.AutoGen/) - 多 Agent 系統

### 進階方向

**研究方向**:
- 閱讀頂會論文 (NeurIPS, ICML, ICLR, ACL, CVPR)
- 複現經典論文
- 關注前沿研究

**工程方向**:
- 模型部署和優化
- 生產環境最佳實踐
- MLOps 工具鏈

**應用方向**:
- 垂直領域應用 (醫療、金融、教育)
- 產品化 LLM 應用
- AI Agent 開發

## 💬 反饋與貢獻

我們歡迎你的反饋和貢獻!

**反饋方式**:
- 📧 提交 Issue 報告問題
- 🔧 提交 Pull Request 改進內容
- 💬 在討論區分享學習心得
- ⭐ Star 本項目支持我們

**貢獻指南**:
1. Fork 本倉庫
2. 創建你的特性分支
3. 提交你的更改
4. 推送到分支
5. 創建 Pull Request

---

⭐ **祝學習愉快!** 有任何問題歡迎提問。

**最後更新**: 2025-01-17
**版本**: v2.0 - 深度擴充版
**維護者**: LLM-agent-Demo 團隊
