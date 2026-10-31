"""Step 2: monsoon rainfall for each year, and which years were droughts."""
import numpy as np
import pandas as pd
import xarray as xr

rain = xr.open_dataset('data/monthly_rain.nc')['rain']

# Monsoon = June to September. Add up those 4 months for each year.
monsoon = rain.where(rain['time'].dt.month.isin([6, 7, 8, 9]), drop=True)
monsoon = monsoon.groupby('time.year').sum(skipna=False)    # mm, per year, per grid square

# "Normal" for each grid square = its average monsoon in 2000-2020
normal = monsoon.sel(year=slice(2000, 2020)).mean('year')
land = normal.notnull()                                      # squares inside India

# Squares further north are slightly smaller, so weight them by cos(latitude)
weights = np.cos(np.deg2rad(rain['lat']))

# 1) All-India monsoon rain and % departure from normal
india = monsoon.weighted(weights).mean(['lat', 'lon'])
india_normal = 868.6   # IMD's official all-India monsoon normal (LPA, 1971-2020), in mm
departure = (india / india_normal - 1) * 100

# 2) % of India's area in drought (20% or more below its own normal)
in_drought = (monsoon <= 0.8 * normal).astype(float).where(land)
drought_area = in_drought.weighted(weights).mean(['lat', 'lon']) * 100

# 3) IMD's categories for the all-India monsoon
def category(p):
    if p < -10:  return 'Deficient'
    if p < -4:   return 'Below normal'
    if p <= 4:   return 'Normal'
    if p <= 10:  return 'Above normal'
    return 'Excess'

table = pd.DataFrame({
    'year': monsoon['year'].values,
    'monsoon_mm': india.values.round(0),
    'departure_pct': departure.values.round(1),
    'drought_area_pct': drought_area.values.round(1),
})
table['category'] = table['departure_pct'].apply(category)
table.to_csv('data/monsoon_summary.csv', index=False)
print(table.to_string(index=False))