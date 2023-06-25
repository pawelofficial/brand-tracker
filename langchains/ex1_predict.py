#https://python.langchain.com/docs/get_started/quickstart
import json 
from langchain.llms import OpenAI


key=dict(json.load(open('./secrets.json')))['openai']

temperature=0.5
llm = OpenAI(openai_api_key=key,temperature=temperature)

s='when i was 2 years old my sister was twice as old as me, i am fifteen now, how old is my sister?'
x=llm.predict(s)
print(x)
