#https://python.langchain.com/docs/get_started/quickstart
import json 
from langchain.llms import OpenAI
openai_api_key=dict(json.load(open('./secrets.json')))['openai']


from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
chat = ChatOpenAI(temperature=0,openai_api_key=openai_api_key)

if 0: # easy question 
    s="when i was 2 years old my sister was twice as old as me, i am fifteen now, how old is my sister?"
    c=chat.predict_messages([HumanMessage(content=s)])
    print(c.content)

if 0:
    s='in a game show scenario where i have to choose between three doors, one of which has a car behind it, and the other two have goats, i choose door number one, the host opens door number two to reveal a goat, should i switch to door number three?'
    c=chat.predict_messages([HumanMessage(content=s)])
    print(c.content)

if 0: # hardest question 
    s=f'if i take handful of rocks and balance them against feathers on an old fashioned scale, which will weigh more - feathers or rocks?'
    c=chat.predict_messages([HumanMessage(content=s)])
    print(c.content)