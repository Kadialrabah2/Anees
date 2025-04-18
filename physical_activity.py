from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import psycopg2

DB_CONFIG = {
    "dbname": "neondb",
    "user": "neondb_owner",
    "password": "npg_5jbqJcQnrk7K",
    "host": "ep-small-snowflake-a59tq9qy-pooler.us-east-2.aws.neon.tech",
    "port": "5432"
}

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

def setup_qa_chain(user_id, vector_db, llm):
    retriever = vector_db.as_retriever()
    memory = ConversationBufferMemory(memory_key="chat_history", input_key="question")
    for role, msg in get_conversation_history(user_id):
        memory.save_context({"question": msg}, {"output": msg})

    prompt_template = """ You are an expert in the relationship between physical activity and mental health, specializing in how movement impacts emotional well-being.
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

Chatbot Response : """

    prompt = PromptTemplate(template=prompt_template, input_variables=['chat_history', 'context', 'question'])

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt, "memory": memory}
    )

def get_physical_response(user_id, message, vector_db, llm):
    qa_chain = setup_qa_chain(user_id, vector_db, llm)
    save_message(user_id, message, "user")
    response = qa_chain.run(message)
    if not response:
        response = "I'm sorry, I couldn't find a relevant answer. Could you please provide more details?"
    save_message(user_id, response, "assistant")
    return response