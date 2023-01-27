#!/bin/python3

import json
import subprocess
from flask import Flask, render_template

server_port = 7667
server_name = "OrbitSrv"

def getDaily():
    raw_day_data = json.loads(subprocess.getoutput("vnstat --json d 7 -i eth0"))
    daily_data = raw_day_data['interfaces'][0]
    last_updated = parseDateTime(daily_data['updated']['date'],daily_data['updated']['time'])
    daily_traffic = daily_data['traffic']['day']
    return daily_traffic,last_updated

def getMonthly():
    raw_month_data = json.loads(subprocess.getoutput("vnstat --json m 6 -i eth0"))
    monthly_traffic = raw_month_data['interfaces'][0]['traffic']['month']
    return monthly_traffic

def getTop():
    raw_top_data = json.loads(subprocess.getoutput("vnstat --json t 5 -i eth0"))
    top_traffic = raw_top_data['interfaces'][0]['traffic']['top']
    return top_traffic

def parseDateTime(raw_date,raw_time=""):
    try:
        date = (f"{raw_date['day']:02d}/{raw_date['month']:02d}/{raw_date['year']}")
    except KeyError:
        date = (f"{raw_date['month']:02d}/{raw_date['year']}")
    datetime = date
    if raw_time != "":
        time = (f"{raw_time['hour']:02d}:{raw_time['minute']:02d}")
        datetime = (date+" at "+time)
        
    return datetime

def getData(item):
    date = parseDateTime(item['date'])
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
    monthly_traffic = getMonthly()
    daily_traffic,last_updated = getDaily()
    top_traffic = getTop()
    
    hd_dates,hd_vrx,hd_vtx,hd_total=getHist(daily_traffic) # hd stands for Historical Daily, td is This Day
    hm_dates,hm_vrx,hm_vtx,hm_total=getHist(monthly_traffic) # hm stands for Historical Monthly, tm is This Month
    t_dates,t_vrx,t_vtx,t_total=getHist(top_traffic) # t stands for Top
    return render_template("index.html",last_updated=last_updated,server_name=server_name,
                           hd_dates=hd_dates,hd_vrx=hd_vrx,hd_vtx=hd_vtx,hd_total=hd_total,
                           hm_dates=hm_dates,hm_vrx=hm_vrx,hm_vtx=hm_vtx,hm_total=hm_total,
                           t_dates=t_dates,t_vrx=t_vrx,t_vtx=t_vtx,t_total=t_total,
                           td_vrx=hd_vrx[-1],td_vtx=hd_vtx[-1],td_total=hd_total[-1],
                           tm_vrx=hm_vrx[-1],tm_vtx=hm_vtx[-1],tm_total=hm_total[-1])
    
app.run(host="0.0.0.0", port=server_port)