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

def get_conversation_history(user_id, limit=50):
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

    prompt_template = """ You are a mental health diagnostic support chatbot.
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

Chatbot Response:"""

    prompt = PromptTemplate(template=prompt_template, input_variables=['chat_history', 'context', 'question'])

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt, "memory": memory}
    )

def calculate_mood_level(text):
    keywords = {
        "stress": ["stress", "tension", "nervous", "anxiety", "الإجهاد", "التوتر", "العصبية", "القلق"],
        "anxiety": ["anxious", "worry", "fear", "قلق", "خوف"],
        "panic": ["panic", "attack", "overwhelmed", "ذعر", "هجوم", "مُثقل"],
        "loneliness": ["lonely", "isolated", "alone", "وحيد", "منعزل", "وحده"],
        "burnout": ["burnout", "exhausted", "tired", "الإرهاق", "التعب"],
        "depression": ["depressed", "down", "sad", "hopeless", "مكتئب", "حزين", "يائس"]
    }

    mood_scores = {}
    for mood, words in keywords.items():
        score = sum(word in text.lower() for word in words) * 25
        mood_scores[f"{mood}_level"] = min(score, 100)

    return mood_scores

def get_diagnosis_response(user_id, message, vector_db, llm):
    print(">> get_diagnosis_response START")
    print(">> user_id:", user_id)
    print(">> message:", message)
    print(">> vector_db type:", type(vector_db))
    print(">> llm type:", type(llm))

    try:
        qa_chain = setup_qa_chain(user_id, vector_db, llm)

        print(">> QA Chain setup complete. Saving user message...")
        save_message(user_id, message, "user")

        print(">> Running QA Chain...")
        response = qa_chain.run(message)
        if not response:
            response = "I'm sorry, I couldn't find a relevant answer. Could you please provide more details?"

        print(">> Saving assistant response...")
        save_message(user_id, response, "assistant")

        print(">> Calculating mood level...")
        mood = calculate_mood_level(message)

        print(">> get_diagnosis_response END")
        return {"reply": response, "mood": mood}

    except Exception as e:
        print(">> ERROR in get_diagnosis_response:", e)
        return {"reply": "Something went wrong while processing your request.", "mood": {}}