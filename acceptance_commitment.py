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
import matplotlib.pyplot as plt
from psycopg2 import sql

DB_CONFIG = {
    "dbname": "neondb",
    "user": "neondb_owner",
    "password": "npg_5jbqJcQnrk7K",
    "host": "ep-small-snowflake-a59tq9qy-pooler.us-east-2.aws.neon.tech",
    "port": "5432"
}

def save_message(user_id, message, role):
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG, sslmode='require')
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

def get_conversation_history(user_id, limit=10):
    try:
        conn = psycopg2.connect(**DB_CONFIG, sslmode='require')
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

  data_path = os.path.join(os.getcwd(), "data/acceptance_commitmentDATA")  
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
  prompt_templates = """ You are an expert in Acceptance and Commitment Therapy (ACT), helping individuals embrace their emotions and build psychological flexibility.
You use mindfulness, cognitive defusion, and value-based action strategies to help users manage difficult emotions and improve their quality of life.

**Rules:
- Always respond in the same language as the user's input.
- Be concise but informative.
- Provide actionable mindfulness techniques and exercises.
- Do NOT add references, sources, links, or citations unless the user asks for them.
- Do NOT switch to any language other than the user's input, even if the source material includes other languages.
- Avoid using unfamiliar or foreign characters (e.g., Chinese or symbols).
- Keep the tone supportive and practical.

Previous Conversation History:
{chat_history}

Context:
{context}

User Question:
{question}

Chatbot Response (in the same language as the user’s input): """
  PROMPT = PromptTemplate(template=prompt_templates, input_variables=['chat_history', 'context', 'question'])

  qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT, "memory": memory}
    )
    
  return qa_chain

def calculate_mood_level(text):
    stress_keywords = ["stress", "tension", "nervous", "anxiety"]
    anxiety_keywords = ["anxious", "worry", "fear"]
    panic_keywords = ["panic", "attack", "overwhelmed"]
    loneliness_keywords = ["lonely", "isolated", "alone"]
    burnout_keywords = ["burnout", "exhausted", "tired"]
    depression_keywords = ["depressed", "down", "sad", "hopeless"]

    stress_level = sum(word in text.lower() for word in stress_keywords) * 25
    anxiety_level = sum(word in text.lower() for word in anxiety_keywords) * 25
    panic_level = sum(word in text.lower() for word in panic_keywords) * 25
    loneliness_level = sum(word in text.lower() for word in loneliness_keywords) * 25
    burnout_level = sum(word in text.lower() for word in burnout_keywords) * 25
    depression_level = sum(word in text.lower() for word in depression_keywords) * 25

    return {
        "stress_level": min(stress_level, 100),
        "anxiety_level": min(anxiety_level, 100),
        "panic_level": min(panic_level, 100),
        "loneliness_level": min(loneliness_level, 100),
        "burnout_level": min(burnout_level, 100),
        "depression_level": min(depression_level, 100)
    }

def display_progress_bar(levels):
    categories = ["Stress", "Anxiety", "Panic", "Loneliness", "Burnout", "Depression"]
    values = [levels['stress_level'], levels['anxiety_level'], levels['panic_level'],
              levels['loneliness_level'], levels['burnout_level'], levels['depression_level']]

    plt.figure(figsize=(10, 6))
    plt.barh(categories, values, color='lightblue')
    plt.xlabel("Level")
    plt.title("Mood Tracker")
    plt.show()

def main():
  if len(sys.argv) < 2:
      print("Error: No user ID provided.")
      return

  user_id = sys.argv[1]
  user_age = int(sys.argv[1]) 
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
    response = qa_chain.run(query)
    if not response:
        response = "I'm sorry, I couldn't find a relevant answer. Could you please provide more details or rephrase your question?"
    print(f"Chatbot: {response}")

if __name__ == "__main__":
  main()