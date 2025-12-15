# Makefile 快速開始指南

## 查看所有可用命令
```bash
make help
```

## 新用戶快速開始

### 方案 1: 快速開始（僅環境設置）
```bash
make quick-start
source venv/bin/activate      # 激活虛擬環境
make install-all              # 安裝所有依賴
```

### 方案 2: 完整設置（一鍵完成）
```bash
make full-setup
# 然後編輯 .env 文件添加 API keys
```

## 常用命令速查

### 安裝
```bash
make venv                # 創建虛擬環境
make install             # 安裝生產依賴
make install-dev         # 安裝開發依賴
make install-all         # 安裝所有依賴（含 Playwright）
make setup-env           # 創建 .env 文件
```

### 測試
```bash
make test                # 運行所有測試
make test-quick          # 快速測試（跳過慢速測試）
make test-watch          # 監視模式（自動重新運行）
make test-cov            # 測試 + 覆蓋率報告
make test-report         # 生成並打開報告
```

### 代碼質量
```bash
make format              # 格式化代碼
make lint                # 運行 linting
make lint-fix            # 自動修復 linting 問題
make type-check          # 類型檢查
make dev-check           # 完整開發檢查
```

### 文檔
```bash
make docs                # 構建文檔
make serve-docs          # 本地預覽文檔
make api-docs            # 生成 API 文檔
make docs-deploy         # 部署到 GitHub Pages
```

### 清理
```bash
make clean               # 清理生成的文件
make clean-cache         # 只清理緩存
make clean-test          # 只清理測試文件
make clean-all           # 完全清理（含數據庫）
```

### 實用工具
```bash
make verify-env          # 驗證環境配置
make show-config         # 顯示當前配置
make tree                # 顯示目錄結構
make list-examples       # 列出所有示例
make info                # 專案信息
```

### 組合命令（推薦）
```bash
make daily               # 每日開發流程
make dev-check           # 開發檢查
make ci-full             # 完整 CI 檢查
make rebuild             # 重新構建
```

## 典型工作流

### 每日開發
```bash
make daily               # 拉取代碼、安裝依賴、格式化、測試
make test-watch          # 啟動測試監視模式
# ... 編碼 ...
make dev-check           # 提交前檢查
```

### 提交前
```bash
make format              # 格式化代碼
make lint                # 檢查代碼質量
make test                # 運行測試
# 或一鍵完成
make dev-check
```

### 問題排查
```bash
make verify-env          # 檢查環境配置
make show-config         # 查看當前配置
make info                # 查看專案信息
```

## 提示

💡 **自動完成**: 大多數 shell 支持 Tab 自動完成，輸入 `make` 後按 Tab 查看選項

💡 **組合使用**: 可以按順序運行多個命令：
```bash
make clean && make install && make test
```

💡 **查看命令執行的操作**: 每個命令都有清晰的輸出說明正在執行的操作

💡 **顏色輸出**:
- 🔵 藍色 = 標題/信息
- 🟢 綠色 = 成功/進度
- 🟡 黃色 = 警告/提示
- 🔴 紅色 = 錯誤

## 獲取幫助

```bash
make help                # 查看所有命令
make version             # 查看版本信息
```

---

詳細文檔請參閱: [MAKEFILE_ENHANCEMENTS.md](./MAKEFILE_ENHANCEMENTS.md)
