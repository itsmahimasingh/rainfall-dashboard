"""Step 3: two charts from the monsoon summary table."""
import os
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('data/monsoon_summary.csv')
os.makedirs('charts', exist_ok=True)

# One colour per IMD category: brown = dry, green = normal, blue = wet
colors = {'Deficient': '#B5562B', 'Below normal': '#E3A857', 'Normal': '#8DB580',
          'Above normal': '#5FA8C8', 'Excess': '#2B6CB0'}

# Chart 1: % above or below normal, every year
fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(df['year'], df['departure_pct'], color=df['category'].map(colors))
ax.axhline(0, color='black', linewidth=0.8)
ax.axhspan(-4, 4, color='grey', alpha=0.1)                  # IMD's "normal" band
ax.set_title('All-India monsoon rainfall vs normal, 2000-2025')
ax.set_ylabel('% above or below normal')
for c, col in colors.items():                               # legend
    ax.bar(0, 0, color=col, label=c)
ax.legend(frameon=False, ncol=5, loc='lower center', bbox_to_anchor=(0.5, -0.25))
ax.set_xlim(1999, 2026)
fig.tight_layout()
fig.savefig('charts/monsoon_departure.png', dpi=150)

# Chart 2: how much of India was in drought each year
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df['year'], df['drought_area_pct'], marker='o', color='#B5562B')
worst = df.nlargest(4, 'drought_area_pct')                  # label the 4 worst years
for _, r in worst.iterrows():
    ax.annotate(int(r['year']), (r['year'], r['drought_area_pct']),
                textcoords='offset points', xytext=(0, 8), ha='center')
ax.set_title('Share of India in monsoon drought (20% or more below local normal)')
ax.set_ylabel('% of India\'s area')
ax.set_ylim(0, 70)
fig.tight_layout()
fig.savefig('charts/drought_area.png', dpi=150)

print('Saved 2 charts in the charts folder')