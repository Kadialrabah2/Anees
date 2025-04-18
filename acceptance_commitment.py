from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from psycopg2 import sql
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

db_path = "./chroma_db"
if os.path.exists(db_path):
    vector_db = Chroma(persist_directory=db_path, embedding_function=embedding_model)
else:
    data_path = os.path.join(os.getcwd(), "data/acceptance_commitmentDATA")
    loader = DirectoryLoader(data_path, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = splitter.split_documents(documents)
    vector_db = Chroma.from_documents(
        texts, 
        embedding_model, 
        persist_directory=db_path,
        collection_metadata={"hnsw:space": "cosine"}
    )
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

    prompt_template = """ You are an expert in Acceptance and Commitment Therapy (ACT), helping individuals embrace their emotions and build psychological flexibility.
You use mindfulness, cognitive defusion, and value-based action strategies to help users manage difficult emotions and improve their quality of life.

**Rules:**
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

Chatbot Response:"""

    prompt = PromptTemplate(template=prompt_template, input_variables=['chat_history', 'context', 'question'])

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt, "memory": memory}
    )

def get_act_response(user_id, message):
    qa_chain = setup_qa_chain(user_id)

    save_message(user_id, message, "user")
    response = qa_chain.run(message)
    if not response:
        response = "I'm sorry, I couldn't find a relevant answer. Could you please provide more details?"

    save_message(user_id, response, "assistant")
    return response
