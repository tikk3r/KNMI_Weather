# KNMI_Weather
Process an hourly data set from the KNMI.

Monthly Averages
================
Full Average
------------
Calculates the average of all months in a year or a specific month by first averaging all hours to get a daily average and then averaging the days to get a monthly average. It automatically assumes a full year if the month is not specified.
### Usage
To calculate the average for all months:
```python
    monAvg(data, yyyy)
```
To calculate the average for a specific month:
```python
    monAvg(data, yyyy, mm=month)
```
The month is specified by its number, i.e. jan = 1, feb = 2 etc.

Partial Average
---------------
Calculates the average of a month for night, morning, afternoon and evening separately. Automatically assumes january when no month is specified.
### Usage
```python
    mondayNightAvg(data, yyyy, mm=month)
```
