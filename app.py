"""India Monsoon & Drought Dashboard (2000-2025), built on IMD gridded rainfall."""
import json

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='India Monsoon & Drought', page_icon='🌧️', layout='wide') 

from assets.rain_effect import add_rain
add_rain()

from assets.clouds_effect import add_clouds
add_clouds()

st.markdown("""
<style>
[data-testid="stPlotlyChart"] { padding: 0 !important; overflow: visible !important; }
div[data-testid="stMetric"], [data-testid="stPlotlyChart"] { position: relative; z-index: 1; }
</style>
""", unsafe_allow_html=True)

# ---------- stormy-sky background and frosted-glass cards ----------
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(ellipse at 15% 0%, rgba(159, 226, 238, 0.30), transparent 50%),
        radial-gradient(ellipse at 85% 10%, rgba(123, 117, 201, 0.45), transparent 55%),
        radial-gradient(ellipse at 50% 100%, rgba(234, 247, 237, 0.18), transparent 60%),
        linear-gradient(180deg, #232C3D 0%, #34475A 45%, #4E6B66 100%);
    background-attachment: fixed;
}
[data-testid="stHeader"] { background: transparent; }
div[data-testid="stMetric"], [data-testid="stPlotlyChart"] {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 20px;
    padding: 14px 18px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
}
h1 { font-weight: 700 !important; letter-spacing: -0.5px; color: #FFFFFF !important; }
[data-testid="stMetricValue"] { font-size: 1.8rem !important; }
</style>
""", unsafe_allow_html=True)

LIGHT_PURPLE = '#BDB9EA'
BORDER = '#A9B4D9'
STATE_COLORS = {'Large deficient': '#7B75C9', 'Deficient': '#BDB9EA', 'Normal': '#EAF7ED',
                'Excess': '#9FE2EE', 'Large excess': '#3FA7C4'}
INDIA_COLORS = {'Deficient': '#7B75C9', 'Below normal': '#BDB9EA', 'Normal': '#CFE8D5',
                'Above normal': '#9FE2EE', 'Excess': '#3FA7C4'}
GRID = 'rgba(255, 255, 255, 0.10)'


@st.cache_data
def load_data():
    india = pd.read_csv('data/monsoon_summary.csv')
    states = pd.read_csv('data/state_monsoon.csv')
    states['category'] = pd.cut(states['departure_pct'], bins=[-1e9, -60, -20, 20, 60, 1e9],
                                labels=list(STATE_COLORS), right=False).astype(str)
    with open('data/india_states.geojson') as f:
        geo = json.load(f)
    return india, states, geo


def glass(fig, height=None):
    """Show a chart with a see-through background and white text, so it sits on the glass card."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E8ECF5', size=13),
        title_font=dict(color='#FFFFFF', size=17),
        legend=dict(bgcolor='rgba(0,0,0,0)', orientation='h', yanchor='top', y=-0.12, x=0),
        hoverlabel=dict(bgcolor='#2E3A4F', font_color='#FFFFFF'),
        margin=dict(l=20, r=20, t=60, b=40))
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID, automargin=True)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, linecolor=GRID, automargin=True)
    if height:
        fig.update_layout(height=height)
    st.plotly_chart(fig, theme=None, width='stretch')


india, states, geo = load_data()

# ---------- header ----------
st.title('🌧️ India Monsoon & Drought Dashboard')
st.caption(f"Official IMD daily rainfall, {india['year'].min()}–{india['year'].max()}. "
           'Monsoon = June to September.')

tab_overview, tab_map, tab_state, tab_about = st.tabs(
    ['📊 Overview', '🗺️ State map', '📍 State history', 'ℹ️ About'])

# ---------- 1. overview ----------
with tab_overview:
    worst = india.loc[india['drought_area_pct'].idxmax()]
    wettest = india.loc[india['departure_pct'].idxmax()]
    latest = india.iloc[-1]
    c1, c2, c3 = st.columns(3)
    c1.metric('Worst drought year', int(worst['year']),
              f"{worst['drought_area_pct']:.0f}% of India in drought", delta_color='off')
    c2.metric('Wettest year', int(wettest['year']),
              f"{wettest['departure_pct']:+.0f}% vs normal", delta_color='off')
    c3.metric(f"Latest monsoon ({int(latest['year'])})", latest['category'],
              f"{latest['departure_pct']:+.0f}% vs normal", delta_color='off')

    fig = px.bar(india, x='year', y='departure_pct', color='category',
                 color_discrete_map=INDIA_COLORS, category_orders={'category': list(INDIA_COLORS)},
                 labels={'departure_pct': '% above or below normal', 'year': '', 'category': ''},
                 title='All-India monsoon rainfall vs normal')
    fig.update_traces(marker_line_color=BORDER, marker_line_width=0.5)
    fig.add_hline(y=0, line_color=LIGHT_PURPLE, line_width=1)
    glass(fig, height=450)

    fig = px.line(india, x='year', y='drought_area_pct', markers=True,
                  labels={'drought_area_pct': "% of India's area", 'year': ''},
                  title='Share of India in drought (20% or more below local normal)')
    fig.update_traces(line_color=LIGHT_PURPLE, marker_color='#9FE2EE')
    glass(fig, height=400)

