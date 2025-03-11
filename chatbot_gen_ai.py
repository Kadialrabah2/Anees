from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
import os
import sys
import psycopg2
import chromadb
from chromadb.config import Settings

def initialize_llm():
  llm = ChatGroq(
    temperature = 0,
    groq_api_key = "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",
    model_name = "llama-3.3-70b-versatile"
)
  return llm

def create_vector_db():

  data_path = os.path.join(os.getcwd(), "data")  # Get the correct path
  loader = DirectoryLoader(data_path, glob="*.pdf", loader_cls=PyPDFLoader)

  documents = loader.load()
  text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)
  texts = text_splitter.split_documents(documents)
  embeddings = HuggingFaceEmbeddings(model_name = 'sentence-transformers/all-MiniLM-L6-v2')
  vector_db = Chroma.from_documents(texts, embeddings, persist_directory = './chroma_db')
  vector_db.persist()

  print("ChromaDB created and data saved")

  return vector_db

def setup_qa_chain(vector_db, llm, user_id):
  retriever = vector_db.as_retriever()
  memory = ConversationBufferMemory(memory_key="chat_history", input_key="question")

  prompt_templates = """ You are a supportive and empathetic mental health chatbot. 
Your goal is to provide thoughtful, kind, and well-informed responses in the same language as the user's question.

**Previous Conversation History:** 
    {chat_history}

**Context (What you know):** 
{context}

**User Question:** 
{question}

**Chatbot Response (in the same language as the user’s input):** """
  PROMPT = PromptTemplate(template=prompt_templates, input_variables=['chat_history', 'context', 'question'])

  qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT, "memory": memory}
    )
    
  return qa_chain

def main():
  if len(sys.argv) < 2:
      print("Error: No user ID provided.")
      return

  user_id = sys.argv[1]
   
  print(f"Initializing Chatbot for user: {user_id}")
  llm = initialize_llm()

  db_path = "/content/chroma_db"

  if not os.path.exists(db_path):
    vector_db  = create_vector_db()
  else:
    embeddings = HuggingFaceEmbeddings(model_name = 'sentence-transformers/all-MiniLM-L6-v2')
    vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings)
  qa_chain = setup_qa_chain(vector_db, llm, user_id)

  while True:
    query = input(f"\nUser {user_id}: ") 
    if query.lower() == "exit":
          print("Chatbot: Take care of yourself, goodbye!")
          break

    response = qa_chain.run(query)
    print(f"Chatbot: {response}")

if __name__ == "__main__":
  main()