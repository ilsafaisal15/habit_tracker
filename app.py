import streamlit as st
import pandas as pd
from datetime import date
import os
from textblob import TextBlob

# ---------- CONFIG ----------
st.set_page_config(page_title="Advanced Habit Tracker", layout="centered")
st.title("📅 Advanced Daily Habit Tracker")

# ---------- FILES ----------
HABIT_FILE = "user_habits.csv"
DATA_FILE = "data.csv"
TODAY = str(date.today())

# ---------- INIT STORAGE FILES ----------
def init_file(path, cols):
    if not os.path.exists(path):
        pd.DataFrame(columns=cols).to_csv(path, index=False)

init_file(HABIT_FILE, ["username", "habit"])
init_file(DATA_FILE, ["username", "date", "mood", "mood_note", "habit", "completed"])

# ---------- USER LOGIN ----------
username = st.text_input("Enter your name to begin:", max_chars=20)
if not username:
    st.warning("Please enter your name to continue.")
    st.stop()

# ---------- LOAD USER HABITS ----------
user_habits_df = pd.read_csv(HABIT_FILE)
user_habits = user_habits_df[user_habits_df["username"] == username]["habit"].tolist()

# ---------- FIRST-TIME HABIT SETUP ----------
if not user_habits:
    st.markdown("### 🛠️ Setup Your Habits")
    st.info("Please enter at least 3 habits you want to track:")

    habit_inputs = []
    for i in range(1, 6):
        habit = st.text_input(f"Habit {i} (optional):")
        if habit:
            habit_inputs.append(habit)

    if st.button("✅ Save My Habits"):
        if len(habit_inputs) < 3:
            st.warning("Please enter at least 3 habits.")
        else:
            new_df = pd.DataFrame([{"username": username, "habit": h} for h in habit_inputs])
            new_df.to_csv(HABIT_FILE, mode="a", index=False, header=False)
            st.success("✅ Your habits are saved! Please reload the app.")
            st.stop()
    else:
        st.stop()

# ---------- MOOD & NOTE ----------
st.markdown(f"### Hello, {username}! Today is **{TODAY}**")
mood = st.selectbox("How are you feeling today?", ["😊 Happy", "😐 Okay", "😔 Sad", "😡 Angry", "😴 Tired"])
mood_note = st.text_area("📝 Describe how you're feeling today (optional):")

# ---------- HABIT CHECKLIST ----------
st.markdown("### ✅ Select completed habits:")
completed_today = []
for habit in user_habits:
    if st.checkbox(habit):
        completed_today.append(habit)

# ---------- SAVE ENTRY ----------
if st.button("✅ Save Today's Entry"):
    if completed_today:
        entry = pd.DataFrame([{
            "username": username,
            "date": TODAY,
            "mood": mood,
            "mood_note": mood_note,
            "habit": h,
            "completed": 1
        } for h in completed_today])
        entry.to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.success("✅ Your habits and mood have been logged!")
    else:
        st.warning("Please select at least one habit to save.")

st.divider()

# ---------- LOAD USER DATA ----------
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    df = df[df["username"] == username]
    if df.empty:
        st.info("You haven’t logged any habits yet.")
        st.stop()

    df["date"] = pd.to_datetime(df["date"])
    df["week"] = df["date"].dt.strftime('%Y-%U')
    df["month"] = df["date"].dt.strftime('%Y-%m')

    # ---------- GRAPHS ----------
    st.markdown("### 📊 Progress Overview")

    daily_summary = df.groupby("date").agg({"completed": "sum"}).reset_index()
    st.markdown("#### 📆 Daily Habit Completion")
    st.line_chart(daily_summary.set_index("date"))

    weekly_summary = df.groupby("week").agg({"completed": "sum"}).reset_index()
    with st.expander("📅 Weekly Summary"):
        st.bar_chart(weekly_summary.set_index("week"))

    monthly_summary = df.groupby("month").agg({"completed": "sum"}).reset_index()
    with st.expander("🗓️ Monthly Summary"):
        st.bar_chart(monthly_summary.set_index("month"))

    # ---------- MOOD-HABIT ANALYSIS ----------
    st.markdown("### 🧠 Mood vs Habit Analysis")
    mood_analysis = df.groupby(["mood", "habit"]).agg({"completed": "mean"}).reset_index()
    st.dataframe(
        mood_analysis.pivot(index="habit", columns="mood", values="completed").fillna(0),
        use_container_width=True
    )

    # ---------- SENTIMENT SUGGESTION ----------
    st.markdown("### 💡 Sentiment-Based Suggestions")
    if mood_note:
        sentiment = TextBlob(mood_note).sentiment.polarity
        if sentiment < -0.3:
            st.warning("😟 You seem down. Try habits like 🧘 meditation, 📝 journaling, or 🌿 going outside.")
        elif sentiment > 0.3:
            st.success("😄 You're in a great mood! Keep it up with creative or social activities.")
        else:
            st.info("🙂 You're neutral. How about trying something new today or reflecting with a short walk?")
    else:
        st.info("Add a mood note above to get smart suggestions.")

    # ---------- HISTORY ----------
    with st.expander("📜 Full History Table"):
        st.dataframe(df.sort_values(by="date", ascending=False), use_container_width=True)
else:
    st.info("Start tracking to view analytics.")
