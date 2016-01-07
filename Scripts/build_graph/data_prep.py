# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 13:08:30 2015

@author: fcastrillon3
"""

import pandas as pd
from collections import defaultdict
from geopy.distance import vincenty
import math
import json
from math import sqrt,floor,pow
from operator import itemgetter
import os

GRID_SIZE = 2 # number of decimal points. Approximates .5 mi +/- in Atlanta
DAYCODE = 5 # 3 is Saturday, 4 is Sunday, 5 is weekday
TRIP_FILTER = [] #trip id's that fall in daycode
ROUTES = {}
STOP_NAME ={}
ROUTE_FILTER = [8746,7658] #7658-buford
RAIL_LINES = [8766,8746,8748,8747]
STOP_FILTER = [] #filter for stops that are in the route filter
TIME_FILTER = [7.00,8.0]
LAT = {} # lattitutde and longitude of each stop
LON = {}

def readStopTimes():    
    df = pd.read_csv("../Data/stop_times.txt")
    #df = pd.read_csv("C:\\Users\\felipecastrillon\\Documents\\Marta" \
    #"\\stop_times.txt",nrows=100)
    def fx(x):
        l = x.split(':')
        return (float(l[0]) * 3600 + float(l[1]) * 60 + float(l[2]))/3600.0

    df['thrs'] = df.arrival_time.apply(fx)
    return df

def readStops():
    df = pd.read_csv("../Data/stops.txt")
    return df

def prepareStopData(df):          
    for j, row in df.iterrows():   
        #create lat-lon coordinates        
        this_stop = row['stop_id']  
        #save lattitude and longitude
        if this_stop not in STOP_NAME:
          STOP_NAME[this_stop] = row['stop_name']
          LAT[STOP_NAME[this_stop]] = row['stop_lat']
          LON[STOP_NAME[this_stop]] = row['stop_lon']

def prepareStopTimeData(df):
    #populate stop filters 
    for j, row in df.iterrows(): 
        this_stop = STOP_NAME[row['stop_id']]  
        if ROUTES[row['trip_id']] in ROUTE_FILTER and this_stop not in STOP_FILTER: 
            STOP_FILTER.append(this_stop) 

def prepareTripData():   
    df = pd.read_csv("../Data/trips.txt")
    
    for j, row in df.iterrows(): 
        #populate trips on by day code
        if row['service_id'] == DAYCODE:
            TRIP_FILTER.append(row['trip_id'])    
        #populate routes for each trip
        ROUTES[row['trip_id']] = row['route_id']  
    print len(TRIP_FILTER)

def saveStopandWalkEvents(df):
    events_at_stop = defaultdict(list) 
    event_id = defaultdict(list)
    stop_id = json.load(open('stop_id.json'))
    event_pos = defaultdict(list)
    nearby_stops = json.load(open('nearby_stops.json'))
    outfile = open('links.txt', 'a')
    outfile2 = open('nodes.txt', 'a')
    avg_walk_spd = 3.1 #mph
    i = 1
    j=0
    
    print "read stop_times.txt"
    length = float(len(df))
    for j, row in df.iterrows():  
        
        #keep track of file progress
        if j%100000 ==0:
            print "progress reading file..."
            print j/length
            j+=1

        #filter by routes, hour and days
        if ROUTES[row['trip_id']] not in ROUTE_FILTER:
            continue
        if row['thrs']<TIME_FILTER[0] or row['thrs']>TIME_FILTER[1]:
            continue       
        if row['trip_id'] not in TRIP_FILTER: 
            continue; 

        #create node code   
        this_stop = STOP_NAME[row['stop_id']]          
        this_time = row['thrs']
        this_event = "s"+str(this_stop)+"t"+str(row['thrs'])
        
        #save event by stop by stop_id
        events_at_stop[this_stop].append(this_time)                    
        
        #walk events
        if str(this_stop) not in nearby_stops:
            continue;
        if False:
            #create walk events
            for tup in nearby_stops[str(this_stop)]:
                nearby_stop = tup[0]
                distance = tup[1]
    
                #walk_times
                manhattan_dist = distance * (2/sqrt(2)) 
                walk_time = manhattan_dist/avg_walk_spd

                #create next event 
                next_event = "s"+str(nearby_stop)+"t"+str(this_time+walk_time)

                if LAT[this_stop] == LAT[nearby_stop] and \
                            LON[this_stop] == LON[nearby_stop]:
                        continue

                outfile.write(str(this_event)+str(next_event)+","+str(walk_time)+","+
                              "walk"+","+str(LAT[this_stop])+","+ str(LAT[nearby_stop])+
                    str(LON[this_stop])+","+str(LON[nearby_stop]) +
                    ","+ str(this_time)+","+str(this_time+walk_time)+"\n")
                
                events_at_stop[nearby_stop].append(this_time+walk_time) 

                outfile2.write(str(LAT[nearby_stop])+','+str(LON[nearby_stop])+
                    ','+str(this_time+walk_time)+','+next_event+"\n")                   
        
     #json.dump(events_walk, open('events_walk.json', 'w'))
    #json.dump(event_id, open('event_id.json', 'w'))
    #json.dump(event_pos, open('event_pos.json', 'w'))
    json.dump(events_at_stop, open('events_at_stop.json', 'w'))
    events_at_stop = []            
    outfile.close() 
    outfile2.close()

def printEventsAtStop():
    events_at_stop = json.load(open('events_at_stop.json')) 
    outfile=open('links.txt','a')
    j = 1
    
    print "creating events at stop from dict"
    length = float(len(events_at_stop))
    for this_stop,events in events_at_stop.iteritems():              

        #keep track of file progress
        if j%50000 ==0:
            print "progress..."
            print j/length
            j+=1

        # create 'wait at stop' links
        if len(events) > 1:   
            events.sort()
            last_time = 0
            #create links between every stop
            for this_time in events:   
                this_event = "s"+str(this_stop)+"t"+str(this_time)
            # create stop links from last to current node
                if last_time != 0:
                    last_event = "s"+str(this_stop)+"t"+str(last_time)
                    #edge_list.append((last_event,this_event,this_time-last_time))
                    outfile.write(str(last_event)+","+str(this_event)+","+str(this_time-last_time)+","+
                      'wait'+ "," + str(LAT[this_stop])+","+ str(LAT[this_stop])+","+ str(LON[this_stop])+","+
                      str(LON[this_stop]) + ","+ str(last_time)+","+ str(this_time)+"\n")

                #update last node
                last_time = this_time
    outfile.close()
     
def saveBusEvents(df):
    events_bus = defaultdict(list)
    outfile = open('links.txt', 'w')
    j = 0

   #read all events and save in dict-----
    print "reading stop_times.txt"
    length  = float(len(df))

    for j, row in df.iterrows():  
        
        #filter by defined routes and time
        if ROUTES[row['trip_id']] not in ROUTE_FILTER:
            continue
        if row['thrs']<TIME_FILTER[0] or row['thrs']>TIME_FILTER[1]:
            continue        

        #keep track of file progress
        if j%100000 ==0:
            print "progress..."            
            print j/length
            j+=1        
        
        if row['trip_id'] in TRIP_FILTER:    
            code = (STOP_NAME[row['stop_id']], row['thrs'])  
            
            # save stop event for every bus trip   
            this_bus = row['trip_id']
            events_bus[this_bus].append(code)     
    
    #create graph links for every bus trip   
    j=1    
    
    print "create graph links for bus trips"
    length  = float(len(events_bus))

    for this_bus,events in events_bus.iteritems():  

        #keep track of file progress
        if j%100000 ==0:
            print "progress..."            
            print j/length
            j+=1   

        if len(events) == 1:   
            continue

        #check if bus or rail
        type = "bus"    
        if ROUTES[this_bus] in RAIL_LINES:
            type = "rail"

        #initialize    
        last_event = 0
        last_stop = 0
        this_time = 0
        last_time = 0
        
        #sort events by time
        sorted(events, key=itemgetter(1))
        
        #create links between every stop
        for this_event_tup in events:     
            this_stop = this_event_tup[0]
            this_time = this_event_tup[1]
            this_event = "s"+str(this_stop)+"t"+str(this_time)                
            cont = 0
            
            # create edge from last to current node
            if last_event > 0 and cont == 0:
                #edge_list.append((last_event,this_event,this_time-last_time))
                outfile.write(str(last_event)+","+str(this_event)+","+str(this_time-last_time)+','+
                      type+","+str(LAT[last_stop])+","+str(LAT[this_stop])+","+
                      str(LON[last_stop])+","+str(LON[this_stop]) + ","+str(last_time)+","+
                      str(this_time)+"\n") 
         
            #update last node
            last_event = this_event  
            last_stop = this_stop
            last_time = this_time
                
                
    #add links to graph
    #GRAPH.add_weighted_edges_from(edge_list,linktype="bus") 
    outfile.close()                
        
def getStopsByGrid(df):
    stop_id = defaultdict(list)
    grid_pts =  defaultdict(list) #divide space into a grid an place points on
                                #square
    k = 1
    
    for j, row in df.iterrows():         
        this_stop = STOP_NAME[row['stop_id']]         
        
        #filter by defined route stops
        if this_stop not in STOP_FILTER:
            continue
              
        lat_sq = floor(row['stop_lat']*pow(10.0,GRID_SIZE))/pow(10.0,GRID_SIZE)
        lon_sq = floor(row['stop_lon']*pow(10.0,GRID_SIZE))/pow(10.0,GRID_SIZE)
        if this_stop not in grid_pts:
          grid_pts[str(lat_sq)+","+ str(lon_sq)].append(this_stop)   
  
    return grid_pts
    
def saveNearbyStopsFromStop(df,grid_pts):
    nearby_stops = defaultdict(list)    
    
    #get nearby stops using square grid
    for j, row in df.iterrows():
        this_stop = STOP_NAME[row['stop_id']]

        #filter by defined route stops
        if this_stop not in STOP_FILTER:
            continue

        #get lat lon coords        
        lat_sq = floor(row['stop_lat']*pow(10.0,GRID_SIZE))/pow(10.0,GRID_SIZE)
        lon_sq = floor(row['stop_lon']*pow(10.0,GRID_SIZE))/pow(10.0,GRID_SIZE)
        #loop through stops in sourrouding grids
        for x in (lat_sq-0.01,lat_sq,lat_sq+0.01):
            for y in (lon_sq-0.01,lon_sq,lon_sq+0.01):
                for other_stop in grid_pts[str(x)+","+ str(y)]:
                    if (this_stop == other_stop or 
                            other_stop in nearby_stops[this_stop]):
                        continue
                    #if two stops are within X miles
                    print "this stop" + str(this_stop)
                    print "other stop" + str(other_stop)
                    print "this stop lat" + str(LAT[this_stop])
                    print "this stop lon" + str(LON[this_stop])
                    print "other stop lat" + str(LAT[other_stop])
                    print "other stop lon" + str(LON[other_stop])
                    distance = vincenty((LAT[this_stop],LON[this_stop]),(LAT[other_stop],LON[other_stop])).miles
                    if distance <= 0.5:              
                        nearby_stops[this_stop].append((other_stop,distance))  
                        nearby_stops[other_stop].append((this_stop,distance)) 
    
    json.dump(nearby_stops, open('nearby_stops.json', 'w'))

def createNodes(df):
    outf = open('nodes.txt','w')
    
    #read stop times and save
    for i, row in df.iterrows(): 
        #filter by defined routes
        if ROUTES[row['trip_id']] not in ROUTE_FILTER:
            continue
        if row['thrs']<TIME_FILTER[0] or row['thrs']>TIME_FILTER[1]:
            continue 
        if row['trip_id'] not in TRIP_FILTER:         
            continue    
        this_stop = STOP_NAME[row['stop_id']]
        this_event = "s"+str(this_stop)+"t"+str(row['thrs'])  

        outf.write(str(LAT[this_stop])+","+str(LON[this_stop])+","+str(row['thrs'])+","+str(STOP_NAME[row['stop_id']])+'\n')

    outf.close()

def main():
    #prepare data and filters
    print "\npreparing trip data---------"
    prepareTripData() 
    print "\npreparing stop data---------"
    df_stops = readStops()
    prepareStopData(df_stops)
    print "\npreparing stop time data---------"
    df_stop_times = readStopTimes()
    prepareStopTimeData(df_stop_times)
        
    #print "\nsave nearby stops from stop---------"
    #saveNearbyStopsFromStop(df_stops, getStopsByGrid(df_stops))
    print "\ncreate nodes---------"
    createNodes(df_stop_times)
    #print "\nsave bus events---------"
    #saveBusEvents(df_stop_times)
    #print "\nsave stop and walk events---------"
    #saveStopandWalkEvents(df_stop_times)   
    #print "\nprint events at stop---------"
    #printEventsAtStop()
    
main()    


