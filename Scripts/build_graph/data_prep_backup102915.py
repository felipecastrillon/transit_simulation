# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 13:08:30 2015

@author: fcastrillon3
"""

import pandas as pd
from collections import defaultdict
from geopy.distance import vincenty
from math import floor,pow
import json
from math import sqrt
from operator import itemgetter


GRID_SIZE = 2 # number of decimal points. Approximates .5 mi +/- in Atlanta
DAYCODE = 5 # 3 is Saturday, 4 is Sunday, 5 is weekday
TRIP_FILTER = [] #trip id's that fall in daycode

def readStopTimes():    
    df = pd.read_csv("Y:\\rg49-winsrv1-gis\\gis_data\\BaseMap" \
    "\\Maps for Dr. Guensler\\I-285 Corridor\\grfs 08082015" \
    "\\gtfs_08082015_alldata\\stop_times.txt")
    #df = pd.read_csv("C:\\Users\\felipecastrillon\\Documents\\Marta" \
    #"\\stop_times.txt",nrows=100)
    def fx(x):
        l = x.split(':')
        return int(l[0]) * 3600 + int(l[1]) * 60 + int(l[2])

    df['tseg'] = df.arrival_time.apply(fx)
    return df


def readStops():
    df = pd.read_csv("Y:\\rg49-winsrv1-gis\\gis_data\\BaseMap" \
    "\\Maps for Dr. Guensler\\I-285 Corridor\\grfs 08082015" \
    "\\gtfs_08082015_alldata\\stops.txt")
    #df = pd.read_csv("C:\\Users\\felipecastrillon\\Documents\\Marta\\stops.txt")
        
    return df

def createTripFilter():   
    df = pd.read_csv("Y:\\rg49-winsrv1-gis\\gis_data\\BaseMap" \
    "\\Maps for Dr. Guensler\\I-285 Corridor\\grfs 08082015" \
    "\\gtfs_08082015_alldata\\trips.txt")
    #df = pd.read_csv("C:\\Users\\felipecastrillon\\Documents\\Marta\\stops.txt")
    
    for j, row in df.iterrows(): 
        if row['service_id'] == DAYCODE:
            TRIP_FILTER.append(row['trip_id'])     
    print len(TRIP_FILTER)
    
def saveStopandWalkEvents(df):
    events_at_stop = defaultdict(list) 
    event_id = defaultdict(list)
    stop_id = json.load(open('stop_id.json'))
    event_pos = defaultdict(list)
    nearby_stops = json.load(open('nearby_stops.json'))
    #outfile = open('graph.txt', 'a')
    avg_walk_spd = 3.1
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
        
        #filter out trips by day        
        if row['trip_id'] not in TRIP_FILTER: 
            continue;        
        
        #create node code   
        this_event = "s"+str(row['stop_id'])+"t"+str(row['tseg'])
        this_stop = row['stop_id']          
        this_time = row['tseg']
        
        if True:
            # if new stop event, create hash value based on codes
            #if this_event not in event_id:
            #    event_id[this_event] = i
            #    event_pos[this_event] = (this_time,stop_id[str(this_stop)])                         
            #    i = i + 1
                
            #save event by stop by stop_id
            events_at_stop[this_stop].append(this_time)                    
        
        if str(this_stop) not in nearby_stops:
            continue;
        if True:
            #create walk events
            for tup in nearby_stops[str(this_stop)]:
                nearby_stop = tup[0]
                distance = tup[1]
    
                #walk_times
                manhattan_dist = distance * 2 /sqrt(2) 
                walk_time = int(manhattan_dist*3600/avg_walk_spd)
                
                #create next event 
                #next_event = "s"+str(nearby_stop)+"t"+str(this_time+walk_time)
                #outfile.write(str(this_event)+","+str(next_event)+","+
                #    str(walk_time)+","+"walk"+"\n")
                # if new stop event, create hash value based on codes
                #if next_event not in event_id:
                #    event_id[next_event] = i
                #    event_pos[next_event] = (this_time+walk_time,stop_id[str(nearby_stop)])                         
                #    i = i + 1
                
                events_at_stop[nearby_stop].append(this_time+walk_time)                    
                outfile.write(this_event+","+next_event+"\n")
        
     #json.dump(events_walk, open('events_walk.json', 'w'))
    #json.dump(event_id, open('event_id.json', 'w'))
    #json.dump(event_pos, open('event_pos.json', 'w'))
    json.dump(events_at_stop, open('events_at_stop.json', 'w'))
                
    outfile.close() 

def printEventsAtStop():
    events_at_stop = json.load(open('events_at_stop.json')) 
    outfile=open('graph.txt','a')
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
                    outfile.write(str(last_event)+","+str(this_event)+","+
                        str(this_time-last_time)+","+"wait"+"\n")
                    
                #update last node
                last_time = this_time
    outfile.close()

def saveWalkEventsAtStops(df):

    
    #json.dump(events_walk, open('events_walk.json', 'w'))
    json.dump(event_id, open('event_id.json', 'w'))
    json.dump(event_pos, open('event_pos.json', 'w'))
    json.dump(events_at_stop, open('events_at_stop.json', 'w'))

         
def saveBusEvents(df):
    events_bus = defaultdict(list)
    outfile = open('graph.txt', 'a')
    j = 0

   #read all events and save in dict
    print "reading stop_times.txt"
    length  = float(len(df))

    for j, row in df.iterrows():  
        
                #keep track of file progress
        if j%100000 ==0:
            print "progress..."            
            print j/length
            j+=1        
        
        if row['trip_id'] in TRIP_FILTER:    
            code = (row['stop_id'], row['tseg'])  
            
            # save stop event for every bus trip   s
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
                outfile.write(str(last_event)+","+str(this_event)+","+
                    str(this_time-last_time)+","+"transit"+"\n")                
                
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
        
        #create stop id            
        if row['stop_id'] not in stop_id:
            stop_id[row['stop_id']] = k
            k = k + 1
        
        this_stop = row['stop_id']    
        
        lat_sq = floor(row['stop_lat']*pow(10.0,GRID_SIZE))/pow(10.0,GRID_SIZE)
        lon_sq = floor(row['stop_lon']*pow(10.0,GRID_SIZE))/pow(10.0,GRID_SIZE)
        grid_pts[str(lat_sq)+","+ str(lon_sq)].append(this_stop)   

    json.dump(stop_id, open('stop_id.json', 'w'))

    return grid_pts
    
    
def saveNearbyStopsFromStop(df,grid_pts):
    nearby_stops = defaultdict(list)    
    latlon = {}  
    #create lat-lon coordinates       
    for j, row in df.iterrows():          
        this_stop = row['stop_id']   
        #save lattitude and longitude
        latlon[this_stop] = (row['stop_lat'], row['stop_lon'])
    
    #get nearby stops using square grid
    for j, row in df.iterrows():
        this_stop = row['stop_id']
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
                    distance = vincenty(latlon[this_stop],latlon[other_stop]).miles
                    if distance <= 1.0:              
                        nearby_stops[this_stop].append((other_stop,distance))  
                        nearby_stops[other_stop].append((this_stop,distance)) 
    
    json.dump(nearby_stops, open('nearby_stops.json', 'w'))

        
def main():
    #must be run in this order
    #createTripFilter()
    #df_stops = readStops()
    #df_stop_times = readStopTimes()
    #saveTripDays(df_trips)
    #saveNearbyStopsFromStop(df_stops, getStopsByGrid(df_stops))
    #saveStopandWalkEvents(df_stop_times)   
    #saveBusEvents(df_stop_times)
    printEventsAtStop()
    
main()    
