from __future__ import division, absolute_import, print_function
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, os, sys
import numpy as np
import echo_chamber_util as e_util
import util as my_util
import user_diversity as polar
import pandas as pd
from time import time
from operator import itemgetter
from graph_tool import util
from graph_tool.all import *
from random import shuffle
from random import randrange


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
    #colors = [(255,255,204), (161,218,180), (65,182,196), (44,127,184), (37,52,148), (254,204,92)]
    #colors = [(213,62,79), (244,109,67), (253,174,97), (254,224,139), (255,255,191), (230,245,152), (171,221,164), (102,194,165), (50,136,189), (26,152,80), (255,255,0)]
    #colors = [(255,255,217), (247,252,240), (237,248,177), (199,233,180), (127,205,187), (65,182,196), (29,145,192), (34,94,168), (37,52,148), (8,29,88), (255,255,0)]
    #colors = [(178,24,43), (214,96,77), (244,165,130), (253,219,199), (255,255,255), (224,224,224), (186,186,186), (135,135,135), (77,77,77), (255,255,0)]
    #colors = [(178,24,43), (214,96,77), (244,165,130), (253,219,199), (247,247,247), (209,229,240), (146,197,222),(67,147,195),(33,102,173), (255,255,0)]
    #colors = [(244,243,248), (244,165,130), (178,24,43), (33,102,172)]
    colors = [(244,243,248), (244,165,130), (33,102,172)]
    #colors = [(253,174,97),(171,217,233),(217,239,139),(215,48,39),(69,117,180),(26,152,80)]
    colors = [tuple(map(lambda x : x/255, color)) for color in colors]
    echo_colors = colors[-1]

    files = os.listdir('RetweetNew/')
    shuffle(files)
    vertices = {}
    nodes = {}
    nodes_per_user = {}
    root_tweet = {}
    ccc = 0
    count = 0
    set_a = ['9535', '143145', '134286']
    set_b = ['134584', '143061', '152694']
    set_c = ['161471', '29947', '151476']
    set_d = ['134286', '11955', '148182']

    tweet_list = {} #tweetid, rumorid, echo chamber or not 
    edge_list = [] #tid1, tid2, edge between group (outgroup)
    echo_root={}
    cascade_size = {}

    with open('Data/temp_network_root.json', 'r') as f:
        filter_root = json.load(f)

    filter_root = ['1024472909883076608', '978744542592749568', '1032608222312628225']

    #for postid in files:
    for postid in set_d:
        f = open('RetweetNew/' + postid, 'r') 
        tweets = json.load(f)
        f.close()

        parent_child = {}
        vertices[postid] = {}
        nodes[postid] = {}
        nodes_per_user[postid] = {}
        users = {}
        tweet_list[postid] = {}
            
        ######
        #use only tweet size 300~1000
        if len(tweets) < 200 or len(tweets) > 700:
            continue
        print(postid)
    

        #parent and child set 
        for tweet in tweets.values():
            parent = tweet['parent_tweet']
            parent_user = tweet['parent']
            root = tweet['origin_tweet']
            tid = tweet['tweet']
            user = tweet['user']
            size = tweet['cascade']
            if size < 5:
                continue
            if root not in filter_root:
                continue

            if size > 30:
                echo_root[root] = size

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

                #tweet_ist.append({'tweet_id' : tid, 'rumor_id' : postid, 'is_echo' : 0})
                #tweet_list.append({'tweet_id' : parent, 'rumor_id' : postid, 'is_echo' : 0})
                tweet_list[postid][tid] = 0
                tweet_list[postid][parent] = 0

        #print(cascade_size.values())
        #parent-child add in the graph tool  
        for p in parent_child.keys():
            if nodes[postid].get(p, None) == None:
                v1 = g.add_vertex()
                nodes[postid][p] = str(v1)
                vertices[postid][str(v1)] = p
                vcolor[v1] = colors[ccc]
                vuser[v1] = users[p]
                vsize[v1] = 4
                vprop[v1] = str(v1)
                nodes_per_user[postid][users[p]].append(v1)
            else:
                v1 = nodes[postid][p]

            #print(v1, len(parent_child[p]))
            for c in parent_child[p]:
                if nodes[postid].get(c, None) == None:
                    v2 = g.add_vertex()
                    nodes[postid][c] = str(v2)
                    vertices[postid][str(v2)] = c
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
                edge_list.append({'tweet_id1':p, 'tweet_id2':c, 'outgroup': 0})
                #cascade_size[root_tweet[c]] -= 1

        if count == 2:
            break
        count += 1
        #ccc += 1
    ccc += 1  
    with open('Data/echo_chamber2.json', 'r') as f:
        echo_chamber = json.load(f)

    #edge between echo chambers 
    rumors = nodes.keys()
    dup_check = {}
    for i in range(len(rumors)):
        tweet_list1 = nodes[rumors[i]].values() #vertex list 1
        for j in range(i+1, len(rumors)):
        
            r1 = rumors[i]
            r2 = rumors[j]
           
            vlist1 = nodes[r1].values()
            vlist2 = nodes[r2].values()

            for _ in range(20):
                k1 = randrange(0, len(vlist1))
                k2 = randrange(0, len(vlist2))
                if dup_check.get(k1, -1) != -1 or  dup_check.get(k2, -1) != -1:
                    continue
                v1 = vlist1[k1]
                v2 = vlist2[k2]
                r = randrange(1, 10)
                if r < 5:
                    vcolor[v1] = colors[ccc]
                    vcolor[v2] = colors[ccc]
                    vsize[v1] = 6
                    vsize[v2] = 6 
            """
            continue        
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
                            #g.add_edge(v1, v2)
                            #vcolor[v1] = echo_colors
                            #vcolor[v2] = echo_colors
                            v1 = v_list1[i]
                            v2 = v_list2[j]
                            vcolor[v1] = colors[ccc]
                            vcolor[v2] = colors[ccc]
                            vsize[v1] = 6
                            vsize[v2] = 6 
                            edge_list.append({'tweet_id1':vertices[r1][str(v1)], 'tweet_id2':vertices[r2][str(v2)], 'outgroup': 1})
                            tweet_list[r1][vertices[r1][str(v1)]] = 1
                            tweet_list[r2][vertices[r2][str(v2)]] = 1
                            root1 = root_tweet[vertices[r1][str(v1)]]
                            root2 = root_tweet[vertices[r2][str(v2)]]
                            #print(cascade_size.keys())
                            print(root1, cascade_size[root1])
                            print(root2, cascade_size[root2])
                            #if cascade_size[root1] > 10:
                                #echo_root[root_tweet[vertices[r1][str(v1)]]] = 1
                            #    echo_root.append(root1)
                            #if cascade_size[root2] > 10:
                               #echo_root[root_tweet[vertices[r2][str(v2)]]] = 1
                            #   echo_root.append(root2)
                except KeyError as e:
                    print(e)
                    pass
            """        
            ccc += 1 
            print(ccc)
            if ccc == 3:
                is_out = True
                break
        if is_out == True:
            break
    print('root', len(echo_root.keys()))
    print(echo_root)
    with open('Data/temp_network_root.json', 'w') as f:
        json.dump(echo_root.keys(), f)

    num = randrange(100000)
    output_path = "%s/graph-draw-sfdp_%s.pdf"%(folder, num)
    print(output_path)
    pos = sfdp_layout(g)
    graph_draw(g, pos=pos, 
            vertex_size=vsize,
            vertex_fill_color=vcolor,
            output=output_path)
            
    tweet_id = []
    rumor_id = []
    is_echo = []
    for rid in tweet_list.keys():
        for vid in tweet_list[rid].keys():
            tweet_id.append(vid)
            rumor_id.append(rid)
            is_echo.append(tweet_list[rid][vid])
    
    tweet_id1 = []
    tweet_id2 = []
    is_outgroup = []
    for item in edge_list:
        tweet_id1.append(item['tweet_id1'])
        tweet_id2.append(item['tweet_id2'])
        is_outgroup.append(item['outgroup'])
    #save meta file for graph 
    df = pd.DataFrame({'tweet_id':tweet_id, 'rumor_id':rumor_id, 'is_echo':is_echo}, columns = ['tweet_id', 'rumor_id', 'is_echo'])
    df.to_csv('%s/73828_node.csv'%folder, mode='w')
    df = pd.DataFrame({'tweet_id1':tweet_id1, 'tweet_id2':tweet_id2, 'is_outgroup':is_outgroup}, columns = ['tweet_id1', 'tweet_id2', 'is_outgroup'])
    df.to_csv('%s/73828_edge.csv'%folder, mode='w')

if __name__ == "__main__":
    
    date = '20181101'
    folder = 'Image/%s/network'%date

    if not os.path.exists(folder):
        os.makedirs(folder)

    draw_graph()
    #for i in range(10):
    #    draw_graph()
