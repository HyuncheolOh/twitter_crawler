#node, edge, properties 
from __future__ import division, absolute_import, print_function
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json, os, sys
import numpy as np
import echo_chamber_util as e_util
import util as my_util
from time import time
from operator import itemgetter
from graph_tool import util
from graph_tool.all import *
from draw_tools.cdf_plot import CDFPlot
from draw_tools.ccdf_plot import CCDFPlot
from draw_tools.line_plot import LinePlot
from sklearn.metrics import jaccard_similarity_score

#construct echo chamber network 
def find_echo_chamber_network():
    filename = 'Data/echo_chamber2.json'
    with open(filename, 'r') as f:
        echo_chamber = json.load(f)

    all_echo_chambers = {} 
    count = 0
    for key in echo_chamber:
        e = echo_chamber[key]

        if len(e) > 1:
            #set uses  - echo chamber  
    
            all_echo_chambers.update({key:echo_chamber[key]})

            count += 1 

            #if count > 100:
            #    break


    g = Graph(directed=False)
    keys = all_echo_chambers.keys()
    vprop = g.new_vertex_property("string")
    eprop = g.new_edge_property("string")
    eweight = g.new_edge_property("int")
    d = {}
    for key in keys:
        v = g.add_vertex()
        vprop[v] = key
        d[key] = v


    for i in range(0, len(keys)):
        key1 = keys[i]
        #v1 = util.find_vertex(g, vprop, key1)[0]
        v1 = d[key1]
        #if i % 100 == 0:
        #    print(i)
        for j in range(i+1, len(keys)):
            key2 = keys[j]

            #print(key1, key2)
            if [item in key1 for item in key2.split('_')].count(True) > 0:
                continue
            
            intersection = set(all_echo_chambers[key1]) & set(all_echo_chambers[key2])
            if len(intersection) > 1:
                #print(intersection)
                #edge between key1 node & key2 node
                v2 = d[key2]
                e1 = g.add_edge(v1, v2)
                #print(e1, len(intersection))
                eprop[e1] = '%s_%s'%(str(v1), str(v2)) 
                eweight[e1] = len(intersection)
    

    #print(g.get_out_degrees(g.get_vertices()))
    #out_hist = vertex_hist(g, "out")
    #print(out_hist)
    #degree, weighted degree rank 
    weighted_degree = {}
    degree = {} 
    #for v in g.vertices():
    #    weighted_degree[v] = sum([eweight[e] for e in v.out_edges()])
        #degree[v] = len(v.out_edges())
    #    for e in v.out_edges():
    #        print(e)
        
    print(g.get_out_degrees(g.get_vertices()))
    print(sum(g.get_out_degrees(g.get_vertices())))
    print(np.count_nonzero(g.get_out_degrees(g.get_vertices())))
    print(g.num_vertices())    
    dist = shortest_distance(g)
    all_path = []
    path_num = 0
    for item in dist:
        #print(item)
        a = np.array(item)
        a = a[np.where(a < 2147483647)]
        a = a[np.where(a > 0)]
        all_path.append(sum(a))
        path_num += len(a)

    print('path', path_num)
    print('avg', sum(all_path) / path_num)
        
    avg_path_length = sum([sum(i) for i in dist]) / (g.num_vertices()**2 - g.num_vertices())
    print('avg path', avg_path_length)
    #cascade_centrality_analysis(g, vprop)
    #rumor_centrality_analysis(g, vprop)
    print('done')
    g.edge_properties['edge'] = eprop
    g.edge_properties['weight'] = eweight
    g.vertex_properties['vertex'] = vprop
    g.save('Data/graph.xml.gz')
    #graph_draw(g, output='graph.pdf')

def jaccard_similarity(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection/union)
#    return round(float(intersection / union),2)

