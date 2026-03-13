import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# Page configuration
st.set_page_config(page_title="Campus Event Tracker", page_icon="📅", layout="wide")

DATA_FILE = "events.csv"

# -----------------------------
# Load Data
# -----------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, parse_dates=["datetime"])
            return df
        except:
            return pd.DataFrame(columns=["title","datetime","category","description"])
    else:
        return pd.DataFrame(columns=["title","datetime","category","description"])

# -----------------------------
# Save Data
# -----------------------------
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# -----------------------------
# Add Event
# -----------------------------
def add_event(title, dt, category, description):
    df = load_data()

    new_event = pd.DataFrame([{
        "title": title,
        "datetime": dt,
        "category": category,
        "description": description
    }])

    df = pd.concat([df, new_event], ignore_index=True)

    save_data(df)
    return df

# -----------------------------
# Main App
# -----------------------------
def main():

    st.title("📅 Smart Campus Event & Deadline Tracker")

    st.write("Track your academic, campus and personal events in one place.")

    # -----------------------------
    # Sidebar - Add Event
    # -----------------------------
    st.sidebar.header("Add New Event")

    with st.sidebar.form("event_form"):

        title = st.text_input("Event Title")

        date = st.date_input("Date", datetime.today())

        time = st.time_input("Time", datetime.now().time())

        category = st.selectbox(
            "Category",
            ["Academic","Campus","Personal","Other"]
        )

        description = st.text_area("Description")

        submitted = st.form_submit_button("Add Event")

    if submitted:

        if title.strip() == "":
            st.error("Event title cannot be empty")

        else:
            dt = datetime.combine(date,time)

            add_event(title,dt,category,description)

            st.success("Event added successfully")

            st.rerun()

    # -----------------------------
    # Load Data
    # -----------------------------
    df = load_data()

    if df.empty:
        st.info("No events yet. Add an event from the sidebar.")
        return

    # -----------------------------
    # Search
    # -----------------------------
    search = st.text_input("🔍 Search Event")

    if search:
        df = df[df["title"].str.contains(search, case=False, na=False)]

    # -----------------------------
    # Filters
    # -----------------------------
    with st.expander("Filters"):

        col1, col2 = st.columns(2)

        with col1:
            category_filter = st.multiselect(
                "Category",
                options=df["category"].unique(),
                default=df["category"].unique()
            )

        with col2:
            start_date = st.date_input("Start Date", df["datetime"].min().date())

            end_date = st.date_input("End Date", df["datetime"].max().date())

    mask = df["category"].isin(category_filter)

    mask &= df["datetime"].dt.date.between(start_date, end_date)

    df_filtered = df[mask].sort_values("datetime")

    # -----------------------------
    # Display Events
    # -----------------------------
    st.subheader("Event List")

    st.dataframe(df_filtered, use_container_width=True)

    # -----------------------------
    # Upcoming Event Alert
    # -----------------------------
    now = pd.Timestamp.now()

    soon = now + pd.Timedelta(days=1)

    upcoming = df[
        (df["datetime"] >= now) &
        (df["datetime"] <= soon)
    ]

    if not upcoming.empty:

        st.warning("⚠ Upcoming events within next 24 hours")

        for _, row in upcoming.iterrows():

            st.write(f"**{row['title']}** ({row['category']}) - {row['datetime']}")

    # -----------------------------
    # Analytics
    # -----------------------------
    st.subheader("Event Analytics")

    col1, col2 = st.columns(2)

    # Bar Chart
    with col1:

        count_by_category = df_filtered["category"].value_counts().reset_index()

        count_by_category.columns = ["category","count"]

        fig1 = px.bar(
            count_by_category,
            x="category",
            y="count",
            title="Events by Category"
        )

        st.plotly_chart(fig1, use_container_width=True)

    # Histogram
    with col2:

        fig2 = px.histogram(
            df_filtered,
            x="datetime",
            nbins=20,
            title="Events Over Time"
        )

        st.plotly_chart(fig2, use_container_width=True)


# Run app
if __name__ == "__main__":
    main()
