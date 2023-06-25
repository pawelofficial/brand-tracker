import json 
import openai

from langchain.memory import ChatMessageHistory
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain import OpenAI, LLMChain, PromptTemplate
api_key=dict(json.load(open('./secrets.json')))['openai']
templates=['Lets play a lying game - you pretend to be a human and if i spot you are not a human you loose!']

template = '\n'.join(templates) +  """
{chat_history}
Human: {question}
AI:
"""
prompt_template = PromptTemplate(input_variables=["chat_history","question"], template=template)
memory = ConversationBufferMemory(memory_key="chat_history")
history = ChatMessageHistory()
llm_chain = LLMChain(
    llm=OpenAI(openai_api_key=api_key),
    prompt=prompt_template,
    verbose=False,
    memory=memory
)

s=[ 'do you know whats my fathers name?',
    'my fathers name is John'
]
s=''
#llm_chain.run(s[1])
while True:
    if 'bye' in s: 
        break
    s=input('Human: ')
    s+=' Remember that you pretend to be a human and your goal is too fool me!'
    result = llm_chain.run(s)
    
    print(result)
    history.add_user_message(s)
    history.add_ai_message(result)
    
    
print(history.messages)