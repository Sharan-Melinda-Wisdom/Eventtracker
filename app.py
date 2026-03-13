import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os

DATA_FILE = "events.csv"

# Utility functions

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, parse_dates=["datetime"])
            return df
        except Exception:
            st.error("Failed to read data file. The format may be corrupted.")
            return pd.DataFrame(columns=["title", "datetime", "category", "description"])
    else:
        return pd.DataFrame(columns=["title", "datetime", "category", "description"])


def save_data(df: pd.DataFrame):
    df.to_csv(DATA_FILE, index=False)


def add_event(title, dt, category, description):
    df = load_data()
    df = df.append({
        "title": title,
        "datetime": dt,
        "category": category,
        "description": description,
    }, ignore_index=True)
    save_data(df)
    return df


def filter_upcoming(df, days=7):
    now = pd.Timestamp.now()
    future = now + pd.Timedelta(days=days)
    return df[(df["datetime"] >= now) & (df["datetime"] <= future)]


def main():
    st.title("Smart Campus Event & Deadline Tracker")
    st.markdown(
        "An interactive real-time tracker for academic and campus events. Add events, filter, and inspect analytics."
    )

    # Sidebar for adding events
    st.sidebar.header("Add new event")
    with st.sidebar.form(key="event_form"):
        title = st.text_input("Title")
        date = st.date_input("Date", datetime.today())
        time = st.time_input("Time", datetime.now().time())
        category = st.selectbox(
            "Category", ["Academic", "Campus", "Personal", "Other"]
        )
        description = st.text_area("Description")
        submitted = st.form_submit_button("Add Event")

    if submitted:
        dt = datetime.combine(date, time)
        df = add_event(title, dt, category, description)
        st.success(f"Event '{title}' added for {dt}")

    # Load data
    df = load_data()
    if df.empty:
        st.info("No events found. Add one using the sidebar.")
        return

    # Filters
    with st.expander("Filters"):
        col1, col2 = st.columns(2)
        with col1:
            filt_cat = st.multiselect("Category", options=df["category"].unique(), default=df["category"].unique())
        with col2:
            days = st.slider("Within days", 1, 365, 30)
        start_date = st.date_input("Start date", df["datetime"].min().date())
        end_date = st.date_input("End date", df["datetime"].max().date())

    mask = df["category"].isin(filt_cat)
    mask &= df["datetime"].dt.date.between(start_date, end_date)
    df_filtered = df[mask].sort_values("datetime")

    # Alert for imminent events
    now = pd.Timestamp.now()
    soon = now + pd.Timedelta(days=1)
    upcoming_soon = df[(df["datetime"] >= now) & (df["datetime"] <= soon)]
    if not upcoming_soon.empty:
        st.warning("⚠️ Upcoming events within next 24 hours:")
        for _, row in upcoming_soon.sort_values("datetime").iterrows():
            st.write(f"**{row['title']}** ({row['category']}) - {row['datetime']}\n{row['description']}")

    # Display table
    st.subheader("Events")
    st.dataframe(df_filtered)

    # Analytics
    st.subheader("Analytics")
    colA, colB = st.columns(2)
    with colA:
        count_by_cat = df_filtered["category"].value_counts().reset_index()
        count_by_cat.columns = ["category", "count"]
        fig1 = px.bar(count_by_cat, x="category", y="count", title="Events by Category")
        st.plotly_chart(fig1, use_container_width=True)
    with colB:
        if not df_filtered.empty:
            fig2 = px.histogram(df_filtered, x="datetime", nbins=20, title="Events over Time")
            st.plotly_chart(fig2, use_container_width=True)

    # Real-time refresh button
    if st.button("Refresh"):
        st.rerun()


if __name__ == "__main__":
    main()
