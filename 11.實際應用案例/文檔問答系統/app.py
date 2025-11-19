#!/usr/bin/env python3
"""
文檔問答系統 - Streamlit Web 應用

提供友好的 Web 界面來使用文檔問答系統。
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
import time
import yaml

# 載入環境變數
load_dotenv()

# 導入 RAG 系統
try:
    from rag_system import DocumentQASystem, QueryResult
except ImportError:
    st.error("無法導入 rag_system，請確保文件存在")
    st.stop()

# 頁面配置
st.set_page_config(
    page_title="文檔問答系統",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定義 CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .source-box {
        background-color: #f0f2f6;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
    }
    .stat-box {
        background-color: #e1f5fe;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""",
    unsafe_allow_html=True,
)


# 初始化 Session State
def init_session_state():
    """初始化 Session State"""
    if "qa_system" not in st.session_state:
        st.session_state.qa_system = None

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "index_loaded" not in st.session_state:
        st.session_state.index_loaded = False


init_session_state()


# 側邊欄
def render_sidebar():
    """渲染側邊欄"""
    with st.sidebar:
        st.markdown("## ⚙️ 系統設置")

        # API 配置檢查
        openai_key = os.getenv("OPENAI_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")

        if openai_key:
            st.success("✅ OpenAI API Key 已配置")
        elif google_key:
            st.success("✅ Google API Key 已配置")
        else:
            st.error("❌ 未配置 API Key")
            st.info("請在 .env 文件中設置 OPENAI_API_KEY 或 GOOGLE_API_KEY")

        st.markdown("---")

        # 配置文件
        st.markdown("### 📋 配置")

        config_file = st.text_input("配置文件", value="config.yaml")

        if st.button("載入配置"):
            try:
                st.session_state.qa_system = DocumentQASystem(config_path=config_file)
                st.success("✅ 配置載入成功")
            except Exception as e:
                st.error(f"❌ 配置載入失敗: {str(e)}")

        st.markdown("---")

        # 文檔索引
        st.markdown("### 📂 文檔管理")

        data_dir = st.text_input("文檔目錄", value="./data")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📥 索引文檔", use_container_width=True):
                if not Path(data_dir).exists():
                    st.error(f"目錄不存在: {data_dir}")
                else:
                    index_documents(data_dir)

        with col2:
            if st.button("🔄 載入索引", use_container_width=True):
                load_index()

        st.markdown("---")

        # 系統狀態
        st.markdown("### 📊 系統狀態")

        if st.session_state.qa_system:
            try:
                stats = st.session_state.qa_system.get_stats()

                st.markdown(
                    f"""
                <div class="stat-box">
                    <strong>狀態:</strong> {stats['status']}<br>
                    <strong>LLM:</strong> {stats['config']['llm_model']}<br>
                    <strong>嵌入:</strong> {stats['config']['embedding_model']}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            except:
                st.info("系統未初始化")
        else:
            st.info("系統未初始化")

        st.markdown("---")

        # 清除歷史
        if st.button("🗑️ 清除對話歷史", use_container_width=True):
            st.session_state.chat_history = []
            st.success("✅ 已清除歷史")
            st.rerun()


def index_documents(data_dir: str):
    """索引文檔"""
    if st.session_state.qa_system is None:
        st.session_state.qa_system = DocumentQASystem()

    with st.spinner("正在索引文檔，請稍候..."):
        try:
            st.session_state.qa_system.index_documents(
                data_dir, show_progress=False, force_reindex=True
            )
            st.session_state.index_loaded = True
            st.success("✅ 文檔索引完成")
            st.rerun()
        except Exception as e:
            st.error(f"❌ 索引失敗: {str(e)}")


def load_index():
    """載入索引"""
    if st.session_state.qa_system is None:
        st.session_state.qa_system = DocumentQASystem()

    with st.spinner("正在載入索引..."):
        try:
            st.session_state.qa_system.load_index()
            st.session_state.index_loaded = True
            st.success("✅ 索引載入完成")
            st.rerun()
        except Exception as e:
            st.error(f"❌ 載入失敗: {str(e)}")


def render_main_content():
    """渲染主要內容"""
    st.markdown('<div class="main-header">📚 文檔問答系統</div>', unsafe_allow_html=True)

    st.markdown(
        """
    這是一個基於 RAG（檢索增強生成）技術的智能文檔問答系統。
    請先在側邊欄索引或載入文檔，然後開始提問。
    """
    )

    # 檢查系統狀態
    if not st.session_state.index_loaded:
        st.warning("⚠️ 請先在側邊欄索引或載入文檔")
        return

    # 對話界面
    st.markdown("---")
    st.markdown("### 💬 開始對話")

    # 顯示歷史對話
    for i, chat in enumerate(st.session_state.chat_history):
        with st.container():
            # 用戶問題
            st.markdown(
                f"""
            <div style="background-color: #e3f2fd; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">
                <strong>🧑 您:</strong> {chat['question']}
            </div>
            """,
                unsafe_allow_html=True,
            )

            # AI 回答
            st.markdown(
                f"""
            <div style="background-color: #f1f8e9; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0;">
                <strong>🤖 AI:</strong> {chat['answer']}
            </div>
            """,
                unsafe_allow_html=True,
            )

            # 來源信息
            if chat.get("sources"):
                with st.expander(f"📚 查看來源 ({len(chat['sources'])} 個文檔)"):
                    for j, source in enumerate(chat["sources"], 1):
                        st.markdown(
                            f"""
                        <div class="source-box">
                            <strong>{j}. {source['file_name']}</strong><br>
                            相似度: {source['score']:.2%}<br>
                            <small>{source['text_preview']}</small>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

            # 元數據
            st.caption(f"⏱️ 響應時間: {chat['response_time']:.2f}秒")

    # 輸入框
    st.markdown("---")

    question = st.text_input(
        "💭 您的問題:",
        placeholder="請輸入您的問題...",
        key="question_input",
    )

    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        submit_button = st.button("🚀 提問", use_container_width=True)

    with col2:
        example_button = st.button("💡 範例問題", use_container_width=True)

    # 範例問題
    if example_button:
        examples = [
            "這份文檔的主要內容是什麼？",
            "有哪些重要的政策或規定？",
            "文檔中提到了哪些關鍵日期？",
        ]
        selected_example = st.selectbox("選擇一個範例問題:", examples)
        if st.button("使用此問題"):
            question = selected_example

    # 處理提問
    if submit_button and question:
        handle_query(question)


def handle_query(question: str):
    """處理查詢"""
    if st.session_state.qa_system is None or not st.session_state.index_loaded:
        st.error("❌ 系統未初始化，請先載入索引")
        return

    with st.spinner("🤔 正在思考..."):
        try:
            # 執行查詢
            result = st.session_state.qa_system.query(question, verbose=False)

            # 添加到歷史
            chat_entry = {
                "question": question,
                "answer": result.answer,
                "sources": result.sources,
                "response_time": result.response_time,
            }
            st.session_state.chat_history.append(chat_entry)

            # 重新渲染
            st.rerun()

        except Exception as e:
            st.error(f"❌ 查詢失敗: {str(e)}")


def main():
    """主函數"""
    render_sidebar()
    render_main_content()

    # 頁腳
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        Powered by LlamaIndex & Streamlit |
        <a href="https://github.com/markl-a/LLM-agent-Demo" target="_blank">GitHub</a>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
