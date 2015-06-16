# -*- coding: utf-8 -*-
"""
Created on Wed May 27 09:13:01 2015

@author: tliu2
"""

import glob, re, sys, csv
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import dates
import datetime, time

# plot style defs
plot_markers = ('.','o','v','^','<','>','1','2','3','4','8','s','p','*','+','x','D','d')
plot_colors = ('m','r','g','b','k')
plot_gen_labels = ("acl", "alarm", "ahc", "forensic", "forensicSize", "reset", "http", "httpTP", "err401", "err409", "senderr", "respMin", "respMax", "respAvg", "recycleSta", "recycleStaAct", "recycleAp", "recycleApAct", "Captured", "RebootReason")
plot_gen_factors = (1,    1,       1,      1,          1,              1,      0.01,   0.00001,  1,        1,        1,         1,         0.1,       0.1,       1,            1,               1,           1,              1,          1)
plot_gen_index =   (1,    1,       0,      1,          0,              0,      0,      0,        0,        0,        0,         0,         0,         0,         1,            0,               1,           0,              0,          0)

def GetFactorStr(factor):
    f = int(round(1/factor))
    if f == 1:
        return ""
    else:
        return "/" + str(f)

def ReadLog(fname):
    with open(fname, 'rb') as f:
        sline = f.readline()
        if sline.startswith("=~=~=~=~=~=~=~=~=~=~=~= PuTTY log"):
            print "found:", fname
            content = f.read()
        else:
            print "not a log:", fname
            
    if content:
        re_GEN = re.compile(r"\[GEN\] (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), Pack SensorStats: acl\((\d+)\) alarm\((\d+)\) ahc\((\d+)\) forensic\((\d+)\) forensicSize\((\d+)\) reset\((\d+)\) http\((\d+)\) httpTP\((\d+)\) err401\((\d+)\) err409\((\d+)\) senderr\((\d+)\) respMin\((\d+)\) respMax\((\d+)\) respAvg\((\d+)\) recycleSta\((\d+)\) recycleStaAct\((\d+)\) recycleAp\((\d+)\) recycleApAct\((\d+)\)")
        re_INFO = re.compile(r"INFO:FFFLC:STATIS:Scan=(\d+):\d+,Parse=\d+:\d+,Drop=d+:d+,Time=(\d+)")
        re_REBOOT = re.compile(r"QueryRebootReason: reason - (\d+), time - (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \((\d+)\)")
        
        
        genList = re_GEN.findall(content)
        infoList = re_INFO.findall(content)
        rebootList = re_REBOOT.findall(content)
        return genList, infoList, rebootList
    else:
        return None, None

def ProcessLists(genList, infoList, rebootList, srcFileName):
    csvName = srcFileName[0:-3] + '_GEN.csv'
    figName = srcFileName[0:-3] + '_GEN.jpg'
    
    # write the csv
    with open(csvName, 'wb') as f:
        w = csv.writer(f)
        # header
        w.writerow(["Timedate", "acl", "alarm", "ahc", "forensic", "forensicSize", "reset", "http", "httpTP", "err401", "err409", "senderr", "respMin", "respMax", "respAvg", "recycleSta", "recycleStaAct", "recycleAp", "recycleApAct"])
        w.writerows(genList)

    # now plot
    arrList = []
    dateList = []
    for l in genList:
        tmpList = [ int(i) for i in l[1:] ]
        dateList.append(datetime.datetime.strptime(l[0], "%Y-%m-%d %H:%M:%S"))
        #tmpList.append(int((time.mktime(time.strptime(l[0], "%Y-%m-%d %H:%M:%S")))))
        arrList.append(tmpList)
    arr = np.asarray(arrList)
    fds = dates.date2num(dateList)
    
    # matplotlib date format object
    hfmt = dates.DateFormatter('%m/%d %H:%M')

    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    for i in range(len(arr[0,:])):
        if (plot_gen_index[i] == 0):
            continue
        markerIdx = i % len(plot_markers)
        colorIdx = i % len(plot_colors)
        ax.plot(fds, arr[:,i] * plot_gen_factors[i],
                plot_markers[markerIdx] + plot_colors[colorIdx],
                label=plot_gen_labels[i] + GetFactorStr(plot_gen_factors[i]))

    ax.xaxis.set_major_locator(dates.HourLocator())
    ax.xaxis.set_major_formatter(hfmt)
    ax.set_ylim(bottom = 0)
    plt.xticks(rotation='vertical')
    plt.subplots_adjust(bottom=0.05, left=0.05, right=0.95, top=0.95)
    plt.legend(loc='upper left', bbox_to_anchor=[0,1],
               ncol=2, fancybox=True)
    fig.set_size_inches(40, 30)
    plt.savefig(figName, dpi=100)
    
def ProcessInfoList(infoList, srcFileName):
    csvName = srcFileName[0:-3] + '_INFO.csv'
    figName = srcFileName[0:-3] + '_INFO.jpg'
    
    # write the csv
    with open(csvName, 'wb') as f:
        w = csv.writer(f)
        # header
        w.writerow(["Timedate", "Frames"])
        w.writerows(infoList)


def main():
    # arg: log directory
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "<log directory>"
        return
    
    fList = glob.glob(sys.argv[1] + '/*.txt')
    fList.extend(glob.glob(sys.argv[1] + '/*.log'))
    for fname in fList:
        # print fname
        genList, infoList, rebootList = ReadLog(fname)
        ProcessLists(genList, infoList, rebootList, fname)

if __name__ == '__main__':
    main()