#!/bin/python3

import json
import subprocess
from flask import Flask, render_template

server_port = 7667

def getDaily():
    raw_day_data = json.loads(subprocess.getoutput("vnstat --json d 7 -i eth0"))
    daily_data = raw_day_data['interfaces'][0]['traffic']['day']
    return daily_data

def getMonthly():
    raw_month_data = json.loads(subprocess.getoutput("vnstat --json m 6 -i eth0"))
    monthly_data = raw_month_data['interfaces'][0]['traffic']['month']
    return monthly_data

def parseDate(raw_date):
    try:
        date = (f"{raw_date['day']}/{raw_date['month']}/{raw_date['year']}")
    except KeyError:
        date = (f"{raw_date['month']}/{raw_date['year']}")
    return date

def getData(item):
    date = parseDate(item['date'])
    
    rx = item['rx']
    tx = item['tx']

    vrx = round(rx/1000000000,2)
    vtx = round(tx/1000000000,2)
    total = round(vrx+vtx,2)
    
    return date,vrx,vtx,total

def getHist(data):
    dates = []
    vrxs = []
    vtxs = []
    totals = []
    for item in data:
        date,vrx,vtx,total=getData(item)
        dates.append(date)
        vrxs.append(vrx)
        vtxs.append(vtx)
        totals.append(total)
        
    return dates,vrxs,vtxs,totals

app = Flask(__name__)
@app.route("/")
def index():
    monthly_data = getMonthly()
    daily_data = getDaily()
    
    hd_dates,hd_vrx,hd_vtx,hd_total=getHist(daily_data) # hd stands for Historical Daily, td is This Day
    hm_dates,hm_vrx,hm_vtx,hm_total=getHist(monthly_data) # hm stands for Historical Monthly, tm is This Month
    return render_template("index.html",hd_dates=hd_dates,hd_vrx=hd_vrx,hd_vtx=hd_vtx,hd_total=hd_total,
                           hm_dates=hm_dates,hm_vrx=hm_vrx,hm_vtx=hm_vtx,hm_total=hm_total,
                           td_vrx=hd_vrx[-1],td_vtx=hd_vtx[-1],td_total=hd_total[-1],
                           tm_vrx=hm_vrx[-1],tm_vtx=hm_vtx[-1],tm_total=hm_total[-1])
app.run(host="0.0.0.0", port=server_port)