from module import *

location_list = ['Akkrum', 'Aldeboarn', 'Ameland-Natuurcentrum-Nes', 'Borkum', 'Borkum-Ostland', 'DeZilk', 'Gorredijk', 'Groningen-DeHeld', 'Heerenveen-Station', 'Heerenveen01', 'Hippolytushoef', 'Katlijk', 'Lauwersoog', 'Lauwersoog-haven', 'Leiden-Sterrewacht', 'Lochem', 'Noordpolderzijl', 'Oostkapelle', 'Rijswijk', 'Schiermonnikoog-dorp', 'Sellingen', 'Texel', 'Tolbert', 'Vlieland-Oost', 'Weerribben', 'Westhoek', 'ZwarteHaan', 'tZandt']
pollution_list = [0.35, 0.35, 0.25, 0.77, 0.36, 13.1, 1.96, 5.7, 5.7, 5.7, 2, 2.39, 0.68, 0.68, 36.2, 3.1, 0.61, 2.39, 110.1, 0.4, 1.06, 1.48, 2.58, 0.37, 11.7, 1.15, 0.87, 1.29]
days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
h = 2023

for i in range(len(location_list)):   # Stations
    for j in range(1, 12+1):   # Months
        for k in range(days_in_month[j-1]):   # Days
                try:

                    date = datetime(h, j, k+1)
                    location = location_list[i]
                    file = "data.dat"
                    WHD = Analyser(date, location, file)
    
                    WHD.get_file()
                    WHD.find_prefix_auto(14, 40)
                    lat, lon = WHD.find_location()
    
                    time_data, temp_data, msas_data = WHD.read_file()
                    date_objects = [datetime.strptime(timestamp, '%Y:%m:%d %H:%M:%S') for timestamp in time_data]
    
                    new_msas_datetimes, new_msas = WHD.hourly_data(date_objects, msas_data)
                    new_temp_datetimes, new_temp = WHD.hourly_data(date_objects, temp_data)
    
                    is_moon, moon_alt, moon_frac, frac = WHD.moon_list(new_msas_datetimes)
                    frac = frac*100
    
                    first_datetime = new_msas_datetimes[0]
                    last_datetime = new_msas_datetimes[-1]
                    first_hour_str = first_datetime.replace(minute=0, second=0, microsecond=0).strftime('%H:%M:%S')
                    last_hour_str = last_datetime.replace(minute=0, second=0, microsecond=0).strftime('%H:%M:%S')
                    clouds, cloud_time = WHD.weather_api(first_hour_str, last_hour_str, "cloud_cover")
                    clouds_2, cloud_time_2 = WHD.weather_api(first_hour_str, last_hour_str, "cloud_cover_low")
                    clouds_3, cloud_time_3 = WHD.weather_api(first_hour_str, last_hour_str, "cloud_cover_mid")
                    clouds_4, cloud_time_4 = WHD.weather_api(first_hour_str, last_hour_str, "cloud_cover_high")
    
                    maan_fractie = [frac] * len(new_msas)
    
                    moon_alt_rounded = [round(num) for num in moon_alt]
                    moon_frac_rounded = [round(num) for num in maan_fractie]
                    clouds_rounded_tot = [round(num) for num in clouds]
                    clouds_rounded_low = [round(num) for num in clouds_2]
                    clouds_rounded_mid = [round(num) for num in clouds_3]
                    clouds_rounded_high = [round(num) for num in clouds_4]
    
                    pollution = pollution_list[i]
                    day = k+1
    
                    Jaar = [h] * len(new_msas)
                    Maand = [j] * len(new_msas)
                    Dag = [day] * len(new_msas)
                    Locatie = [location_list[i]] * len(new_msas)
                    Vervuiling = [pollution_list[i]] * len(new_msas)
    
    
                    rows = zip(Locatie,Jaar,Maand,Dag,Vervuiling,new_msas,new_temp,is_moon,moon_alt_rounded,
                               moon_frac_rounded,cloud_time,clouds_rounded_tot,clouds_rounded_low,clouds_rounded_mid,clouds_rounded_high)
                    header = ['Location', 'Year', 'Month', 'Day', 'Ratio', 'MSAS', 'Temp', 'Moon', 'Moon_alt', 'Moon_frac',
                              'Cloud_time', 'Clouds', 'Clouds_low', 'Clouds_mid', 'Clouds_high']
                    WHD.csv_file('4loc_cloud_types_2.csv', 'a', rows, header)
                except:
                    print("failed to add data to csv")


