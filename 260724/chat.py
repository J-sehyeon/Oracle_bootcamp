from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_postgres import PGEngine, PGVectorStore
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
load_dotenv()
import os

embedding = OllamaEmbeddings(
    model="embeddinggemma:300m",
    base_url="http://host.docker.internal:11434"
)
embedding.embed_query("대한민국")



DB_USER = os.getenv("DB_USER", "langchain")
DB_PASSWORD = os.getenv("DB_PASSWORD", "langchain")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "langchain")

CONNECTION_STRING = (
    f"postgresql+psycopg://"
    f"{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = PGEngine.from_connection_string(
    url=CONNECTION_STRING,
)


vector_store= PGVectorStore.create_sync(
    engine=engine,
    table_name = "stocks",
    embedding_service=embedding
)


retriever = vector_store.as_retriever(search_type='mmr', 
                                      search_kwargs={
                                           'k' : 10,
                                          'fetch_k' : 30, 
                                      'lambda_mult' : 0.5}
                                      )







api_key = os.getenv("OLLAMA_API_KEY")


headers = {
   "Authorization": f"Bearer {api_key}"
}


llm = ChatOllama(
   base_url="http://host.docker.internal:11434", # 원격 서버 주소
   model="gemma4:31b-mlx",
#    client_kwargs={"headers": headers},
   temperature=0.2,
   reasoning=True
)

prompt = ChatPromptTemplate.from_messages(
    [('system', """당신은 유능한 애널리스트입니다. 제시된 질문과 자료를 바탕으로 기업에 대해서 평가하세요.
                    규칙 : 
                    1. 제공된 정보에서 이야기 할 것 
                    2. 제공된 정보의 출처를 알려줄 것
                    {context} 
                """),
     MessagesPlaceholder(variable_name="chat_history"),
     ('human', "{question}")
    ]
    
)

history_store = {}

def get_session_history(session_id : str) -> BaseChatMessageHistory:
    if session_id not in history_store:
        history_store[session_id] = InMemoryChatMessageHistory()

    return history_store[session_id]


config = {
    'configurable' :{
        'session_id' : 'oracle-01'
    }
}
rag_chain = (
    {
        "context": lambda x: retriever.invoke(x["question"]),
        "question": lambda x: x["question"],
        "chat_history": lambda x: x.get("chat_history", []),
    }
    | prompt
    | llm
)


conversation_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key='question',
    history_messages_key='chat_history'
)


if __name__ == "__main__":
    while True:
        q = input("질문 : ")
        if q == "Quit":
            break
        for chunk in conversation_chain.stream(
        {
            'question' : q
        },
        config=config):
            print(chunk.content, end='', flush=True)

        print("\n\n\n")
