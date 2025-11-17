# 實用工具腳本

本目錄包含三個實用工具腳本，用於多模態 RAG 系統的開發和維護。

## 工具列表

### 1. batch_processor.py - 批量 PDF 處理器

批量處理 PDF 文件，提取文本、圖像和表格，並生成摘要。

**功能**：
- 並行處理多個 PDF 文件
- 自動分類元素（文本、圖像、表格）
- 生成優化的摘要用於檢索
- 進度追蹤和錯誤處理
- 生成處理報告

**使用方法**：

```bash
# 基本使用
python batch_processor.py /path/to/pdfs --output-dir ./output

# 自定義配置
python batch_processor.py /path/to/pdfs \
  --output-dir ./output \
  --max-workers 8 \
  --chunk-size 2000

# 環境變數
export OPENAI_API_KEY=your_key
```

**參數**：
- `input_dir`: PDF 文件目錄（必需）
- `--output-dir`: 輸出目錄（默認：./output）
- `--max-workers`: 最大並行工作數（默認：4）
- `--chunk-size`: 文本塊大小（默認：2000）

**輸出**：
- `{filename}_result.json`: 每個 PDF 的處理結果
- `processing_report.json`: 整體處理報告

---

### 2. cost_calculator.py - 成本計算器

計算和優化多模態 RAG 系統的運營成本。

**功能**：
- 計算單次查詢成本
- 計算文檔處理成本
- 估算月度成本
- 提供成本優化建議
- 生成詳細成本報告

**使用方法**：

```bash
# 基本使用
python cost_calculator.py --daily-queries 1000

# 包含文檔處理
python cost_calculator.py \
  --daily-queries 1000 \
  --new-docs 100 \
  --llm-model gpt-4o-mini

# 導出報告
python cost_calculator.py \
  --daily-queries 1000 \
  --output cost_report.json
```

**參數**：
- `--daily-queries`: 每日查詢數（必需）
- `--new-docs`: 每月新增文檔數（默認：0）
- `--llm-model`: LLM 模型選擇（默認：gpt-4o）
  - 可選：gpt-4o, gpt-4o-mini, gpt-4-turbo
- `--output`: 輸出報告文件路徑

**示例輸出**：

```
========================================
RAG 系統成本報告
========================================

月度成本分解：
  query_processing: $45.00
  document_processing: $12.50
  vector_database: $70.00
  infrastructure: $100.00

總成本：$227.50/月
每次查詢成本：$0.0015
每 1000 次查詢成本：$1.50

成本優化建議：
  1. 使用 GPT-4o-mini 替代 GPT-4o 處理簡單查詢
     預估節省：$27.00
     權衡：性能略微下降（約 5-10%）
     優先級：high

總潛在節省：$40.00/月
```

---

### 3. image_quality_checker.py - 圖像質量檢查器

評估圖像質量，識別問題，並提供優化建議。

**功能**：
- 檢查圖像質量（解析度、清晰度、大小）
- 分類圖像類型（圖表、流程圖、照片等）
- 評估圖像對 RAG 的價值
- 識別常見問題
- 提供優化建議

**使用方法**：

```bash
# 檢查單個圖像
python image_quality_checker.py image.jpg

# 檢查目錄
python image_quality_checker.py /path/to/images

# 生成詳細報告
python image_quality_checker.py /path/to/images \
  --detailed \
  --output quality_report.json
```

**參數**：
- `input`: 圖像文件或目錄路徑（必需）
- `--output`: 輸出報告文件路徑
- `--detailed`: 顯示詳細報告

**圖像質量評級**：
- **Excellent**: 高解析度、清晰、適合 RAG
- **Good**: 質量良好，可以使用
- **Acceptable**: 可接受，但有改進空間
- **Poor**: 質量較差，建議重新獲取
- **Unusable**: 無法使用

**圖像類型分類**：
- **chart**: 圖表（高 RAG 價值）
- **diagram**: 示意圖（高 RAG 價值）
- **flowchart**: 流程圖（高 RAG 價值）
- **table**: 表格圖像（高 RAG 價值）
- **screenshot**: 截圖（中等價值）
- **photo**: 照片（低價值）
- **decorative**: 裝飾性圖片（建議跳過）

**示例輸出**：

```
========================================
圖像質量總結報告
========================================

總圖像數：50

質量分佈：
  excellent: 15 (30.0%)
  good: 20 (40.0%)
  acceptable: 10 (20.0%)
  poor: 5 (10.0%)

類型分佈：
  chart: 20 (40.0%)
  diagram: 15 (30.0%)
  photo: 10 (20.0%)
  decorative: 5 (10.0%)

RAG 價值分佈：
  high_value: 35 (70.0%)
  medium_value: 10 (20.0%)
  low_value: 5 (10.0%)

常見問題：
  文件過大（> 5MB）: 8 次
  解析度過低（< 400x300）: 5 次

整體建議：
  • 建議跳過 5 個裝飾性圖像以節省成本
  • 8 個圖像文件過大，建議壓縮
```

---

## 依賴安裝

```bash
# 所有工具的通用依賴
pip install langchain openai langchain-chroma langchain-experimental

# batch_processor 額外依賴
pip install unstructured[all-docs] nltk tiktoken

# image_quality_checker 額外依賴
pip install Pillow numpy opencv-python

# 完整安裝
pip install -r requirements.txt
```

## 工作流示例

### 完整的 RAG 系統構建流程

```bash
# 1. 評估源圖像質量
python image_quality_checker.py ./source_images \
  --output image_quality_report.json

# 根據報告優化圖像（移除低質量、壓縮大文件等）

# 2. 批量處理 PDF 文件
python batch_processor.py ./pdfs \
  --output-dir ./processed \
  --max-workers 8

# 3. 計算成本
python cost_calculator.py \
  --daily-queries 500 \
  --new-docs 50 \
  --output cost_estimate.json

# 根據成本報告進行優化
```

### 生產環境監控

```bash
# 定期檢查新增圖像質量
python image_quality_checker.py ./new_images \
  --output daily_quality_check.json

# 監控成本變化
python cost_calculator.py \
  --daily-queries $(get_daily_query_count) \
  --output monthly_cost_$(date +%Y%m).json
```

## 最佳實踐

### 圖像處理
1. 使用 `image_quality_checker.py` 預先評估圖像
2. 跳過低價值圖像（裝飾性、低質量）
3. 壓縮大文件以降低成本
4. 保持圖表和示意圖的高質量

### 批量處理
1. 根據服務器性能調整 `--max-workers`
2. 監控 API 使用限額
3. 實現錯誤重試機制
4. 定期備份處理結果

### 成本控制
1. 定期運行成本計算器評估支出
2. 實施優化建議（模型選擇、圖像處理等）
3. 監控每次查詢成本的變化
4. 設置成本告警閾值

## 故障排除

### batch_processor.py

**問題**：處理速度慢
```bash
# 解決方案：增加並行數
python batch_processor.py ./pdfs --max-workers 16
```

**問題**：API 限流錯誤
```bash
# 解決方案：減少並行數
python batch_processor.py ./pdfs --max-workers 2
```

### cost_calculator.py

**問題**：成本估算不準確
```bash
# 解決方案：使用實際統計數據
python cost_calculator.py \
  --daily-queries $(實際日均查詢數) \
  --new-docs $(實際月度新增文檔數)
```

### image_quality_checker.py

**問題**：OpenCV 安裝失敗
```bash
# 解決方案：使用預編譯版本
pip install opencv-python-headless
```

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 授權

MIT License
