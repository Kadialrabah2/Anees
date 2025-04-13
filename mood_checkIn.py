from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

def get_db_connection():
     return psycopg2.connect(
        dbname="aneesdatabase",
        user="aneesdatabase_user",
        password="C4wxOis8WgGT3zPXTgcdh8vpycpmqoCt",
        host="dpg-cuob70l6l47c73cbtgqg-a"
    )
     
def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE moods (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    mood_date DATE,
    mood_value INTEGER
     );

    """)
    conn.commit()

# نموذج البيانات
class MoodEntry(BaseModel):
    user_id: int
    mood_value: int  # من 1 إلى 6 مثلاً

# حفظ المزاج
@app.post("/save-mood/")
def save_mood(entry: MoodEntry):
    today = str(date.today())

    conn = get_db_connection()
    cur = conn.cursor()

    # تحقق من أن المستخدم موجود
    cur.execute("SELECT id FROM users WHERE id = %s", (entry.user_id,))
    user = cur.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    # حذف مزاج اليوم إن وجد
    cur.execute("DELETE FROM moods WHERE user_id = %s AND mood_date = %s", (entry.user_id, today))

    # إضافة المزاج
    cur.execute("INSERT INTO moods (user_id, mood_date, mood_value) VALUES (%s, %s, %s)",
                (entry.user_id, today, entry.mood_value))

    conn.commit()
    conn.close()

    return {"message": "تم حفظ المزاج بنجاح ✅"}

# عرض المزاج لآخر ٧ أيام
@app.get("/get-weekly-mood/{user_id}")
def get_weekly_mood(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # تحقق من أن المستخدم موجود
    cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    # جلب آخر ٧ أيام
    cur.execute("""
        SELECT mood_date, mood_value FROM moods
        WHERE user_id = %s
        ORDER BY mood_date DESC
        LIMIT 7
    """, (user_id,))
    data = cur.fetchall()
    conn.close()

    # ترتيب حسب التاريخ (من الأقدم للأحدث)
    data_sorted = sorted(data, key=lambda x: x['mood_date'])

    return {"moods": data_sorted}
