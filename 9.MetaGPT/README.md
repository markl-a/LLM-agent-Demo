# MetaGPT 學習教程

## 📚 簡介

MetaGPT 是一個多 Agent 元編程框架，將軟體公司的整個開發流程（產品經理、架構師、工程師等）編碼成 Agent，實現自動化軟體開發。

### 核心理念

**軟體公司 = LLM + SOP（標準作業流程）**

MetaGPT 模擬真實軟體公司的工作流程：
1. 產品經理編寫需求文檔（PRD）
2. 架構師設計系統架構
3. 工程師編寫程式碼
4. QA 進行測試

### 主要特性

- **標準化流程**: 基於軟體工程最佳實踐的 SOP
- **角色專業化**: 每個 Agent 扮演特定角色
- **文檔驅動**: 通過結構化文檔傳遞信息
- **完整開發流程**: 從需求到程式碼的全流程自動化

## 🎯 教程內容

### 0. 基礎概念 (0.基礎概念.ipynb)
- MetaGPT 架構理解
- 安裝和配置
- 第一個軟體開發專案
- 各個角色的職責

### 1. 軟體開發流程 (1.軟體開發流程.ipynb)
- 需求分析（ProductManager）
- 系統設計（Architect）
- 程式碼實現（Engineer）
- 測試驗證（QA Engineer）
- 自定義角色和流程

## 🚀 快速示例

```python
from metagpt.software_company import SoftwareCompany
from metagpt.roles import ProductManager, Architect, Engineer

# 創建軟體公司
company = SoftwareCompany()

# 添加角色
company.hire([
    ProductManager(),
    Architect(),
    Engineer()
])

# 啟動專案
company.run_project("開發一個待辦事項管理應用")
```

## 📐 架構圖

```
需求 → ProductManager（PRD）→ Architect（設計文檔）→ Engineer（程式碼）→ 完成
                                        ↓
                                   QA Engineer（測試）
```

## 💡 應用場景

- **快速原型開發**: 從想法到可運行程式碼
- **程式碼生成**: 自動化重複性編碼工作
- **架構設計**: 生成系統設計文檔
- **學習參考**: 理解軟體開發流程

## 🔑 關鍵角色

### ProductManager（產品經理）
- 編寫 PRD（產品需求文檔）
- 定義功能和用戶故事
- 確定優先級

### Architect（架構師）
- 設計系統架構
- 選擇技術棧
- 定義接口和數據模型

### Engineer（工程師）
- 編寫實現程式碼
- 遵循設計文檔
- 實現功能模組

### QA Engineer（測試工程師）
- 編寫測試用例
- 執行測試
- 報告缺陷

## 📖 學習資源

- [MetaGPT 官方文檔](https://docs.deepwisdom.ai/)
- [GitHub 倉庫](https://github.com/geekan/MetaGPT)
- [論文](https://arxiv.org/abs/2308.00352)

## ⚠️ 注意事項

1. **成本控制**: MetaGPT 會進行多次 LLM 調用，注意 API 成本
2. **輸出質量**: 生成的程式碼需要人工審核
3. **適用範圍**: 適合中小型專案和原型開發
4. **配置要求**: 建議使用 GPT-4 以獲得更好效果
