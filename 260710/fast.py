# %%
from fastapi import FastAPI
from pydantic import BaseModel

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from pydantic import BaseModel, ValidationError, Field, field_validator
from typing import Optional
from langchain_core.output_parsers import PydanticOutputParser

# %%
llm = ChatOpenAI(
    model='gpt-5-nano',
    temperature=0.2,
    reasoning_effort='medium'
)

# %%
class _transfer(BaseModel):
    language: str = Field(description="번역 언어")
    text: str = Field(description=f"사용자가 입력한 값을 {language}로 변경한 결과를 출력하는 컬럼")

# %%
parser = PydanticOutputParser(pydantic_object=_transfer)

# %%
prompt = PromptTemplate(
    input_variables=['input', 'language'],
    partial_variables={
        'format_instructions': parser.get_format_instructions()
    },
    template=(
        '당신은 번역하는 AI입니다. 아래 사용자 입력 정보를 {language}로 번역하세요.\n'
        '{input}\n\n'
        '{format_instructions}'
    )
)

# %%
chain = prompt | llm | parser

# %%
chain.invoke({
    'input': '안녕',
    'language': '일본어'
}).text

# %%
app = FastAPI()

class PredictRequest(BaseModel):
    text: str

@app.get('/')
def root():
    return {'message': '처음 api 실행'}

@app.post('/what')
def predict(request: PredictRequest):
    text = request.text

    return {'result': 'test'}

@app.post('/transfer')
def transfer(request: _transfer):
    text = request.text
    language = request.language

    output = chain.invoke(
        {
            'input': text,
            'language': language
        }
    )

    return output