def jaccard_distribution():
    filename = 'Data/echo_chamber2.json'
    with open(filename, 'r') as f:
        echo_chamber = json.load(f)

    keys = echo_chamber.keys()

    jaccard_list = []
    for i in range(len(keys)):
        key1 = keys[i]
        users1 = echo_chamber[key1]
        
        if len(users1) < 2:
            continue

        for j in range(i+1, len(keys)):

            key2 = keys[j]
            users2 = echo_chamber[key2]

            if len(users2) < 2:
                continue

            jaccard_list.append(jaccard_similarity(users1, users2))
 
    print('jaccard count : %s'%(len(jaccard_list)))
    
    #jaccard distribution
    cdf = CDFPlot()
    cdf.set_label('Jaccard Similarity', 'CDF')
    cdf.set_data(jaccard_list, '')
    cdf.save_image("%s/jaccard_cdf"%(folder_name))

    cdf = CCDFPlot()
    cdf.set_label('Jaccard Similarity', 'CCDF')
    cdf.set_data(jaccard_list)
    cdf.save_image("%s/jaccard_ccdf"%(folder_name))


def cascade_centrality_analysis(g, vprop, eweight):
    print('Compare cascade characteristics of echo chamber users')
    pr = pagerank(g)
    vp, ep = betweenness(g)
    c = closeness(g)

    #degree, weighted degree rank 
    weighted_degree = {}
    degree = {} 
    for v in g.vertices():
        weighted_degree[v] = sum([eweight[e] for e in v.out_edges()])

    for i, num in enumerate(g.get_out_degrees(g.get_vertices())):
        degree[i] = num


    p_rank = {}; b_rank = {}; c_rank = {}
    i = 0
    import math
    for p_v, b_v, c_v in zip(pr, vp, c):
        if not math.isnan(p_v):
            p_rank[i] = p_v 
        if not math.isnan(b_v):
            b_rank[i] = b_v
        if not math.isnan(c_v):
            c_rank[i] = c_v
        i += 1

    p_sort = sorted(p_rank.items(), key=itemgetter(1), reverse=True)
    b_sort = sorted(b_rank.items(), key=itemgetter(1), reverse=True)
    c_sort = sorted(c_rank.items(), key=itemgetter(1), reverse=True)
    d_sort = sorted(degree.items(), key=itemgetter(1), reverse=True)
    wd_sort = sorted(weighted_degree.items(), key=itemgetter(1), reverse=True)

    #print(d_sort)
    #print(wd_sort)
    #print(c_sort)
    c_breadth, c_depth, c_unique_users = e_util.get_cascade_max_breadth()
    
    keys1 = [vprop[item[0]] for item in p_sort[:10]]
    keys2 = [vprop[item[0]] for item in b_sort[:10]]
    keys3 = [vprop[item[0]] for item in c_sort[:10]]
    keys4 = [vprop[item[0]] for item in d_sort[:10]]
    keys5 = [vprop[item[0]] for item in wd_sort[:10]]
    keys = [vprop[item[0]] for item in p_sort] #for all cascade 


    #unique rumor set 
    temp = []; temp2 = []
    for i in range(10):
        temp.extend(keys1[i].split('_'))

    for i in range(len(keys)):
        temp2.extend(keys[i].split('_'))
 
    print('unique rumors from top 10 echo chambers %s'%len(set(temp)))
    print('common rumor num : %s'%(len(set(temp) & set(temp2))))

    #get unique rumor set from keys
    #a = []; b = []; c = []; d= []; e = []; f = []

    with open('Data/echo_chamber2.json', 'r') as f:
        echo_chamber = json.load(f)

    #get unique echo chamber users
    echo_chamber_users1 = get_unique_echo_chamber_users(echo_chamber, keys1) 
    echo_chamber_users2 = get_unique_echo_chamber_users(echo_chamber, keys2) 
    echo_chamber_users3 = get_unique_echo_chamber_users(echo_chamber, keys3) 
    echo_chamber_users4 = get_unique_echo_chamber_users(echo_chamber, keys4) 
    echo_chamber_users5 = get_unique_echo_chamber_users(echo_chamber, keys5) 
    echo_chamber_users = get_unique_echo_chamber_users(echo_chamber, keys) 

    #max_cascade1 = {};  max_cascade2 = {}; max_cascade3 = {}; max_cascade4 = {}; max_cascade5 = {}; max_cascade6 = {}; 
    #max_breadth1 = {};  max_breadth2 = {}; max_breadth3 = {}; max_breadth4 = {}; max_breadth5 = {}; max_breadth6 = {}; 
    #max_depth1 = {};  max_depth2 = {}; max_depth3 = {}; max_depth4 = {}; max_depth5 = {}; max_depth6 = {}; 
    #max_users1 = {};  max_users2 = {}; max_users3 = {}; max_users4 = {}; max_users5 = {}; max_users6 = {};
    pagerank1 = {}; pagerank2 = {}; betweenness1 = {}; betweenness2 = {}; closeness1 = {}; closeness2 = {}
    degree_rank = {}; wdegree_rank = {}; all_data = {};
    for item in ['max_depth', 'max_breadth', 'cascade', 'unique_users']:
        pagerank1[item] = {}
        pagerank2[item] = {}
        betweenness1[item] = {}
        betweenness2[item] = {}
        closeness1[item] = {}
        closeness2[item] = {}
        degree_rank[item] = {}
        wdegree_rank[item] = {}
        all_data[item] = {}

    #get cacade info 
    files = os.listdir('RetweetNew')
    for postid in files:

        with open('RetweetNew/%s'%postid, 'r') as f:
            tweets = json.load(f)

        users1 = echo_chamber_users1.get(postid, [])
        users2 = echo_chamber_users2.get(postid, [])
        users3 = echo_chamber_users3.get(postid, [])
        users4 = echo_chamber_users4.get(postid, [])
        users5 = echo_chamber_users5.get(postid, [])
        users = echo_chamber_users.get(postid, [])
        for tweet in tweets.values():
            origin_tweet = tweet['origin_tweet']
            if tweet['user'] in users1:
                pagerank1['max_depth'][origin_tweet] = c_depth[origin_tweet]
                pagerank1['cascade'][origin_tweet] = tweet['cascade']
                pagerank1['max_breadth'][origin_tweet] = c_breadth[origin_tweet]
                pagerank1['unique_users'][origin_tweet] = c_unique_users[origin_tweet]

            if tweet['user'] in users2:
                betweenness1['max_depth'][origin_tweet] = c_depth[origin_tweet]
                betweenness1['cascade'][origin_tweet] = tweet['cascade']
                betweenness1['max_breadth'][origin_tweet] = c_breadth[origin_tweet]
                betweenness1['unique_users'][origin_tweet] = c_unique_users[origin_tweet]

            if tweet['user'] in users3:
                closeness1['max_depth'][origin_tweet] = c_depth[origin_tweet]
                closeness1['cascade'][origin_tweet] = tweet['cascade']
                closeness1['max_breadth'][origin_tweet] = c_breadth[origin_tweet]
                closeness1['unique_users'][origin_tweet] = c_unique_users[origin_tweet]
            
            if tweet['user'] in users4:
                degree_rank['max_depth'][origin_tweet] = c_depth[origin_tweet]
                degree_rank['cascade'][origin_tweet] = tweet['cascade']
                degree_rank['max_breadth'][origin_tweet] = c_breadth[origin_tweet]
                degree_rank['unique_users'][origin_tweet] = c_unique_users[origin_tweet]

            if tweet['user'] in users5:
                wdegree_rank['max_depth'][origin_tweet] = c_depth[origin_tweet]
                wdegree_rank['cascade'][origin_tweet] = tweet['cascade']
                wdegree_rank['max_breadth'][origin_tweet] = c_breadth[origin_tweet]
                wdegree_rank['unique_users'][origin_tweet] = c_unique_users[origin_tweet]

            all_data['max_depth'][origin_tweet] = c_depth[origin_tweet]
            all_data['cascade'][origin_tweet] = tweet['cascade']
            all_data['max_breadth'][origin_tweet] = c_breadth[origin_tweet]
            all_data['unique_users'][origin_tweet] = c_unique_users[origin_tweet]
    
    #compare cascade, depth, breadth, users by centrality metric
    draw_cdf_graph([pagerank1['cascade'].values(), betweenness1['cascade'].values(), closeness1['cascade'].values(), degree_rank['cascade'].values(), 
        wdegree_rank['cascade'].values(), all_data['cascade'].values()], 'Cascade Size', ['PageRank', 'Betweenness', 'Closeness', 'Degree', 'Weighted Degree', 'All'], 'Rank Metric', 'centrality_user_cascade')
    draw_cdf_graph([pagerank1['max_depth'].values(), betweenness1['max_depth'].values(), closeness1['max_depth'].values(), degree_rank['max_depth'].values(), 
        wdegree_rank['max_depth'].values(), all_data['max_depth'].values()], 'Max Depth', ['PageRank', 'Betweenness', 'Closeness', 'Degree', 'Weighted Degree', 'All'], 'Rank Metric', 'centrality_user_depth')
    draw_cdf_graph([pagerank1['max_breadth'].values(), betweenness1['max_breadth'].values(), closeness1['max_breadth'].values(), degree_rank['max_breadth'].values(), 
        wdegree_rank['max_breadth'].values(), all_data['max_breadth'].values()], 'Max Breadth', ['PageRank', 'Betweenness', 'Closeness', 'Degree', 'Weighted Degree', 'All'], 'Rank Metric', 'centrality_user_breadth')
    draw_cdf_graph([pagerank1['unique_users'].values(), betweenness1['unique_users'].values(), closeness1['unique_users'].values(), degree_rank['unique_users'].values(), 
        wdegree_rank['unique_users'].values(), all_data['unique_users'].values()], 'Number of Users', ['PageRank', 'Betweenness', 'Closeness', 'Degree', 'Weighted Degree', 'All'], 'Rank Metric', 'centrality_user_users')

    draw_cdf_graph([pagerank1['cascade'].values(), all_data['cascade'].values()], 'Cascade Size', ['Top 10', 'All'], 'PageRank', 'centrality_user_cascade_pagerank')
    draw_cdf_graph([betweenness1['cascade'].values(), all_data['cascade'].values()], 'Cascade Size', ['Top 10', 'All'], 'Betweenness', 'centrality_user_cascade_betweenness')
    draw_cdf_graph([closeness1['cascade'].values(), all_data['cascade'].values()], 'Cascade Size', ['Top 10', 'All'], 'Closeness', 'centrality_user_cascade_closeness')
    draw_cdf_graph([pagerank1['max_breadth'].values(), all_data['max_breadth'].values()], 'Max Breadth', ['Top 10', 'All'], 'PageRank', 'centrality_user_breadth_pagerank')
    draw_cdf_graph([betweenness1['max_breadth'].values(), all_data['max_breadth'].values()], 'Max Breadth', ['Top 10', 'All'], 'Betweenness', 'centrality_user_breadth_betweenness')
    draw_cdf_graph([closeness1['max_breadth'].values(), all_data['max_breadth'].values()], 'Max Breadth', ['Top 10', 'All'], 'Closeness', 'centrality_user_breadth_closeness')
    draw_cdf_graph([pagerank1['max_depth'].values(), all_data['max_depth'].values()], 'Max Depth', ['Top 10', 'All'], 'PageRank', 'centrality_user_depth_pagerank', log_scale=False)
    draw_cdf_graph([betweenness1['max_depth'].values(), all_data['max_depth'].values()], 'Max Depth', ['Top 10', 'All'], 'Betweenness', 'centrality_user_depth_betweenness', log_scale=False)
    draw_cdf_graph([closeness1['max_depth'].values(), all_data['max_depth'].values()], 'Max Depth', ['Top 10', 'All'], 'Closeness', 'centrality_user_depth_closeness', log_scale=False)
    draw_cdf_graph([pagerank1['unique_users'].values(), all_data['unique_users'].values()], 'Number of Users', ['Top 10', 'All'], 'PageRank', 'centrality_user_unique_users_pagerank')
    draw_cdf_graph([betweenness1['unique_users'].values(), all_data['unique_users'].values()], 'Number of Users', ['Top 10', 'All'], 'Betweenness', 'centrality_user_unique_users_betweenness')
    draw_cdf_graph([closeness1['unique_users'].values(), all_data['unique_users'].values()], 'Number of Users', ['Top 10', 'All'], 'Closeness', 'centrality_user_unique_users_closeness')


    #participated user information 
    #depth, child, cascade 
    cascade1, depth1, child1 = get_user_info(echo_chamber_users1)
    cascade2, depth2, child2 = get_user_info(echo_chamber_users2)
    cascade3, depth3, child3 = get_user_info(echo_chamber_users3)
    cascade4, depth4, child4 = get_user_info(echo_chamber_users4)
    cascade5, depth5, child5 = get_user_info(echo_chamber_users5)
    cascade6, depth6, child6 = get_user_info(echo_chamber_users)
    draw_cdf_graph([cascade1, cascade2,cascade3,cascade4,cascade5,cascade6], 'Cascade Size', ['PageRank', 'Betweenness','Closeness','Degree','Weighted Degree', 'All'], 'Rank Metric', 'rank_user_cascade')
    draw_cdf_graph([depth1, depth2, depth3, depth4, depth5, depth6 ], 'Depth', ['PageRank', 'Betweenness','Closeness','Degree','Weighted Degree', 'All'], 'Rank Metric', 'rank_user_depth', log_scale=False)
    draw_cdf_graph([child1, child2, child3, child4, child5, child6 ], 'Child', ['PageRank', 'Betweenness','Closeness','Degree','Weighted Degree', 'All'], 'Rank Metric', 'rank_user_child')

    print('pagerank : %s, all : %s'%(len(cascade1), len(cascade6)))
    print('cascade' , np.mean(cascade1),np.mean(cascade2),np.mean(cascade3),np.mean(cascade4),np.mean(cascade5),np.mean(cascade6))
    print('depth' , np.mean(depth1), np.mean(depth2), np.mean(depth3),np.mean(depth4),np.mean(depth5),np.mean(depth6))
    print('breadth' , np.mean(child1),  np.mean(child2), np.mean(child3), np.mean(child4), np.mean(child5), np.mean(child6)) 


    print('cascade' , np.median(cascade1),np.median(cascade2),np.median(cascade3),np.median(cascade4),np.median(cascade5),np.median(cascade6))
    print('depth' , np.median(depth1), np.median(depth2), np.median(depth3),np.median(depth4),np.median(depth5),np.median(depth6))
    print('breadth' , np.median(child1),  np.median(child2), np.median(child3), np.median(child4), np.median(child5), np.median(child6)) 

