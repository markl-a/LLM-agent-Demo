"""
LangChain 工具模組 - 提供 LangChain 相關的實用工具

本模組包含：
- 便捷的 LLM 初始化函數
- RAG 管道構建工具
- 常用 Prompt 模板
- 對話記憶管理
"""

from typing import Optional, List, Dict, Any

__all__ = [
    "create_chat_model",
    "create_embeddings",
    "create_vector_store",
    "RAGConfig",
    "SYSTEM_PROMPTS",
]


# ==================== 常用系統提示詞模板 ====================
SYSTEM_PROMPTS = {
    "assistant": "你是一個有幫助的 AI 助手。請用專業且友善的語氣回答問題。",
    "coder": "你是一個專業的程式設計助手。請提供清晰、可維護的代碼，並解釋你的實現思路。",
    "analyst": "你是一個數據分析專家。請提供詳細的分析和可視化建議。",
    "translator": "你是一個專業翻譯。請保持原文的語氣和風格，同時確保翻譯的準確性。",
    "summarizer": "你是一個摘要專家。請提取文檔的關鍵信息，生成簡潔準確的摘要。",
    "qa_rag": """你是一個基於檢索增強生成 (RAG) 的問答助手。
請根據提供的上下文回答問題。如果上下文中沒有相關信息，請誠實地說明。

上下文：
{context}

問題：{question}

請提供準確、有幫助的回答：""",
}


class RAGConfig:
    """
    RAG (檢索增強生成) 配置類

    用於統一管理 RAG 管道的各項參數。

    Attributes:
        chunk_size: 文檔分塊大小
        chunk_overlap: 分塊重疊大小
        top_k: 檢索返回的文檔數量
        score_threshold: 相似度閾值
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        top_k: int = 5,
        score_threshold: float = 0.7,
        embedding_model: str = "text-embedding-3-small",
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.embedding_model = embedding_model

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "top_k": self.top_k,
            "score_threshold": self.score_threshold,
            "embedding_model": self.embedding_model,
        }


def create_chat_model(
    provider: str = "openai",
    model: Optional[str] = None,
    temperature: float = 0.7,
    api_key: Optional[str] = None,
    **kwargs,
):
    """
    創建聊天模型實例的便捷函數

    支援多個 LLM 提供商：OpenAI、Anthropic、Google 等。

    Args:
        provider: LLM 提供商 ("openai", "anthropic", "google")
        model: 模型名稱，如不指定則使用預設值
        temperature: 生成溫度 (0-2)
        api_key: API 密鑰，如不指定則從環境變數讀取
        **kwargs: 其他模型參數

    Returns:
        聊天模型實例

    Raises:
        ImportError: 如果相關依賴未安裝
        ValueError: 如果提供商不支援

    Example:
        >>> llm = create_chat_model("openai", model="gpt-4o-mini")
        >>> response = llm.invoke("你好！")
    """
    import os

    provider = provider.lower()

    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError("請安裝 langchain-openai: pip install langchain-openai")

        return ChatOpenAI(
            model=model or "gpt-4o-mini",
            temperature=temperature,
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            **kwargs,
        )

    elif provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError("請安裝 langchain-anthropic: pip install langchain-anthropic")

        return ChatAnthropic(
            model=model or "claude-3-5-sonnet-20241022",
            temperature=temperature,
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            **kwargs,
        )

    elif provider == "google":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise ImportError(
                "請安裝 langchain-google-genai: pip install langchain-google-genai"
            )

        return ChatGoogleGenerativeAI(
            model=model or "gemini-2.0-flash-exp",
            temperature=temperature,
            google_api_key=api_key or os.getenv("GOOGLE_API_KEY"),
            **kwargs,
        )

    else:
        raise ValueError(
            f"不支援的提供商: {provider}。支援的提供商: openai, anthropic, google"
        )


def create_embeddings(
    provider: str = "openai",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
):
    """
    創建嵌入模型實例的便捷函數

    Args:
        provider: 提供商 ("openai", "huggingface")
        model: 模型名稱
        api_key: API 密鑰

    Returns:
        嵌入模型實例

    Example:
        >>> embeddings = create_embeddings("openai")
        >>> vectors = embeddings.embed_documents(["Hello", "World"])
    """
    import os

    provider = provider.lower()

    if provider == "openai":
        try:
            from langchain_openai import OpenAIEmbeddings
        except ImportError:
            raise ImportError("請安裝 langchain-openai: pip install langchain-openai")

        return OpenAIEmbeddings(
            model=model or "text-embedding-3-small",
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
        )

    elif provider == "huggingface":
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            raise ImportError(
                "請安裝 langchain-huggingface: pip install langchain-huggingface"
            )

        return HuggingFaceEmbeddings(
            model_name=model or "sentence-transformers/all-MiniLM-L6-v2",
        )

    else:
        raise ValueError(f"不支援的提供商: {provider}。支援的提供商: openai, huggingface")


def create_vector_store(
    store_type: str = "chroma",
    embeddings=None,
    persist_directory: Optional[str] = None,
    collection_name: str = "default",
    **kwargs,
):
    """
    創建向量存儲實例的便捷函數

    Args:
        store_type: 向量存儲類型 ("chroma", "faiss")
        embeddings: 嵌入模型實例
        persist_directory: 持久化目錄
        collection_name: 集合名稱
        **kwargs: 其他參數

    Returns:
        向量存儲實例

    Example:
        >>> embeddings = create_embeddings()
        >>> vectorstore = create_vector_store("chroma", embeddings=embeddings)
    """
    if embeddings is None:
        embeddings = create_embeddings()

    store_type = store_type.lower()

    if store_type == "chroma":
        try:
            from langchain_chroma import Chroma
        except ImportError:
            raise ImportError("請安裝 langchain-chroma: pip install langchain-chroma")

        return Chroma(
            embedding_function=embeddings,
            persist_directory=persist_directory,
            collection_name=collection_name,
            **kwargs,
        )

    elif store_type == "faiss":
        try:
            from langchain_community.vectorstores import FAISS
        except ImportError:
            raise ImportError(
                "請安裝 langchain-community 和 faiss: pip install langchain-community faiss-cpu"
            )

        # FAISS 需要先有文檔才能創建
        return FAISS

    else:
        raise ValueError(f"不支援的向量存儲: {store_type}。支援的類型: chroma, faiss")
