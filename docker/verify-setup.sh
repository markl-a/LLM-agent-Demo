#!/bin/bash
# Docker 配置驗證腳本

echo "======================================"
echo "Docker 配置驗證"
echo "======================================"
echo ""

errors=0

# 檢查必需文件
echo "檢查必需文件..."
files=(
    "Dockerfile"
    ".dockerignore"
    "docker-compose.yml"
    "docker-compose.dev.yml"
    "docker/entrypoint.sh"
    "docker/healthcheck.py"
    "docker/init.sql"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file (missing)"
        errors=$((errors + 1))
    fi
done

echo ""

# 檢查腳本執行權限
echo "檢查執行權限..."
if [ -x "docker/entrypoint.sh" ]; then
    echo "✓ docker/entrypoint.sh 可執行"
else
    echo "✗ docker/entrypoint.sh 不可執行"
    errors=$((errors + 1))
fi

if [ -x "docker/healthcheck.py" ]; then
    echo "✓ docker/healthcheck.py 可執行"
else
    echo "✗ docker/healthcheck.py 不可執行"
    errors=$((errors + 1))
fi

echo ""

# 檢查 .env 文件
echo "檢查環境配置..."
if [ -f ".env" ]; then
    echo "✓ .env 文件存在"
else
    echo "⚠ .env 文件不存在（將使用 .env.example）"
fi

echo ""
echo "======================================"
if [ $errors -eq 0 ]; then
    echo "✓ 所有檢查通過！"
    echo "======================================"
    echo ""
    echo "你可以使用以下命令啟動服務："
    echo "  ./docker-start.sh"
    echo "  或"
    echo "  docker-compose up -d"
    exit 0
else
    echo "✗ 發現 $errors 個錯誤"
    echo "======================================"
    exit 1
fi
