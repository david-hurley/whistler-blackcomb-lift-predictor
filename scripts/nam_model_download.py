# ----------------------------------------------------
# downloads historical model analysis data from North American Mesoscale (NAM) model for wind speed and direction near a specific location 
#
# author David Hurley
# email hurleyldave@gmail.com
# date November 04 2020
# ----------------------------------------------------

import json
import pandas as pd
import os
from helper import url_paths, download

# read user inputs
with open('nam_download_inputs.json', 'r') as f:
    inputs = json.load(f)

# format list of dates to download NAM data for
dates_to_download = pd.date_range(inputs['start_date'], inputs['end_date'])
months_to_download = [1, 2, 3, 4, 5, 11, 12]  # only scrape months during ski season
dates_to_download = dates_to_download[dates_to_download.month.isin(months_to_download)]

# function to create list of url paths
url_paths = url_paths(dates_to_download)  # commment out once list of paths generated

# create dataframe of url paths
df_url_paths = pd.DataFrame(url_paths)
df_url_paths.columns = ['url_paths']

# export url paths to csv
df_url_paths.to_csv(os.path.join(inputs['relative_data_path'], 'nam_data_url_paths.csv'), index=False)

# download model wind speed and direction data
df_output = download(os.path.join(inputs['relative_data_path'], 'nam_data_url_paths.csv'), inputs['requested_lat'], inputs['requested_lon'], inputs['pressure_levels'])

# export data to gzip compressed csv
df_output.to_csv(os.path.join(inputs['relative_data_path'], 'nam_data.csv.gz'), index=False, compression='gzip')