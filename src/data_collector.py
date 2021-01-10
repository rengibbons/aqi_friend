"""
Author: Ren Gibbons
Email: gibbons.ren@gmail.com
Date Created: 2021-01-09

Helpful reference links:
    https://hackernoon.com/how-to-measure-particulate-matter-with-a-raspberry-pi-75faa470ec35
    https://gist.github.com/kadamski/92653913a53baf9dd1a8
    https://cdn-reichelt.de/documents/datenblatt/X200/SDS011-DATASHEET.pdf
    https://forum.airnowtech.org/t/the-aqi-equation/169
"""
from datetime import datetime
from pytz import timezone
import serial

import numpy as np
from sense_hat import SenseHat

from aqi_tables import PM_25_AQI_SCALE, PM_10_AQI_SCALE


sense = SenseHat()
serial_device = serial.Serial()

serial_device.port = "/dev/ttyUSB0"
serial_device.baudrate = 9600
serial_device.open()

PM_PROTOCAL_SIZE = 10
PM_25_IND = (2, 3)
PM_10_IND = (4, 5)
PM_SCALE_FACTOR = 10
PM_BYTE_FIRST = b'\xaa'
PM_BYTE_LAST = b'\xab'


def celsius_to_farhrenheit(temp: float):
    """ Converts temperature in Celsius to Fahrenheit. """
    return 9.0 / 5.0 * temp + 32.0


def millibar_to_inhg(pressure: float):
    """ Converts pressure in millibars to in-Hg. """
    conversion_factor = 1.0 / 33.8639
    return conversion_factor * pressure


def convert_bytes_to_particulate_reading(data: list):
    """
    Converts list of byes to PM reading.

    Args:
        data: list of UART bytes for PM reading

    Returns:
        PM reading as float
    """
    return int.from_bytes(b''.join(data), byteorder='little') / PM_SCALE_FACTOR


def get_particulate_readings():
    """
    Streams UART buffer from SDS011 and computes PM2.5 and PM10 values
    
    Args:
        None
    
    Returns:
        Tuple with PM2.5 and PM10 readings
    """
    # Reset buffer and get new data packet.
    serial_device.reset_input_buffer()
    data = [serial_device.read(size=1) for _ in range(PM_PROTOCAL_SIZE)]

    # Checks buffer is good.
    if data[0] != PM_BYTE_FIRST or data[-1] != PM_BYTE_LAST:
        raise Exception('Data packet incorrectly configured. Terminating.')

    pm_25 = convert_bytes_to_particulate_reading(data[PM_25_IND[0]: PM_25_IND[1]+1])
    pm_10 = convert_bytes_to_particulate_reading(data[PM_10_IND[0]: PM_10_IND[1]+1])
    return pm_25, pm_10


def find_aqi_group(pm: float, aqi_scale: np.array):
    """ Get information about the AQI group.

    Args:
        pm: the PM reading
        aqi_scale: np.array (DataFrame style) with AQI table cutoffs

    Returns:
        Tuple with AQI category, high and low concentration and AQI"""
    if pm > aqi_scale["c_hi"].max():
        return "exceeds_scale", 999, 999, 999, 999

    aqi_scale = aqi_scale[aqi_scale["c_lo"] <= pm]
    aqi_scale = aqi_scale[aqi_scale["c_hi"] >= pm]
    if aqi_scale.shape[0] != 1:
        raise Exception(f"{aqi_scale.shape[0]} AQI groups found for PM = {pm}. Something went wrong.")
    return aqi_scale[0]


def compute_aqi(pm: float, pm_size: str):
    """ Computes air quality index (AQI) for a PM readings

    Args:
        pm: the PM reading
        pm_size: flag specifying PM2.5 or PM10

    Returns:
        AQI value
    """
    if pm_size not in ["2.5", "10"]:
        raise Exception(f"Valid pm_size options are 2.5 and 10. {pm_size} was given.")
    n_demicals = {"2.5": 1, "10": 0}[pm_size]
    pm = round(pm, n_demicals)

    aqi_scale = {"2.5": PM_25_AQI_SCALE, "10": PM_10_AQI_SCALE}[pm_size]
    aqi_group, c_lo, c_hi, aqi_lo, aqi_hi = find_aqi_group(pm, aqi_scale)
    if aqi_group == "exceeds_scale":
        return 999, aqi_group
    aqi = (aqi_hi - aqi_lo) / (c_hi - c_lo) * (pm - c_lo) + aqi_lo

    # print(f"AQI: {aqi_group}\nc_low: {c_lo}\nc_high: {c_hi}\naqi_low: {aqi_lo}\naqi_high: {aqi_hi}")
    # print(pd.DataFrame(aqi_scale))
    return round(aqi)


def collect_weather_data():
    """ Collects relevant data.

    Args:
        None

    Returns:
        Tuple with temperature, humidity, pressure, pm2.5, annd pm10
    """
    temp = celsius_to_farhrenheit(sense.get_temperature())
    humidity = sense.get_humidity()
    sense.get_pressure() # on Pi reboot, first call often returns 0
    pressure = millibar_to_inhg(sense.get_pressure())
    return temp, humidity, pressure


def get_timestamp_string(tz="UTC", str_fmt="%Y-%m-%d %H:%M:%S"):
    """ Gets the current timestamp for now.

    Args:
        tz: timezone string
        str_fmt: string format for writing datetime to string

    Returns:
        String of timestamps
    """
    return datetime.now().astimezone(timezone(tz)).strftime(str_fmt)


def main():
    """
    Calls main.
    """
    timestamp = get_timestamp_string()
    temp, humidity, pressure = collect_weather_data()
    pm_25, pm_10 = get_particulate_readings()

    aqi_25 = compute_aqi(pm_25, "2.5")
    aqi_10 = compute_aqi(pm_10, "10")
    aqi = max(aqi_25, aqi_10)

    print(f"Time: {timestamp}")
    print(f"Temp: {temp:.1f}\nHumidity: {humidity:.1f}\nPressure: {pressure:.1f}")
    print(f"PM2.5:  {pm_25}  PM10: {pm_10}")
    print(f"AQI2.5: {aqi_25}   AQI10: {aqi_10} -> AQI {aqi}")


if __name__ == "__main__":
    main()
