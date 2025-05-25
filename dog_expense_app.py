import streamlit as st
from supabase import create_client, Client
import datetime
import uuid
import calendar

# ✅ Supabase 設定
SUPABASE_URL = "https://tswddsttzsjavmtrcjmv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRzd2Rkc3R0enNqYXZtdHJjam12Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc4NDI5NDAsImV4cCI6MjA2MzQxODk0MH0.2JHt-dCeHkW0_St5Ya671VqCDvxpWWgb9PYnKl5FOs8"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="🐶 狗狗健康與花費記錄")
st.title("🐾 狗狗健康與花費記錄")

# 🧑 使用者登入
user_email = st.text_input("請輸入您的 Email 或帳號名稱（請自行保密）")
user_id = None

def get_or_create_user(email):
    response = supabase.table("users").select("id").eq("email", email).execute()
    data = response.data
    if data:
        return data[0]["id"]
    else:
        new_id = str(uuid.uuid4())
        supabase.table("users").insert({"id": new_id, "email": email}).execute()
        return new_id

if user_email:
    user_id = get_or_create_user(user_email)
    st.success(f"歡迎，{user_email}")

    # 🐶 基本資料
    st.subheader("🐶 輸入狗狗基本資料")
    name = st.text_input("狗狗名字")
    age = st.number_input("狗狗年齡", min_value=0, step=1)
    breed = st.text_input("狗狗品種")
    if st.button("儲存狗狗資料"):
        if name and breed:
            profile_data = {
                "name": name,
                "age": age,
                "breed": breed,
                "user_id": user_id,
                "user_email": user_email
            }
            supabase.table("dog_profiles").upsert(profile_data, on_conflict=["user_id", "name"]).execute()
            st.success("✅ 已儲存狗狗資料")
        else:
            st.warning("請輸入完整資料")

    # 🩺 疾病記錄
    st.subheader("🩺 新增疾病紀錄")
    disease = st.text_input("疾病名稱")
    diagnosed_date = st.date_input("診斷日期")
    notes = st.text_area("醫師備註")
    if st.button("儲存疾病紀錄"):
        if disease:
            disease_data = {
                "disease": disease,
                "diagnosed_date": str(diagnosed_date),
                "notes": notes,
                "user_id": user_id,
                "user_email": user_email
            }
            supabase.table("dog_diseases").insert(disease_data).execute()
            st.success("✅ 已儲存疾病紀錄")
        else:
            st.warning("請輸入疾病名稱")

    # 📋 預覽基本資料與疾病記錄
    st.subheader("📋 狗狗資料預覽")
    profile_resp = supabase.table("dog_profiles").select("*").eq("user_id", user_id).execute()
    disease_resp = supabase.table("dog_diseases").select("*").eq("user_id", user_id).execute()

    if profile_resp.data:
        for p in profile_resp.data:
            st.markdown(f"**🐶 名字：** {p['name']}  \n**🎂 年齡：** {p['age']}  \n**🐕 品種：** {p['breed']}")
    if disease_resp.data:
        st.markdown("**🩺 疾病紀錄：**")
        for d in disease_resp.data:
            st.markdown(f"- {d['diagnosed_date']}: {d['disease']}（備註：{d['notes']}）")
    else:
        st.info("尚無疾病紀錄")

    # 💸 新增花費
    st.subheader("💸 新增花費紀錄")
    exp_date = st.date_input("花費日期", datetime.date.today())
    exp_item = st.text_input("項目")
    exp_amount = st.number_input("金額", min_value=0.0, format="%.2f")
    if st.button("儲存花費紀錄"):
        if exp_item:
            expense_data = {
                "date": str(exp_date),
                "item": exp_item,
                "amount": exp_amount,
                "user_id": user_id,
                "user_email": user_email
            }
            supabase.table("dog_expenses").insert(expense_data).execute()
            st.success("✅ 已儲存花費紀錄")
        else:
            st.warning("請輸入項目名稱")

    # 📊 選擇月份花費總覽（修改重點）
    st.subheader("📊 選擇月份查看花費總覽")
    selected_month = st.date_input("選擇月份", datetime.date.today().replace(day=1))

    year = selected_month.year
    month = selected_month.month
    first_day = datetime.date(year, month, 1)
    last_day = datetime.date(year, month, calendar.monthrange(year, month)[1])

    expenses_resp = supabase.table("dog_expenses").select("*").eq("user_id", user_id).gte("date", str(first_day)).lte("date", str(last_day)).execute()
    monthly_expenses = expenses_resp.data

    if monthly_expenses:
        total = sum(item["amount"] for item in monthly_expenses)
        st.metric(f"💰 {year}年{month}月總花費", f"${total:.2f}")

        for expense in monthly_expenses:
            col1, col2, col3 = st.columns([2, 4, 2])
            with col1:
                st.write(expense["date"])
            with col2:
                st.write(expense["item"])
            with col3:
                st.write(f"${expense['amount']:.2f}")
    else:
        st.info(f"📭 {year}年{month}月尚無花費紀錄")

else:
    st.warning("請輸入並登入 Email 或帳號名稱以使用應用程式功能")
