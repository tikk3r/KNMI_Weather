# KNMI_Weather
Process an hourly data set from the KNMI.

Monthly Averages
================
Day/Night Average
-----------------
Calculates the average of a given data array for separate parts of the day. It is split in night (0-6), morning (6-12), afternoon (12-18) and evening (18-24). It calculates for all months by default, but can be given a specific month. To calculate for all months use
    monDayNightAvg(data, year)
To calculate for a specific month use
    monDayNightAvg(data, year, mm=month)

