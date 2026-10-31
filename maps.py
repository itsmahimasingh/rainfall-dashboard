"""Step 4: maps of India showing where the monsoon was above or below normal."""
import os
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
from matplotlib.patches import Patch

# ---------- state boundaries (downloaded once, then saved) ----------
STATES_FILE = 'data/india_states.geojson'
if not os.path.exists(STATES_FILE):
    url = 'https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_1_states_provinces.zip'
    world = gpd.read_file(url)
    world[world['admin'] == 'India'][['name', 'geometry']].to_file(STATES_FILE, driver='GeoJSON')
states = gpd.read_file(STATES_FILE)
india_outline = states.dissolve()

# ---------- rainfall ----------
rain = xr.open_dataset('data/monthly_rain.nc')['rain']
monsoon = rain.where(rain['time'].dt.month.isin([6, 7, 8, 9]), drop=True)
monsoon = monsoon.groupby('time.year').sum(skipna=False)
monsoon = monsoon.coarsen(lat=2, lon=2, boundary='trim').mean()      # about 50 km squares

normal = monsoon.sel(year=slice(2000, 2020)).mean('year')
departure = ((monsoon / normal - 1) * 100).where(normal > 50).clip(-99, 99)

# IMD's five rainfall categories
levels = [-100, -60, -20, 20, 60, 100]
colors = ['#8C3B1F', '#E3A857', '#C9E2BC', '#7FB3D5', '#2B6CB0']
labels = ['Large deficient (below -60%)', 'Deficient (-60% to -20%)',
          'Normal (-20% to +20%)', 'Excess (+20% to +60%)', 'Large excess (above +60%)']

summary = pd.read_csv('data/monsoon_summary.csv').set_index('year')
years = [2002, 2009, 2019]

# ---------- draw ----------
fig, axes = plt.subplots(1, 3, figsize=(16, 6.5))
for ax, year in zip(axes, years):
    departure.sel(year=year).plot(ax=ax, levels=levels, colors=colors, add_colorbar=False)
    states.boundary.plot(ax=ax, color='#555555', linewidth=0.35)     # state borders
    india_outline.boundary.plot(ax=ax, color='#222222', linewidth=0.8)  # country outline
    ax.set_xlim(67.5, 97.5)
    ax.set_ylim(6.5, 37.5)
    ax.set_aspect('equal')
    ax.axis('off')
    row = summary.loc[year]
    ax.set_title(f"{year}\nAll-India {row['departure_pct']:+.0f}%  ·  {row['category']}", fontsize=13)

fig.suptitle('Where the monsoon failed: two drought years vs a wet year', fontsize=17, fontweight='bold')
fig.legend(handles=[Patch(color=c, label=l) for c, l in zip(colors, labels)],
           loc='lower center', ncol=5, frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.03))
fig.text(0.5, -0.01, 'Data: IMD gridded daily rainfall (0.25°), June–September. '
         'Normal = 2000–2020 average for each location. State boundaries: Natural Earth.',
         ha='center', fontsize=9, color='grey')
fig.subplots_adjust(top=0.85, bottom=0.12, wspace=0.02)
fig.savefig('charts/monsoon_maps.png', dpi=150, bbox_inches='tight')
print('Saved charts/monsoon_maps.png')