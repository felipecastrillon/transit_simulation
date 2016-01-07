# -*- coding: utf-8 -*-
"""
Created on Mon Oct 05 11:31:04 2015

@author: fcastrillon3
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
import datetime
import os
import math
import collections
import sys

origin = 'AIRPORT STATION'
destination = 'BUFORD HWY @ CHAMBLEE TUCKER RD'
arrivalt = '7:00:00'


os.chdir('/home/felipe/Dropbox/Research/Energy/Scripts')
print "reading stop events. Current time"+str(datetime.datetime.now())
STOP_EVENTS = json.load(open('events_at_stop.json'))
print "saving graph. Current time"+str(datetime.datetime.now())
  
GRAPH = nx.read_edgelist('links.txt', nodetype=str, delimiter=",", \
    data=(('weight',float),('type',str),('lat_or',float),('lat_dest',float),('lon_or',float),
    ('lon_dest',float),('time_or',float),('time_dest',float),),create_using=nx.DiGraph() )

def printGraph():
    event_pos = {k:[int(i) for i in v] for k,v in EVENT_POS.items()}
    nx.draw(GRAPH,event_pos,node_size=15)
    plt.rcParams['figure.figsize'] = 20, 5    
    plt.show()
    
def clearAll():
    global STOP_EVENTS
    global EVENT_POS
    global GRAPH
    STOP_EVENTS = []
    EVENT_POS = []
    GRAPH = []    

def getShortestTravelTime(start_time, origin, destination):
    path = []
    print "start time "+start_time
    print "start station "+str(origin)
    print "end station "+str(destination)
    foo = start_time.split(':')    
    startt = float(foo[0]) + float(foo[1]) / 60 + float(foo[2])/3600
    print "startt " + str(startt)    
    
    #get events at origin and destination
    events_start = STOP_EVENTS[str(origin)]
    events_end  = STOP_EVENTS[str(destination)] 
    events_start.sort()
    events_end.sort()
    print "events start" + str(events_start)
    print "events end" + str(events_end)

    #loop through event times and get nearest arrival time at destination
    arrival_time = 24 #hours in day    
        
    for t1 in events_start:
        if t1 < startt or t1 > arrival_time:
            continue;
        for t2 in events_end:
            if t2 < t1 or t2 < startt or t2 >= arrival_time:
                continue;      
            
            #get start and end nodes
            start_node = "s"+str(origin)+"t"+str(t1)            
            end_node = "s"+str(destination)+"t"+str(t2) 
            print "testing if shortest path from "+str(t1)+ "to"+str(t2)+"exists\n"
            if nx.has_path(GRAPH,start_node,end_node):
                arrival_time = t2
                path = nx.dijkstra_path(GRAPH,start_node,end_node)
                print arrival_time

    if not path:
      print "no path exists"
      sys.exit(0)             
    return (arrival_time,path)            

def path_edge_attributes(path):
    return [(GRAPH[u][v]['lat_or'],GRAPH[u][v]['lon_or'],GRAPH[u][v]['time_or'],GRAPH[u][v]['lat_dest'],GRAPH[u][v]['lon_dest'], GRAPH[u][v]['time_dest']) for (u,v )in zip(path[0:],path[1:])]

def drawGraph():
    global event_pos
    event_pos = {int(k):[int(i) for i in v] for k,v in event_pos.items()}
    nx.draw(GRAPH,event_pos,node_size=15)
    plt.rcParams['figure.figsize'] = 20, 5    
    plt.show()
           
def outputPath(edges):
    outfile = open("path.txt","w")
    outfile.write("lat,lon,time\n")
    for i,x in enumerate(edges):
        outfile.write(str(x[0])+","+str(x[1])+","+str(x[2])+"\n")
        if i == len(edges)-1:
          outfile.write(str(x[3])+","+str(x[4])+","+str(x[5])+"\n")
    outfile.close()
           
#printGraph()
print "getting shortest path. Current time"+str(datetime.datetime.now())
tup = getShortestTravelTime(arrivalt,origin,destination)
arrival_t = tup[0]*3600
path = tup[1]
print "done getting shortest path. Current time"+str(datetime.datetime.now())
print "unix time" + str(arrival_t * 3600)
hrs = int(math.floor(arrival_t/3600))
mins = int(math.floor((arrival_t-3600*hrs)/60))
secs = int(arrival_t-3600*hrs-60*mins)
if len(str(mins)) == 1:
  mins = "0"+str(mins)
if len(str(secs)) == 1:
  secs = "0"+str(secs)
print "arrival time" + str(hrs) +":"+ str(mins) +":"+ str(secs)
outputPath(path_edge_attributes(path))


