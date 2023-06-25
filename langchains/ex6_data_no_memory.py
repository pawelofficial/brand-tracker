from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ChatMessageHistory
from langchain.llms import OpenAI
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Chroma
import os 
from langchain.chains.conversation.memory import ConversationBufferMemory
import json 
os.environ["OPENAI_API_KEY"] = dict(json.load(open('./secrets.json')))['openai']




fp=os.path.join(os.path.dirname(__file__),'state_of_the_union.txt')
loader = TextLoader(file_path=fp,encoding="utf-8")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(texts, embeddings)


memory = ConversationBufferMemory(memory_key="chat_history")
history = ChatMessageHistory()
chain = ConversationalRetrievalChain.from_llm(
llm = ChatOpenAI(temperature=0.0,model_name='gpt-3.5-turbo'),
retriever=vectorstore.as_retriever()
,memory=memory
)
#qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=docsearch.as_retriever())

while True:
    print(history)
    history=list(history)
    query='hi there'
    
    langchain_history = [(msg[1], history[i+1][1] if i+1 < len(history) else "") for i, msg in enumerate(history) if i % 2 == 0]
    result = chain.run({'question':query,"chat_history": langchain_history})
    print(result)
    input('wait')