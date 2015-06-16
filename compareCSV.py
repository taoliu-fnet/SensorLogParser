# -*- coding: utf-8 -*-
"""
Created on Wed May 27 09:13:01 2015

@author: tliu2
"""

import glob, re, sys, csv, os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import dates
import datetime, time
import argparse

# plot style defs
plot_markers = ('.','o','v','^','<','>','1','2','3','4','8','s','p','*','+','x')
plot_colors = ('m','r','g','b','k')
plot_gen_labels = ("acl",       "alarm",    "ahc", "forensic", "forensicSize", "reset", "http", "httpTP", "err401", "err409", "senderr", "respMin", "respMax", "respAvg", "recycleSta", "recycleStaAct", "recycleAp", "recycleApAct", "Captured", "RebootReason")
# use this to scale down/up the corresponding values.
plot_gen_factors = (0.000001,   0.000001,   1,     1,          1,              1,      0.01,   0.000001, 1,        1,        1,         1,         0.1,       0.1,       0.000001,     0.000001,        0.000001,    0.000001,       1,          1)
plot_gen_index =   (1,    1,       0,      1,          0,              0,      0,      0,        0,        0,        0,         0,         0,         0,         1,            0,               1,           0,              0,          0)

def ReadCSV(csvName):
    with open(csvName, 'rb') as f:
        rdr = csv.reader(f)
        header = next(rdr)
        csvList = []
        for arow in rdr:
            csvList.append(arow)
    return header, csvList


def GetFactorStr(factor):
    f = int(round(1/factor))
    if f == 1:
        return ""
    else:
        return "/" + str(f)
        
