'''
   
   calender generator

   Author: John Oldman - May 2017

'''

import time
import datetime as dt
import calendar
import matplotlib.pyplot as plt
import numpy as np


#constants
CALENDER_YEAR = 2017
FIRST_DAY_OF_WEEK = calendar.MONDAY


def main():
    ''' main function '''

    # time this module
    start = time.clock()

    # invoke calender class c
    c = calendar.TextCalendar(FIRST_DAY_OF_WEEK)

    # output basic year calendar
    #for month in range (1,13):
    #    print c.formatmonth(CALENDER_YEAR, month)

    print c.yeardayscalendar(CALENDER_YEAR, 2)
    
    #print c.formatyear(CALENDER_YEAR, 2, 2, 2)

    print c.formatmonth(CALENDER_YEAR, 5, 2, 2)

    dates, data = generate_data()
    fig, ax = plt.subplots(figsize=(6, 10))
    calendar_heatmap(ax, dates, data)
    plt.show()

    # calculate module run time 
    print 'Run time was ' + str(time.clock() - start) + ' seconds.'


def generate_data():
    num = 365
    data = np.random.randint(0, 20, num)
    start = dt.datetime(2017, 1, 1)
    dates = [start + dt.timedelta(days=i) for i in range(num)]
    return dates, data



def calendar_array(dates, data):
    i, j = zip(*[d.isocalendar()[1:] for d in dates])
    i = np.array(i) - min(i)
    j = np.array(j) - 1
    ni = max(i) + 1

    calendar = np.nan * np.zeros((ni, 7))
    calendar[i, j] = data
    return i, j, calendar



def calendar_heatmap(ax, dates, data):
    i, j, calendar = calendar_array(dates, data)
    im = ax.imshow(calendar, interpolation='none', cmap='summer')
    label_days(ax, dates, i, j, calendar)
    label_months(ax, dates, i, j, calendar)
    #ax.figure.colorbar(im)



def label_days(ax, dates, i, j, calendar):
    ni, nj = calendar.shape
    day_of_month = np.nan * np.zeros((ni, 7))
    day_of_month[i, j] = [d.day for d in dates]

    for (i, j), day in np.ndenumerate(day_of_month):
        if np.isfinite(day):
            ax.text(j, i, int(day), ha='center', va='center')

    ax.set(xticks=np.arange(7), 
           xticklabels=['M', 'T', 'W', 'T', 'F', 'S', 'S'])
    ax.xaxis.tick_top()



def label_months(ax, dates, i, j, calendar):
    month_labels = np.array(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
                             'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    months = np.array([d.month for d in dates])
    uniq_months = sorted(set(months))
    yticks = [i[months == m].mean() for m in uniq_months]
    labels = [month_labels[m - 1] for m in uniq_months]
    ax.set(yticks=yticks)
    ax.set_yticklabels(labels, rotation=90)


if __name__ == "__main__":
    main()


