from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
<<<<<<< HEAD
=======
from psycopg2 import sql
>>>>>>> f2610ab7ecccb062ff3248fc78ff87b588ade233
from langchain.memory import ConversationBufferMemory
import os
import sys
import psycopg2
import chromadb
<<<<<<< HEAD
from chromadb.config import Settings
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

# Initialize ChromaDB client
client = chromadb.Client(Settings(persist_directory="./chroma_db"))

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="",
            user="",
            password="",
            host="",
            port=""
            
        )
        print("Database connection successful!")
        return conn
    except psycopg2.OperationalError as e:
        print(f"OperationalError: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None

def save_chat_to_db(user_id, message, role):
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to the database.")
        return

    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO chat_history (user_id, message, role) VALUES (%s, %s, %s)", (user_id, message, role))
        conn.commit()
        print(f"Saved message: {message}, Role: {role}")
    except Exception as e:
        print(f"Error saving chat history: {e}")
    finally:
        cur.close()
        conn.close()

def get_chat_history(user_id):
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to the database.")
        return []

    try:
        cur = conn.cursor()
        cur.execute("SELECT message, role FROM chat_history WHERE user_id = %s ORDER BY timestamp", (user_id,))
        history = cur.fetchall()
        print(f"Retrieved chat history: {history}")
        return history
    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        return []
    finally:
        cur.close()
        conn.close()
=======
from psycopg2 import sql

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

# Function to retrieve conversation history for a user
def get_conversation_history(user_id, limit=10):
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
>>>>>>> f2610ab7ecccb062ff3248fc78ff87b588ade233

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
<<<<<<< HEAD
  #Load chat history from PostgreSQL
  chat_history = get_chat_history(user_id)
  for message, role in chat_history:
      if role == "user":
          memory.chat_memory.add_user_message(message)
      elif role == "bot":
          memory.chat_memory.add_ai_message(message)


=======
  chat_history = get_conversation_history(user_id)
  for role, message in chat_history:
      memory.save_context({"question": message}, {"output": message})
>>>>>>> f2610ab7ecccb062ff3248fc78ff87b588ade233
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
<<<<<<< HEAD
    query = input("\nHuman: ")
    if query.lower()  == "exit":
      print("Chatbot: Take Care of yourself, Goodbye!")
      break
    #get bot response
    response = qa_chain.run(query)
    #save conversation to database
    save_chat_to_db(user_id, query, "user")
    save_chat_to_db(user_id, response, "bot")
    print(f"Chatbot: {response}")
=======
    query = input(f"\nUser {user_id}: ") 
    if query.lower() == "exit":
          print("Chatbot: Take care of yourself, goodbye!")
          break
    save_message(user_id, query, "user")
    response = qa_chain.run(query)
    print(f"Chatbot: {response}")
    save_message(user_id, response, "assistant")
>>>>>>> f2610ab7ecccb062ff3248fc78ff87b588ade233

if __name__ == "__main__":
  main()