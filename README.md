# Smart Campus Event & Deadline Tracker

This Streamlit application enables students to manage academic and campus-related events in real time. Features include:

- Add and store events with title, date/time, category, and description.
- Filter events by category and date range.
- Alerts for events occurring within the next 24 hours.
- Analytics dashboard using Plotly to visualize events by category and over time.
- Deployable on Streamlit Cloud with automatic refresh support.

## Getting Started

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run locally

```bash
streamlit run app.py
```

### Deployment (Streamlit Cloud)

1. Push this repository to GitHub.
2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and create a new app.
3. Connect your GitHub repo and set `app.py` as the main file.
4. Ensure `requirements.txt` is included and contains the necessary packages.

The app uses a local file (`events.csv`) for persistent storage. Streamlit Cloud will persist this file between sessions automatically.

## Usage

- Use the sidebar to add new events.
- Apply filters to view a subset of events.
- Check alerts at the top of the page for imminent deadlines.
- Explore the analytics section for visual insights.

## File Structure

```
/app.py
/requirements.txt
/README.md
```

## Notes

- This prototype uses a CSV file for storage. For production, consider using a database or cloud storage.
- Adjust alert time windows, categories, and appearance as needed.