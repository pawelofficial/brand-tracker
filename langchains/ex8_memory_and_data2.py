import faiss
from datetime import datetime
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.llms import OpenAI
from langchain.memory import VectorStoreRetrieverMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.docstore import InMemoryDocstore
from langchain.vectorstores import FAISS
import os 
from langchain.indexes import VectorstoreIndexCreator
import json
os.environ["OPENAI_API_KEY"] = dict(json.load(open('./secrets.json')))['openai']
#https://pub.towardsai.net/building-a-q-a-bot-over-private-documents-with-openai-and-langchain-be975559c1e8
# Specify the directory path. Replace this with your own directory
directory = './data'

# Get all files in the directory
files = os.listdir(directory)
# Create an emty list to store a list of all the files in the folder
mylist=[]
# Iterate over the files
for file_name in files:
    # Get the relative path of each file

    fp=os.path.join(os.path.dirname(__file__),'data',file_name)
     # Append the file to a list for further processing
    mylist.append(TextLoader(fp))
    
    
# Save the documents from the list in to vector database 
#vectorstore = VectorstoreIndexCreator().from_loaders(mylist)

from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
fp=os.path.join(os.path.dirname(__file__),'data','schema_ddls.txt')

loader=TextLoader()
loader.encoding="utf-8"
loader.file_path=mylist[0]
loader.load()

documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=10000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
embeddings = OpenAIEmbeddings()


vectorstore = Chroma.from_documents( texts, embeddings)



retriever = vectorstore.as_retriever()
memory = VectorStoreRetrieverMemory(retriever=retriever)
memory.save_context({"input": "My favorite food is pizza"}, {"output": "thats good to know"})
memory.save_context({"input": "My favorite sport is soccer"}, {"output": "..."})
memory.save_context({"input": "I don't the Celtics"}, {"output": "ok"}) #

llm = OpenAI(temperature=0) # Can be any valid LLM
_DEFAULT_TEMPLATE = """The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.

Relevant pieces of previous conversation:
{history}

(You do not need to use these pieces of information if not relevant)

Current conversation:
Human: {input}
AI:"""
PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=_DEFAULT_TEMPLATE
)
conversation_with_summary = ConversationChain(
    llm=llm, 
    prompt=PROMPT,
    # We set a very low max_token_limit for the purposes of testing.
    memory=memory,
    verbose=False
)

while True:

#    s=input('input:')
    s='list tables in the dump, does it contain all the tables? '
    s='how many example queries do you have available?'
    r=conversation_with_summary.run(input=s)
    print(r)
    exit(1)