#!/usr/bin/env python
from __future__ import division
import cgitb;# cgitb.enable()
import cgi
import math
import numpy as np

DATE, HOUR, TEMP, CLOUD = [], [], [], []
YR_START = 0; YR_END = 0
month_labels = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
hour_labels = [''] + range(1, 25)

# Define a substitute for numpy's nan avoiding functions.
def nanmean(arr):
    x = np.ma.MaskedArray(arr, np.isnan(arr))
    return np.mean(x)

def nanstd(arr):
    x = np.ma.MaskedArray(arr, np.isnan(arr))
    return np.std(x)

def nanmin(arr):
    x = np.ma.MaskedArray(arr, np.isnan(arr))
    return np.min(x)

def nanmax(arr):
    x = np.ma.MaskedArray(arr, np.isnan(arr))
    return np.max(x)
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
    date, hour, temp, cloud = np.genfromtxt('./KNMI_hourly.txt', delimiter=',', filling_values=None, skip_header=14, usecols=(1,2,3,4), unpack=True)
    # Convert temperatures to celcius.
    temp /= 10

    # Group the data per year: date = [year1, year2, ...] > year = [hour1, hour2, ...]
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

def hourDat(data, yyyy, mm=1, dd=1, hh=0):
    ''' Provides the hourly data of a day or of one specific hour.
    Args:
        ndarray data - data to search.
        int yyyy - year to get.
        int mm - month to get.
        int dd - day to get.
        int hh - hour to get.
    Returns:
        ndarray/float dat - array with data for all hours or float with data specific to the hour hh.
        float 0 - dummy result used for easier plotting in combination with the web interface.
    '''
    if hh == 0:
        # Take all hours for specified day.
        dat = data[yyyy - YR_START][mm-1][dd-1]
        return dat, 0
    elif 1 < hh < 24:
        dat = data[yyyy - YR_START][mm-1][dd-1][hh-1]
        return dat, 0

def dayMax(data, yyyy, mm=1, dd=0):
    ''' Calculate the daily maximum.
    Assumes january and all days by default.
    Args:
        ndarray data - data to be analyzed.
        int yyyy - the year.
        int mm - the month.
        int dd - the day.
    Returns:
        ndarray/float dmax - maximum of the day.
        ndarray/float dstd - standard deviation of the day.
    '''
    if dd == 0:
        # Take all days for the specified month.
        dat = data[yyyy - YR_START][mm-1]
        dmax = []
        for day in dat:
            max = nanmax(day)
            dmax.append(max)
        return np.asarray(dmax), np.zeros(len(dmax))# Fake standard deviation.
    else:
        # Take the specific day.
        dat = data[yyyy - YR_START][mm-1][dd-1]
        dmax = nanmax(dat)
        dstd = 0
        return dmax, dstd

def dayAvg(data, yyyy, mm=1, dd=0):
    ''' Calculate the daily average.
    Assumes january and all days by default.
    Args:
        ndarray data - data to be analyzed.
        int yyyy - the year.
        int mm - the month.
        int dd - the day.
    Returns:
        ndarray/float davg - average of the day.
        ndarray/float dstd - standard deviation of the day.
    '''
    if dd == 0:
        # Take all days for the specified month.
        dat = data[yyyy - YR_START][mm-1]
        davg = []; dstd = []
        for day in dat:
            avg = nanmean(day)
            std = nanstd(day)
            davg.append(avg)
            dstd.append(std)
        return np.asarray(davg), np.asarray(dstd)
    else:
        # Take the specific day.
        dat = data[yyyy - YR_START][mm-1][dd-1]
        davg = nanmean(dat)
        dstd = nanstd(dat)
        return davg, dstd

def dayMin(data, yyyy, mm=1, dd=0):
    ''' Calculate the daily minimum.
    Assumes january and all days by default.
    Args:
        ndarray data - data to be analyzed.
        int yyyy - the year.
        int mm - the month.
        int dd - the day.
    Returns:
        ndarray/float dmin - minimum of the day.
        ndarray/float dstd - standard deviation of the day.
    '''
    if dd == 0:
        # Take all days for the specified month.
        dat = data[yyyy - YR_START][mm-1]
        dmin = []
        for day in dat:
            min = nanmin(day)
            dmin.append(min)
        return np.asarray(dmin), np.zeros(len(dmin))# Fake standard deviation.
    else:
        # Take the specific day.
        dat = data[yyyy - YR_START][mm-1][dd-1]
        dmin = nanmin(dat)
        dstd = 0
        return dmin, dstd

