"""
Langfuse 生產部署示例

這個示例展示如何將 Langfuse 部署到生產環境，包括：
- 生產環境最佳實踐
- 高可用性配置
- 性能優化
- 安全加固
- 監控和告警
- 災難恢復

主要內容：
1. 生產環境架構設計
2. 高可用性部署
3. 性能優化配置
4. 安全最佳實踐
5. 監控和日誌
6. 備份和災難恢復
7. CI/CD 集成

作者: Langfuse Team
日期: 2025-01-01
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional


# ============================================================================
# 第一部分：生產環境架構
# ============================================================================

class ProductionArchitecture:
    """
    生產環境架構設計

    展示生產級別的系統架構。
    """

    @staticmethod
    def display_architecture():
        """
        顯示生產環境架構圖

        展示推薦的生產環境架構。
        """
        print("\n" + "="*60)
        print("生產環境架構設計")
        print("="*60)

        architecture = """
╔══════════════════════════════════════════════════════════════╗
║              Langfuse 生產環境架構圖                         ║
╚══════════════════════════════════════════════════════════════╝

                        Internet
                            │
                            ▼
                    ┌───────────────┐
                    │  Load Balancer│  ← CDN/WAF
                    │   (AWS ALB)   │
                    └───────┬───────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌──────────────┐┌──────────────┐┌──────────────┐
    │ Langfuse App ││ Langfuse App ││ Langfuse App │
    │  Instance 1  ││  Instance 2  ││  Instance 3  │
    └──────┬───────┘└──────┬───────┘└──────┬───────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
    ┌──────────────┐┌──────────────┐┌──────────────┐
    │   Redis      ││  PostgreSQL  ││   S3/MinIO   │
    │  Cluster     ││   Primary    ││    存儲      │
    │  (緩存)      ││              ││              │
    └──────────────┘│              │└──────────────┘
                    │              │
                    ▼              ▼
            ┌──────────────┐┌──────────────┐
            │  PostgreSQL  ││  PostgreSQL  │
            │   Replica 1  ││   Replica 2  │
            └──────────────┘└──────────────┘
                    │
                    ▼
            ┌──────────────┐
            │   Backup     │
            │   Storage    │
            └──────────────┘

        ┌─────────────────────────────────────┐
        │         監控和日誌層                │
        ├─────────────────────────────────────┤
        │  • Prometheus (指標收集)            │
        │  • Grafana (可視化)                 │
        │  • ELK Stack (日誌管理)             │
        │  • Alertmanager (告警)              │
        └─────────────────────────────────────┘

關鍵組件說明:
═══════════════════════════════════════════════════════

1. 負載均衡器 (Load Balancer)
   • 功能: 分發流量到多個應用實例
   • 建議: AWS ALB, GCP Load Balancer, Nginx
   • 配置: 健康檢查、SSL 終止、會話保持

2. 應用層 (Langfuse Instances)
   • 部署: 至少 3 個實例（跨可用區）
   • 資源: 每個實例 2-4 CPU, 4-8GB RAM
   • 擴展: 基於 CPU/內存使用自動擴展

3. 數據層
   • PostgreSQL: 主從複製，至少 1 主 2 從
   • Redis: 集群模式，用於緩存和會話
   • S3/MinIO: 對象存儲，用於大文件

4. 監控層
   • 實時監控系統健康狀態
   • 收集和分析日誌
   • 自動告警機制

5. 備份
   • 數據庫: 每日全量 + 增量備份
   • 文件: 版本化存儲
   • 異地備份: 至少一個異地副本
"""

        print(architecture)
        print("\n✅ 架構設計展示完成")

    @staticmethod
    def generate_infrastructure_code():
        """
        生成基礎設施代碼

        提供 Terraform 配置示例。
        """
        print("\n" + "="*60)
        print("基礎設施即代碼 (Terraform)")
        print("="*60)

        terraform_config = """# Langfuse 生產環境 Terraform 配置
# Provider: AWS

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "your-terraform-state"
    key    = "langfuse/production/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC 和網絡
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "langfuse-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false

  tags = {
    Environment = "production"
    Project     = "langfuse"
  }
}

# RDS PostgreSQL
module "db" {
  source = "terraform-aws-modules/rds/aws"

  identifier = "langfuse-postgres"

  engine               = "postgres"
  engine_version       = "15.4"
  family              = "postgres15"
  major_engine_version = "15"
  instance_class       = "db.r6g.xlarge"

