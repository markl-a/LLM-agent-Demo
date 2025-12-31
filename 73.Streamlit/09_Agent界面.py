"""
Streamlit Agent 界面示例

運行方式：streamlit run 09_Agent界面.py
需要設置：export OPENAI_API_KEY='your-key'
"""

import streamlit as st
from openai import OpenAI
import os
import json

st.set_page_config(page_title="Agent 界面", page_icon="🤖", layout="wide")

st.title("🤖 AI Agent 對話界面")
st.markdown("---")

# 初始化 OpenAI
client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 初始化狀態
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

if "agent_thinking" not in st.session_state:
    st.session_state.agent_thinking = []

# 側邊欄 - Agent 設置
with st.sidebar:
    st.header("⚙️ Agent 設置")

    system_prompt = st.text_area(
        "系統提示",
        value="你是一個有幫助的 AI 助手，可以使用工具來回答問題。",
        height=100
    )

    temperature = st.slider("Temperature", 0.0, 2.0, 0.7)

    st.markdown("---")

    st.header("🛠️ 可用工具")
    st.write("- 📊 數據分析")
    st.write("- 🔍 網絡搜索")
    st.write("- 📝 文本生成")

    st.markdown("---")

    if st.button("🗑️ 清空對話"):
        st.session_state.agent_messages = []
        st.session_state.agent_thinking = []
        st.rerun()

# 主界面 - 對話區域
st.header("💬 對話")

# 顯示對話歷史
for msg in st.session_state.agent_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # 如果有工具調用，顯示
        if "tool_calls" in msg:
            with st.expander("🔧 工具調用詳情"):
                st.json(msg["tool_calls"])

# 聊天輸入
if prompt := st.chat_input("輸入你的問題..."):
    # 添加用戶消息
    st.session_state.agent_messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 回覆
    with st.chat_message("assistant"):
        if client:
            # 模擬 Agent 思考過程
            with st.status("🤔 Agent 思考中...", expanded=True) as status:
                st.write("📝 理解問題...")
                st.write("🔍 搜索相關信息...")
                st.write("💡 生成回答...")

                # 調用 OpenAI
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.agent_messages]
                    ],
                    temperature=temperature
                )

                status.update(label="✅ 完成！", state="complete")

            answer = response.choices[0].message.content
            st.markdown(answer)

            # 保存消息
            st.session_state.agent_messages.append({
                "role": "assistant",
                "content": answer
            })
        else:
            st.warning("⚠️ OpenAI API 未配置")
            st.info("這是模擬回覆。請設置 OPENAI_API_KEY 使用真實的 Agent。")

# 思考過程可視化
if st.session_state.agent_thinking:
    st.header("🧠 思考過程")

    for step in st.session_state.agent_thinking:
        with st.expander(f"步驟 {step['step']}: {step['action']}"):
            st.write(step['detail'])

# 使用統計
st.markdown("---")
st.header("📊 使用統計")

col1, col2, col3 = st.columns(3)
col1.metric("對話輪數", len(st.session_state.agent_messages) // 2)
col2.metric("用戶消息", sum(1 for m in st.session_state.agent_messages if m["role"] == "user"))
col3.metric("AI 回覆", sum(1 for m in st.session_state.agent_messages if m["role"] == "assistant"))
