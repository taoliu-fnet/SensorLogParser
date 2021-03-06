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

# plot style defs
plot_markers = ('.','o','v','^','<','>','1','2','3','4','8','s','p','*','+','x')
plot_colors = ('m','r','g','b','k')
plot_gen_labels = ("acl",       "alarm",    "ahc", "forensic", "forensicSize", "reset", "http", "httpTP", "err401", "err409", "senderr", "respMin", "respMax", "respAvg", "recycleSta", "recycleStaAct", "recycleAp", "recycleApAct", "Captured", "RebootReason")
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

# main entry
if __name__ == '__main__':
    # arg: log directory
    if len(sys.argv) < 4:
        print "Usage:", sys.argv[0], "<CSV1> <CSV2> <Column Name>"
        sys.exit()
    
    csv1 = sys.argv[1]
    csv2 = sys.argv[2]
    colList = [i for i in sys.argv[3:]]
    
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
    fds1 = dates.date2num(dateList)
    
    arrList = []
    dateList = []
    for l in csvList2:
        tmpList = [float(i if i else 'nan') for i in l[1:]]
        dateList.append(datetime.datetime.strptime(l[0], "%Y-%m-%d %H:%M:%S"))
        arrList.append(tmpList)
    arr2 = np.asarray(arrList)
    fds2 = dates.date2num(dateList)

    # matplotlib date format object
    hfmt = dates.DateFormatter('%m/%d %H:%M')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    ## For arr1
    for i in range(len(arr1[0,:])):
        if plot_idx[i]:
            markerIdx = i % len(plot_markers)
            colorIdx = i % len(plot_colors)
            data = arr1[:,i]
            ax.plot(fds1, data, plot_markers[markerIdx] + 'r',
                    label=plot_gen_labels[i] + ' (' + csv1 + ')')

    ## for arr2
    for i in range(len(arr2[0,:])):
        if (plot_idx[i] == 0):
            continue
        markerIdx = i % len(plot_markers)
        colorIdx = i % len(plot_colors)
        data = arr2[:,i]
        ax.plot(fds2, data,
                plot_markers[markerIdx] + 'b',
                label=plot_gen_labels[i] + ' (' + csv2 + ')')
    
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

    # set the figure
    loc = dates.HourLocator(interval=4)
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(hfmt)
    ax.set_ylim(bottom = 0)
    # ax.set_yscale('log')
    #ax.grid(True)
    
    plt.xticks(rotation='vertical')
    plt.subplots_adjust(bottom=0.1, left=0.05, right=0.95, top=0.95)
    plt.legend(loc='upper left', bbox_to_anchor=[0,1],
               ncol=2, fancybox=True)
    fig.set_size_inches(20, 12)
    
    # save file
    figName = os.path.splitext(os.path.basename(csv1))[0]
    figName += '_VS_'
    figName += os.path.splitext(os.path.basename(csv2))[0]
    figName += '.jpg'
    plt.savefig(figName, dpi=100)