  allocated_storage     = 100
  max_allocated_storage = 500

  db_name  = "langfuse"
  username = "langfuse"
  port     = 5432

  multi_az               = true
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [aws_security_group.db.id]

  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  tags = {
    Environment = "production"
  }
}

# ElastiCache Redis
module "redis" {
  source = "terraform-aws-modules/elasticache/aws"

  cluster_id           = "langfuse-redis"
  engine              = "redis"
  engine_version      = "7.0"
  node_type           = "cache.r6g.large"
  num_cache_nodes     = 3
  parameter_group_name = "default.redis7"

  subnet_group_name    = module.vpc.elasticache_subnet_group_name
  security_group_ids   = [aws_security_group.redis.id]

  automatic_failover_enabled = true
  multi_az_enabled          = true

  tags = {
    Environment = "production"
  }
}

# ECS Cluster (用於運行 Langfuse)
resource "aws_ecs_cluster" "main" {
  name = "langfuse-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Environment = "production"
  }
}

# Application Load Balancer
module "alb" {
  source = "terraform-aws-modules/alb/aws"

  name = "langfuse-alb"

  load_balancer_type = "application"

  vpc_id          = module.vpc.vpc_id
  subnets         = module.vpc.public_subnets
  security_groups = [aws_security_group.alb.id]

  target_groups = [
    {
      name_prefix      = "lang-"
      backend_protocol = "HTTP"
      backend_port     = 3000
      target_type      = "ip"
      health_check = {
        enabled             = true
        interval            = 30
        path                = "/api/health"
        port                = "traffic-port"
        healthy_threshold   = 3
        unhealthy_threshold = 3
        timeout             = 6
        protocol            = "HTTP"
        matcher             = "200"
      }
    }
  ]

  https_listeners = [
    {
      port               = 443
      protocol           = "HTTPS"
      certificate_arn    = aws_acm_certificate.main.arn
      target_group_index = 0
    }
  ]