def monMin(data, yyyy, mm=00):
    ''' Calculate the full monthly minimum.
        Args:
            ndarray data - array containing data to analyze. Should be accessible as data[year][month][day][hour]
            float yyyy - the year in yyyy format.
            float mm - the month in mm format, normally assumes all months.
        Returns:
            ndarray/float mminmean - monthly minima.
            ndarray/float mminstd - fake standard deviation of the monthly minimum to ease plotting automization.
    '''
    if mm == 0: # User wants all months.
        mminmean = []
        for month in data[int(yyyy - YR_START)]:
            dmin = []
            for day in month:
                # Average of the day.
                min = nanmin(day); dmin.append(min)
            # Average of the month.
            mminmean.append(nanmean(dmin))
        return np.asarray(mminmean), np.zeros(len(mminmean))
    else: # User specifies a month.
        # Select the required month.
        dat = data[int(yyyy - YR_START)][mm-1]
        dmin = []
        for day in dat:
            # Daily average.
            dmin.append(nanmin(day))
        # Average of the month.
        mminmean = nanmin(dmin)
        mminstd = 0
        return mminmean, mminstd

def monAvg(data, yyyy, mm=00):
    ''' Calculate the full monthly average.
        Args:
            ndarray data - array containing data to analyze. Should be accessible as data[year][month][day][hour]
            float yyyy - the year in yyyy format.
            float mm - the month in mm format, normally assumes all months.
        Returns:
            ndarray/float mavgmean - monthly averages.
            ndarray/float mavgstd - standard deviation of the monthly averages.
    '''
    if mm == 0: # User wants all months.
        mavgmean = []; mavgstd = []
        for month in data[int(yyyy - YR_START)]:
            davg = []
            for day in month:
                # Average of the day.
                avg = nanmean(day); davg.append(avg)
            # Average of the month.
            mavgmean.append(nanmean(davg))
            mavgstd.append(nanstd(davg))
        return np.asarray(mavgmean), np.asarray(mavgstd)
    else: # User specifies a month.
        # Select the required month.
        dat = data[int(yyyy - YR_START)][mm-1]
        davg = []
        for day in dat:
            # Daily average.
            davg.append(nanmean(day))
        # Average of the month.
        mavgmean = np.asarray(nanmean(davg))
        mavgstd = np.asarray(nanstd(davg))
        return mavgmean, mavgstd

def monMax(data, yyyy, mm=00):
    ''' Calculate the full monthly maximum.
        Args:
            ndarray data - array containing data to analyze. Should be accessible as data[year][month][day][hour]
            float yyyy - the year in yyyy format.
            float mm - the month in mm format, normally assumes all months.
        Returns:
            ndarray/float mmaxmean - monthly maxima.
            ndarray/float mmaxstd - fake standard deviation of the monthly maximum to ease plotting automization.
    '''
    if mm == 0: # User wants all months.
        mmaxmean = []
        for month in data[int(yyyy - YR_START)]:
            dmax = []
            for day in month:
                # Average of the day.
                max = nanmax(day); dmax.append(max)
            # Average of the month.
            mmaxmean.append(nanmean(dmax))
        return np.asarray(mmaxmean), np.zeros(len(mmaxmean))
    else: # User specifies a month.
        # Select the required month.
        dat = data[int(yyyy - YR_START)][mm-1]
        dmax = []
        for day in dat:
            # Daily average.
            dmax.append(nanmax(day))
        # Average of the month.
        mmaxmean = nanmax(dmax)
        mmaxstd = 0
        return mmaxmean, mmaxstd

