from module import *
import time

a = time.time()

date = datetime(2023, 12, 14) # TODO 22 december Rijswijk is goede demsonstratie voor bewlokingsdata
location = 'ZwarteHaan'
file = "data.dat"

yesterday = date-timedelta(days=1)

WHD = Analyser(date, location, file)

WHD.get_file()
WHD.find_prefix_auto(14, 0)
lat, lon = WHD.find_location()

time_data, temp_data, msas_data = WHD.read_file()
date_objects = [datetime.strptime(timestamp, '%Y:%m:%d %H:%M:%S') for timestamp in time_data]


start_date = datetime(yesterday.year, yesterday.month, yesterday.day, 17)
moon_long_date_objects = [start_date + timedelta(seconds=42 * i) for i in range(1286)]


moon_date_objects = moon_long_date_objects[::20]

is_moon, moon_alt, moon_frac, frac = WHD.moon_list(moon_date_objects)
frac = frac*100


new_msas_datetimes, new_msas = WHD.hourly_data(date_objects, msas_data)

first_datetime = new_msas_datetimes[0]
last_datetime = new_msas_datetimes[-1]

# Format time component of the datetime objects
first_hour_str = first_datetime.replace(minute=0, second=0, microsecond=0).strftime('%H:%M:%S')
last_hour_str = last_datetime.replace(minute=0, second=0, microsecond=0).strftime('%H:%M:%S')

clouds, cloud_time = WHD.weather_api(first_hour_str, last_hour_str, "cloud_cover")
clouds_2, cloud_time_2 = WHD.weather_api(first_hour_str, last_hour_str, "cloud_cover_low")
clouds_3, cloud_time_3 = WHD.weather_api(first_hour_str, last_hour_str, "cloud_cover_mid")
clouds_4, cloud_time_4 = WHD.weather_api(first_hour_str, last_hour_str, "cloud_cover_high")




# Initialize plot
fig, ax = plt.subplots(figsize=(10, 4))
fig.subplots_adjust(right=0.75)

# Create multiple y axes
ax2 = ax.twinx()
ax3 = ax.twinx()
ax4 = ax.twinx()

ax3.spines.right.set_position(("axes", 1.15))
ax4.spines.right.set_position(("axes", 1.3))

# Plot moon data
ax3.plot(moon_date_objects, moon_alt, color='gold', linewidth=2, label='moon')
ax3.fill_between(moon_date_objects, 0, moon_alt, color='gold', alpha=(frac/100)*0.75)

# Plot temp data
ax4.plot(date_objects, temp_data, color='green', linewidth=1, label='temp')

# Plot MSAS data
ax.plot(date_objects, msas_data, color='red', linewidth=2, label='MSAS')

# Plot clouds data
ax2.scatter(cloud_time, clouds, color='blue', marker='o', s=25, label='clouds')
ax2.plot(cloud_time, clouds, linestyle='--', color='blue')


# Set the title of the plot
plt.title(f'SQM-{location}, lat: {lat}, lon: {lon}', loc='left')
plt.title(f'moon: {str(frac)}%, max {round(max(moon_alt),1)}°', loc='right')




ax.set_xlabel(f'{int(yesterday.strftime("%d"))} {(yesterday.strftime("%b"))} '
              f'{(yesterday.strftime("%Y"))} → 'f'{int(date.strftime("%d"))} '
              f'{(date.strftime("%b"))} {(date.strftime("%Y"))}', loc='left')


ax.set_ylabel('MSAS')
ax2.set_ylabel('Cloud coverage (percentage)')
ax3.set_ylabel('Moon altitude (degrees)')
ax4.set_ylabel('Temperature (Celsius)')


# Set the ticks of the x ax
start_date = datetime(int(yesterday.strftime("%Y")),
                      int(yesterday.strftime("%m")),
                      int(yesterday.strftime("%d")), 17)
hours = range(17)
x_ticks = [start_date + timedelta(hours=hour) for hour in hours]

ax.set_xticks(x_ticks)
ax.set_xticklabels(['17','18','19','20','21','22','23','00',
                    '01','02','03','04','05','06','07','08','09'])


# Set the ticks of the y ax
y_ticks = [14, 16, 18, 20, 22]
y2_ticks = [0, 25, 50, 75, 100]
y3_ticks = [0, 10, 20, 30, 40, 50, 60]
y4_ticks = [-10, -5, 0, 5, 10, 15, 20]

ax.set_yticks(y_ticks)
ax2.set_yticks(y2_ticks)
ax3.set_yticks(y3_ticks)
ax4.set_yticks(y4_ticks)

lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
lines3, labels3 = ax3.get_legend_handles_labels()
lines4, labels4 = ax4.get_legend_handles_labels()
ax2.legend(lines + lines2 + lines3 + lines4, labels +
           labels2 + labels3 + labels4, loc='upper right')

ax.grid()
plt.savefig("C:\\Users\\Tim\\Downloads\\Verslag ZwarteHaan geen maan", dpi=600)

b = time.time()
print(f'time = {b-a}')

plt.show()