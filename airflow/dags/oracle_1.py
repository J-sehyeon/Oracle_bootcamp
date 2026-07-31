import pendulum
from airflow.sdk import DAG, task
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from datetime import date


with DAG(
	dag_id="oracle_first",
	schedule="00 12 * * *",
    start_date=pendulum.datetime(2026, 6, 30, tz="Asia/Seoul"),
    catchup=False,
    tags=['oracle']
) as dag:

	@task.external_python(
			python="/Users/hyeon/virtualenv/.venv/bin/python"
	)
	def get_news():
		import requests
		from bs4 import BeautifulSoup
		from bs4 import SoupStrainer
		import json
		import langchain_core
		from langchain_community.document_loaders import WebBaseLoader


		print(f"langchain_core ->{langchain_core.__version__}")


		url = "https://www.medicaltimes.com/Main/"
		target = [ url + x.find('a')['href'][2:] \
		for x in BeautifulSoup(requests.get(url).text).find("div", class_="midNews_main").find_all("span", class_="head")][:5]
		print(f"list -> {len(target)}")
		print(f"WebBaseLoader -> {WebBaseLoader}")
		data = WebBaseLoader(target,
					bs_kwargs={'parse_only' : SoupStrainer("div", class_='view_cont ck-content clearfix')}).load()
		# return data
		data_list = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in data]
		serialized_data = json.dumps(data_list, ensure_ascii=False)
		
		return serialized_data



	@task.external_python(
			python="/Users/hyeon/virtualenv/.venv/bin/python"
	)
	def set_report(data):
		from langchain_core.prompts import PromptTemplate
		from langchain_openai import ChatOpenAI
		from langchain_ollama import ChatOllama
		from langchain_core.output_parsers import StrOutputParser
		from dotenv import load_dotenv
		from langchain.tools import tool
		import os
		import pandas as pd
		import io
		import requests
		from langgraph.prebuilt import create_react_agent
		from langchain_core.documents import Document
		import json


		load_dotenv(dotenv_path="/Users/hyeon/3_AI/.env")
		
		# 2. 역직렬화 (JSON 문자열 -> dict -> Document 객체)
		data_list = json.loads(data)
		docs = [Document(page_content=item["page_content"], metadata=item["metadata"]) for item in data_list]


		print(f"정보 수집 완료 -> {len(docs)}건")
		api_key = os.getenv("OLLAMA_API_KEY")
		headers = {
				"Authorization": f"Bearer {api_key}"
				}
		llm = ChatOllama(
				base_url="https://ollama.com", # 원격 서버 주소
				model="gemma4:31b-cloud",
				client_kwargs={"headers": headers},
				temperature=0.2,
				reasoning=True
			)
		# print(llm.invoke('hi'))
		persona = """
				당신은 의료 관련 업무 담당자입니다.  제공된 뉴스 정보를 핵심 정보 누락없이 보기 좋게
				요약하고 정리해주세요.
				\n\n
				{context}
				"""
		summary_prompt = PromptTemplate(
				template=persona,
				input_variables=["context"] )


		summary_chain = summary_prompt | llm | StrOutputParser()
		report = summary_chain.invoke(docs)


		print(report)
		return str(report)
	
	@task
	def send_email(report):
		id_ = "zip235789@gmail.com"  # 보내는 사람 Gmail 주소
		pass_ = 'eypp cfir fjlw fqyq'  # Gmail 앱 비밀번호 (실제 사용 시 본인 것으로 변경)
		
		# 2. SMTP 서버 연결 (SSL 사용, 포트 465)
		smtp = smtplib.SMTP_SSL("smtp.gmail.com", 465)
		smtp.login(id_, pass_)


		msg = MIMEMultipart('alternative')
		msg['To'] = 'zip235789@gmail.com'
		msg['Date'] = str(date.today())
		msg['Subject'] = f"{date.today()} 뉴스 요약 "
		msg.attach(MIMEText(report, 'html'))


		smtp.sendmail('seowoong362@gmail.com', 'zip235789@gmail.com', msg.as_string())


		return 1



		
	news = get_news()
	report = set_report(news)
	result = send_email(report)


	news >> report >> result
