import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

DATA_FILE = "events.csv"

st.set_page_config(page_title="Campus Event Tracker", layout="wide")

# -------------------------
# CUSTOM CSS (UI Styling)
# -------------------------

st.markdown("""
<style>

.metric-card {
background-color:#f0f2f6;
padding:15px;
border-radius:10px;
text-align:center;
font-weight:bold;
}

.event-card {
background-color:white;
padding:15px;
border-radius:10px;
box-shadow:0 3px 10px rgba(0,0,0,0.1);
margin-bottom:10px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# Utility Functions
# -------------------------

def load_data():

    if os.path.exists(DATA_FILE):

        try:
            df = pd.read_csv(DATA_FILE, parse_dates=["datetime"])
            return df

        except:
            return pd.DataFrame(columns=[
                "title","datetime","category","priority","description"
            ])

    return pd.DataFrame(columns=[
        "title","datetime","category","priority","description"
    ])


def save_data(df):
    df.to_csv(DATA_FILE,index=False)


def add_event(title,dt,category,priority,description):

    df = load_data()

    new_event = pd.DataFrame({
        "title":[title],
        "datetime":[dt],
        "category":[category],
        "priority":[priority],
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


# -------------------------
# MAIN APP
# -------------------------

def main():

    st.title("Smart Campus Event Tracker")
    st.caption("Organize Academic, Campus & Personal Events")

    df = load_data()

# -------------------------
# Sidebar - Add Event
# -------------------------

    st.sidebar.header("Add Event")

    with st.sidebar.form("add_event"):

        title = st.text_input("Event Title")

        date = st.date_input("Date")

        time = st.time_input("Time")

        category = st.selectbox(
            "Category",
            ["Academic","Campus","Personal","Other"]
        )

        priority = st.selectbox(
            "Priority",
            ["High","Medium","Low"]
        )

        description = st.text_area("Description")

        submit = st.form_submit_button("Add Event")

    if submit:

        dt = datetime.combine(date,time)

        df = add_event(title,dt,category,priority,description)

        st.success("Event Added")

# -------------------------
# Dashboard Metrics
# -------------------------

    total = len(df)
    academic = len(df[df["category"]=="Academic"])
    campus = len(df[df["category"]=="Campus"])
    personal = len(df[df["category"]=="Personal"])

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Total Events",total)
    c2.metric("Academic",academic)
    c3.metric("Campus",campus)
    c4.metric("Personal",personal)

    st.divider()

# -------------------------
# Search
# -------------------------

    search = st.text_input("Search Event")

    if search:
        df = df[df["title"].str.contains(search,case=False)]

# -------------------------
# Delete Event
# -------------------------

    st.subheader("Delete Event")

    if not df.empty:

        event = st.selectbox(
            "Select Event to Delete",
            df["title"].unique()
        )

        if st.button("Delete Event"):

            delete_event(event)

            st.success("Event Deleted")

            st.rerun()

# -------------------------
# Upcoming Alerts
# -------------------------

    now = pd.Timestamp.now()

    tomorrow = now + pd.Timedelta(days=1)

    upcoming = df[(df["datetime"]>=now)&(df["datetime"]<=tomorrow)]

    if not upcoming.empty:

        st.warning("Upcoming Events in Next 24 Hours")

        for _,row in upcoming.iterrows():

            st.write(
                f"**{row['title']}** | {row['category']} | {row['priority']} | {row['datetime']}"
            )

# -------------------------
# Event Cards
# -------------------------

    st.subheader("Event List")

    df = df.sort_values("datetime")

    for _,row in df.iterrows():

        st.markdown(f"""
        <div class="event-card">
        <h4>{row['title']}</h4>
        <b>Date:</b> {row['datetime']} <br>
        <b>Category:</b> {row['category']} <br>
        <b>Priority:</b> {row['priority']} <br>
        <b>Description:</b> {row['description']}
        </div>
        """, unsafe_allow_html=True)

# -------------------------
# Download Data
# -------------------------

    st.download_button(
        "Download Events CSV",
        df.to_csv(index=False),
        file_name="events.csv"
    )

# -------------------------
# Charts
# -------------------------

    st.subheader("Analytics")

    col1,col2 = st.columns(2)

    with col1:

        cat_count = df["category"].value_counts().reset_index()

        cat_count.columns = ["Category","Count"]

        fig1 = px.bar(cat_count,x="Category",y="Count")

        st.plotly_chart(fig1,use_container_width=True)

    with col2:

        if not df.empty:

            fig2 = px.histogram(df,x="datetime",nbins=20)

            st.plotly_chart(fig2,use_container_width=True)


if __name__ == "__main__":
    main()
