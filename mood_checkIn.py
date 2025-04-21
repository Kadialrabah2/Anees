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

# نموذج البيانات المعدل
class MoodEntry(BaseModel):
    username: str  # تغيير من user_id إلى username
    mood_value: int  # من 1 إلى 5

# حفظ المزاج اليومي
@app.post("/save-daily-mood/")
def save_daily_mood(entry: MoodEntry):
    today = date.today()

    conn = get_db_connection()
    cur = conn.cursor()

    # التحقق من وجود المستخدم
    cur.execute("SELECT username FROM users WHERE username = %s", (entry.username,))
    user = cur.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    # حذف أي بيانات مزاج موجودة لنفس اليوم
    cur.execute("""
        DELETE FROM daily_mood 
        WHERE username = %s AND mood_date = %s
    """, (entry.username, today))

    # إدخال بيانات المزاج الجديدة
    cur.execute("""
        INSERT INTO daily_mood (username, mood_date, mood_value)
        VALUES (%s, %s, %s)
    """, (entry.username, today, entry.mood_value))

    conn.commit()
    conn.close()

    return {"message": "تم حفظ المزاج اليومي بنجاح ✅", "date": str(today)}

# استرجاع بيانات المزاج الأسبوعية
@app.get("/get-weekly-mood/{username}")
def get_weekly_mood(username: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # التحقق من وجود المستخدم
    cur.execute("SELECT username FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    # جلب بيانات آخر 7 أيام
    cur.execute("""
        SELECT mood_date, mood_value 
        FROM daily_mood
        WHERE username = %s
        ORDER BY mood_date DESC
        LIMIT 7
    """, (username,))
    
    moods = cur.fetchall()
    conn.close()

   

    weekly_data = []
    for mood in moods:
        weekly_data.append({
            "date": mood['mood_date'],
            "mood_value": mood['mood_value']
        })

    # ترتيب حسب التاريخ (من الأقدم للأحدث)
    weekly_data_sorted = sorted(weekly_data, key=lambda x: x['date'])

    return {
        "username": username,
        "weekly_moods": weekly_data_sorted
    }