def get_user_info(echo_chamber_users):
    depth = []
    child = []
    cascade = []

    for postid in echo_chamber_users.keys():
        with open('RetweetNew/' + postid , 'r') as f:
            tweets = json.load(f)

        e_users = echo_chamber_users[postid].keys()
        for tweet in tweets.values():
            if tweet['user'] in e_users:
                depth.append(tweet['depth'])
                child.append(tweet['child'])
                cascade.append(tweet['cascade'])

    return cascade, depth, child

def get_unique_echo_chamber_users(echo_chamber, keys):
    echo_chamber_users = {}
    for key in keys:
        users = echo_chamber[key]
        postids = key.split('_')
        for postid in postids:
            echo_chamber_users[postid] = echo_chamber_users.get(postid, {})
            for user in users:
                echo_chamber_users[postid][user] = 1

    return echo_chamber_users


def rumor_centrality_analysis(g, vprop):
    print('Compare rumor characteristics by centrality')
    pr = pagerank(g)
    vp, ep = betweenness(g)
    c = closeness(g)

    p_rank = {}; b_rank = {}; c_rank = {}
    i = 0
    import math
    for p_v, b_v, c_v in zip(pr, vp, c):
        if not math.isnan(p_v):
            p_rank[i] = p_v 
        if not math.isnan(b_v):
            b_rank[i] = b_v
        if not math.isnan(c_v):
            c_rank[i] = c_v
        i += 1

    p_sort = sorted(p_rank.items(), key=itemgetter(1), reverse=True)
    b_sort = sorted(b_rank.items(), key=itemgetter(1), reverse=True)
    c_sort = sorted(c_rank.items(), key=itemgetter(1), reverse=True)
    #return p_sort[:100], b_sort[:100], c_sort[:100]
    
    raw_data = {'pagerank' :[vprop[item[0]] for item in p_sort[:10]], 
            'betweenness':[vprop[item[0]] for item in b_sort[:10]],
            'closeness':[vprop[item[0]] for item in c_sort[:10/d]]}


    #raw_data2 = {'pagerank' :[vprop[item[0]] for item in p_sort[len(p_sort)-100:]], 
    #        'betweenness':[vprop[item[0]] for item in b_sort[len(b_sort)-100:]],
    #        'closeness':[vprop[item[0]] for item in c_sort[len(c_sort)-100:]]}

    
    raw_data2 = {'pagerank' :[vprop[item[0]] for item in p_sort], 
            'betweenness':[vprop[item[0]] for item in b_sort],
            'closeness':[vprop[item[0]] for item in c_sort]}

    with open('Data/echo_chamber2.json', 'r') as f:
        echo_chamber = json.load(f)

    #user num of rank 
    p_user = [len(echo_chamber[item]) for item in raw_data['pagerank']]
    b_user = [len(echo_chamber[item]) for item in raw_data['betweenness']]
    c_user = [len(echo_chamber[item]) for item in raw_data['closeness']]

    raw_data.update({'p_usernum':p_user, 'b_usernum':b_user, 'c_usernum':c_user})

    #from pandas import DataFrame
    #data = DataFrame(raw_data)
    #data.to_csv('Data/centrality.csv', mode='w')
    #print('Result saved in Data/centrality.csv')

    max_breadth, max_depth, max_unique_users, max_cascade = e_util.get_rumor_max_properties()
    
    keys = raw_data['pagerank']
    keys2 = raw_data['betweenness']
    keys3 = raw_data['closeness']
    keys4 = raw_data2['pagerank']

    print('length', len(keys), len(keys4))
    a = []; b = []; c = []; d= []; e = []; f = []
    #unique rumor set 
    for i in range(100):
        a.extend(keys[i].split('_'))
        b.extend(keys2[i].split('_'))
        c.extend(keys3[i].split('_'))
    for i in range(len(keys4)):
        d.extend(keys4[i].split('_'))
    
    keys = list(set(a))
    keys2 = list(set(b))
    keys3 = list(set(c))
   
    cascade = [max_cascade[key] for key in keys]
    cascade2 = [max_cascade[key] for key in keys2]
    cascade3 = [max_cascade[key] for key in keys3]
    breadth = [max_breadth[key] for key in keys]
    breadth2 = [max_breadth[key] for key in keys2]
    breadth3 = [max_breadth[key] for key in keys3]
    u_users = [max_unique_users[key] for key in keys]
    u_users2 = [max_unique_users[key] for key in keys2]
    u_users3 = [max_unique_users[key] for key in keys3]
    depth = [max_depth[key] for key in keys]
    depth2 = [max_depth[key] for key in keys2]
    depth3 = [max_depth[key] for key in keys3]

    
    keys_all = list(set(d))
    cascade_all = [max_cascade[key] for key in keys_all]
    breadth_all = [max_breadth[key] for key in keys_all]
    u_users_all = [max_unique_users[key] for key in keys_all]
    depth_all = [max_depth[key] for key in keys_all]

   
    print('unique rumors from top 100 echo chambers %s'%len(set(keys)))
    print('common rumor num : %s'%(len(set(keys) & set(keys_all))))
    #compare centrality and cascade, depth, breadth 
    draw_cdf_graph([cascade, cascade2, cascade3, cascade_all], 'Max Cascade of a Rumor', ['PageRank', 'Betweenness', 'Closeness', 'All'], 'Centrality', 'centrality_cascade')
    draw_cdf_graph([breadth, breadth2, breadth3, breadth_all], 'Max Breadth of a Rumor', ['PageRank', 'Betweenness', 'Closeness', 'All'], 'Centrality', 'centrality_breadth')
    draw_cdf_graph([depth, depth2, depth3, depth_all], 'Max Depth of a Rumor', ['PageRank', 'Betweenness', 'Closeness', 'All'], 'Centrality', 'centrality_depth')
    draw_cdf_graph([u_users, u_users2, u_users3, u_users_all], 'Number of Users of a Rumor', ['PageRank', 'Betweenness', 'Closeness', 'All'], 'Centrality', 'centrality_users')

    #compare with Top 100 and all other rumors  
    draw_cdf_graph([cascade, cascade_all], 'Max Cascade of a Rumor', ['Top 100', 'All'], 'PageRank', 'centrality_cascade_pagerank')
    draw_cdf_graph([cascade2, cascade_all], 'Max Cascade of a Rumor', ['Top 100', 'All'], 'Betweenness', 'centrality_cascade_betweenness')
    draw_cdf_graph([cascade3, cascade_all], 'Max Cascade of a Rumor', ['Top 100', 'All'], 'Closeness', 'centrality_cascade_closeness')
    draw_cdf_graph([breadth, breadth_all], 'Max Breadth of a Rumor', ['Top 100', 'All'], 'PageRank', 'centrality_breadth_pagerank')
    draw_cdf_graph([breadth2, breadth_all], 'Max Breadth of a Rumor', ['Top 100', 'All'], 'Betweenness', 'centrality_breadth_betweenness')
    draw_cdf_graph([breadth3, breadth_all], 'Max Breadth of a Rumor', ['Top 100', 'All'], 'Closeness', 'centrality_breadth_closeness')
    draw_cdf_graph([depth, depth_all], 'Max Depth of a Rumor', ['Top 100', 'All'], 'PageRank', 'centrality_depth_pagerank', log_scale=False)
    draw_cdf_graph([depth2, depth_all], 'Max Depth of a Rumor', ['Top 100', 'All'], 'Betweenness', 'centrality_depth_betweenness', log_scale=False)
    draw_cdf_graph([depth3, depth_all], 'Max Depth of a Rumor', ['Top 100', 'All'], 'Closeness', 'centrality_depth_closeness', log_scale=False)
    draw_cdf_graph([u_users, u_users_all], 'Number of Users', ['Top 100', 'All'], 'PageRank', 'centrality_users_pagerank')
    draw_cdf_graph([u_users2, u_users_all], 'Number of Users', ['Top 100', 'All'], 'Betweenness', 'centrality_users_betweenness')
    draw_cdf_graph([u_users3, u_users_all], 'Number of Users', ['Top 100', 'All'], 'Closeness', 'centrality_users_closeness')

