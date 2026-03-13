import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Smart Campus Event Tracker",
    page_icon="📅",
    layout="wide"
)

DATA_FILE = "events.csv"

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, parse_dates=["datetime"])
            return df
        except Exception:
            st.error("Failed to read data file.")
            return pd.DataFrame(columns=["title","datetime","category","description"])
    else:
        return pd.DataFrame(columns=["title","datetime","category","description"])

# -------------------------------
# Save Data
# -------------------------------
def save_data(df):
    df.to_csv(DATA_FILE,index=False)

# -------------------------------
# Add Event
# -------------------------------
def add_event(title, dt, category, description):
    df = load_data()

    new_row = pd.DataFrame([{
        "title":title,
        "datetime":dt,
        "category":category,
        "description":description
    }])

    df = pd.concat([df,new_row],ignore_index=True)
    save_data(df)
    return df

# -------------------------------
# Upcoming Events Filter
# -------------------------------
def filter_upcoming(df,days=7):
    now = pd.Timestamp.now()
    future = now + pd.Timedelta(days=days)
    return df[(df["datetime"]>=now) & (df["datetime"]<=future)]

# -------------------------------
# Main App
# -------------------------------
def main():

    # Header
    st.markdown(
        """
        <h1 style='text-align:center;'>📅 Smart Campus Event & Deadline Tracker</h1>
        <p style='text-align:center;color:gray;'>Track assignments, campus events and personal reminders</p>
        """,
        unsafe_allow_html=True
    )

    df = load_data()

    # -------------------------------
    # Sidebar Add Event
    # -------------------------------
    st.sidebar.markdown("## ➕ Add New Event")

    with st.sidebar.form("event_form"):

        title = st.text_input("Event Title")

        date = st.date_input("Date",datetime.today())

        time = st.time_input("Time",datetime.now().time())

        category = st.selectbox(
            "Category",
            ["📚 Academic","🏫 Campus","🧑 Personal","📌 Other"]
        )

        description = st.text_area("Description")

        submitted = st.form_submit_button("Add Event")

    if submitted:

        if title == "":
            st.error("Title cannot be empty")
        else:
            dt = datetime.combine(date,time)
            df = add_event(title,dt,category,description)
            st.success(f"Event '{title}' added successfully")
            st.rerun()

    # If no events
    if df.empty:
        st.info("No events yet. Add one using the sidebar.")
        return

    # -------------------------------
    # Dashboard Metrics
    # -------------------------------
    col1,col2,col3 = st.columns(3)

    total_events = len(df)

    academic_events = len(df[df["category"].str.contains("Academic")])

    upcoming_events = len(filter_upcoming(df,7))

    col1.metric("Total Events",total_events)

    col2.metric("Academic Events",academic_events)

    col3.metric("Next 7 Days",upcoming_events)

    # -------------------------------
    # Filters
    # -------------------------------
    with st.expander("🔍 Filters"):

        col1,col2 = st.columns(2)

        with col1:
            filt_cat = st.multiselect(
                "Category",
                options=df["category"].unique(),
                default=df["category"].unique()
            )

        with col2:
            start_date = st.date_input(
                "Start Date",
                df["datetime"].min().date()
            )

            end_date = st.date_input(
                "End Date",
                df["datetime"].max().date()
            )

    mask = df["category"].isin(filt_cat)

    mask &= df["datetime"].dt.date.between(start_date,end_date)

    df_filtered = df[mask].sort_values("datetime")

    # -------------------------------
    # Search Feature
    # -------------------------------
    search = st.text_input("🔍 Search Events")

    if search:
        df_filtered = df_filtered[
            df_filtered["title"].str.contains(search,case=False)
        ]

    # -------------------------------
    # Event Countdown
    # -------------------------------
    df_filtered["Days Left"] = (
        df_filtered["datetime"] - pd.Timestamp.now()
    ).dt.days

    # -------------------------------
    # Upcoming Alerts
    # -------------------------------
    now = pd.Timestamp.now()

    soon = now + pd.Timedelta(days=1)

    upcoming = df[
        (df["datetime"]>=now) & (df["datetime"]<=soon)
    ]

    if not upcoming.empty:

        st.warning("⚠ Events within next 24 hours")

        for _,row in upcoming.iterrows():

            st.write(
                f"**{row['title']}** ({row['category']}) - {row['datetime']}"
            )

    # -------------------------------
    # Today's Events
    # -------------------------------
    today_events = df[
        df["datetime"].dt.date == datetime.today().date()
    ]

    if not today_events.empty:

        st.success("📍 Events Today")

        st.dataframe(today_events)

    # -------------------------------
    # Highlight Urgent Events
    # -------------------------------
    def highlight(row):

        if row["Days Left"] <= 1:
            return ['background-color:#ffcccc']*len(row)

        elif row["Days Left"] <= 3:
            return ['background-color:#fff3cd']*len(row)

        else:
            return ['']*len(row)

    st.subheader("📋 Event List")

    st.dataframe(
        df_filtered.style.apply(highlight,axis=1)
    )

    # -------------------------------
    # Delete Event
    # -------------------------------
    st.subheader("🗑 Delete Event")

    event_to_delete = st.selectbox(
        "Select Event",
        df["title"].tolist()
    )

    if st.button("Delete Event"):

        df = df[df["title"] != event_to_delete]

        save_data(df)

        st.success("Event deleted")

        st.rerun()

    # -------------------------------
    # Download Data
    # -------------------------------
    csv = df.to_csv(index=False)

    st.download_button(
        "📥 Download Events CSV",
        csv,
        "events_backup.csv",
        "text/csv"
    )

    # -------------------------------
    # Analytics
    # -------------------------------
    st.subheader("📊 Analytics")

    colA,colB = st.columns(2)

    with colA:

        count_cat = df_filtered["category"].value_counts().reset_index()

        count_cat.columns = ["category","count"]

        fig1 = px.pie(
            count_cat,
            names="category",
            values="count",
            title="Event Distribution"
        )

        st.plotly_chart(fig1,use_container_width=True)

    with colB:

        fig2 = px.scatter(
            df_filtered,
            x="datetime",
            y="category",
            color="category",
            title="Event Timeline"
        )

        st.plotly_chart(fig2,use_container_width=True)

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    main()
