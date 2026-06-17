import streamlit as st
import calendar
from datetime import date, datetime
import pandas as pd

st.set_page_config(page_title="EmoMaterialist Habit Tracker", page_icon="🖤", layout="wide")

# ---- Gothic Palette ----
VAMPIRE_BLACK = "#0E0204"
WINE_RED = "#A30E2B"
PINK_LAVENDER = "#DFB8CA"
TWILIGHT_LAVENDER = "#774972"
BG_PURPLE_GREY = "#2A2330"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {BG_PURPLE_GREY};
        color: {PINK_LAVENDER};
    }}
    h1, h2, h3 {{
        color: {WINE_RED} !important;
        font-family: 'Georgia', serif;
    }}
    .day-cell {{
        background-color: {VAMPIRE_BLACK};
        border: 1px solid {TWILIGHT_LAVENDER};
        border-radius: 6px;
        padding: 8px;
        text-align: center;
        color: {PINK_LAVENDER};
    }}
    .stButton button {{
        background-color: {TWILIGHT_LAVENDER};
        color: {PINK_LAVENDER};
        border: 1px solid {WINE_RED};
        border-radius: 6px;
    }}
    .stButton button:hover {{
        background-color: {WINE_RED};
        color: white;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("🖤 Habit Tracker")
st.write("Click a date, log your habits, watch your consistency build over the year.")

# ---- Session State Setup ----
if "habits" not in st.session_state:
    st.session_state.habits = ["Workout", "Skincare", "Journaling"]

if "log" not in st.session_state:
    # log structure: { "2026-06-17": {"Workout": True, "Skincare": False, ...} }
    st.session_state.log = {}

if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

# ---- Sidebar: Manage Habits ----
with st.sidebar:
    st.header("Your Habits")
    new_habit = st.text_input("Add a new habit")
    if st.button("Add Habit") and new_habit:
        if new_habit not in st.session_state.habits:
            st.session_state.habits.append(new_habit)

    for h in st.session_state.habits:
        col1, col2 = st.columns([4, 1])
        col1.write(h)
        if col2.button("✕", key=f"remove_{h}"):
            st.session_state.habits.remove(h)
            st.rerun()

# ---- Calendar Navigation ----
col_prev, col_label, col_next = st.columns([1, 3, 1])
year = st.session_state.selected_date.year
month = st.session_state.selected_date.month

with col_prev:
    if st.button("◀ Prev Month"):
        if month == 1:
            st.session_state.selected_date = date(year - 1, 12, 1)
        else:
            st.session_state.selected_date = date(year, month - 1, 1)
        st.rerun()

with col_label:
    st.markdown(f"<h2 style='text-align:center;'>{calendar.month_name[month]} {year}</h2>", unsafe_allow_html=True)

with col_next:
    if st.button("Next Month ▶"):
        if month == 12:
            st.session_state.selected_date = date(year + 1, 1, 1)
        else:
            st.session_state.selected_date = date(year, month + 1, 1)
        st.rerun()

# ---- Calendar Grid ----
cal = calendar.Calendar(firstweekday=6)  # Sunday start
month_days = cal.monthdayscalendar(year, month)

day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
header_cols = st.columns(7)
for i, name in enumerate(day_names):
    header_cols[i].markdown(f"<div style='text-align:center; color:{WINE_RED}; font-weight:bold;'>{name}</div>", unsafe_allow_html=True)

for week in month_days:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].write("")
            continue

        day_date = date(year, month, day)
        date_key = day_date.isoformat()
        habits_done = st.session_state.log.get(date_key, {})
        completed_count = sum(1 for v in habits_done.values() if v)
        total_habits = len(st.session_state.habits)

        # Intensity-based label
        if total_habits == 0:
            label = f"{day}"
        elif completed_count == total_habits and total_habits > 0:
            label = f"{day} 🖤"
        elif completed_count > 0:
            label = f"{day} 🩸"
        else:
            label = f"{day}"

        if cols[i].button(label, key=f"day_{date_key}"):
            st.session_state.selected_date = day_date
            st.rerun()

st.divider()

# ---- Selected Day Detail ----
selected = st.session_state.selected_date
st.subheader(f"Log for {selected.strftime('%B %d, %Y')}")

date_key = selected.isoformat()
if date_key not in st.session_state.log:
    st.session_state.log[date_key] = {h: False for h in st.session_state.habits}

for h in st.session_state.habits:
    current_val = st.session_state.log[date_key].get(h, False)
    new_val = st.checkbox(h, value=current_val, key=f"check_{date_key}_{h}")
    st.session_state.log[date_key][h] = new_val

st.divider()

# ---- Yearly Consistency View ----
st.subheader("Yearly Consistency")

if st.session_state.habits:
    chosen_habit = st.selectbox("View consistency for:", st.session_state.habits)

    rows = []
    for date_key, habits_done in st.session_state.log.items():
        if habits_done.get(chosen_habit):
            rows.append(datetime.fromisoformat(date_key))

    if rows:
        df = pd.DataFrame({"date": rows})
        df["month"] = df["date"].dt.to_period("M").astype(str)
        monthly_counts = df.groupby("month").size().reset_index(name="days completed")
        st.bar_chart(monthly_counts.set_index("month"))

        total_done = len(rows)
        st.metric(f"Total days completed: {chosen_habit}", total_done)
    else:
        st.write("No entries logged yet for this habit. Start checking off days above!")
else:
    st.write("Add a habit in the sidebar to get started.")