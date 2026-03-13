import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

DATA_FILE = "events.csv"

st.set_page_config(page_title="Campus Event Tracker", page_icon="", layout="wide")

# -----------------------------
# Utility Functions
# -----------------------------

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, parse_dates=["datetime"])
            return df
        except:
            return pd.DataFrame(columns=["title","datetime","category","description"])
    return pd.DataFrame(columns=["title","datetime","category","description"])


def save_data(df):
    df.to_csv(DATA_FILE,index=False)


def add_event(title,dt,category,description):
    df = load_data()

    new_event = pd.DataFrame({
        "title":[title],
        "datetime":[dt],
        "category":[category],
        "description":[description]
    })

    df = pd.concat([df,new_event],ignore_index=True)

    save_data(df)
    return df


def delete_event(title):
    df = load_data()
    df = df[df["title"]!=title]
    save_data(df)
    return df


# -----------------------------
# MAIN APP
# -----------------------------

def main():

    st.title("Smart Campus Event Tracker")
    st.caption("Track Academic, Campus and Personal Events")

    df = load_data()

    # -----------------------------
    # Sidebar - Add Event
    # -----------------------------

    st.sidebar.header("➕ Add Event")

    with st.sidebar.form("event_form"):

        title = st.text_input("Event Title")

        date = st.date_input("Date")

        time = st.time_input("Time")

        category = st.selectbox(
            "Category",
            ["Academic","Campus","Personal","Other"]
        )

        description = st.text_area("Description")

        submit = st.form_submit_button("Add Event")

    if submit:

        dt = datetime.combine(date,time)

        df = add_event(title,dt,category,description)

        st.success("Event Added Successfully")

    # -----------------------------
    # Dashboard Metrics
    # -----------------------------

    total = len(df)
    academic = len(df[df["category"]=="Academic"])
    campus = len(df[df["category"]=="Campus"])
    personal = len(df[df["category"]=="Personal"])

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Total Events",total)
    c2.metric("Academic Events",academic)
    c3.metric("Campus Events",campus)
    c4.metric("Personal Events",personal)

    st.divider()

    # -----------------------------
    # Search
    # -----------------------------

    search = st.text_input("Search Event")

    if search:
        df = df[df["title"].str.contains(search,case=False)]

    # -----------------------------
    # Delete Event
    # -----------------------------

    st.subheader("Delete Event")

    if not df.empty:

        event_to_delete = st.selectbox(
            "Select Event",
            df["title"].unique()
        )

        if st.button("Delete Event"):

            delete_event(event_to_delete)

            st.success("Event Deleted")

            st.rerun()

    # -----------------------------
    # Upcoming Events Alert
    # -----------------------------

    now = pd.Timestamp.now()
    tomorrow = now + pd.Timedelta(days=1)

    upcoming = df[(df["datetime"]>=now)&(df["datetime"]<=tomorrow)]

    if not upcoming.empty:

        st.warning("Upcoming Events within 24 Hours")

        for _,row in upcoming.iterrows():
            st.write(f"**{row['title']}** ({row['category']}) - {row['datetime']}")

    # -----------------------------
    # Events Table
    # -----------------------------

    st.subheader("Event List")

    st.dataframe(df.sort_values("datetime"),use_container_width=True)

    # -----------------------------
    # Charts
    # -----------------------------

    st.subheader("Analytics")

    col1,col2 = st.columns(2)

    with col1:

        cat_count = df["category"].value_counts().reset_index()

        cat_count.columns = ["Category","Count"]

        fig1 = px.bar(
            cat_count,
            x="Category",
            y="Count",
            title="Events by Category"
        )

        st.plotly_chart(fig1,use_container_width=True)

    with col2:

        if not df.empty:

            fig2 = px.histogram(
                df,
                x="datetime",
                nbins=20,
                title="Events Timeline"
            )

            st.plotly_chart(fig2,use_container_width=True)


if __name__ == "__main__":
    main()

