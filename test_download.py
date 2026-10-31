import imdlib as imd

# download daily rainfall for every year from 2000 to 2025 into data/rain/
imd.get_data('rain', 2000, 2025, fn_format='yearwise', file_dir='data')
print("Download finished")