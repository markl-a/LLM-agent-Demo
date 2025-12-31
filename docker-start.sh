#!/bin/bash
# LLM Agent Demo - Docker 快速啟動腳本
# 簡化 Docker 部署流程

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印帶顏色的消息
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

# 顯示橫幅
show_banner() {
    echo "======================================"
    echo "  LLM Agent Demo - Docker 啟動工具"
    echo "======================================"
    echo ""
}

# 檢查 Docker 和 Docker Compose
check_requirements() {
    print_info "檢查系統要求..."

    # 檢查 Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安裝！請先安裝 Docker。"
        echo "訪問: https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_success "Docker 已安裝: $(docker --version)"

    # 檢查 Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安裝！請先安裝 Docker Compose。"
        echo "訪問: https://docs.docker.com/compose/install/"
        exit 1
    fi
    print_success "Docker Compose 已安裝"

    # 檢查 Docker daemon
    if ! docker info &> /dev/null; then
        print_error "Docker daemon 未運行！請啟動 Docker。"
        exit 1
    fi
    print_success "Docker daemon 正在運行"

    echo ""
}

# 檢查 .env 文件
check_env_file() {
    print_info "檢查環境配置..."

    if [ ! -f .env ]; then
        print_warning ".env 文件不存在"
        echo ""
        read -p "是否從 .env.example 創建 .env 文件？(y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cp .env.example .env
            print_success ".env 文件已創建"
            print_warning "請編輯 .env 文件並填入你的 API Keys"
            echo ""
            read -p "現在編輯 .env 文件？(y/n) " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                ${EDITOR:-nano} .env
            fi
        else
            print_error "需要 .env 文件才能繼續"
            exit 1
        fi
    else
        print_success ".env 文件已存在"
    fi

    # 檢查是否配置了至少一個 API Key
    if ! grep -q "OPENAI_API_KEY=sk-" .env && \
       ! grep -q "GOOGLE_API_KEY=.*" .env && \
       ! grep -q "ANTHROPIC_API_KEY=.*" .env && \
       ! grep -q "GROQ_API_KEY=.*" .env; then
        print_warning "未檢測到有效的 API Key 配置"
        print_warning "某些功能可能無法使用"
    fi

    echo ""
}

# 選擇運行模式
select_mode() {
    print_info "請選擇運行模式:"
    echo ""
    echo "1) 生產模式 (精簡，只包含核心服務)"
    echo "2) 開發模式 (完整，包含調試工具和額外服務)"
    echo "3) 僅 Jupyter Lab (最小化配置)"
    echo "4) 退出"
    echo ""

    read -p "請選擇 [1-4]: " mode

    case $mode in
        1)
            MODE="production"
            COMPOSE_FILES="-f docker-compose.yml"
            ;;
        2)
            MODE="development"
            COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"
            ;;
        3)
            MODE="minimal"
            COMPOSE_FILES="-f docker-compose.yml"
            SERVICES="app"
            ;;
        4)
            print_info "退出"
            exit 0
            ;;
        *)
            print_error "無效的選擇"
            exit 1
            ;;
    esac

    print_success "已選擇: $MODE 模式"
    echo ""
}

# 檢查 GPU 支持
check_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        print_info "檢測到 NVIDIA GPU"
        nvidia-smi --query-gpu=name --format=csv,noheader
        print_success "GPU 支持已啟用（用於 Ollama）"
    else
        print_warning "未檢測到 NVIDIA GPU"
        print_warning "Ollama 將在 CPU 模式下運行（較慢）"
    fi
    echo ""
}

# 拉取最新鏡像
pull_images() {
    print_info "拉取最新的 Docker 鏡像..."
    docker-compose $COMPOSE_FILES pull
    print_success "鏡像拉取完成"
    echo ""
}

# 構建鏡像
build_images() {
    print_info "構建 Docker 鏡像..."

    read -p "是否使用緩存構建？(y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose $COMPOSE_FILES build
    else
        docker-compose $COMPOSE_FILES build --no-cache
    fi

    print_success "鏡像構建完成"
    echo ""
}

# 啟動服務
start_services() {
    print_info "啟動服務..."

    if [ -n "$SERVICES" ]; then
        docker-compose $COMPOSE_FILES up -d $SERVICES
    else
        docker-compose $COMPOSE_FILES up -d
    fi

    print_success "服務已啟動"
    echo ""
}

# 顯示服務狀態
show_status() {
    print_info "服務狀態:"
    echo ""
    docker-compose $COMPOSE_FILES ps
    echo ""
}

# 顯示訪問信息
show_access_info() {
    print_success "部署完成！"
    echo ""
    echo "======================================"
    echo "  訪問信息"
    echo "======================================"
    echo ""
    echo "📊 Jupyter Lab:"
    echo "   http://localhost:8888"
    echo ""
    echo "🗄️  ChromaDB API:"
    echo "   http://localhost:8000"
    echo ""
    echo "🤖 Ollama API:"
    echo "   http://localhost:11434"
    echo ""

    if [ "$MODE" = "development" ]; then
        echo "📦 開發工具:"
        echo "   Adminer (數據庫):  http://localhost:8081"
        echo "   Portainer (容器):  http://localhost:9000"
        echo "   PostgreSQL:        localhost:5432"
        echo "   Redis:             localhost:6379"
        echo ""
    fi

    echo "======================================"
    echo "  常用命令"
    echo "======================================"
    echo ""
    echo "查看日誌:"
    echo "  docker-compose logs -f"
    echo ""
    echo "停止服務:"
    echo "  docker-compose down"
    echo ""
    echo "重啟服務:"
    echo "  docker-compose restart"
    echo ""
    echo "進入容器:"
    echo "  docker-compose exec app bash"
    echo ""
    echo "查看更多信息，請閱讀 DOCKER.md"
    echo ""
}

# 等待服務就緒
wait_for_services() {
    print_info "等待服務啟動..."

    # 等待應用容器健康
    max_wait=60
    counter=0

    while [ $counter -lt $max_wait ]; do
        if docker-compose $COMPOSE_FILES ps | grep -q "healthy"; then
            print_success "服務已就緒"
            return 0
        fi
        sleep 2
        counter=$((counter + 2))
        echo -n "."
    done

    echo ""
    print_warning "服務可能需要更長時間啟動"
    print_info "使用 'docker-compose logs -f' 查看詳細信息"
}

# 主函數
main() {
    show_banner
    check_requirements
    check_env_file
    select_mode
    check_gpu

    # 詢問是否拉取最新鏡像
    read -p "是否拉取最新的基礎鏡像？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pull_images
    fi

    # 詢問是否重新構建
    read -p "是否重新構建應用鏡像？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_images
    fi

    start_services
    wait_for_services
    show_status
    show_access_info
}

# 運行主函數
main
