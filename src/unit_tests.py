import data_collector as dc
import numpy as np

timestamp = dc.get_timestamp_string()
print(f"Time: {timestamp}")

pm_25, pm_10 = dc.get_particulate_readings()
print(f"PM2.5: {pm_25} PM10: {pm_10}")

temp, humidity, pressure = dc.collect_weather_data()
print(f"Temp: {temp:.1f} Humidity: {humidity:.1f} Pressure: {pressure:.1f}")

pm_arr = np.arange(0, 605, 0.1)
for idx in range(pm_arr.shape[0]):
    dc.compute_aqi(pm_arr[idx], "2.5")
    dc.compute_aqi(pm_arr[idx], "10")
