"""
Author: Ren Gibbons
Email: gibbons.ren@gmail.com
Date Created: 2021-01-09

Generate custom numpy arrays with PM cut offs for AQI calculations.

Helpful reference links:
    https://forum.airnowtech.org/t/the-aqi-equation/169
"""
import numpy as np


dt = np.dtype(
    {
        "names": ("cat", "c_lo", "c_hi", "aqi_lo", "aqi_hi"),
        "formats": ((np.unicode_, 32), np.float64, np.float64, np.float64, np.float64)
     }
)

PM_25_AQI_SCALE = np.array(
    [
        ("good", 0, 12, 0, 50),
        ("moderate", 12.1, 35.4, 51, 100),
        ("unhealthy_sensitive", 35.5, 55.4, 101, 150),
        ("unhealthy", 55.5, 150.4, 151, 200),
        ("very_unhealthy", 150.5, 250.4, 201, 300),
        ("hazardous", 250.5, 500.4, 301, 500)
    ],
    dtype=dt
)

PM_10_AQI_SCALE = np.array(
    [
        ("good", 0, 54, 0, 50),
        ("moderate", 55, 154, 51, 100),
        ("unhealthy_sensitive", 155, 254, 101, 150),
        ("unhealthy", 255, 354, 151, 200),
        ("very_unhealthy", 355, 424, 201, 300),
        ("hazardous", 425, 604, 301, 500)
    ],
    dtype=dt
)

# import pandas as pd
# print(pd.DataFrame(PM_25_SCALE))
# print(pd.DataFrame(PM_10_SCALE))
