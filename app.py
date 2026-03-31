import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ─────────────────────────────────────────────────
st.set_page_config(
    page_title="IPL Analytics Dashboard",
    page_icon="🏏",
    layout="wide"
)

# ── Custom CSS ───────────────────────────────────────────────────
st.markdown("""
    <style>
    .main { background-color: #0f1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2e5fa3);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        color: white;
    }
    h1, h2, h3 { color: #f0a500; }
    </style>
""", unsafe_allow_html=True)

# ── Load Data ────────────────────────────────────────────────────
@st.cache_data
def load_data():
    matches = pd.read_csv("matches.csv")
deliveries = pd.read_csv("compressed_data.csv.gz", compression="gzip")
    return matches, deliveries

matches, deliveries = load_data()

# ── Sidebar ──────────────────────────────────────────────────────
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/8/84/Indian_Premier_League_Official_Logo.svg/200px-Indian_Premier_League_Official_Logo.svg.png", width=120)
st.sidebar.title("🏏 IPL Dashboard")
st.sidebar.markdown("---")

seasons = sorted(matches["season"].unique())
selected_seasons = st.sidebar.multiselect("Select Season(s)", seasons, default=seasons)

all_teams = sorted(set(matches["team1"].unique()) | set(matches["team2"].unique()))
selected_team = st.sidebar.selectbox("Select a Team (for detail)", ["All"] + all_teams)

filtered = matches[matches["season"].isin(selected_seasons)]

# ── Title ────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center;'>🏏 IPL Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#aaa;'>Comprehensive analysis of IPL matches from 2008–2020</p>", unsafe_allow_html=True)
st.markdown("---")

# ── KPI Metrics ──────────────────────────────────────────────────
total_matches   = len(filtered)
total_seasons   = filtered["season"].nunique()
total_teams     = len(all_teams)
total_venues    = filtered["venue"].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("🏟️ Total Matches",  total_matches)
c2.metric("📅 Seasons",         total_seasons)
c3.metric("🤝 Teams",           total_teams)
c4.metric("📍 Venues",          total_venues)

st.markdown("---")

# ── Row 1: Most Successful Teams & Toss Analysis ─────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Most Successful Teams")
    wins = filtered["winner"].value_counts().reset_index()
    wins.columns = ["Team", "Wins"]
    wins = wins.dropna().head(10)
    fig = px.bar(wins, x="Wins", y="Team", orientation="h",
                 color="Wins", color_continuous_scale="Blues",
                 title="Top 10 Teams by Wins")
    fig.update_layout(yaxis=dict(autorange="reversed"),
                      plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                      font_color="white")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎲 Toss Decision Impact")
    toss = filtered.copy()
    toss["toss_match_win"] = toss["toss_winner"] == toss["winner"]
    toss_summary = toss["toss_match_win"].value_counts().reset_index()
    toss_summary.columns = ["Won Match After Toss", "Count"]
    toss_summary["Won Match After Toss"] = toss_summary["Won Match After Toss"].map({True: "Won", False: "Lost"})
    fig2 = px.pie(toss_summary, names="Won Match After Toss", values="Count",
                  color_discrete_sequence=["#2e5fa3", "#f0a500"],
                  title="Did Winning Toss Help Win the Match?")
    fig2.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117", font_color="white")
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Season Wins & Venue Analysis ──────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("📈 Wins Per Season (Top Teams)")
    top_teams = filtered["winner"].value_counts().head(5).index.tolist()
    season_wins = (
        filtered[filtered["winner"].isin(top_teams)]
        .groupby(["season", "winner"])
        .size()
        .reset_index(name="Wins")
    )
    fig3 = px.line(season_wins, x="season", y="Wins", color="winner",
                   markers=True, title="Season-wise Wins for Top 5 Teams",
                   color_discrete_sequence=px.colors.qualitative.Bold)
    fig3.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117", font_color="white")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("🏟️ Top Venues by Matches Hosted")
    venues = filtered["venue"].value_counts().head(10).reset_index()
    venues.columns = ["Venue", "Matches"]
    fig4 = px.bar(venues, x="Matches", y="Venue", orientation="h",
                  color="Matches", color_continuous_scale="Oranges",
                  title="Top 10 Venues")
    fig4.update_layout(yaxis=dict(autorange="reversed"),
                       plot_bgcolor="#0f1117", paper_bgcolor="#0f1117",
                       font_color="white")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ── Row 3: Batting Stats ──────────────────────────────────────────
st.subheader("🏏 Top Run Scorers")

season_deliveries = deliveries[deliveries["match_id"].isin(filtered["id"])]

# Auto-detect column names for batsman and runs
batsman_col = "batter" if "batter" in season_deliveries.columns else "batsman"
runs_col    = "batsman_runs" if "batsman_runs" in season_deliveries.columns else "runs_off_bat"

top_batsmen = (
    season_deliveries.groupby(batsman_col)[runs_col]
    .sum()
    .reset_index()
    .sort_values(runs_col, ascending=False)
    .head(15)
)
top_batsmen.columns = ["Batsman", "Total Runs"]

fig5 = px.bar(top_batsmen, x="Batsman", y="Total Runs",
              color="Total Runs", color_continuous_scale="Reds",
              title="Top 15 Run Scorers (Selected Seasons)")
fig5.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117", font_color="white")
st.plotly_chart(fig5, use_container_width=True)

# ── Row 4: Bowling Stats ──────────────────────────────────────────
st.subheader("🎳 Top Wicket Takers")

# Auto-detect dismissal column
dismissal_col = "dismissal_kind" if "dismissal_kind" in season_deliveries.columns else "wicket_type"

wickets = season_deliveries[season_deliveries[dismissal_col].notna() &
                             (season_deliveries[dismissal_col] != "run out")]
top_bowlers = (
    wickets.groupby("bowler")[dismissal_col]
    .count()
    .reset_index()
    .sort_values(dismissal_col, ascending=False)
    .head(15)
)
top_bowlers.columns = ["Bowler", "Wickets"]

fig6 = px.bar(top_bowlers, x="Bowler", y="Wickets",
              color="Wickets", color_continuous_scale="Greens",
              title="Top 15 Wicket Takers (Selected Seasons)")
fig6.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117", font_color="white")
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# ── Team Deep Dive ────────────────────────────────────────────────
if selected_team != "All":
    st.subheader(f"🔍 Deep Dive: {selected_team}")

    team_matches = filtered[(filtered["team1"] == selected_team) |
                             (filtered["team2"] == selected_team)]
    team_wins    = filtered[filtered["winner"] == selected_team]
    win_rate     = round(len(team_wins) / len(team_matches) * 100, 1) if len(team_matches) > 0 else 0

    t1, t2, t3 = st.columns(3)
    t1.metric("Matches Played", len(team_matches))
    t2.metric("Matches Won",    len(team_wins))
    t3.metric("Win Rate",       f"{win_rate}%")

    # Season-wise wins for selected team
    sw = team_wins.groupby("season").size().reset_index(name="Wins")
    fig7 = px.bar(sw, x="season", y="Wins",
                  color="Wins", color_continuous_scale="Blues",
                  title=f"{selected_team} — Wins Per Season")
    fig7.update_layout(plot_bgcolor="#0f1117", paper_bgcolor="#0f1117", font_color="white")
    st.plotly_chart(fig7, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#555;'>Built by Shawchol Chandro Ghosh &nbsp;|&nbsp; "
    "Data Source: Kaggle IPL Dataset 2008–2020</p>",
    unsafe_allow_html=True
)
