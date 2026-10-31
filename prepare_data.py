"""Step 1: turn 26 years of daily rainfall into monthly totals (smaller and faster to use)."""
import imdlib as imd
import xarray as xr

months = []
for year in range(2000, 2026):
    ds = imd.open_data('rain', year, year, 'yearwise', 'data').get_xarray()
    rain = ds['rain'].where(ds['rain'] >= 0)                # treat missing values (-999) as empty
    monthly = rain.resample(time='MS').sum(skipna=False)    # total rain in each month, in mm
    months.append(monthly.astype('float32'))
    print(year, 'done')

all_months = xr.concat(months, dim='time')                 # join all years into one
all_months.to_dataset(name='rain').to_netcdf('data/monthly_rain.nc')
print(all_months)