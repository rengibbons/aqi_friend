import numpy as np

import data_collector as dc
import sql_utils as su

# Check timestamp
timestamp = dc.get_timestamp_string()
print(f"Time: {timestamp}")

# Check PM readings
pm_25, pm_10 = dc.get_particulate_readings()
print(f"PM2.5: {pm_25} PM10: {pm_10}")

# Check SenseHat readings
temp, humidity, pressure = dc.collect_weather_data()
print(f"Temp: {temp:.1f} Humidity: {humidity:.1f} Pressure: {pressure:.1f}")

# Log to SQLite database
su.create_table()
air_quality = ("2021-01-16 20:56:05", 71.1, 32.4, 55.4, 11.2, 9.3, 33)
# air_quality = (timestamp, temp, pressure, humidity, pm_25, pm_10, 999)
su.insert_air_quality_reading(air_quality)
df = su.select_all_table_data()
su.close_db_connection()
print(df.head())

# Check extremes of aqi
pm_arr = np.arange(0, 605, 0.1)
for idx in range(pm_arr.shape[0]):
    dc.compute_aqi(pm_arr[idx], "2.5")
    dc.compute_aqi(pm_arr[idx], "10")

