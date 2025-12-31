"""
Google ADK - Vertex AI 整合範例

這個範例展示如何使用 Google Vertex AI 平台：
- Vertex AI 環境配置
- 模型部署和管理
- 企業級功能（監控、日誌、安全）
- AutoML 整合
- 批次預測
"""

import os
from typing import Optional, List, Dict, Any
from google.cloud import aiplatform
from google_adk import VertexAgent
from google_adk.vertex import VertexConfig, ModelRegistry


class VertexAIExample:
    """Vertex AI 整合範例類"""

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1"
    ):
        """
        初始化 Vertex AI 範例

        Args:
            project_id: Google Cloud 專案 ID
            location: Vertex AI 區域
        """
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location

        if not self.project_id:
            raise ValueError("請設置 GOOGLE_CLOUD_PROJECT 環境變量")

        # 初始化 Vertex AI
        aiplatform.init(
            project=self.project_id,
            location=self.location
        )

        print(f"Vertex AI 初始化完成")
        print(f"  專案: {self.project_id}")
        print(f"  區域: {self.location}")

    def example_1_basic_vertex_agent(self):
        """範例 1: 創建基礎 Vertex AI Agent"""
        print("\n" + "="*60)
        print("範例 1: 創建基礎 Vertex AI Agent")
        print("="*60)

        # 配置 Vertex AI
        config = VertexConfig(
            project_id=self.project_id,
            location=self.location,
            model_name="gemini-pro",
            endpoint_name="default"
        )

        # 創建 Vertex Agent
        agent = VertexAgent(
            config=config,
            name="vertex-basic-agent",
            instructions="你是一個企業級 AI 助手。"
        )

        # 測試對話
        prompt = "請介紹 Vertex AI 的主要功能。"
        print(f"\n問題: {prompt}")

        response = agent.run(prompt)
        print(f"\n回答: {response.content}")

        return agent

    def example_2_model_deployment(self):
        """範例 2: 模型部署"""
        print("\n" + "="*60)
        print("範例 2: 模型部署")
        print("="*60)

        # 模型部署配置
        deployment_config = {
            "model_name": "gemini-pro",
            "machine_type": "n1-standard-4",
            "min_replica_count": 1,
            "max_replica_count": 3,
            "accelerator_type": None  # 或 "NVIDIA_TESLA_T4"
        }

        print("部署配置:")
        for key, value in deployment_config.items():
            print(f"  {key}: {value}")

        # 部署模型（示意）
        """
        from google.cloud.aiplatform import Model, Endpoint

        # 上傳模型
        model = Model.upload(
            display_name="my-gemini-model",
            artifact_uri="gs://your-bucket/model",
            serving_container_image_uri="gcr.io/vertex-ai/prediction/..."
        )

        # 創建端點
        endpoint = Endpoint.create(
            display_name="my-endpoint",
            project=self.project_id,
            location=self.location
        )

        # 部署到端點
        model.deploy(
            endpoint=endpoint,
            deployed_model_display_name="gemini-deployment",
            machine_type=deployment_config["machine_type"],
            min_replica_count=deployment_config["min_replica_count"],
            max_replica_count=deployment_config["max_replica_count"]
        )
        """

        print("\n✓ 模型部署流程示意完成")

    def example_3_model_versioning(self):
        """範例 3: 模型版本管理"""
        print("\n" + "="*60)
        print("範例 3: 模型版本管理")
        print("="*60)

        # 使用模型註冊表
        registry = ModelRegistry(
            project_id=self.project_id,
            location=self.location
        )

        # 註冊新模型版本
        model_info = {
            "name": "customer-service-agent",
            "version": "v1.2.0",
            "base_model": "gemini-pro",
            "description": "客服 Agent 模型 v1.2.0",
            "tags": ["production", "customer-service"]
        }

        print("註冊模型版本:")
        for key, value in model_info.items():
            print(f"  {key}: {value}")

        # 模擬模型版本操作
        """
        # 註冊版本
        registry.register_version(
            model_name=model_info["name"],
            version=model_info["version"],
            model_uri="gs://bucket/models/v1.2.0",
            metadata=model_info
        )

        # 列出所有版本
        versions = registry.list_versions(model_info["name"])

        # 設置默認版本
        registry.set_default_version(
            model_name=model_info["name"],
            version=model_info["version"]
        )
        """

        print("\n✓ 模型版本管理示意完成")

    def example_4_batch_prediction(self):
        """範例 4: 批次預測"""
        print("\n" + "="*60)
        print("範例 4: 批次預測")
        print("="*60)

        # 批次預測配置
        batch_config = {
            "input_uri": "gs://your-bucket/input/data.jsonl",
            "output_uri": "gs://your-bucket/output/",
            "instances_format": "jsonl",
            "predictions_format": "jsonl",
            "machine_type": "n1-standard-4"
        }

        print("批次預測配置:")
        for key, value in batch_config.items():
            print(f"  {key}: {value}")

        # 執行批次預測（示意）
        """
        from google.cloud.aiplatform import Model

        model = Model("projects/.../locations/.../models/...")

        batch_prediction_job = model.batch_predict(
            job_display_name="batch-prediction-job",
            gcs_source=batch_config["input_uri"],
            gcs_destination_prefix=batch_config["output_uri"],
            instances_format=batch_config["instances_format"],
            predictions_format=batch_config["predictions_format"],
            machine_type=batch_config["machine_type"]
        )

        # 等待完成
        batch_prediction_job.wait()

        print(f"批次預測完成: {batch_prediction_job.state}")
        print(f"輸出位置: {batch_prediction_job.output_info}")
        """

        print("\n✓ 批次預測流程示意完成")

    def example_5_monitoring_logging(self):
        """範例 5: 監控和日誌"""
        print("\n" + "="*60)
        print("範例 5: 監控和日誌")
        print("="*60)

        from google.cloud import logging as cloud_logging
        from google_adk.monitoring import VertexMonitoring

        # 配置日誌
        logging_client = cloud_logging.Client(project=self.project_id)
        logger = logging_client.logger("vertex-ai-agent")

        # 配置監控
        monitoring = VertexMonitoring(
            project_id=self.project_id,
            metrics=[
                "prediction_count",
                "prediction_latency",
                "error_count",
                "token_usage"
            ]
        )

        # 創建帶監控的 Agent
        config = VertexConfig(
            project_id=self.project_id,
            location=self.location,
            model_name="gemini-pro"
        )

        agent = VertexAgent(
            config=config,
            monitoring=monitoring,
            logger=logger
        )

        print("監控指標:")
        print("  - 預測次數")
        print("  - 預測延遲")
        print("  - 錯誤計數")
        print("  - Token 使用量")

        # 記錄日誌
        logger.log_text("Agent 初始化完成", severity="INFO")

        # 執行預測並記錄
        prompt = "測試監控功能"
        response = agent.run(prompt)

        # 記錄指標
        monitoring.record_metric("prediction_count", 1)
        monitoring.record_metric("token_usage", len(response.content))

        print("\n✓ 監控和日誌配置完成")

        return agent

    def example_6_automl_integration(self):
        """範例 6: AutoML 整合"""
        print("\n" + "="*60)
        print("範例 6: AutoML 整合")
        print("="*60)

        # AutoML 訓練配置
        automl_config = {
            "dataset_id": "your-dataset-id",
            "model_type": "text-classification",
            "training_budget": 1,  # 小時
            "optimization_objective": "maximize-au-prc"
        }

        print("AutoML 配置:")
        for key, value in automl_config.items():
            print(f"  {key}: {value}")

        # AutoML 訓練流程（示意）
        """
        from google.cloud import automl_v1

        client = automl_v1.AutoMlClient()

        # 創建數據集
        dataset = client.create_dataset(
            parent=f"projects/{self.project_id}/locations/{self.location}",
            dataset={
                "display_name": "my-dataset",
                "text_classification_dataset_metadata": {}
            }
        )

        # 導入數據
        client.import_data(
            name=dataset.name,
            input_config={
                "gcs_source": {
                    "input_uris": ["gs://bucket/data.csv"]
                }
            }
        )

        # 訓練模型
        model = client.create_model(
            parent=f"projects/{self.project_id}/locations/{self.location}",
            model={
                "display_name": "automl-text-model",
                "dataset_id": dataset.name.split("/")[-1],
                "text_classification_model_metadata": {}
            }
        )
        """

        print("\n✓ AutoML 整合示意完成")

    def example_7_security_compliance(self):
        """範例 7: 安全性和合規性"""
        print("\n" + "="*60)
        print("範例 7: 安全性和合規性")
        print("="*60)

        from google_adk.security import SecurityPolicy, AuditLogger

        # 配置安全策略
        security_policy = SecurityPolicy(
            encryption_enabled=True,
            data_residency="us",
            compliance_standards=["SOC2", "ISO27001"],
            allowed_ip_ranges=["10.0.0.0/8"],
            require_authentication=True
        )

        # 配置審計日誌
        audit_logger = AuditLogger(
            project_id=self.project_id,
            log_name="vertex-ai-audit"
        )

        # 創建安全的 Agent
        config = VertexConfig(
            project_id=self.project_id,
            location=self.location,
            model_name="gemini-pro",
            security_policy=security_policy
        )

        agent = VertexAgent(
            config=config,
            audit_logger=audit_logger
        )

        print("安全配置:")
        print(f"  加密: {security_policy.encryption_enabled}")
        print(f"  資料駐留: {security_policy.data_residency}")
        print(f"  合規標準: {', '.join(security_policy.compliance_standards)}")

        # 執行帶審計的請求
        prompt = "測試安全功能"
        response = agent.run(prompt)

        # 記錄審計日誌
        audit_logger.log({
            "action": "predict",
            "user": "system",
            "timestamp": "2025-12-31T00:00:00Z",
            "resource": agent.name,
            "result": "success"
        })

        print("\n✓ 安全性和合規性配置完成")

        return agent

    def example_8_custom_endpoints(self):
        """範例 8: 自定義端點"""
        print("\n" + "="*60)
        print("範例 8: 自定義端點")
        print("="*60)

        # 創建自定義端點
        endpoint_config = {
            "display_name": "custom-gemini-endpoint",
            "description": "自定義的 Gemini 部署端點",
            "network": "projects/{}/global/networks/default".format(self.project_id),
            "enable_private_endpoint": False
        }

        print("端點配置:")
        for key, value in endpoint_config.items():
            print(f"  {key}: {value}")

        # 創建端點（示意）
        """
        from google.cloud.aiplatform import Endpoint

        endpoint = Endpoint.create(
            display_name=endpoint_config["display_name"],
            description=endpoint_config["description"],
            project=self.project_id,
            location=self.location,
            network=endpoint_config["network"]
        )

        print(f"端點創建完成: {endpoint.resource_name}")
        print(f"端點 URL: {endpoint.predict_http_uri}")
        """

        print("\n✓ 自定義端點配置完成")

    def example_9_pipeline_integration(self):
        """範例 9: Vertex AI Pipeline 整合"""
        print("\n" + "="*60)
        print("範例 9: Vertex AI Pipeline 整合")
        print("="*60)

        # Pipeline 定義
        print("定義 AI Pipeline:")

        pipeline_steps = """
        from kfp.v2 import dsl, compiler
        from google_cloud_pipeline_components import aiplatform as gcc_aip

        @dsl.pipeline(
            name='agent-training-pipeline',
            description='Agent 訓練和部署 Pipeline'
        )
        def agent_pipeline(
            project_id: str,
            location: str,
            model_name: str
        ):
            # 步驟 1: 數據準備
            data_prep_op = dsl.ContainerOp(
                name='data-preparation',
                image='gcr.io/project/data-prep:latest'
            )

            # 步驟 2: 模型訓練
            training_op = gcc_aip.CustomTrainingJobOp(
                project=project_id,
                location=location,
                display_name='agent-training',
                container_uri='gcr.io/project/trainer:latest'
            )

            # 步驟 3: 模型評估
            eval_op = dsl.ContainerOp(
                name='model-evaluation',
                image='gcr.io/project/evaluator:latest'
            )

            # 步驟 4: 模型部署
            deploy_op = gcc_aip.ModelDeployOp(
                project=project_id,
                location=location,
                model=training_op.outputs['model']
            )

        # 編譯 Pipeline
        compiler.Compiler().compile(
            pipeline_func=agent_pipeline,
            package_path='agent_pipeline.json'
        )
        """

        print(pipeline_steps)
        print("\n✓ Pipeline 整合示意完成")

    def example_10_cost_optimization(self):
        """範例 10: 成本優化"""
        print("\n" + "="*60)
        print("範例 10: 成本優化")
        print("="*60)

        from google_adk.optimization import CostOptimizer

        # 配置成本優化器
        optimizer = CostOptimizer(
            project_id=self.project_id,
            strategies=[
                "auto_scaling",      # 自動擴展
                "batch_processing",  # 批次處理
                "cache_responses",   # 響應緩存
                "smart_routing"      # 智能路由
            ]
        )

        print("成本優化策略:")
        print("  1. 自動擴展: 根據負載動態調整資源")
        print("  2. 批次處理: 合併請求減少調用次數")
        print("  3. 響應緩存: 緩存常見查詢結果")
        print("  4. 智能路由: 選擇性價比最高的模型")

        # 應用優化策略
        config = VertexConfig(
            project_id=self.project_id,
            location=self.location,
            model_name="gemini-pro",
            cost_optimizer=optimizer
        )

        agent = VertexAgent(config=config)

        # 成本報告
        cost_report = {
            "total_requests": 1000,
            "cached_requests": 300,
            "cache_hit_rate": "30%",
            "estimated_savings": "$50",
            "optimization_recommendations": [
                "增加緩存 TTL 到 2 小時",
                "使用批次 API 處理大量請求",
                "在低峰時段處理非緊急任務"
            ]
        }

        print("\n成本報告:")
        for key, value in cost_report.items():
            if isinstance(value, list):
                print(f"  {key}:")
                for item in value:
                    print(f"    - {item}")
            else:
                print(f"  {key}: {value}")

        return agent


def main():
    """主函數"""
    print("="*60)
    print("Google ADK - Vertex AI 整合範例")
    print("="*60)

    # 檢查環境變量
    if not os.getenv("GOOGLE_CLOUD_PROJECT"):
        print("\n⚠️  請先設置 GOOGLE_CLOUD_PROJECT 環境變量")
        print("export GOOGLE_CLOUD_PROJECT='your-project-id'")
        return

    try:
        # 創建範例實例
        example = VertexAIExample()

        # 運行所有範例
        example.example_1_basic_vertex_agent()
        example.example_2_model_deployment()
        example.example_3_model_versioning()
        example.example_4_batch_prediction()
        example.example_5_monitoring_logging()
        example.example_6_automl_integration()
        example.example_7_security_compliance()
        example.example_8_custom_endpoints()
        example.example_9_pipeline_integration()
        example.example_10_cost_optimization()

        print("\n" + "="*60)
        print("所有 Vertex AI 整合範例執行完成！")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 執行錯誤: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
