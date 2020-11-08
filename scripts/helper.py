# ----------------------------------------------------
# scrapes historical Avalanche Canada conditions and forecast conditions and problem text
#
# author David Hurley
# email hurleyldave@gmail.com
# date November 04 2020
# ----------------------------------------------------

import pandas as pd
import requests
import urllib.request
import os
import numpy as np
import pygrib

from progress.bar import Bar
from bs4 import BeautifulSoup

def compute_great_circle_distance(lat_A, lon_A, lat_B, lon_B):
    """ Compute distance between lat/lon locations A and B on great circle"""

    lat1, lon1 = np.radians([np.float64(lat_A), np.float64(lon_A)])
    lat2, lon2 = np.radians([lat_B, lon_B])
    a = np.sin((lat2 - lat1) / 2.0) ** 2 + np.cos(lat1) * \
        np.cos(lat2) * np.sin((lon2 - lon1) / 2.0) ** 2
    earth_radius_km = 6371

    return earth_radius_km * 2 * np.arcsin(np.sqrt(a))

def url_paths(dates):
    """ Create url paths for all grb files to be downloaded """

    # empty list for url paths
    url_path_list = []

    # url path to root folder grb files
    grb_base_url = 'https://www.ncei.noaa.gov/data/north-american-mesoscale-model/access/historical/analysis/{}/{}'

    # start progress bar and loop through dates
    with Bar('Downloading NAM Data URL Paths', max=len(dates), suffix='%(percent)d%%') as bar:

        for date in dates:

            # url of grb file
            yyyymm = date.strftime('%Y') + date.strftime('%m')
            yyyymmdd = yyyymm + date.strftime('%d')

            # get page html
            response = requests.get(grb_base_url.format(yyyymm, yyyymmdd))

            # if the page exists then scrape the filenames
            if response.status_code == 200:

                soup = BeautifulSoup(response.text, 'html.parser')  # page html

                text = soup.findAll('a')  # get all html under <a> </a> tag

                grb_filenames = [a['href'] for a in text]   # grb filenames are associated with "href" tag

                grb_filenames = ([a for a in grb_filenames if a.endswith('000.grb') | a.endswith('000.grb2')])  # keep only files for the 000 forecast hour

                # if both .grb and .grb2 version of file exist keep only .grb2
                if len(grb_filenames) > 4:

                    grb_filenames = [file for file in grb_filenames if '.grb2' in file]

                # create url path to grb file
                url_paths = [os.path.join(grb_base_url.format(yyyymm, yyyymmdd), a) for a in grb_filenames]

                url_path_list.append(url_paths)

            bar.next()

    url_path_list = [url for sublist in url_path_list for url in sublist]

    return url_path_list

def download(url_paths_csv, lat_site, lon_site, press_levels):
    """ Download NAM historical forecast data for paths in url csv for 5 nearest grid cells at a specified pressure levels """

    df_grb = pd.read_csv(url_paths_csv, dtype='str')

    # empty dataframe to store NAM model data
    df_temp = pd.DataFrame(columns=['time', 'lat', 'lon', 'dist_to_pnt_interest', 'pressure_height', 'u', 'v', 'wnd_spd', 'wnd_dir'])
    df_output = pd.DataFrame(columns=['time', 'lat', 'lon', 'dist_to_pnt_interest', 'pressure_height', 'u', 'v', 'wnd_spd', 'wnd_dir'])
    
    with Bar('Downloading NAM Data', max=len(df_grb), suffix='%(percent)d%%') as bar:

        for i, url in enumerate(df_grb.url_paths):

            timestamp = '-'.join(url.split('_')[2:4])  # create timestamp of each forecast period from url
            file_format = url.split('.')[-1]
            temp_filename = timestamp + '.' + file_format  # for opening the file and error tracking
            pressure_levels = list(map(int, press_levels.values()))  # pressure levels to extract wind data for

            # download each grb file for NAM model 
            urllib.request.urlretrieve(url, temp_filename)

            # wait until file exists before going ahead
            while not os.path.exists(temp_filename):

                time.sleep(0.5)

            if os.path.isfile(temp_filename):

                grb_data = pygrib.open(temp_filename)

                try:
                    u_data_list = grb_data.select(name='U component of wind')
                    v_data_list = grb_data.select(name='V component of wind')

                    if file_format == 'grb2':
                        pressure_levels = pressure_levels * 10

                    for pressure in pressure_levels:
                        index = [i for i, s in enumerate(u_data_list) if str(pressure) in str(s)]

                        # extract U and V data
                        temp_u_data, temp_lats, temp_lons = u_data_list[index[0]].data(lat1=float(lat_site)-1, lat2=float(lat_site)+1, lon1=float(lon_site)-1, lon2=float(lon_site)+1)
                        temp_v_data, temp_lats, temp_lons = v_data_list[index[0]].data(lat1=float(lat_site)-1, lat2=float(lat_site)+1, lon1=float(lon_site)-1, lon2=float(lon_site)+1)

                        # find nearest model grid cells
                        dist = compute_great_circle_distance(temp_lats, temp_lons, float(lat_site), float(lon_site))
                        dist_index = list(dist.argsort()[0:5])

                        # assign output to temporary dataframe
                        df_temp['time'] = [timestamp] * len(dist_index)
                        df_temp['pressure_height'] = [pressure] * len(dist_index)
                        df_temp['dist_to_pnt_interest'] = dist[dist_index]
                        df_temp['lat'] = temp_lats[dist_index]
                        df_temp['lon'] = temp_lons[dist_index]
                        df_temp['u'] = temp_u_data[dist_index]
                        df_temp['v'] = temp_v_data[dist_index]
                        df_temp['wnd_spd'] = np.sqrt(temp_u_data[dist_index]**2 + temp_v_data[dist_index]**2)
                        df_temp['wnd_dir'] = np.mod(180 + np.rad2deg(np.arctan(temp_u_data[dist_index], temp_v_data[dist_index])), 360)

                        # combine dataframes to final
                        df_output = pd.concat([df_output, df_temp])
                except:
                    pass

            os.remove(temp_filename)
            bar.next()

    return df_output


