from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from psycopg2 import sql
from flask import Flask, request, jsonify
import psycopg2
import os

DB_CONFIG = {
    "dbname": "neondb",
    "user": "neondb_owner",
    "password": "npg_5jbqJcQnrk7K",
    "host": "ep-small-snowflake-a59tq9qy-pooler.us-east-2.aws.neon.tech",
    "port": "5432"
}

embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

cognitive_db_path = "./chroma_db"
if os.path.exists(cognitive_db_path):
    vector_db = Chroma(persist_directory=cognitive_db_path, embedding_function=embedding_model)
else:
    data_path = os.path.join(os.getcwd(), "data/cognitive_therapyDATA")
    loader = DirectoryLoader(data_path, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = splitter.split_documents(documents)
    vector_db = Chroma.from_documents(texts, embedding_model, persist_directory=cognitive_db_path)
    vector_db.persist()

llm = ChatGroq(
    temperature=0,
    groq_api_key="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",
    model_name="llama-3.3-70b-versatile"
)

def save_message(user_id, message, role):
    conn, cur = None, None
    try:
        conn = psycopg2.connect(**DB_CONFIG, sslmode='require')
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO conversations (user_id, message, role) VALUES (%s, %s, %s)",
            (user_id, message, role)
        )
        conn.commit()
    except Exception as e:
        print("DB Save Error:", e)
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_conversation_history(user_id, limit=10):
    conn, cur = None, None
    try:
        conn = psycopg2.connect(**DB_CONFIG, sslmode='require')
        cur = conn.cursor()
        cur.execute("""
            SELECT role, message FROM conversations
            WHERE user_id = %s ORDER BY timestamp DESC LIMIT %s
        """, (user_id, limit))
        return cur.fetchall()
    except Exception as e:
        print("DB Read Error:", e)
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()

def setup_qa_chain(user_id):
    retriever = vector_db.as_retriever()
    memory = ConversationBufferMemory(memory_key="chat_history", input_key="question")
    for role, msg in get_conversation_history(user_id):
        memory.save_context({"question": msg}, {"output": msg})

    prompt_template = """ You are an expert in Cognitive Therapy, specializing in helping individuals identify and challenge negative thought patterns to improve their mental well-being.
You use evidence-based techniques such as cognitive restructuring, thought reframing, and behavioral experiments to guide users toward healthier thinking.

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

Chatbot Response:"""

    prompt = PromptTemplate(template=prompt_template, input_variables=['chat_history', 'context', 'question'])

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt, "memory": memory}
    )

# ========= Main Function ==========
def get_cognitive_response(user_id, message):
    qa_chain = setup_qa_chain(user_id)

    save_message(user_id, message, "user")
    response = qa_chain.run(message)

    if not response:
        response = "I'm sorry, I couldn't find a relevant answer. Could you please provide more details?"

    save_message(user_id, response, "assistant")
    return response