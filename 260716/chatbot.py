import streamlit as st
import uuid
from langchain_community.chat_message_histories import  SQLChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import (
    ChatPromptTemplate, MessagesPlaceholder,
)
from langchain_core.runnables.history import  RunnableWithMessageHistory
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
load_dotenv()
import os


api_key = os.getenv("OLLAMA_API_KEY")
headers = {
   "Authorization": f"Bearer {api_key}"
}




st.set_page_config(
    page_title="나만의 챗봇 친구",
    layout="centered"
)




st.title("나의 친구(챗봇)")

if "session_id" not in st.session_state:
    st.session_state.session_id = "sesac_01"


with st.sidebar:
    st.header('설정')




    session_id = st.text_input(
        "대화 세션 ID",
        value=st.session_state.session_id,
        help=(
            "같은 세션 ID를 사용하면 앱을 다시 실행해도 "
            "이전 대화를 불러옵니다."
        ),
    )




    st.session_state.session_id = session_id.strip()
