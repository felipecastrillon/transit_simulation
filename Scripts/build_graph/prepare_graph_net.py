import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import pandas as pd
import json
from operator import itemgetter
from math import sqrt
import operator


GRAPH = nx.DiGraph()
GRID_SIZE = 2 #decimal points. Approximates .5 mi +/- in Atlanta
nearby_stops = json.load(open('nearby_stops.json'))
stop_id = json.load(open('stop_id.json'))
event_id = json.load(open('event_id.json'))
event_pos = json.load(open('event_pos.json'))
events_at_stop = json.load(open('events_at_stop.json')) 
BUS_EVENTS = json.load(open('event_bus.json')) 

def clearAll():
    global nearby_stops
    global stop_id
    global event_id
    global event_pos
    global events_at_stop
    global BUS_EVENTS
    nearby_stops = []
    stop_id = []
    event_id = []
    event_pos = []
    events_at_stop = []
    BUS_EVENTS = []
    

def createBusLinks():
    edge_list = []
    last_event = 0

    for this_bus,events in BUS_EVENTS.iteritems():  

        # create 'wait at stop' links
        if len(events) == 1:   
            continue
        last_event = 0
        last_stop = 0
        this_time = 0
        
        #sort events by time
        sorted(events, key=itemgetter(1))
        
        #create links between every stop
        for this_event_tup in events:     
            this_stop = this_event_tup[0]
            this_time = this_event_tup[1]
            this_event = "s"+str(this_stop)+"t"+str(this_time)                
            cont = 0
            if int(this_time) < 6*3600 or int(this_time) > 9*3600:
                cont = 1;
            if stop_id[str(this_stop)] != 5001 and stop_id[str(this_stop)] != 4975 \
            and stop_id[str(this_stop)] != 4966 and stop_id[str(this_stop)] != 4947 \
            and stop_id[str(this_stop)] != 4948 and stop_id[str(this_stop)] != 4949 \
            and stop_id[str(this_stop)] != 4977 and stop_id[str(this_stop)] != 4933:
                cont=1     
            if last_stop != 0 and stop_id[str(last_stop)] != 5001 \
            and stop_id[str(last_stop)] != 4975 \
            and stop_id[str(last_stop)] != 4966 and stop_id[str(last_stop)] != 4947 \
            and stop_id[str(last_stop)] != 4948 and stop_id[str(this_stop)] != 4949 \
            and stop_id[str(this_stop)] != 4977 and stop_id[str(this_stop)] != 4933:
                cont=1 
            
            # create edge from last to current node
            if last_event > 0 and cont == 0:
                edge_list.append((last_event,this_event,this_time-last_time))

            #update last node
            last_event = this_event  
            last_stop = this_stop
            last_time = this_time
                
                
    #add links to graph
    GRAPH.add_weighted_edges_from(edge_list,linktype="bus")    

def createStopAndWalkLinks():
    edge_list = []   
    avg_walk_spd = 3.1
    i = event_id[max(event_id.iteritems(), key=operator.itemgetter(1))[0]] + 1
    #create links at each stop    
    for this_stop,events in events_at_stop.iteritems():              
        
        if stop_id[str(this_stop)] != 5001 and stop_id[str(this_stop)] != 4975 \
                and stop_id[str(this_stop)] != 4966 and stop_id[str(this_stop)] != 4947 \
                and stop_id[str(this_stop)] != 4948 and stop_id[str(this_stop)] != 4949 \
                and stop_id[str(this_stop)] != 4977 and stop_id[str(this_stop)] != 4933:
                    continue           

        # create 'wait at stop' links
        if len(events) > 1:   
            events.sort()
            last_time = 0
            #create links between every stop
            for this_time in events:   
                if int(this_time) < 6*3600 or int(this_time) > 9*3600:
                    continue
                this_event = "s"+str(this_stop)+"t"+str(this_time)
                
                #create walk links to nearby stops
                for tup in nearby_stops[this_stop]:
                    nearby_stop = tup[0]
                    distance = tup[1]
                    
                    #filter
                    if stop_id[str(nearby_stop)] != 5001 and stop_id[str(nearby_stop)] != 4975 \
                            and stop_id[str(nearby_stop)] != 4966 and stop_id[str(nearby_stop)] != 4947 \
                            and stop_id[str(nearby_stop)] != 4948 and stop_id[str(nearby_stop)] != 4949 \
                            and stop_id[str(nearby_stop)] != 4977 and stop_id[str(nearby_stop)] != 4933:
                        continue                      

                    #walk_times
                    manhattan_dist = distance * 2 /sqrt(2) 
                    walk_time = int(manhattan_dist*3600/avg_walk_spd)
                    
                    #create link and save
                    next_event = "s"+str(nearby_stop)+"t"+str(this_time+walk_time)
                                        
                    #add walk links to graph
                    if next_event not in event_id:
                        event_id[next_event] = i
                        i+=1                          
                    event_pos[next_event] = (this_time+walk_time,stop_id[str(nearby_stop)])                      
                    edge_list.append((this_event,next_event,walk_time))                
            
                # create stop links from last to current node
                if last_time != 0 and int(this_time) >= 6*3600 and int(this_time) <= 9*3600:
                    last_event = "s"+str(this_stop)+"t"+str(last_time)
                    edge_list.append((last_event,this_event,this_time-last_time))
                #update last node
                last_time = this_time
    #add links to graph
    json.dump(event_id, open('event_id.json', 'w'))
    json.dump(event_pos, open('event_pos.json', 'w'))
    GRAPH.add_weighted_edges_from(edge_list,linktype ='walk')
        
def drawGraph():
    global event_pos
    event_pos = {int(k):[int(i) for i in v] for k,v in event_pos.items()}
    nx.draw(GRAPH,event_pos,node_size=15)
    plt.rcParams['figure.figsize'] = 20, 5    
    plt.show()

def outputGraph():
    d = dict(id='id', source='source', target='target', key='key')
    graph = json_graph.node_link_data(GRAPH,d)
    json.dump(graph, open('graph.json', 'w'))

createStopAndWalkLinks()
createBusLinks()
outputGraph()
clearAll()