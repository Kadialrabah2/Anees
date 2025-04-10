from flask import Flask, request, jsonify
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from psycopg2 import sql
import os
import psycopg2
import chromadb
from flask import Blueprint

acceptance_bp = Blueprint('acceptance', __name__)

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
    return ChatGroq(
        temperature=0,
        groq_api_key="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",
        model_name="llama-3.3-70b-versatile"
    )

def create_or_load_vector_db():
    db_path = os.path.join(os.getcwd(), "chroma_db")
    if not os.path.exists(db_path):
        data_path = os.path.join(os.getcwd(), "data/cognitive_therapyDATA")
        loader = DirectoryLoader(data_path, glob="*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        texts = splitter.split_documents(documents)
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        vector_db = Chroma.from_documents(texts, embeddings, persist_directory=db_path)
        vector_db.persist()
    else:
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        vector_db = Chroma(persist_directory=db_path, embedding_function=embeddings)
    return vector_db

def setup_qa_chain(vector_db, llm, user_id):
    retriever = vector_db.as_retriever()
    memory = ConversationBufferMemory(memory_key="chat_history", input_key="question")
    chat_history = get_conversation_history(user_id)
    for role, message in chat_history:
        memory.save_context({"question": message}, {"output": message})

    prompt_template = """ You are an expert in Cognitive Therapy...

**Rules:**
- Always respond in the same language as the user's input.
- Be concise but informative.
- Provide practical strategies and exercises where relevant.
- Do NOT include references, citations, or links unless the user asks.
- Do NOT use any other languages, symbols, or characters unless the user does.
- Maintain a calm, supportive, and empowering tone.
- Encourage realistic, self-compassionate thinking when applicable.

Previous Conversation History:
{chat_history}

Context:
{context}

User Question:
{question}

Chatbot Response (in the same language as the user’s input): """
    PROMPT = PromptTemplate(template=prompt_template, input_variables=['chat_history', 'context', 'question'])

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT, "memory": memory}
    )
    return qa_chain

@acceptance_bp.route("/acceptance_commitment", methods=["POST"])
def chat():
    data = request.get_json()
    user_id = str(data.get("user_id"))
    message = data.get("message")

    if not user_id or not message:
        return jsonify({"error": "Missing user_id or message"}), 400

    #llm = initialize_llm()
    #vector_db = create_or_load_vector_db()
    qa_chain = setup_qa_chain(vector_db, llm, user_id)

    response = qa_chain.run(message)
    if not response:
        response = "I'm sorry, I couldn't find a relevant answer. Could you please provide more details or rephrase your question?"

    save_message(user_id, message, "user")
    save_message(user_id, response, "assistant")

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)