def monDayNightMin(data, yyyy, mm=1):
    ''' Calculate monthly minimum for the day hours and for the night hours separately.
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
    dat = data[int(yyyy - YR_START)][mm-1]
    nad, mad, aad, ead = [], [], [], []
    for day in dat:
        na = nanmin(day[0:6]); nad.append(na)
        ma = nanmin(day[6:12]); mad.append(ma)
        aa = nanmin(day[12:18]); aad.append(aa)
        ea = nanmin(day[18:24]); ead.append(ea)
    return (np.asarray(nad),), (np.asarray(mad),), (np.asarray(aad),), (np.asarray(ead),)

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
    dat = data[int(yyyy - YR_START)][mm-1]
    nad, mad, aad, ead = [], [], [], []
    nastd, mastd, aastd, eastd = [], [], [], []
    for day in dat:
        na = nanmean(day[0:6]); nad.append(na); nastd.append(nanstd(day[0:6]))
        ma = nanmean(day[6:12]); mad.append(ma); mastd.append(nanstd(day[6:12]))
        aa = nanmean(day[12:18]); aad.append(aa); aastd.append(nanstd(day[12:18]))
        ea = nanmean(day[18:24]); ead.append(ea); eastd.append(nanstd(day[18:24]))
    return (np.asarray(nad), np.asarray(nastd)), (np.asarray(mad), np.asarray(mastd)), (np.asarray(aad), np.asarray(aastd)), (np.asarray(ead), np.asarray(eastd))

def monDayNightMax(data, yyyy, mm=1):
    ''' Calculate monthly maximum for the day hours and for the night hours separately.
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
    dat = data[int(yyyy - YR_START)][mm-1]
    nad, mad, aad, ead = [], [], [], []
    for day in dat:
        na = nanmax(day[0:6]); nad.append(na)
        ma = nanmax(day[6:12]); mad.append(ma)
        aa = nanmax(day[12:18]); aad.append(aa)
        ea = nanmax(day[18:24]); ead.append(ea)
    return (np.asarray(nad),), (np.asarray(mad),), (np.asarray(aad),), (np.asarray(ead),)

def plot(ax, y, typ, yerror=None, title='', ylabel='', formt='o-', leg=False, lbl=''):
    ''' Eases the plotting of data by helping with the axes formtting.
    Args:
        Axis ax - the axis to plot on.
        ndarray y - dependend variable.
        str typ - type of data to plot. Can be year, month or day.
        xlabel - text for the xaxis.
        ylabel - text for the yaxis.
    Returns:
        None
    '''
    ax.set_title(title, fontweight='bold')
    ax.set_ylabel(ylabel)
    if typ == 'year':
        x = range(12)
        ax.set_xlim(-1, 13)
        ax.xaxis.set_ticks(np.linspace(ax.get_xlim()[0], ax.get_xlim()[1], 15))
        ax.set_xticklabels(month_labels)
        ax.set_xlabel('Month')
    elif typ == 'month':
        ax.set_xlim(-1, 32)
        day_labels = range(1, len(y)+1)
        ax.xaxis.set_ticks(day_labels)
        ax.set_xlabel('Day')
    elif typ == 'day':
        ax.set_xlim(-1, 25)
        ax.xaxis.set_ticks(np.linspace(ax.get_xlim()[0], ax.get_xlim()[1], len(y)+3))
        ax.set_xticklabels(hour_labels)
        ax.set_xlabel('Hour')
    else:
        print '[plot] Please specify a correct typ.'
    if yerror is not None:
        x = range(len(y))
        ax.errorbar(x, y, yerr=yerror, fmt=formt, label=lbl)
    else:
        x = range(len(y))
        ax.plot(x, y, formt, label=lbl)
    if leg:
        ax.legend()

##############################################################################################################################################################
# Data processing finished. Access the data as date_m[year][month][day] or variable[year][month][day][hour] where variable can be hour_m, temp_m or cloud_m. #
##############################################################################################################################################################
if __name__ == '__main__':
    from matplotlib.pyplot import figure, show
    # Demonstrate all data from 2010 till now.
    reduce_data()
    # Plot minimum, average and maximum temperature for every day.
    fig = figure()
    fig.suptitle('Temperature per Day', fontweight='bold')
    for i, yr in enumerate(range(2015 - YR_START + 1)):
        ax = fig.add_subplot(math.floor(math.sqrt(len(DATE))), math.ceil(math.sqrt(len(DATE))), i+1)
        y_min, y_avg, y_max = [], [], []
        for month in range(len(DATE[yr])):
            for day in range(len(DATE[yr][month])):
                y_min.append(np.min(TEMP[yr][month][day]))
                y_avg.append(np.mean(TEMP[yr][month][day]))
                y_max.append(np.max(TEMP[yr][month][day]))
        x = range(len(y_avg))
        ax.set_xlim(-5, 370)
        ax.set_ylim(-20, 40)
        ax.xaxis.set_ticks(np.linspace(ax.get_xlim()[0], ax.get_xlim()[1], 13))
        ax.set_xticklabels(month_labels[1:])
        ax.plot(x, y_min, 'bx', label='$T_{min}$')
        ax.plot(x, y_avg, 'yo', label='$T_{avg}$')
        ax.plot(x, y_max, 'rx', label='$T_{max}$')
        ax.set_title(YR_START + i, fontweight='bold')
        ax.legend()
    show()
