from module import *

location_list_all = ['Akkrum', 'Aldeboarn', 'Ameland-Natuurcentrum-Nes', 'Borkum', 'Borkum-Ostland', 'DeZilk', 'Gorredijk', 'Groningen-DeHeld', 'Heerenveen-Station', 'Heerenveen01', 'Hippolytushoef', 'Katlijk', 'Lauwersoog', 'Lauwersoog-haven', 'Leiden-Sterrewacht', 'Lochem', 'Noordpolderzijl', 'Oostkapelle', 'Rijswijk', 'Schiermonnikoog-dorp', 'Sellingen', 'Texel', 'Tolbert', 'Vlieland-Oost', 'Weerribben', 'Westhoek', 'ZwarteHaan', 'tZandt']
pollution_list_all = [0.35, 0.35, 0.25, 0.77, 0.36, 13.1, 1.96, 5.7, 5.7, 5.7, 2, 2.39, 0.68, 0.68, 36.2, 3.1, 0.61, 2.39, 110.1, 0.4, 1.06, 1.48, 2.58, 0.37, 11.7, 1.15, 0.87, 1.29]

location_list = ['Noordpolderzijl']
pollution_list = [0.61, 0.36, 110.1, 121.4]

days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


counter = 300

h = 2023
for i in range(1):   # Stations
    for j in range(9, 12+1):   # Months
        for k in range(days_in_month[j-1]):   # Days
            try:
                print(j)
                print(k)

                date = datetime(h, j, k+1)
                print(date)
                location = location_list[i]
                file = "data.dat"
                print(location)
                yesterday = date - timedelta(days=1)

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
                frac = frac * 100

                new_msas_datetimes, new_msas = WHD.hourly_data(date_objects, msas_data)

                first_datetime = new_msas_datetimes[0]
                last_datetime = new_msas_datetimes[-1]

                # Format time component of the datetime objects
                first_hour_str = first_datetime.replace(minute=0, second=0, microsecond=0).strftime('%H:%M:%S')
                last_hour_str = last_datetime.replace(minute=0, second=0, microsecond=0).strftime('%H:%M:%S')

                clouds, cloud_time = WHD.weather_api(first_hour_str, last_hour_str, "cloud_cover")

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
                ax3.fill_between(moon_date_objects, 0, moon_alt, color='gold', alpha=(frac / 100) * 0.75)

                # Plot temp data
                ax4.plot(date_objects, temp_data, color='green', linewidth=1, label='temp')

                # Plot MSAS data
                ax.plot(date_objects, msas_data, color='red', linewidth=2, label='MSAS')

                # Plot clouds data
                ax2.scatter(cloud_time, clouds, color='blue', marker='o', s=25, label='clouds')
                ax2.plot(cloud_time, clouds, linestyle='--', color='blue')

                # Set the title of the plot
                plt.title(f'SQM-{location}, lat: {lat}, lon: {lon}', loc='left')
                plt.title(f'moon: {str(frac)}%, max {round(max(moon_alt), 1)}°', loc='right')

                ax.set_xlabel(
                    f'{int(yesterday.strftime("%d"))} {(yesterday.strftime("%b"))} {(yesterday.strftime("%Y"))} → '
                    f'{int(date.strftime("%d"))} {(date.strftime("%b"))} {(date.strftime("%Y"))}', loc='left')

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
                ax.set_xticklabels(
                    ['17', '18', '19', '20', '21', '22', '23', '00', '01', '02', '03', '04', '05', '06', '07', '08', '09'])

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
                ax2.legend(lines + lines2 + lines3 + lines4, labels + labels2 + labels3 + labels4, loc='upper right')

                '''
                # Line at 00:00
                ax.vlines(datetime(int(date.strftime("%Y")),
                                      int(date.strftime("%m")),
                                      int(date.strftime("%d"))), 14, 22, colors='k', linestyles='solid')
                '''

                ax.grid()
                plt.savefig(f'C:\\Users\\Tim\\Desktop\\Code\\Python\\Wegmelkweg 1\\V5\\animatie\\v6\\{counter}', dpi=400)
                counter = counter+1

                #plt.show()
            except:
                continue


