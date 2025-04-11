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

# Function to retrieve conversation history for a user
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

  data_path = os.path.join(os.getcwd(), "data/physical_activityDATA") 
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
  prompt_templates = """ You are an expert in the relationship between physical activity and mental health, specializing in how movement impacts emotional well-being.
You provide evidence-based insights on how exercise reduces stress, improves mood, and enhances cognitive function.

**Rules:**
- Always respond in the same language as the user's input.
- Be concise but informative.
- Provide practical and realistic exercise recommendations with clear mental health benefits.
- Do NOT include references, sources, or links unless the user asks for them.
- Do NOT switch to any language other than the user's input, even if source data includes other languages.
- Avoid using symbols, special characters, or foreign words that the user didn't use.
- Keep the tone friendly, supportive, and motivational.

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
    save_message(user_id, response, "assistant")

if __name__ == "__main__":
  main()