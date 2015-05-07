#!/usr/bin/env python
from __future__ import division
from matplotlib.pyplot import figure, show

import math
import numpy as np

DATE, HOUR, TEMP, CLOUD = [], [], [], []
YR_START = 0; YR_END = 0
month_labels = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
###########################
# Pre-use data reduction. #
###########################
def reduce_data():
    ''' Reduce the KNMI data to a workable format for further analysis. It extracts the hour, temperature and cloud coverage accessible as data[year][month][day][hour].
    It modifies global variables defined at the start of the script.
    Args:
        None
    Returns:
        None
    '''
    print 'Processing hourly data.'
    date, hour, temp, cloud = np.genfromtxt('./KNMI_20150424_hourly.txt', delimiter=',', filling_values=None, skip_header=14, usecols=(1,2,3,4), unpack=True)
    # Convert temperatures to celcius.
    temp /= 10
    print '[Hourly] Grouping data by hour...'

    # Group the data per year: date = [year1, year2, ...] > year = [hour1, hour2, ...]
    print '[Hourly] Grouping data by year...'
    date_y, hours_y, temp_y, cloud_y = [], [], [], []
    dy, hy, ty, cy = [], [], [], []
    nyear = date[0]//1e4 + 1
    for k, h in enumerate(date): # For every hour...
        year = int(h//1e4)
        if year < nyear:
            dy.append(h); hy.append(hour[k]); ty.append(temp[k]); cy.append(cloud[k])
        else:
            date_y.append(dy); hours_y.append(hy); temp_y.append(ty); cloud_y.append(cy)
            nyear += 1
            dy, hy, ty, cy = [], [], [], []
            dy.append(h); hy.append(hour[k]); ty.append(temp[k]); cy.append(cloud[k])
    # Append the remaining, incomplete year.
    date_y.append(dy); hours_y.append(hy); temp_y.append(ty); cloud_y.append(cy)

    # Group the data by hour: data = [year1, year2, ...] > year = [day1, day2, ...] > day = [hour1, hour2, ...]
    print '[Hourly] Grouping data by hour...'
    date_h, hour_h, temp_h, cloud_h = [], [], [] ,[]
    for k, yr in enumerate(date_y):
        dh, hh, th, ch = [], [], [] ,[]
        for i in range(len(yr)//24):
            dh.append(date_y[k][24*i])
            hh.append(hours_y[k][24*i:24*(i+1)])
            th.append(temp_y[k][24*i:24*(i+1)])
            ch.append(cloud_y[k][24*i:24*(i+1)])
        date_h.append(dh); hour_h.append(hh); temp_h.append(th); cloud_h.append(ch)

    # Group the data by month: data = [year1, year2, ...] > year = [month1, month2, ...] > month = [day1, day2, ...] > day = [hour1, hour2, ...]
    print '[Hourly] Grouping data by month...'
    date_m, hour_m, temp_m, cloud_m = [], [] ,[], []
    for i, yr in enumerate(date_h):
        dm, hm, tm, cm = [], [], [] ,[]
        for _ in range(12):
            dm.append([])
            hm.append([])
            tm.append([])
            cm.append([])
        for d, h, t, c in zip(date_h[i], hour_h[i], temp_h[i], cloud_h[i]):
            month = int((d % 1e4) // 100)
            dm[month-1].append(int(d))
            hm[month-1].append(h)
            tm[month-1].append(t)
            cm[month-1].append(c)
        if [] in dm: # There is an incomplete year, add all available months.
            date_m.append(dm[:dm.index([])])
            hour_m.append(hm[:hm.index([])])
            temp_m.append(tm[:tm.index([])])
            cloud_m.append(cm[:cm.index([])])
        else:
            date_m.append(dm)
            hour_m.append(hm)
            temp_m.append(tm)
            cloud_m.append(cm)
    global DATE, HOUR, TEMP, CLOUD
    global YR_START, YR_END
    DATE = date_m; HOUR = hour_m; TEMP = temp_m; CLOUD = cloud_m
    YR_START = int(date[0] // 1e4); YR_END = int(date[len(date)-1] //1e4)


def monAvg(data, yyyy, mm=-1):
    ''' Calculate the full monthly average.
        Args:
            ndarray data - array containing data to analyze. Should be accessible as data[year][month][day][hour]
            float yyyy - the year in yyyy format.
            float mm - the month in mm format, normally assumes all months.
        Returns:
            ndarray mavgmean - monthly averages.
            ndarray mavgstd - standard deviation of the monthly averages.
    '''
    if mm < 0: # User wants all months.
        mavgmean = []; mavgstd = []
        for month in data[int(yyyy - YR_START)]:
            davg = []
            for day in month:
                # Average of the day.
                avg = np.nanmean(day); davg.append(avg)
            # Average of the month.
            mavgmean.append(np.nanmean(davg))
            mavgstd.append(np.nanstd(davg))
        return np.asarray(mavgmean), np.asarray(mavgstd)
    else: # User specifies a month.
        # Select the required month.
        dat = data[int(yyyy - YR_START)][mm]
        davg = []
        for day in dat:
            # Daily average.
            davg.append(np.nanmean(day))
        # Average of the month.
        mavgmean = np.asarray(np.nanmean(davg))
        mavgstd = np.asarray(np.nanstd(davg))
        return mavgmean, mavgstd

def monDayNightAvg(data, yyyy, mm=1):
    ''' Calculate monthly average for the day hours and for the night hours separately.
    Gives the monthly average for the specified month.
    Args:
        ndarray data - array containing data to analyze. Should be accessible as data[year][month][day][hour]
        float yyyy - the year in yyyy format.
        float mm - the month in mm format, normally assumes january.
    Returns:
        ndarray/float nam - nightly average and standard deviation, 00-06.
        ndarray/float mam - morning average and standard deviation, 06-12.
        ndarray/float aam - afternoon average and standard deviation, 12-18.
        ndarray/float eam - evening average and standard deviation, 18-24
    '''
    # Select the required month.
    dat = data[int(yyyy - YR_START)][mm]
    nad, mad, aad, ead = [], [], [], []
    for day in dat:
        na = np.nanmean(day[0:6]); nad.append(na)
        ma = np.nanmean(day[6:12]); mad.append(ma)
        aa = np.nanmean(day[12:18]); aad.append(aa)
        ea = np.nanmean(day[18:24]); ead.append(ea)
    return np.asarray(nad), np.asarray(mad), np.asarray(aad), np.asarray(ead)

def plot(ax, x, y, type, yerror=None, title='', xlabel='', ylabel='', format='o-'):
    ''' Eases the plotting of data by helping with the axes formatting.
    Args:
        Axis ax - the axis to plot on.
        ndarray x - independent variable.
        ndarray y - dependend variable.
        str type - type of data to plot. Can be year, month or day.
        xlabel - text for the xaxis.
        ylabel - text for the yaxis.
    Returns:
        None
    '''
    if type == 'year':
        pass
    elif type == 'month':
        ax.set_xlim(-1, 13); ax.set_ylim(-10, 30)
        ax.set_title(title)
        ax.xaxis.set_ticks(np.linspace(ax.get_xlim()[0], ax.get_xlim()[1], 15))
        ax.set_xticklabels(month_labels)
        ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
        if yerror is not None:
            ax.errorbar(x, y, yerr=yerror, fmt=format)
        else:
            ax.plot(x, y, format)
############

reduce_data()
##############################################################################################################################################################
# Data processing finished. Access the data as date_m[year][month][day] or variable[year][month][day][hour] where variable can be hour_m, temp_m or cloud_m. #
##############################################################################################################################################################
if __name__ == '__main__':
    d = 2013021518
    #DATE = input('Enter date as yyyymmdd: ')
    yyyy = int(d // 1e6)
    mm = int((d % 1e6) // 1e4)
    dd = int((d % 1e4) // 100)
    indx_y = yyyy - YR_START
    indx_m = mm - 1
    indx_d = dd - 1
    print mm
    print monAvg(TEMP, yyyy), len(monAvg(TEMP, yyyy))  
    
    fig = figure()
    ax = fig.add_subplot(111)
    #ax.plot(range(12), monAvg(TEMP, yyyy))
    #ax.set_ylim(-10, 30)
    plot(ax, range(12), monAvg(TEMP, yyyy)[0], yerror=monAvg(TEMP,yyyy)[1], type='month', xlabel='Month', ylabel='Temperature $\\degree$C')
    show()
