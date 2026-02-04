import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- إعدادات الحماية ---
PASSWORD = "sharm_tourism_2024"

def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔐 نظام ERP سياحة شرم الشيخ")
        password_input = st.text_input("أدخل كلمة مرور الشركة:", type="password")
        if st.button("دخول"):
            if password_input == PASSWORD:
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("❌ كلمة المرور غير صحيحة")
        return False
    return True

# --- قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('sharm_v1.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, client TEXT, 
                  hotel TEXT, trip TEXT, count INTEGER, total REAL, paid REAL, 
                  agent TEXT, status TEXT)''')
    conn.commit()
    return conn

# --- التطبيق الرئيسي ---
if check_password():
    conn = init_db()
    st.sidebar.title("🏨 إدارة سياحة شرم")
    page = st.sidebar.radio("القائمة:", ["لوحة التحكم", "إضافة حجز", "الأوبريشن", "الحسابات"])

    if page == "لوحة التحكم":
        st.title("📊 ملخص الأداء")
        df = pd.read_sql("SELECT * FROM bookings", conn)
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("الحجوزات", len(df))
            c2.metric("المبيعات", f"${df['total'].sum():,.2f}")
            c3.metric("المحصل", f"${df['paid'].sum():,.2f}")
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.info("السيستم جاهز، ابدأ بإضافة أول حجز.")

    elif page == "إضافة حجز":
        st.title("📝 حجز جديد")
        with st.form("b_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                d = st.date_input("التاريخ")
                cl = st.text_input("العميل")
                ht = st.selectbox("الفندق", ["Rixos", "Sunrise", "Jaz", "Albatros", "أخرى"])
                tr = st.selectbox("الرحلة", ["سفاري", "غوص", "بحرية", "دولفين"])
            with col2:
                co = st.number_input("العدد", min_value=1)
                to = st.number_input("السعر")
                pa = st.number_input("المقدم")
                ag = st.text_input("المندوب")
            
            if st.form_submit_button("حفظ"):
                conn.execute("INSERT INTO bookings (date, client, hotel, trip, count, total, paid, agent, status) VALUES (?,?,?,?,?,?,?,?,?)",
                             (str(d), cl, ht, tr, co, to, pa, ag, "مؤكد"))
                conn.commit()
                st.success("تم الحفظ!")

    elif page == "الأوبريشن":
        st.title("🚌 جدول التشغيل")
        search_date = st.date_input("اختر اليوم")
        res = pd.read_sql(f"SELECT * FROM bookings WHERE date='{search_date}'", conn)
        st.dataframe(res, use_container_width=True)

    elif page == "الحسابات":
        st.title("💰 المالية")
        data = pd.read_sql("SELECT client, total, paid, (total-paid) as debt FROM bookings", conn)
        st.dataframe(data, use_container_width=True)