# ---------- 2. state map ----------
with tab_map:
    year = st.select_slider('Pick a year', options=india['year'].tolist(), value=2002)
    row = india.set_index('year').loc[year]
    year_states = states[states['year'] == year]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric('All-India rainfall', f"{row['monsoon_mm']:.0f} mm")
    m2.metric('Compared with normal', f"{row['departure_pct']:+.1f}%")
    m3.metric('Category (IMD)', row['category'])
    m4.metric('Area in drought', f"{row['drought_area_pct']:.0f}%")

    left, right = st.columns([3, 2])
    with left:
        fig = px.choropleth(
            year_states, geojson=geo, locations='name', featureidkey='properties.name',
            color='category', color_discrete_map=STATE_COLORS,
            category_orders={'category': list(STATE_COLORS)}, hover_name='name',
            hover_data={'departure_pct': ':+.0f', 'monsoon_mm': ':.0f', 'name': False, 'category': False},
            labels={'departure_pct': '% vs normal', 'monsoon_mm': 'Rain (mm)', 'category': ''},
            title=f'Monsoon {year}: each state vs its normal')
        fig.update_geos(visible=False, projection_type='mercator', bgcolor='rgba(0,0,0,0)',
                        lataxis_range=[6, 37.5], lonaxis_range=[67.5, 97.5])
        fig.update_traces(marker_line_color=BORDER, marker_line_width=0.6)
        glass(fig, height=640)
        st.caption('Hover over a state to see its numbers.')
    with right:
        ranked = year_states.sort_values('departure_pct')
        fig = px.bar(ranked, x='departure_pct', y='name', orientation='h', color='category',
                     color_discrete_map=STATE_COLORS,
                     labels={'departure_pct': '% vs normal', 'name': '', 'category': ''},
                     title='Every state, driest to wettest')
        fig.update_traces(marker_line_color=BORDER, marker_line_width=0.5)
        fig.update_layout(showlegend=False)
        glass(fig, height=640)

# ---------- 3. state history ----------
with tab_state:
    names = sorted(states['name'].unique())
    default = names.index('Rajasthan') if 'Rajasthan' in names else 0
    state = st.selectbox('Pick a state', names, index=default)
    history = states[states['name'] == state]
    normal_mm = history['normal_mm'].iloc[0]

    fig = px.bar(history, x='year', y='monsoon_mm', color='category',
                 color_discrete_map=STATE_COLORS, category_orders={'category': list(STATE_COLORS)},
                 labels={'monsoon_mm': 'Monsoon rain (mm)', 'year': '', 'category': ''},
                 title=f'{state}: monsoon rainfall every year')
    fig.update_traces(marker_line_color=BORDER, marker_line_width=0.5)
    fig.add_hline(y=normal_mm, line_dash='dash', line_color=LIGHT_PURPLE,
                  annotation_text=f'Normal: {normal_mm:.0f} mm', annotation_font_color='#FFFFFF')
    glass(fig, height=480)

    driest = history.loc[history['departure_pct'].idxmin()]
    wettest = history.loc[history['departure_pct'].idxmax()]
    st.write(f"Driest monsoon: **{int(driest['year'])}** ({driest['departure_pct']:+.0f}%). "
             f"Wettest: **{int(wettest['year'])}** ({wettest['departure_pct']:+.0f}%).")

# ---------- 4. about ----------
with tab_about:
    st.markdown("""
**Data:** India Meteorological Department (IMD) gridded daily rainfall (0.25°, about 25 km), downloaded with `imdlib`.

**Method**
- Monsoon rainfall = total from June to September.
- All-India categories use IMD's long-period average (868.6 mm) and IMD's thresholds.
- State values = average of all grid squares inside the state, compared with that state's 2000–2020 average.
- A place is "in drought" if it got 20% or more below its own average.

**What I checked:** the method correctly finds India's known drought years (2002, 2009, 2014, 2015),
and the yearly totals are within a few percent of IMD's published figures.

**Limitations**
- "Normal" is the 2000–2020 average, not IMD's official 1971–2020 normal.
- Tamil Nadu gets most of its rain from October to December, so a dry June–September matters less there.
- Boundaries are from Natural Earth and are shown for reference only.
""")