from langchain.embeddings import HuggingFaceEmbeddings
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
import matplotlib.pyplot as plt

DB_CONFIG = {
    "dbname": "neondb",
    "user": "neondb_owner",
    "password": "npg_5jbqJcQnrk7K",
    "host": "ep-small-snowflake-a59tq9qy-pooler.us-east-2.aws.neon.tech",
    "port": "5432"
}
def save_message(user_id, message, role):
    conn = None
    cursor = None
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
      try:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
      except:
        pass

def get_conversation_history(user_id, limit=50):
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
  prompt_templates = """ You are a mental health diagnostic support chatbot.

Your role is to help users by:
- Gathering information about their mental health symptoms.
- Identifying possible mental health conditions based on the information they provide.
- Encouraging users to consult with licensed mental health professionals for an official diagnosis.
- Avoiding giving direct medical advice, treatment plans, or therapeutic recommendations.
- Avoiding mindfulness, breathing exercises, or self-care suggestions unless the user explicitly asks for them.

Guidelines:
- Be clear, informative, and respectful.
- Only respond based on the information provided by the user.
- Always respond in the same language as the user.
- If unsure, politely ask the user to clarify their symptoms.

{context}

User Question:
{question}

Chatbot Response:** """
  PROMPT = PromptTemplate(template=prompt_templates, input_variables=['chat_history', 'context', 'question'])

  qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT, "memory": memory}
    )
    
  return qa_chain

def calculate_mood_level(text):
    stress_keywords = ["stress", "tension", "nervous", "anxiety","الإجهاد", "التوتر", "العصبية", "القلق"]
    anxiety_keywords = ["anxious", "worry", "fear","قلق", "خوف"]
    panic_keywords = ["panic", "attack", "overwhelmed","ذعر","هجوم", "مُثقل"]
    loneliness_keywords = ["lonely", "isolated", "alone","وحيد", "منعزل", "وحده"]
    burnout_keywords = ["burnout", "exhausted", "tired","الإرهاق", "التعب"]
    depression_keywords = ["depressed", "down", "sad", "hopeless","مكتئب", "حزين", "يائس"]

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

def main():
  def get_diagnosis_response(user_id, message):
    db_path = "./chroma_db"

    if not os.path.exists(db_path):
        vector_db = create_vector_db()
    else:
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings)

    llm = initialize_llm()
    qa_chain = setup_qa_chain(vector_db, llm, user_id)

    save_message(user_id, message, "user")
    response = qa_chain.run(message)

    if not response:
        response = "I'm sorry, I couldn't find a relevant answer. Could you please provide more details?"

    save_message(user_id, response, "assistant")

    mood_levels = calculate_mood_level(message)  # Mood analysis on the last message
    return {
        "reply": response,
        "mood": mood_levels
    }

if __name__ == "__main__":
  main()