  http_tcp_listeners = [
    {
      port        = 80
      protocol    = "HTTP"
      action_type = "redirect"
      redirect = {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
  ]

  tags = {
    Environment = "production"
  }
}

# S3 Bucket for storage
resource "aws_s3_bucket" "storage" {
  bucket = "langfuse-production-storage"

  tags = {
    Environment = "production"
  }
}

resource "aws_s3_bucket_versioning" "storage" {
  bucket = aws_s3_bucket.storage.id

  versioning_configuration {
    status = "Enabled"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/langfuse"
  retention_in_days = 30

  tags = {
    Environment = "production"
  }
}

# 變量定義
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# 輸出
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = module.alb.lb_dns_name
}

output "db_endpoint" {
  description = "Database endpoint"
  value       = module.db.db_instance_endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.redis.cache_nodes[0].address
  sensitive   = true
}
"""

        print("📝 Terraform 配置示例:")
        print("-" * 60)
        print(terraform_config[:1000] + "\n...(已截斷)")
        print("-" * 60)

        print("\n💡 使用方法:")
        print("   terraform init")
        print("   terraform plan")
        print("   terraform apply")

        print("\n✅ 基礎設施代碼生成完成")


# ============================================================================
# 第二部分：高可用性配置
# ============================================================================

class HighAvailability:
    """
    高可用性配置

    確保系統的高可用性和容錯能力。
    """

    @staticmethod
    def generate_ha_config():
        """
        生成高可用性配置

        提供 HA 配置指南。
        """
        print("\n" + "="*60)
        print("高可用性配置指南")
        print("="*60)

        ha_guide = """
╔══════════════════════════════════════════════════════════════╗
║              高可用性 (HA) 配置指南                          ║
╚══════════════════════════════════════════════════════════════╝

🎯 可用性目標
─────────────────────────────────────────────────────
• 目標 SLA: 99.9% (每月停機 < 43 分鐘)
• RTO (恢復時間目標): < 15 分鐘
• RPO (恢復點目標): < 5 分鐘
• 容錯能力: 單個可用區失敗不影響服務


📊 應用層 HA
─────────────────────────────────────────────────────
1. 多實例部署
   • 最少 3 個實例（跨 3 個可用區）
   • 自動擴展: 根據 CPU/內存動態調整
   • 健康檢查: 每 10 秒檢查 /api/health

2. 負載均衡
   • 跨區域負載均衡
   • 會話保持（如需要）
   • 自動故障轉移

3. 零停機部署
   • 滾動更新策略
   • 藍綠部署
   • 金絲雀發布

Docker Swarm 配置示例:
───────────────────────────────────────────────
version: '3.8'
services:
  langfuse:
    image: langfuse/langfuse:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: any
        delay: 5s
        max_attempts: 3
      placement:
        max_replicas_per_node: 1
        constraints:
          - node.role == worker


🗄️  數據層 HA
─────────────────────────────────────────────────────
1. PostgreSQL 高可用
   • 主從複製（1 主 + 2 從）
   • 自動故障轉移（使用 Patroni 或雲服務）
   • 同步複製保證數據一致性

2. Redis 高可用
   • Redis Sentinel 或 Redis Cluster
   • 至少 3 個節點
   • 自動故障檢測和轉移

3. 存儲層
   • 使用雲對象存儲（S3/GCS）
   • 跨區域複製
   • 版本控制


Kubernetes StatefulSet 示例:
───────────────────────────────────────────────
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: langfuse-postgres
spec:
  serviceName: postgres
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
          name: postgres
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 100Gi


🔄 備份和恢復
─────────────────────────────────────────────────────
1. 自動備份
   • 數據庫: 每日全量 + 連續歸檔（WAL）
   • 配置: 版本控制（Git）
   • 數據: S3 版本控制

2. 恢復測試
   • 每月執行恢復演練
   • 驗證備份完整性
   • 測試恢復時間

3. 災難恢復
   • 異地備份（不同區域）
   • 災難恢復運行手冊
   • 定期演練


📈 監控和告警
─────────────────────────────────────────────────────
1. 健康檢查
   • 應用: HTTP 200 /api/health
   • 數據庫: pg_isready
   • Redis: PING

2. 關鍵指標
   • 可用性: 99.9% SLA
   • 響應時間: P95 < 500ms
   • 錯誤率: < 0.1%

3. 告警規則
   • 服務不可用: 立即告警
   • 高延遲: 2 分鐘內告警
   • 錯誤激增: 5 分鐘內告警


🔐 安全性
─────────────────────────────────────────────────────
1. 網絡隔離
   • 應用層在私有子網
   • 數據庫層不暴露公網
   • WAF 保護

2. 加密
   • 傳輸加密: TLS 1.3
   • 存儲加密: 數據庫和 S3
   • 密鑰管理: KMS

3. 訪問控制
   • 最小權限原則
   • IAM 角色
   • 定期審計


✅ HA 檢查清單
─────────────────────────────────────────────────────
□ 應用至少 3 個實例
□ 跨多個可用區部署
□ 配置自動擴展
□ 數據庫主從複製
□ 自動故障轉移
□ 定期備份（測試過恢復）
□ 健康檢查和監控
□ 告警配置
□ 災難恢復計劃
□ 定期 HA 演練
"""

        print(ha_guide)
        print("\n✅ HA 配置指南完成")


# ============================================================================
# 第三部分：性能優化
# ============================================================================

class PerformanceOptimization:
    """
    性能優化

    優化生產環境性能。
    """

    @staticmethod
    def generate_optimization_guide():
        """
        生成性能優化指南

        提供性能調優建議。
        """
        print("\n" + "="*60)
        print("性能優化指南")
        print("="*60)

        optimization_guide = """
╔══════════════════════════════════════════════════════════════╗
║                    性能優化指南                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 應用層優化
─────────────────────────────────────────────────────
1. Node.js 優化
   環境變量:
   ─────────────────────────
   NODE_ENV=production
   NODE_OPTIONS=--max-old-space-size=4096
   WEB_CONCURRENCY=4  # CPU 核心數

2. 緩存策略
   • Redis 緩存熱點數據
   • CDN 緩存靜態資源
   • 瀏覽器緩存策略

3. 連接池
   配置示例:
   ─────────────────────────
   DATABASE_POOL_MIN=10
   DATABASE_POOL_MAX=50
   DATABASE_POOL_IDLE_TIMEOUT=30000


🗄️  數據庫優化
─────────────────────────────────────────────────────
1. PostgreSQL 配置
   postgresql.conf:
   ─────────────────────────
   # 內存配置
   shared_buffers = 4GB
   effective_cache_size = 12GB
   work_mem = 64MB
   maintenance_work_mem = 512MB

   # 連接
   max_connections = 200

   # WAL
   wal_buffers = 16MB
   checkpoint_completion_target = 0.9

   # 查詢優化
   random_page_cost = 1.1
   effective_io_concurrency = 200

2. 索引優化
   -- 創建必要索引
   CREATE INDEX CONCURRENTLY idx_traces_user_id
     ON traces(user_id);

   CREATE INDEX CONCURRENTLY idx_traces_created_at
     ON traces(created_at DESC);

   -- 定期維護
   VACUUM ANALYZE;
   REINDEX DATABASE langfuse;

3. 查詢優化
   • 使用 EXPLAIN ANALYZE 分析慢查詢
   • 避免 N+1 查詢
   • 使用連接池


⚡ Redis 優化
─────────────────────────────────────────────────────
redis.conf:
─────────────────────────
# 內存
maxmemory 2gb
maxmemory-policy allkeys-lru

# 持久化（根據需求調整）
save 900 1
save 300 10
save 60 10000

# 網絡
tcp-backlog 511
timeout 0
tcp-keepalive 300


🌐 網絡優化
─────────────────────────────────────────────────────
1. CDN 配置
   • 靜態資源分發
   • 圖片優化
   • Gzip/Brotli 壓縮

2. HTTP/2 和 HTTP/3
   • 啟用多路復用
   • 服務器推送
   • 頭部壓縮

3. 負載均衡優化
   • 連接保持
   • 會話親和性
   • 健康檢查間隔


📊 監控和分析
─────────────────────────────────────────────────────
1. 關鍵性能指標 (KPI)
   • 響應時間: P50, P95, P99
   • 吞吐量: QPS
   • 錯誤率
   • CPU/內存使用率

2. APM (應用性能監控)
   • 分布式追蹤
   • 慢查詢分析
   • 資源使用分析

3. 容量規劃
   • 流量趨勢分析
   • 資源使用預測
   • 擴展計劃


🔧 調優檢查清單
─────────────────────────────────────────────────────
應用層:
□ 生產模式運行
□ 配置連接池
□ 啟用緩存
□ 代碼分割和懶加載
□ 壓縮響應

數據庫:
□ 優化配置參數
□ 創建必要索引
□ 定期 VACUUM
□ 監控慢查詢
□ 使用讀寫分離

緩存:
□ Redis 配置優化
□ 緩存策略制定
□ 緩存命中率監控
□ CDN 配置

網絡:
□ 啟用 HTTP/2
□ 配置 Gzip 壓縮
□ CDN 加速
□ 負載均衡優化

監控:
□ 性能指標收集
□ 告警配置
□ 定期性能測試
□ 容量規劃


📈 性能基準
─────────────────────────────────────────────────────
目標指標:
• P50 響應時間: < 100ms
• P95 響應時間: < 500ms
• P99 響應時間: < 1s
• 吞吐量: > 1000 QPS
• CPU 使用率: < 70%
• 內存使用率: < 80%
• 錯誤率: < 0.1%
"""

        print(optimization_guide)
        print("\n✅ 性能優化指南完成")


# ============================================================================
# 第四部分：安全最佳實踐
# ============================================================================

class SecurityBestPractices:
    """
    安全最佳實踐

    提供生產環境安全配置。
    """

    @staticmethod
    def generate_security_guide():
        """
        生成安全配置指南

        提供全面的安全配置建議。
        """
        print("\n" + "="*60)
        print("安全配置指南")
        print("="*60)

        security_guide = """
╔══════════════════════════════════════════════════════════════╗
║                  生產環境安全指南                            ║
╚══════════════════════════════════════════════════════════════╝

🔐 網絡安全
─────────────────────────────────────────────────────
1. 防火牆規則
   • 只開放必要端口（80, 443）
   • 白名單 IP（管理訪問）
   • DDoS 防護

2. WAF (Web 應用防火牆)
   • OWASP Top 10 保護
   • SQL 注入防護
   • XSS 防護
   • 速率限制

3. VPC 隔離
   • 公共子網: 負載均衡器
   • 私有子網: 應用和數據庫
   • 隔離的數據庫子網


🔒 傳輸加密
─────────────────────────────────────────────────────
1. TLS/SSL 配置
   Nginx 配置:
   ─────────────────────────
   ssl_protocols TLSv1.2 TLSv1.3;
   ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:...;
   ssl_prefer_server_ciphers on;
   ssl_session_cache shared:SSL:10m;

   # HSTS
   add_header Strict-Transport-Security
     "max-age=31536000; includeSubDomains" always;

2. 證書管理
   • 使用可信 CA 證書
   • 自動更新（Let's Encrypt）
   • 證書監控和告警


🗄️  數據加密
─────────────────────────────────────────────────────
1. 靜態數據加密
   • 數據庫加密（透明數據加密）
   • S3 加密（SSE-S3 或 SSE-KMS）
   • 備份加密

2. 密鑰管理
   • AWS KMS / Google Cloud KMS
   • 密鑰輪換策略
   • 最小權限訪問


👤 認證和授權
─────────────────────────────────────────────────────
1. 強密碼策略
   • 最小長度: 12 字符
   • 複雜度要求
   • 定期更換
   • 密碼歷史

2. 多因素認證 (MFA)
   • 管理員賬號必須啟用
   • 支持 TOTP
   • 備用恢復碼

3. OAuth/SSO 集成
   環境變量:
   ─────────────────────────
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-secret
   GITHUB_CLIENT_ID=your-client-id
   GITHUB_CLIENT_SECRET=your-secret

4. API 密鑰管理
   • 定期輪換
   • 範圍限制
   • 使用限制
   • 審計日誌


🛡️  應用安全
─────────────────────────────────────────────────────
1. 安全標頭
   Nginx 配置:
   ─────────────────────────
   add_header X-Frame-Options "DENY";
   add_header X-Content-Type-Options "nosniff";
   add_header X-XSS-Protection "1; mode=block";
   add_header Referrer-Policy "strict-origin-when-cross-origin";
   add_header Content-Security-Policy "default-src 'self'";

2. 輸入驗證
   • 嚴格的類型檢查
   • 長度限制
   • 格式驗證
   • SQL 注入防護

3. 速率限制
   Nginx 配置:
   ─────────────────────────
   limit_req_zone $binary_remote_addr
     zone=api:10m rate=100r/m;

   location /api {
     limit_req zone=api burst=20;
   }


📝 審計和日誌
─────────────────────────────────────────────────────
1. 訪問日誌
   • 記錄所有 API 訪問
   • 包含用戶、IP、時間戳
   • 集中式日誌管理

2. 審計日誌
   • 敏感操作記錄
   • 配置更改
   • 用戶管理操作
   • 數據訪問

3. 日誌保留
   • 訪問日誌: 90 天
   • 審計日誌: 1 年
   • 合規性要求


🔍 漏洞管理
─────────────────────────────────────────────────────
1. 依賴掃描
   # 使用 npm audit
   npm audit
   npm audit fix

   # 使用 Snyk
   snyk test
   snyk monitor

2. 容器掃描
   # 使用 Trivy
   trivy image langfuse/langfuse:latest

3. 定期更新
   • 月度安全更新
   • 及時修復高危漏洞
   • 保持依賴最新


🚨 事件響應
─────────────────────────────────────────────────────
1. 監控和告警
   • 異常登錄檢測
   • 暴力破解檢測
   • 異常 API 調用
   • 數據外洩檢測

2. 響應流程
   • 事件分類和優先級
   • 響應團隊聯絡
   • 隔離和調查
   • 恢復和復盤

3. 災難恢復
   • 備份驗證
   • 恢復演練
   • 業務連續性計劃


✅ 安全檢查清單
─────────────────────────────────────────────────────
網絡:
□ 配置防火牆
□ 啟用 WAF
□ VPC 隔離
□ DDoS 防護

加密:
□ 強制 HTTPS
□ TLS 1.2+
□ 數據庫加密
□ 備份加密

認證:
□ 強密碼策略
□ MFA 啟用
□ SSO 集成
□ API 密鑰管理

應用:
□ 安全標頭
□ 輸入驗證
□ 速率限制
□ 依賴更新

監控:
□ 訪問日誌
□ 審計日誌
□ 安全告警
□ 定期掃描

合規:
□ 數據隱私
□ GDPR 遵循
□ SOC 2
□ ISO 27001
"""

        print(security_guide)
        print("\n✅ 安全配置指南完成")


# ============================================================================
# 第五部分：監控和日誌
# ============================================================================

class MonitoringAndLogging:
    """
    監控和日誌配置

    提供完整的監控和日誌方案。
    """

    @staticmethod
    def generate_monitoring_config():
        """
        生成監控配置

        提供 Prometheus 和 Grafana 配置。
        """
        print("\n" + "="*60)
        print("監控和日誌配置")
        print("="*60)

        prometheus_config = """# Prometheus 配置
# prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - "/etc/prometheus/alerts/*.yml"

scrape_configs:
  # Langfuse 應用指標
  - job_name: 'langfuse'
    static_configs:
      - targets: ['langfuse:3000']
    metrics_path: '/api/metrics'

  # PostgreSQL 指標
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Redis 指標
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  # Node 指標
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']


告警規則示例:
───────────────────────────────────────────────
# alerts/langfuse.yml

groups:
  - name: langfuse
    interval: 30s
    rules:
      # 服務不可用
      - alert: ServiceDown
        expr: up{job="langfuse"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Langfuse服務不可用"
          description: "{{ $labels.instance }} 已停機超過 1 分鐘"

      # 高錯誤率
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "錯誤率過高"
          description: "錯誤率 {{ $value }} 超過 5%"

      # 高延遲
      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "響應時間過長"
          description: "P95 延遲 {{ $value }}s 超過 1 秒"

      # 高 CPU 使用率
      - alert: HighCPU
        expr: rate(process_cpu_seconds_total[5m]) > 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "CPU 使用率過高"

      # 高內存使用率
      - alert: HighMemory
        expr: process_resident_memory_bytes / node_memory_MemTotal_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "內存使用率過高"


Grafana 儀表板配置:
───────────────────────────────────────────────
{
  "dashboard": {
    "title": "Langfuse Production Dashboard",
    "panels": [
      {
        "title": "請求率",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "錯誤率",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "響應時間 (P95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds)"
          }
        ]
      },
      {
        "title": "CPU 使用率",
        "targets": [
          {
            "expr": "rate(process_cpu_seconds_total[5m])"
          }
        ]
      }
    ]
  }
}


ELK Stack 配置（日誌管理）:
───────────────────────────────────────────────
# Filebeat 配置
filebeat.inputs:
  - type: container
    paths:
      - '/var/lib/docker/containers/*/*.log'
    processors:
      - add_docker_metadata: ~

output.elasticsearch:
  hosts: ["elasticsearch:9200"]

# Logstash 配置
input {
  beats {
    port => 5044
  }
}

filter {
  json {
    source => "message"
  }

  if [log][level] == "error" {
    mutate {
      add_tag => [ "error" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "langfuse-%{+YYYY.MM.dd}"
  }
}
"""

        print(prometheus_config)
        print("\n✅ 監控和日誌配置完成")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """
    主函數：展示所有生產部署內容
    """
    print("\n" + "="*70)
    print("Langfuse 生產部署指南")
    print("="*70)

    try:
        # 1. 架構設計
        print("\n第一部分：生產環境架構")
        print("="*70)
        arch = ProductionArchitecture()
        arch.display_architecture()
        arch.generate_infrastructure_code()

        # 2. 高可用性
        print("\n第二部分：高可用性配置")
        print("="*70)
        ha = HighAvailability()
        ha.generate_ha_config()

        # 3. 性能優化
        print("\n第三部分：性能優化")
        print("="*70)
        perf = PerformanceOptimization()
        perf.generate_optimization_guide()

        # 4. 安全性
        print("\n第四部分：安全最佳實踐")
        print("="*70)
        security = SecurityBestPractices()
        security.generate_security_guide()

        # 5. 監控和日誌
        print("\n第五部分：監控和日誌")
        print("="*70)
        monitoring = MonitoringAndLogging()
        monitoring.generate_monitoring_config()

        print("\n" + "="*70)
        print("✅ 生產部署指南完成！")
        print("="*70)

        print("\n📚 文檔清單:")
        print("   ✓ 生產環境架構設計")
        print("   ✓ 基礎設施即代碼 (Terraform)")
        print("   ✓ 高可用性配置")
        print("   ✓ 性能優化指南")
        print("   ✓ 安全最佳實踐")
        print("   ✓ 監控和日誌配置")

        print("\n🎯 部署里程碑:")
        print("   1. ✅ 架構設計評審")
        print("   2. ✅ 基礎設施部署")
        print("   3. ✅ 應用部署和配置")
        print("   4. ✅ 安全加固")
        print("   5. ✅ 監控配置")
        print("   6. ✅ 負載測試")
        print("   7. ✅ 災難恢復演練")
        print("   8. ✅ 上線")

        print("\n⚠️  生產上線前檢查清單:")
        print("   □ 架構評審通過")
        print("   □ 安全掃描通過")
        print("   □ 性能測試通過")
        print("   □ HA 測試通過")
        print("   □ 備份恢復測試")
        print("   □ 監控告警配置")
        print("   □ 文檔完整")
        print("   □ 運維團隊培訓")
        print("   □ 回滾計劃準備")
        print("   □ 上線審批")

    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
