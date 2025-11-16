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

- **2025-01-16**: 創建完整基礎教程系列
  - 新增 AI 基礎概念
  - 新增機器學習基礎
  - 新增深度學習基礎
  - 新增 Transformer 架構詳解
  - 新增 LLM 基礎知識
  - 新增提示工程指南

## 🚀 下一步

完成本系列後,繼續探索:

- 📚 [1.LangchainDemos](../1.LangchainDemos/) - LangChain 實戰
- 🖼️ [2.Multi_modal_RAG](../2.Multi_modal_RAG/) - 多模態 RAG
- 🔍 [6.LlamaIndex](../6.LlamaIndex/) - LlamaIndex 教程
- 🤖 [7.AutoGen](../7.AutoGen/) - 多 Agent 系統

---

⭐ 祝學習愉快!有任何問題歡迎提問。

**最後更新**: 2025-01-16
