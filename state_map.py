"""Step 6: state-level monsoon map in infographic style."""
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.patches import Patch

YEAR = 2019# change this to make a map for any year

states = gpd.read_file('data/india_states.geojson')

# 1) Monsoon (June-September) total for every 25 km grid square and year
rain = xr.open_dataset('data/monthly_rain.nc')['rain']
monsoon = rain.where(rain['time'].dt.month.isin([6, 7, 8, 9]), drop=True)
monsoon = monsoon.groupby('time.year').sum(skipna=False)
grid = monsoon.to_dataframe(name='mm').reset_index().dropna(subset=['mm'])

# 2) Find which state each grid square falls inside
cells = grid[['lat', 'lon']].drop_duplicates()
cells = gpd.GeoDataFrame(cells, geometry=gpd.points_from_xy(cells['lon'], cells['lat']), crs=states.crs)
cells = gpd.sjoin(cells, states[['name', 'geometry']], predicate='within')[['lat', 'lon', 'name']]
grid = grid.merge(cells, on=['lat', 'lon'])

# 3) State average for each year, and % vs the state's own 2000-2020 average
grid['w'] = np.cos(np.deg2rad(grid['lat']))              # squares further north are smaller
grid['mm_w'] = grid['mm'] * grid['w']
sums = grid.groupby(['name', 'year'])[['mm_w', 'w']].sum()
by_state = (sums['mm_w'] / sums['w']).rename('monsoon_mm').reset_index()
normal = by_state[by_state['year'].between(2000, 2020)].groupby('name')['monsoon_mm'].mean()
by_state['normal_mm'] = by_state['name'].map(normal)
by_state['departure_pct'] = (by_state['monsoon_mm'] / by_state['normal_mm'] - 1) * 100
by_state.round(1).to_csv('data/state_monsoon.csv', index=False)

# 4) IMD's five categories and their colours (purple = dry, honeydew = normal, cyan = wet)
labels = ['Large deficient', 'Deficient', 'Normal', 'Excess', 'Large excess']
ranges = ['below -60%', '-60% to -20%', '-20% to +20%', '+20% to +60%', 'above +60%']
colors = dict(zip(labels, ['#7B75C9', '#BDB9EA', '#EAF7ED', '#9FE2EE', '#3FA7C4']))
year_data = by_state[by_state['year'] == YEAR].copy()
year_data['category'] = pd.cut(year_data['departure_pct'], bins=[-np.inf, -60, -20, 20, 60, np.inf],
                               labels=labels, right=False).astype(str)
mapped = states.merge(year_data, on='name', how='left')
mapped['color'] = mapped['category'].map(colors).fillna('#E0E0E0')     # grey = no data

# 5) Draw: map on the left, ranked bars on the right
fig = plt.figure(figsize=(16, 10))
grid_spec = fig.add_gridspec(1, 2, width_ratios=[3, 2], wspace=0.25, top=0.82, bottom=0.12)
ax = fig.add_subplot(grid_spec[0])
bars = fig.add_subplot(grid_spec[1])

mapped.plot(ax=ax, color=mapped['color'], edgecolor='#A9B4D9', linewidth=0.6)
areas = mapped.to_crs(3857).area
for (_, row), area in zip(mapped.iterrows(), areas):
    if pd.notna(row['departure_pct']) and area > 3.5e10:       # skip states too small for a label
        point = row.geometry.representative_point()
        dark = row['category'] in ('Large deficient', 'Large excess')
        ax.text(point.x, point.y, f"{int(round(row['departure_pct'])):+d}%", ha='center', va='center',
                fontsize=8.5, fontweight='bold', color='white' if dark else '#3A3A5C')
ax.set_xlim(67.5, 97.5)
ax.set_ylim(6.5, 37.5)
ax.set_aspect('equal')
ax.axis('off')
ax.legend(handles=[Patch(facecolor=colors[l], edgecolor='#A9B4D9', label=f'{l} ({r})') for l, r in zip(labels, ranges)],
          loc='upper center', bbox_to_anchor=(0.5, 0.0), ncol=3, frameon=False, fontsize=9)

ranked = year_data.sort_values('departure_pct')
bars.barh(ranked['name'], ranked['departure_pct'], color=ranked['category'].map(colors),
          edgecolor='#A9B4D9', linewidth=0.5)
bars.axvline(0, color='#5A54B0', linewidth=0.8)
bars.set_title('Every state, driest to wettest', fontsize=13, loc='left', color='#5A54B0')
bars.set_xlabel('% above or below the state\'s normal')
bars.tick_params(axis='y', labelsize=8)
for side in ['top', 'right']:
    bars.spines[side].set_visible(False)

# 6) Infographic-style headline
india = pd.read_csv('data/monsoon_summary.csv').set_index('year').loc[YEAR]
fig.text(0.05, 0.94, f'Monsoon {YEAR}: which states went dry?', fontsize=24, fontweight='bold', color='#5A54B0')
fig.text(0.05, 0.895, f"All-India rainfall was {india['departure_pct']:+.0f}% vs normal ({india['category']}). "
         'Number on each state = % above or below its own 2000–2020 average.', fontsize=12, color='#555555')
fig.text(0.05, 0.03, 'Data: IMD gridded daily rainfall (0.25°), June–September. '
         'Boundaries: Natural Earth, shown for reference only.', fontsize=9, color='grey')

fig.savefig(f'charts/state_map_{YEAR}.png', dpi=150)
print(f'Saved charts/state_map_{YEAR}.png')