def draw_cdf_graph(datas, x_label, legends, legends_title, file_name, log_scale=True):
    print(log_scale)
    cdf = CDFPlot()
    cdf.set_log(log_scale)
    cdf.set_label(x_label, 'CDF')
    for data in datas:
        cdf.set_data(data, '')
    cdf.set_legends(legends, legends_title)
    cdf.save_image('%s/%s.png'%(folder_name, file_name))

def analyze_echo_chamber_network():
    g = load_graph('Data/graph.xml.gz')
    vprop = g.vertex_properties['vertex']
    eprop = g.edge_properties['edge']
    eweight = g.edge_properties['weight']

    # Let's plot its in-degree distribution
    #out_hist = vertex_hist(g, "out")

    #print('degree max : %s, min : %s'%(max(in_hist), min(in_hist)))

    
    cascade_centrality_analysis(g, vprop, eweight)
    #rumor_centrality_analysis(g, vprop)

    v_count = 0
    e_count = 0 
    for v in g.vertices():
        v_count += 1

    degree = g.get_out_degrees(g.get_vertices())
   
    #calculate vertex all edge weight sum
    #for v in g.vertices():
    #CDF and CCDF of degree of vertex
    cdf = CDFPlot()
    cdf.set_label('Degree', 'CDF')
    cdf.set_log(True)
    cdf.set_data(degree, '')
    cdf.save_image("%s/degree_cdf"%(folder_name))
    
    cdf = CCDFPlot()
    cdf.set_label('Degree', 'CCDF')
    cdf.set_log(True)
    cdf.set_data(degree)
    cdf.save_image("%s/degree_ccdf"%(folder_name))

    #degree, weighted_degree rank 
    weighted_degree = []
    for v in g.vertices():
        weighted_degree.append(sum([eweight[e] for e in v.out_edges()]))


    #CDF and CCDF of weighted degree of vertex
    cdf = CDFPlot()
    cdf.set_label('Weighted Degree', 'CDF')
    cdf.set_log(True)
    cdf.set_data(weighted_degree, '')
    cdf.save_image("%s/weighted_degree_cdf"%(folder_name))
    
    cdf = CCDFPlot()
    cdf.set_label('Weighted Degree', 'CCDF')
    cdf.set_log(True)
    cdf.set_data(weighted_degree)
    cdf.save_image("%s/weighted_degree_ccdf"%(folder_name))

    print('Vertex Count : %s'%v_count)
    print('Vertices which have edges : %s'%(np.count_nonzero(g.get_out_degrees(g.get_vertices()))))
    print('Edge Count : %s'%(sum(degree)))

    
    #weight distribution
    weight_distribution = []
    edges = g.get_edges()
    #for i, e in enumerate(g.get_edges()):
    for i, e in enumerate(edges):
        if i % 1000000 == 0:
            print(i)
        weight_distribution.append(eweight[e])
        
    #print(weight_distribution)
    
    #edge_count = sum(g.get_out_degrees(g.get_vertices()))
    edge_count = my_util.ncr(v_count,2)
    weight_distribution.extend([0] * (edge_count - len(weight_distribution)))
    print('avg weight : %s'%(sum(weight_distribution) / len(weight_distribution)))
    print('median weight : %s'%np.median(weight_distribution))

    #weight_distribution = [eweight[e] for e in g.edges()]
    cdf = CDFPlot()
    cdf.set_label('Weight', 'CDF')
    cdf.set_log(True)
    cdf.set_data(weight_distribution, '')
    cdf.save_image("%s/weight_cdf"%(folder_name))

    cdf = CCDFPlot()
    cdf.set_label('Weight', 'CCDF')
    cdf.set_log(True)
    cdf.set_data(weight_distribution)
    cdf.save_image("%s/weight_ccdf"%(folder_name))
    

    clust = local_clustering(g, undirected=True)
    print('local clustering')
    print(vertex_average(g, clust))

    print('global clustering')
    print(global_clustering(g))

    dist = shortest_distance(g)
    all_path = []
    path_num = 0
    for item in dist:
        #print(item)
        a = np.array(item)
        a = a[np.where(a < 2147483647)]
        a = a[np.where(a > 0)]
        all_path.append(sum(a))
        path_num += len(a)

    print('average path length')
    print('path', path_num)
    print('avg', sum(all_path) / path_num)

    #dist = shortest_distance(g)
    #avg_path_length = sum([sum(i) for i in dist]) / (g.num_vertices()**2 - g.num_vertices())
    #print(avg_path_length)

if __name__ == "__main__":
    folder_name = 'Image/20181016'
    start = time()
    #find_echo_chamber_network()
    jaccard_distribution()
    analyze_echo_chamber_network()
    end = time()
    print('%s takes'%(end - start))
