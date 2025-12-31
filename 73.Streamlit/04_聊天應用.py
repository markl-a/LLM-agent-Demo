"""
Streamlit 聊天應用示例

運行方式：streamlit run 04_聊天應用.py
需要設置：export OPENAI_API_KEY='your-key'
"""

import streamlit as st
from openai import OpenAI
import os

st.set_page_config(page_title="聊天應用", page_icon="💬", layout="wide")

st.title("💬 Streamlit 聊天應用")

# 初始化 OpenAI 客戶端
client = None
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = OpenAI(api_key=api_key)
    st.success("✅ OpenAI API 已配置")
else:
    st.warning("⚠️ 請設置 OPENAI_API_KEY 環境變量")

# 初始化聊天歷史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示聊天歷史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天輸入
if prompt := st.chat_input("輸入你的消息..."):
    # 添加用戶消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 生成 AI 回覆
    with st.chat_message("assistant"):
        if client:
            # 使用 OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": m["role"], "content": m["content"]} 
                         for m in st.session_state.messages],
                stream=True
            )

            # 流式顯示
            full_response = st.write_stream(response)
        else:
            # 模擬回覆
            full_response = f"你說：{prompt}\n\n這是一個示例回覆。請配置 OpenAI API 以使用真實的 AI。"
            st.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# 清空按鈕
if st.button("🗑️ 清空對話"):
    st.session_state.messages = []
    st.rerun()
