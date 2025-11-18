"""
整合測試 - 框架導入測試

測試各個 LLM 框架是否可以正常導入。
"""

import pytest


@pytest.mark.integration
class TestFrameworkImports:
    """測試各個框架的導入"""

    def test_import_langchain(self):
        """測試 LangChain 導入"""
        try:
            import langchain
            from langchain.schema import Document

            assert hasattr(langchain, "__version__")
            # 測試基本類可以實例化
            doc = Document(page_content="test", metadata={})
            assert doc.page_content == "test"
        except ImportError as e:
            pytest.skip(f"LangChain 未安裝: {e}")

    def test_import_langchain_core(self):
        """測試 LangChain Core 導入"""
        try:
            from langchain_core.messages import HumanMessage

            msg = HumanMessage(content="Hello")
            assert msg.content == "Hello"
        except ImportError as e:
            pytest.skip(f"LangChain Core 未安裝: {e}")

    def test_import_langgraph(self):
        """測試 LangGraph 導入"""
        try:
            import langgraph

            assert hasattr(langgraph, "__version__")
        except ImportError as e:
            pytest.skip(f"LangGraph 未安裝: {e}")

    def test_import_llama_index(self):
        """測試 LlamaIndex 導入"""
        try:
            import llama_index

            assert hasattr(llama_index, "__version__")
        except ImportError as e:
            pytest.skip(f"LlamaIndex 未安裝: {e}")

    def test_import_autogen(self):
        """測試 AutoGen 導入"""
        try:
            import autogen

            assert hasattr(autogen, "__version__")
        except ImportError as e:
            pytest.skip(f"AutoGen 未安裝: {e}")

    def test_import_crewai(self):
        """測試 CrewAI 導入"""
        try:
            import crewai

            assert crewai is not None
        except ImportError as e:
            pytest.skip(f"CrewAI 未安裝: {e}")

    def test_import_openai(self):
        """測試 OpenAI 導入"""
        try:
            import openai

            assert hasattr(openai, "__version__")
        except ImportError as e:
            pytest.skip(f"OpenAI 未安裝: {e}")

    def test_import_chromadb(self):
        """測試 ChromaDB 導入"""
        try:
            import chromadb

            assert chromadb is not None
        except ImportError as e:
            pytest.skip(f"ChromaDB 未安裝: {e}")


@pytest.mark.integration
class TestDataProcessingLibraries:
    """測試數據處理庫的導入"""

    def test_import_pandas(self):
        """測試 Pandas 導入"""
        try:
            import pandas as pd

            df = pd.DataFrame({"a": [1, 2, 3]})
            assert len(df) == 3
        except ImportError as e:
            pytest.skip(f"Pandas 未安裝: {e}")

    def test_import_numpy(self):
        """測試 NumPy 導入"""
        try:
            import numpy as np

            arr = np.array([1, 2, 3])
            assert len(arr) == 3
        except ImportError as e:
            pytest.skip(f"NumPy 未安裝: {e}")
