from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from psycopg2 import sql
from langchain.memory import ConversationBufferMemory
import os
import sys
import psycopg2
import chromadb
from psycopg2 import sql
from datasets import load_dataset
import re

english_dataset = load_dataset("marmikpandya/mental-health",split="train")
arabic_dataset = load_dataset("Ahmed-Selem/Shifaa_Arabic_Mental_Health_Consultations", split="train")
qa_pairs = {}
for row in english_dataset:
    qa_pairs[row["input"]] = row["output"]

for row in arabic_dataset:
    qa_pairs[row["question"]] = row["answer"]

DB_CONFIG = {
    "dbname": "postgre_chatbot",
    "user": "postgre_chatbot_user",
    "password": "XhauYxUl4Y5eDSjVAthcSeU3Fe73LXLQ",
    "host": "dpg-cv87b85umphs738beo80-a.oregon-postgres.render.com",
    "port": "5432"
}

def save_message(user_id, message, role):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = sql.SQL("""
            INSERT INTO conversations (user_id, message, role)
            VALUES (%s, %s, %s)
        """)
        cursor.execute(query, (user_id, message, role))
        conn.commit()
    except Exception as e:
        print(f"Error saving message: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()


def get_conversation_history(user_id, limit=50):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = sql.SQL("""
            SELECT role, message FROM conversations
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """)
        cursor.execute(query, (user_id, limit))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error retrieving conversation history: {e}")
        return []
    finally:
        if conn:
            cursor.close()
            conn.close()

def initialize_llm():
  llm = ChatGroq(
    temperature = 0,
    groq_api_key = "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",
    model_name = "llama-3.3-70b-versatile"
)
  return llm

def create_vector_db():

  data_path = os.path.join(os.getcwd(), "data/diagnosisDATA")  
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
  chat_history = get_conversation_history(user_id)
  for role, message in chat_history:
      memory.save_context({"question": message}, {"output": message})
  prompt_templates = """ You are a supportive mental health chatbot.
Please provide empathetic and helpful responses to the user’s queries.

**Rules:**
- Always respond in the same language as the user's input.
- Be concise but informative.
- If relevant, provide self-care suggestions.
- Do NOT give medical advice or diagnose.

**Context:** 
{context}

**User Question:** 
{question}

**Chatbot Response:** """
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
    save_message(user_id, query, "user")

    for question, answer in qa_pairs.items():
        if query.lower() in question.lower():
            response = answer  # Use dataset answer
            break
    else:
      response = qa_chain.run(query) # call AI

    if not response:
        response = "I'm sorry, I couldn't find a relevant answer. Could you please provide more details or rephrase your question?"
    print(f"Chatbot: {response}")
    save_message(user_id, response, "assistant")

if __name__ == "__main__":
  main()