#!/usr/bin/env python3
"""測試所有模組的導入，檢查循環依賴問題"""

import sys
from pathlib import Path

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 70)
print("模組導入測試 - 檢查循環依賴和導出")
print("=" * 70)

# ==================== 測試主模組 ====================
print("\n[1/7] 測試主模組導入...")
try:
    import llm_agent_demo
    print(f"✓ 主模組導入成功")
    print(f"  版本: {llm_agent_demo.__version__}")
    print(f"  作者: {llm_agent_demo.__author__}")
    print(f"  導出項目數: {len(llm_agent_demo.__all__)}")
except Exception as e:
    print(f"✗ 主模組導入失敗: {e}")
    sys.exit(1)

# ==================== 測試 utils 模組 ====================
print("\n[2/7] 測試 utils 模組導入...")
try:
    from llm_agent_demo import utils
    print(f"✓ utils 模組導入成功")
    print(f"  導出項目數: {len(utils.__all__)}")
except Exception as e:
    print(f"✗ utils 模組導入失敗: {e}")
    sys.exit(1)

# ==================== 測試配置管理 ====================
print("\n[3/7] 測試配置管理導入...")
try:
    from llm_agent_demo import (
        Settings,
        get_settings,
        get_openai_config,
        get_logger,
        CostTracker,
    )
    print("✓ 配置管理導入成功")
    print("  - Settings")
    print("  - get_settings")
    print("  - get_openai_config")
    print("  - get_logger")
    print("  - CostTracker")
except Exception as e:
    print(f"✗ 配置管理導入失敗: {e}")
    sys.exit(1)

# ==================== 測試 LangChain 模組 ====================
print("\n[4/7] 測試 LangChain 模組導入...")
try:
    from llm_agent_demo import (
        create_chat_model,
        create_embeddings,
        create_vector_store,
        RAGConfig,
        SYSTEM_PROMPTS,
    )
    print("✓ LangChain 工具導入成功")
    print("  - create_chat_model")
    print("  - create_embeddings")
    print("  - create_vector_store")
    print("  - RAGConfig")
    print("  - SYSTEM_PROMPTS")
    print(f"  系統提示詞模板數: {len(SYSTEM_PROMPTS)}")
except Exception as e:
    print(f"✗ LangChain 工具導入失敗: {e}")
    sys.exit(1)

# ==================== 測試驗證器 ====================
print("\n[5/7] 測試驗證器導入...")
try:
    from llm_agent_demo import (
        validate_api_key,
        validate_model_name,
        validate_temperature,
        ValidationError,
    )
    print("✓ 驗證器導入成功")
    print("  - validate_api_key")
    print("  - validate_model_name")
    print("  - validate_temperature")
    print("  - ValidationError")
except Exception as e:
    print(f"✗ 驗證器導入失敗: {e}")
    sys.exit(1)

# ==================== 測試重試機制 ====================
print("\n[6/7] 測試重試機制導入...")
try:
    from llm_agent_demo import (
        retry_with_exponential_backoff,
        retry_on_rate_limit,
        RetryContext,
    )
    print("✓ 重試機制導入成功")
    print("  - retry_with_exponential_backoff")
    print("  - retry_on_rate_limit")
    print("  - RetryContext")
except Exception as e:
    print(f"✗ 重試機制導入失敗: {e}")
    sys.exit(1)

# ==================== 測試框架模組 ====================
print("\n[7/7] 測試框架模組導入...")
try:
    from llm_agent_demo import autogen, crewai, langchain, llamaindex, metagpt
    print("✓ 框架模組導入成功")
    print("  - autogen")
    print("  - crewai")
    print("  - langchain")
    print("  - llamaindex")
    print("  - metagpt")
except Exception as e:
    print(f"✗ 框架模組導入失敗: {e}")
    sys.exit(1)

# ==================== 測試子模組直接導入 ====================
print("\n" + "=" * 70)
print("子模組直接導入測試")
print("=" * 70)

print("\n測試 utils 子模組...")
try:
    from llm_agent_demo.utils import (
        Settings,
        get_settings,
        get_logger,
        setup_logging,
        CostTracker,
        TokenCounter,
        retry_with_exponential_backoff,
        validate_api_key,
    )
    print("✓ utils 子模組直接導入成功")
except Exception as e:
    print(f"✗ utils 子模組導入失敗: {e}")
    sys.exit(1)

print("\n測試 langchain 子模組...")
try:
    from llm_agent_demo.langchain import (
        create_chat_model,
        create_embeddings,
        RAGConfig,
        SYSTEM_PROMPTS,
    )
    print("✓ langchain 子模組直接導入成功")
except Exception as e:
    print(f"✗ langchain 子模組導入失敗: {e}")
    sys.exit(1)

# ==================== 總結 ====================
print("\n" + "=" * 70)
print("✓ 所有測試通過！沒有發現循環依賴問題。")
print("=" * 70)

# 顯示主模組的所有導出
print("\n主模組 (llm_agent_demo) 的公開 API:")
print("-" * 70)
for i, item in enumerate(llm_agent_demo.__all__, 1):
    print(f"{i:3d}. {item}")

print("\n" + "=" * 70)
print("測試完成！")
print("=" * 70)
