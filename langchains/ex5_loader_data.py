import json 
api_key=dict(json.load(open('./secrets.json')))['openai']
import os 
from langchain.llms import OpenAI
from langchain.document_loaders import TextLoader
from langchain.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
import streamlit as st
from streamlit_chat import message
from langchain.chat_models import ChatOpenAI

API_KEY = api_key
model_id = "gpt-3.5-turbo"

# Add your openai api key for use
os.environ["OPENAI_API_KEY"] = api_key

# Define the LLM we plan to use. Here we are going to use ChatGPT 3.5 turbo
llm=ChatOpenAI(model_name = model_id, temperature=0.2)


# Specify the directory path. Replace this with your own directory
directory = './data'

# Get all files in the directory
files = os.listdir(directory)
# Create an emty list to store a list of all the files in the folder
mylist = []
# Iterate over the files
for file_name in files:
    # Get the relative path of each file
    relative_path = os.path.join(directory, file_name)
     # Append the file to a list for further processing
    mylist.append(TextLoader(relative_path))
    
    
# Save the documents from the list in to vector database 
index = VectorstoreIndexCreator().from_loaders(mylist)


st.title('✨ Query your Documents ')
prompt = st.text_input("Enter your question to query your Financial Data ")

while True:
    prompt=input('> ')
    response = index.query(llm=llm, question = prompt, chain_type = 'stuff')
    print(response)

