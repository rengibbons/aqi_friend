"""
Author: Ren Gibbons
Email: gibbons.ren@gmail.com

Helpful reference links:
    https://hackernoon.com/how-to-measure-particulate-matter-with-a-raspberry-pi-75faa470ec35
    https://gist.github.com/kadamski/92653913a53baf9dd1a8
    https://cdn-reichelt.de/documents/datenblatt/X200/SDS011-DATASHEET.pdf
    https://forum.airnowtech.org/t/the-aqi-equation/169
"""
from datetime import datetime
from pytz import timezone
import serial
from sense_hat import SenseHat

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


def collect_weather_data():
    """ Collects relevant data.

    Args:
        None

    Returns:
        Tuple with temperature, humidity, pressure, pm2.5, annd pm10
    """
    temp = celsius_to_farhrenheit(sense.get_temperature())
    humidity = sense.get_humidity()
    pressure = millibar_to_inhg(sense.get_pressure())
    pm_25, pm_10 = get_particulate_readings()
    return temp, humidity, pressure, pm_25, pm_10

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
    temp, humidity, pressure, pm_25, pm_10 = collect_weather_data()

    print(f"Time: {timestamp}")
    print(f"Temp: {temp:.1f}\nHumidity: {humidity:.1f}\nPressure: {pressure:.1f}")
    print(f"PM2.5: {pm_25}\nPM10: {pm_10}")


if __name__ == "__main__":
    main()
