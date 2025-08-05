import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("spotify_cleaned_data.csv", parse_dates=["ts"])
    df["minutes_played"] = df["ms_played"] / 60000
    df["day_of_week"] = df["ts"].dt.day_name()
    df["hour"] = df["ts"].dt.hour
    df["year"] = df["ts"].dt.year
    df["month"] = df["ts"].dt.to_period("M").astype(str)
    return df

df = load_data()

# App layout
st.title("🎧 Tomisin's Spotify Dashboard")
st.markdown("This is a personal project to use python to analyse my lifetime Spotify history and visualize using Streamlit. Data here is from February 2021 through August 3rd 2025. Feel free to clone and use to visualize your listening history.")

# Filters
media_type = st.selectbox("Media Type", df["media_type"].unique())
years = sorted(df["year"].unique(), reverse=True)
year_options = ["All Years"] + [str(y) for y in years]
selected_year = st.selectbox("Year", year_options)


# Filtered view
if selected_year == "All Years":
    filtered = df[df["media_type"] == media_type]
else:
    filtered = df[(df["media_type"] == media_type) & (df["year"] == int(selected_year))]



st.markdown("### 📊 Summary Stats")

col1, col2, col3 = st.columns(3)
col1.metric("🎧 Total Minutes Played", int(filtered["minutes_played"].sum()))
col2.metric("🎵 Total Tracks Streamed", len(filtered))
col3.metric("📅 Date Range", f"{filtered['ts'].min().date()} → {filtered['ts'].max().date()}")


# Top songs
top_songs = (
    filtered.groupby("master_metadata_track_name")["minutes_played"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    .sort_values("minutes_played", ascending=True)
)

fig = px.bar(top_songs, x="minutes_played", y="master_metadata_track_name", orientation="h",
             title="Top 10 Songs", labels={"master_metadata_track_name": "Track", "minutes_played": "Minutes"})
st.plotly_chart(fig)


# Top Artists
st.subheader("🎤 Top 10 Artists")
top_artists = (
    filtered.groupby("master_metadata_album_artist_name")["minutes_played"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    .sort_values("minutes_played", ascending=True)
)

fig2 = px.bar(top_artists, x="minutes_played", y="master_metadata_album_artist_name", orientation="h",
              title="Top 10 Artists", labels={"master_metadata_album_artist_name": "Artist", "minutes_played": "Minutes"},
              color_discrete_sequence=["orange"])
st.plotly_chart(fig2)


# Most Skipped Artists
st.subheader("🚫 Most Skipped Artists")
skipped = filtered[filtered["skipped"] == True]
skipped_artists = (
    skipped.groupby("master_metadata_album_artist_name")["skipped"]
    .count()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    .sort_values("skipped", ascending=True)
)

fig_skipped = px.bar(skipped_artists, x="skipped", y="master_metadata_album_artist_name", orientation="h",
                     title="Top 10 Most Skipped Artists", labels={"master_metadata_album_artist_name": "Artist", "skipped": "Skips"},
                     color_discrete_sequence=["red"])
st.plotly_chart(fig_skipped)



# Monthly Listening Trend
st.subheader("📈 Monthly Listening Trend")
monthly = (
    filtered.groupby("month")["minutes_played"]
    .sum()
    .reset_index()
    .sort_values("month")
)

fig3 = px.line(monthly, x="month", y="minutes_played", title="Monthly Listening Time")
st.plotly_chart(fig3)


# Day of Week Listening
st.subheader("📆 Listening by Day of Week")
dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
dow = (
    filtered.groupby("day_of_week")["minutes_played"]
    .sum()
    .reindex(dow_order)
    .reset_index()
)

fig4 = px.bar(dow, x="day_of_week", y="minutes_played", title="Listening by Day of Week",
              color="day_of_week", color_discrete_sequence=px.colors.qualitative.Pastel)
st.plotly_chart(fig4)


# Hourly Listening
st.subheader("⏰ Listening by Hour")
hourly = (
    filtered.groupby("hour")["minutes_played"]
    .sum()
    .reset_index()
)

fig5 = px.bar(hourly, x="hour", y="minutes_played", title="Listening by Hour of Day",
              color="hour", color_continuous_scale="Viridis")
st.plotly_chart(fig5)