# main entry
if __name__ == '__main__':
    # arg: log directory
    parser = argparse.ArgumentParser(description='Parse and plot comparison figure of sensor logs.')
    parser.add_argument('-a', action='store_true', default=False, help='Align the time axis')
    parser.add_argument('-s1', default=0, type=int, help='time shift of first CSV (minutes)')
    parser.add_argument('-s2', default=0, type=int, help='time shift of second CSV (minutes)')
    parser.add_argument('csv1', action='store', help = 'CSV file name 1')
    parser.add_argument('csv2', action='store', help = 'CSV file name 2')
    parser.add_argument('column_list', nargs='+', help = 'List of column to be plotted')
    
    args = parser.parse_args()
    #print args
    csv1 = args.csv1
    csv2 = args.csv2
    colList = args.column_list
    tShift1 = args.s1
    tShift2 = args.s2
    tAlign = args.a
    # Set time shift
    if tShift1 or tShift2:
        tAlign = False
        tShift1 = float(tShift1) / (24 * 60) # minute
        tShift2 = float(tShift2) / (24 * 60) # minute
        print 'Shift time axis, ignore align setting'
    
    if tAlign:
        print 'Time will be aligned to', csv2
    
    hdr1, csvList1 = ReadCSV(csv1)
    hdr2, csvList2 = ReadCSV(csv2)
    
    if not csvList1:
        print 'Empty csv', csv1
        sys.exit()
    if  not csvList2:
        print 'Empty csv', csv2
        sys.exit()
    if hdr1 != hdr2:
        print 'CSV format mismatch.'
        sys.exit()

    # cloumns to plot
    plot_idx = [0] * len(hdr1)
    for col in colList:
        if col in hdr1:
            plot_idx[hdr1.index(col)] = 1
    plot_idx = plot_idx[1:]
    
    if np.sum(plot_idx) == 0:
        print 'No matching column found.'
        print 'Available columns:', ','.join(hdr1)
        sys.exit()
    
    # convert to numpy
    arrList = []
    dateList = []
    for l in csvList1:
        tmpList = [float(i if i else 'nan') for i in l[1:]]
        dateList.append(datetime.datetime.strptime(l[0], "%Y-%m-%d %H:%M:%S"))
        arrList.append(tmpList)
    arr1 = np.asarray(arrList)
    fds1 = dates.date2num(dateList) + tShift1
    
    arrList = []
    dateList = []
    for l in csvList2:
        tmpList = [float(i if i else 'nan') for i in l[1:]]
        dateList.append(datetime.datetime.strptime(l[0], "%Y-%m-%d %H:%M:%S"))
        arrList.append(tmpList)
    arr2 = np.asarray(arrList)
    fds2 = dates.date2num(dateList) + tShift2
    
    if (tAlign):
        dt = fds2[0] - fds1[0]
        fds1 += dt

    # matplotlib date format object
    hfmt = dates.DateFormatter('%m/%d %H:%M')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ## For arr1
    for i in range(len(arr1[0,:])):
        if plot_idx[i]:
            markerIdx = i % len(plot_markers)
            colorIdx = i % len(plot_colors)
            data = arr1[:,i] * plot_gen_factors[i]
            ax.plot(fds1, data, plot_markers[markerIdx] + 'r',
                    label=plot_gen_labels[i] + GetFactorStr(plot_gen_factors[i]) + ' (' + csv1 + ')')

    ## for arr2
    for i in range(len(arr2[0,:])):
        if (plot_idx[i] == 0):
            continue
        markerIdx = i % len(plot_markers)
        colorIdx = i % len(plot_colors)
        data = arr2[:,i] * plot_gen_factors[i]
        ax.plot(fds2, data,
                plot_markers[markerIdx] + 'b',
                label=plot_gen_labels[i] + GetFactorStr(plot_gen_factors[i]) + ' (' + csv2 + ')')
    
    # Add the vectial line for reboot
    ymin, ymax = ax.get_ylim()
    # Arr1
    rebootIdx = len(arr1[0,:]) - 1
    prev_tds = fds1[0]
    for i in range(len(fds1)):
        tds = fds1[i]
        reboot = arr1[i, rebootIdx]
        if not np.isnan(reboot):
            if (tds < prev_tds):
                tds = prev_tds
            if (tds < 720000):
                print 'Skip reboot time', datetime.datetime.strftime(dates.num2date(tds), "%Y-%m-%d %H:%M:%S")
                continue
            plt.vlines(tds,ymin,ymax, 'r')
            plt.text(tds, ymax, str(int(reboot)), rotation='vertical', ha='left', va='bottom', color='r')
        prev_tds = tds;

    #arr2
    rebootIdx = len(arr2[0,:]) - 1
    prev_tds = fds2[0]
    for i in range(len(fds2)):
        tds = fds2[i]
        reboot = arr2[i, rebootIdx]
        if not np.isnan(reboot):
            if (tds < prev_tds):
                tds = prev_tds
            if (tds < 720000):
                print 'Skip reboot time', datetime.datetime.strftime(dates.num2date(tds), "%Y-%m-%d %H:%M:%S")
                continue
            plt.vlines(tds,ymin,ymax, 'b')
            plt.text(tds, ymax, str(int(reboot)), rotation='vertical', ha='left', va='bottom', color='b')
        prev_tds = tds;

    # set the figure x-axis ticks. interval = 4 means every 4 hours.
    loc = dates.HourLocator(interval=4)
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(hfmt)
    ax.set_ylim(bottom = 0)
    #ax.grid(True)
    
    plt.xticks(rotation='vertical')
    plt.subplots_adjust(bottom=0.1, left=0.05, right=0.95, top=0.95)
    plt.legend(loc='upper left', bbox_to_anchor=[0,1],
               ncol=2, fancybox=True)
    # Set size here.
    fig.set_size_inches(20, 12)
    
    # save file
    figName = os.path.splitext(os.path.basename(csv1))[0]
    figName += '_VS_'
    figName += os.path.splitext(os.path.basename(csv2))[0]
    figName += '.jpg'
    plt.savefig(figName, dpi=100)
    print 'Figure written to', figName


