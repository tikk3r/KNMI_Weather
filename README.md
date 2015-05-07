# KNMI_Weather
Process an hourly data set from the KNMI.

Daily Averages
==============
Calculate the average of all days over a month or on specific day.
### Usage
To calculate for all days in a month:
```python
    dayAvg(data, year, mm=month)
```
To calculate for a specific day:
```python
    dayAvg(data, year, mm=month, dd=day)
```
Monthly Averages
================
Full Average
------------
Calculates the average of all months in a year or a specific month by first averaging all hours to get a daily average and then averaging the days to get a monthly average. It automatically assumes a full year if the month is not specified.
### Usage
To calculate the average for all months:
```python
    monAvg(data, year)
```
To calculate the average for a specific month:
```python
    monAvg(data, year, mm=month)
```
The month is specified by its number, i.e. jan = 1, feb = 2 etc.

Partial Average
---------------
Calculates the average of a month for night, morning, afternoon and evening separately. Automatically assumes january when no month is specified.
### Usage
```python
    mondayNightAvg(data, year, mm=month)
```
