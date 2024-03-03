import requests
from datetime import datetime, timedelta
from skyfield.api import Topos, load
from almanac import *
import matplotlib.pyplot as plt
import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
import csv
import sys
import math


class Analyser:
    def __init__(self, date, location, path):
        self.location = location
        self.file_path = path

        self.today = date
        self.yesterday = date - timedelta(days=1)

        self.date1 = self.yesterday.strftime('%Y/%m/')
        self.date2 = self.yesterday.strftime('%Y%m%d')

    def get_file(self):
        url = "https://www.washetdonker.nl/data/" + self.location + "/" + self.date1 \
              + self.date2 + "_120000_SQM-" + self.location + ".dat"

        print(url)

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            with open(self.file_path, "wb") as file:
                file.write(response.content)
        except:
            print('File not found, check if you are connected to wifi, '
                  'or if you are using a valid URL')
            sys.exit(1)

    def find_location(self):
        with open(self.file_path, 'r') as file:
            for current_line_number, line in enumerate(file, start=1):
                if current_line_number == 9:
                    a, b, c = line.split(',')
                    d, e = a.split(':')
                    self.lat = float(e)
                    self.lon = float(b)

        return float(e), float(b)

    def find_prefix_auto(self, first_msas, spacing):
        start_msas, end_msas = None, None

        with open(self.file_path, 'r') as file:
            for line_num, line in enumerate(file, start=1):
                if line_num >= 36:  # 36 is the first data line in .dat file

                    # Split each line into values using semicolon as the delimiter
                    values = line.strip().split(';')

                    if values and float(values[-1]) > first_msas:
                        if not start_msas:
                            start_msas = line_num
                        end_msas = line_num

                    if line_num == start_msas:
                        original_time_str = values[0]
                        original_time = datetime.strptime(original_time_str, "%Y-%m-%dT%H:%M:%S.%f")

                        new_time = original_time + timedelta(minutes=spacing)
                        begin_time_str = new_time.strftime("%Y-%m-%dT%H:%M")

                    if line_num == end_msas:
                        original_time_str = values[0]
                        original_time = datetime.strptime(original_time_str, "%Y-%m-%dT%H:%M:%S.%f")

                        new_time = original_time - timedelta(minutes=spacing)
                        end_time_str = new_time.strftime("%Y-%m-%dT%H:%M")

        with open(self.file_path, 'r') as file:
            for start_line_number, line in enumerate(file, start=1):
                if line.startswith(begin_time_str):
                    self.start_line = start_line_number

        with open(self.file_path, 'r') as file:
            for end_line_number, line in enumerate(file, start=1):
                if line.startswith(end_time_str):
                    self.end_line = end_line_number

    def read_file(self):
        # Initializing lists
        time = []
        msas = []
        temp = []

        # Iterate through the lines between two prefixes
        with open(self.file_path, 'r') as file:
            for line_num, line in enumerate(file, start=1):
                if self.start_line <= line_num <= self.end_line:  # 36 is the first data line in .dat file

                    values = line.strip().split(';')  # split the line in the separate values

                    second_value = values[1].replace('.000', '')
                    datetime_object = datetime.strptime(second_value, '%Y-%m-%dT%H:%M:%S')
                    time.append(datetime_object.strftime('%Y:%m:%d %H:%M:%S'))

                    third_value = values[2].replace('.000', '')
                    temp.append(float(third_value))

                    sixth_value = values[5].replace('.000', '')
                    msas.append(float(sixth_value))

        return time, temp, msas

    def hourly_data(self, date_objects, data):
        new_hour_datetimes = []
        new_msas = []

        # Iterate through the list and check for a change in the hour
        for i in range(1, len(date_objects)):
            if date_objects[i].hour != date_objects[i - 1].hour:
                new_hour_datetimes.append(date_objects[i])  # , -i
                new_msas.append(data[i])

        #new_hour_datetimes.append(date_objects[-1])  # , len(date_objects) - 1
        #new_msas.append(data[-1])

        return new_hour_datetimes, new_msas

    def csv_file(self, filepath, action, rows, header):
        with open(filepath, action, newline='') as file:
            writer = csv.writer(file)

            # Write header
            if action == 'w':
                writer.writerow(header)

            # Write rows
            writer.writerows(rows)

    def is_moon_above_horizon(self, datetime_input):
        ts = load.timescale()
        observer = Topos(latitude_degrees=self.lat, longitude_degrees=self.lon)
        t = ts.utc(datetime_input.year, datetime_input.month, datetime_input.day,
                   datetime_input.hour - 1, datetime_input.minute, datetime_input.second)

        planets = load('de421.bsp')
        earth, moon = planets['earth'], planets['moon']

        astrometric = (earth + observer).at(t).observe(moon)
        alt, _, _ = astrometric.apparent().altaz()

        if alt.degrees > 0:
            return alt.degrees > 0, alt.degrees  # (alt.degrees*0.1)+14
        else:
            return alt.degrees > 0, 0

    def moon_list(self, date_list):
        moon = []
        moon_alt = []
        moon_frac = []

        year, moth, day = self.today.year, self.today.month, self.today.day
        frac = round(illuminated_fraction_of_moon(year, moth, day), 2)

        for date in date_list:
            moon.append(self.is_moon_above_horizon(date)[0])
            moon_alt.append(self.is_moon_above_horizon(date)[1])
            moon_frac.append(round(illuminated_fraction_of_moon(year, moth, day), 2))
        return moon, moon_alt, moon_frac, frac

    def weather_api(self, start_hour, end_hour, action):
        cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "start_date": self.yesterday.strftime('%Y-%m-%d'),
            "end_date": self.today.strftime('%Y-%m-%d'),
            "hourly": action,
            "timezone": "Europe/Berlin"
        }
        responses = openmeteo.weather_api(url, params=params)

        response = responses[0]

        hourly = response.Hourly()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s"),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s"),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "cloud_cover": hourly.Variables(0).ValuesAsNumpy()
        }

        time = []
        clouds = []

        for i, date, cloud_cover in zip(range(len(hourly_data["date"])), hourly_data["date"],
                                        hourly_data["cloud_cover"]):
            time.append(date)
            cloud_percentage = cloud_cover  # ((cloud_cover/100)*4)+15
            clouds.append(cloud_percentage)

        date1 = self.yesterday.strftime('%Y-%m-%d')
        date2 = self.today.strftime('%Y-%m-%d')

        find_start = datetime.strptime(f'{date1} {start_hour}', '%Y-%m-%d %H:%M:%S')
        find_end = datetime.strptime(f'{date2} {end_hour}', '%Y-%m-%d %H:%M:%S')

        start = time.index(find_start - timedelta(hours=1))
        end = time.index(find_end - timedelta(hours=1))

        start2 = time.index(find_start)
        end2 = time.index(find_end)

        stripped_cloud_cover = clouds[start:end + 1]
        stripped_time = time[start2:end2 + 1]

        if any(math.isnan(x) for x in stripped_cloud_cover):
            print("Failed to retrieve cloud data")

        return stripped_cloud_cover, stripped_time

    def second_weather_api(self, start_hour, end_hour):
        API_key = '8b585636ab718507152e1b4356c60012'
        lat = self.lat
        lon = self.lon

        start = start_hour
        end = end_hour

        url = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&&appid={API_key}'

        response = requests.get(url)
        data = response.json()
        return data


        return stripped_cloud_cover, stripped_time
        
