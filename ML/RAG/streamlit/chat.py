# chat.py
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from llm import get_ai_response

import streamlit as st
from dotenv import load_dotenv


st.set_page_config(page_title="소득세 챗봇", page_icon="👾")
st.title("👾 소득세 챗봇")
st.caption("소득세에 관련된 모든 것을 답해드립니다!")

load_dotenv()

if 'message_list' not in st.session_state:
    st.session_state.message_list = []

# 기존에 전송된 메시지들을 불러오기
for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message['content'])


# 채팅 input은 사용자의 질문
if user_question := st.chat_input(placeholder="소득세에 관련된 궁금한 내용들을 말씀해주세요!"):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})

    with st.spinner("답변을 생성하는 중입니다."): # loading spinner
        ai_response = get_ai_response(user_question)

        with st.chat_message("ai"):
            ai_message = st.write_stream(ai_response)
            st.session_state.message_list.append({"role": "ai", "content": ai_message})
