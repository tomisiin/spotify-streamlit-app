import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tomi’s Spotify Dashboard", page_icon="🎧", layout="wide")

# ---------- Data ----------
@st.cache_data
def load_data(path="spotify_cleaned_data.csv"):
    df = pd.read_csv(path, parse_dates=["ts"])
    # Defensive columns
    if "ms_played" not in df: df["ms_played"] = 0
    if "skipped" not in df: df["skipped"] = False
    if "media_type" not in df: df["media_type"] = "audio"

    df = df.assign(
        minutes_played = df["ms_played"] / 60000,
        day_of_week    = df["ts"].dt.day_name(),
        hour           = df["ts"].dt.hour,
        year           = df["ts"].dt.year,
        month_period   = df["ts"].dt.to_period("M")  # use for sorting
    )
    # Categorical day order for nice plots
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["day_of_week"] = pd.Categorical(df["day_of_week"], categories=dow_order, ordered=True)
    return df

df = load_data()

# ---------- UI: Header ----------
st.title("🎧 Tomisin's Spotify Dashboard")
st.markdown(
    "Personal project visualising my Spotify history (Feb 2021 → Aug 3, 2025). "
    "Clone and use for your data."
)

# ---------- Sidebar Filters ----------
with st.sidebar:
    st.header("Filters")
    media_vals = ["All Media"] + sorted(df["media_type"].dropna().unique().tolist())
    media_type = st.selectbox("Media Type", media_vals, index=0)

    years = sorted(df["year"].dropna().unique().tolist(), reverse=True)
    year_options = ["All Years"] + [str(y) for y in years]
    selected_year = st.selectbox("Year", year_options, index=0)

    top_n = st.slider("Top N (songs/artists)", 5, 30, 10, step=1)
    min_minutes = st.slider("Ignore plays shorter than (minutes)", 0.0, 3.0, 0.1, 0.1)

    metric = st.radio("Metric", ["Minutes", "Play count"], horizontal=True)

# ---------- Apply Filters ----------
filtered = df.copy()
if media_type != "All Media":
    filtered = filtered[filtered["media_type"] == media_type]

if selected_year != "All Years":
    filtered = filtered[filtered["year"] == int(selected_year)]

# Ignore micro-plays
filtered = filtered[filtered["minutes_played"] >= float(min_minutes)]

# ---------- Empty State ----------
if filtered.empty:
    st.warning("No data for the current filters. Try broadening filters.")
    st.stop()

# ---------- Summary KPIs ----------
st.markdown("### 📊 Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("🎧 Total Minutes", int(filtered["minutes_played"].sum()))
col2.metric("🎵 Streams", int(len(filtered)))
col3.metric("🧑‍🎤 Unique Artists", filtered["master_metadata_album_artist_name"].nunique())
date_range = f"{filtered['ts'].min().date()} → {filtered['ts'].max().date()}"
col4.metric("📅 Date Range", date_range)

st.download_button(
    "⬇️ Download filtered CSV", 
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="spotify_filtered.csv",
    mime="text/csv"
)

# ---------- Helpers ----------
value_col = "minutes_played" if metric == "Minutes" else None  # None means count
value_label = "Minutes" if metric == "Minutes" else "Plays"

def agg_top(df_in, by, n):
    if value_col:
        g = df_in.groupby(by)[value_col].sum().reset_index(name=value_label)
    else:
        g = df_in.groupby(by).size().reset_index(name=value_label)
    return g.sort_values(value_label, ascending=False).head(n).sort_values(value_label, ascending=True)

# ---------- Top Songs ----------
top_songs = agg_top(filtered, "master_metadata_track_name", top_n)
fig = px.bar(
    top_songs, x=value_label, y="master_metadata_track_name", orientation="h",
    title=f"Top {top_n} Songs — {value_label}",
    labels={"master_metadata_track_name": "Track"}
)
st.plotly_chart(fig, use_container_width=True)

# ---------- Top Artists ----------
st.subheader(f"🎤 Top {top_n} Artists — {value_label}")
top_artists = agg_top(filtered, "master_metadata_album_artist_name", top_n)
fig2 = px.bar(
    top_artists, x=value_label, y="master_metadata_album_artist_name", orientation="h",
    labels={"master_metadata_album_art_
