from __future__ import division, absolute_import, print_function
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, os, sys
import numpy as np
import echo_chamber_util as e_util
import util as my_util
import user_diversity as polar
from time import time
from operator import itemgetter
from graph_tool import util
from graph_tool.all import *
from random import shuffle


#draw echo chamber network and save in the file
def draw_graph():
    g = Graph(directed=False)
    vprop = g.new_vertex_property("string")
    vuser = g.new_vertex_property("string")
    vsize = g.new_vertex_property("int")
    vcolor = g.new_vertex_property("vector<double>")
    #vcolor = g.new_vertex_property("string")
    eprop = g.new_edge_property("string")
    eweight = g.new_edge_property("int")

    #colors = ["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"]
    colors = [(255,255,204), (161,218,180), (65,182,196), (44,127,184), (37,52,148), (254,204,92)]
    colors = [(213,62,79), (244,109,67), (253,174,97), (254,224,139), (255,255,191), (230,245,152), (171,221,164), (102,194,165), (50,136,189), (26,152,80), (255,255,0)]
    colors = [(255,255,217), (247,252,240), (237,248,177), (199,233,180), (127,205,187), (65,182,196), (29,145,192), (34,94,168), (37,52,148), (8,29,88), (255,255,0)]
    colors = [tuple(map(lambda x : x/255, color)) for color in colors]
    echo_colors = colors[-1]

    files = os.listdir('RetweetNew/')
    shuffle(files)
    nodes = {}
    nodes_per_user = {}
    root_tweet = {}
    for ccc, postid in enumerate(files):
        f = open('RetweetNew/' + postid, 'r') 
        tweets = json.load(f)
        f.close()

        parent_child = {}
        nodes[postid] = {}
        nodes_per_user[postid] = {}
        users = {}
        cascade_size = {}
        for tweet in tweets.values():
            parent = tweet['parent_tweet']
            parent_user = tweet['parent']
            root = tweet['origin_tweet']
            tid = tweet['tweet']
            user = tweet['user']
            size = tweet['cascade']
            if size < 5:
                continue

            if tid != parent:
                parent_child[parent] = parent_child.get(parent, [])
                parent_child[parent].append(tid)
                users[parent] = parent_user
                users[tid] = user
                nodes_per_user[postid][user] = []
                nodes_per_user[postid][parent_user] = []
                cascade_size[root] = size
                root_tweet[tid] = root
                root_tweet[parent] = root
        
        #for p in parent_child.keys():
            #v = g.add_vertex()
            #nodes[postid][p] = str(v)
            #vcolor[v] = colors[ccc]
            #vuser[v] = users[p]
            #vsize[v] = 5
            #nodes_per_user[postid][users[p]].append(v)

        print(cascade_size.values())
        for p in parent_child.keys():
            if nodes[postid].get(p, None) == None:
                v1 = g.add_vertex()
                nodes[postid][p] = str(v1)
                vcolor[v1] = colors[ccc]
                vuser[v1] = users[p]
                vsize[v1] = 4
                vprop[v1] = str(v1)
                nodes_per_user[postid][users[p]].append(v1)
            else:
                v1 = nodes[postid][c]

            #print(v1, len(parent_child[p]))
            for c in parent_child[p]:
                if nodes[postid].get(c, None) == None:
                    v2 = g.add_vertex()
                    nodes[postid][c] = str(v2)
                    vcolor[v2] = colors[ccc]
                    vuser[v2] = users[c] 
                    vsize[v2] = 4
                    vprop[v2] = str(v2)
                    nodes_per_user[postid][users[c]].append(v2)
                else:
                    v2 = nodes[postid][c]
                
                #print(root_tweet[c], v1, v2)
                #print(root_tweet[c], p, c)
                e1 = g.add_edge(v1, v2)
                cascade_size[root_tweet[c]] -= 1

        print(cascade_size.values())
        if ccc == 6:
            break

    with open('Data/echo_chamber2.json', 'r') as f:
        echo_chamber = json.load(f)

    #edge between echo chambers 
    rumors = nodes.keys()
    #print(rumors)
#    print(nodes)
    for i in range(len(rumors)):
        tweet_list1 = nodes[rumors[i]].values() #vertex list 1
 #       print(tweet_list1) 
        for j in range(i+1, len(rumors)):

            r1 = rumors[i]
            r2 = rumors[j]
            
            #check echo chamber user exist between two rumors 
            if echo_chamber.get('%s_%s'%(r1, r2), None) != None:
                echo_users = echo_chamber['%s_%s'%(r1, r2)]
            else: 
                echo_users = echo_chamber['%s_%s'%(r2, r1)]

            if echo_users < 2:
                continue

            #print(r1, r2)
            #print(echo_users)
            tweet_list2 = nodes[rumors[j]].values() #vetext list 2

            for user in echo_users:
                try : #when user participate in small cascade (lower than 5), key error will happen
                    v_list1 = nodes_per_user[r1][user] #vertex list 
                    v_list2 = nodes_per_user[r2][user] #vertex list 
                    #print(v_list1, v_list2)
                    for v1 in v_list1:
                        for v2 in v_list2:
                            g.add_edge(v1, v2)
                            vcolor[v1] = echo_colors
                            vcolor[v2] = echo_colors
                            vsize[v1] = 6
                            vsize[v2] = 6 
                except:
                    pass

    output_path = "%s/graph-draw-sfdp.pdf"%folder
    print(output_path)
    pos = sfdp_layout(g)
    graph_draw(g, pos=pos, 
            vertex_size=vsize,
            vertex_fill_color=vcolor,
            output=output_path)
            
        

if __name__ == "__main__":
    
    date = '20181024'
    folder = 'Image/%s/network'%date

    if not os.path.exists(folder):
        os.makedirs(folder)

    draw_graph()
