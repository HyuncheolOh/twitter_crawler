#node, edge, properties 
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
from draw_tools.cdf_plot import CDFPlot
from draw_tools.ccdf_plot import CCDFPlot
from draw_tools.line_plot import LinePlot
from draw_tools.scatter_plot import ScatterPlot
from sklearn.metrics import jaccard_similarity_score
from scipy import stats

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
    rd = {}
    for key in keys:
        v = g.add_vertex()
        d[key] = str(v)
        rd[str(v)] = key

    with open('Data/network_key.json', 'w') as f:
        json.dump(rd, f)

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
            if len(intersection) > 4:
                #print(intersection)
                #edge between key1 node & key2 node
                v2 = d[key2]
                e1 = g.add_edge(v1, v2)
                #print(e1, len(intersection))
                eprop[e1] = '%s_%s'%(str(v1), str(v2)) 
                print('%s_%s'%(str(v1), str(v2))) 
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
    #g.save('Data/graph5.xml.gz')
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
    node_num = 0
    for v in g.vertices():
        weighted_degree[v] = sum([eweight[e] for e in v.out_edges()])

    for i, num in enumerate(g.get_out_degrees(g.get_vertices())):
        degree[i] = num

        if num > 0:
            node_num += 1

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
    
    num = node_num
    print(node_num)
    if num * 0.2 < 10:
        num = 10 
    else:
        num = int(num * 0.2)
    #num = 50
    print('top %s rank echo chambers'%num)
    keys1 = [vprop[item[0]] for item in p_sort[:num]]
    keys2 = [vprop[item[0]] for item in b_sort[:num]]
    keys3 = [vprop[item[0]] for item in c_sort[:num]]
    keys4 = [vprop[item[0]] for item in d_sort[:num]]
    keys5 = [vprop[item[0]] for item in wd_sort[:num]]
    keys = [vprop[item[0]] for item in p_sort] #for all cascade 


    #unique rumor set 
    temp = []; temp2 = []
    for i in range(num):
        temp.extend(keys1[i].split('_'))

    for i in range(len(keys)):
        temp2.extend(keys[i].split('_'))
 
    print(set(temp))
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

    #save echo chmabers ranked by degree
    with open('Data/degree_ranked_users.json', 'w') as f:
        json.dump(echo_chamber_users4, f)
    with open('Data/pagerank_ranked_users.json', 'w') as f:
        json.dump(echo_chamber_users1, f)
    with open('Data/betweenness_ranked_users.json', 'w') as f:
        json.dump(echo_chamber_users2, f)
    with open('Data/closeness_ranked_users.json', 'w') as f:
        json.dump(echo_chamber_users3, f)
    with open('Data/weighted_degree_ranked_users.json', 'w') as f:
        json.dump(echo_chamber_users5, f)

    with open('Data/ranked_weight%s_echo_chamber.json'%weight_filter, 'w') as f:
        json.dump(echo_chamber_users1, f)

    with open('Data/ranked_echo_chambers%s.json'%weight_filter, 'w') as f:
        json.dump({'p' : keys1, 'b' : keys2, 'c' : keys3, 'd' : keys4, 'w' : keys5}, f)
    print("degree ranked echo chamber users are saved")        
    return 

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
    g = load_graph(graph_name)
    vprop = g.vertex_properties['vertex']
    eprop = g.edge_properties['edge']
    eweight = g.edge_properties['weight']

    # Let's plot its in-degree distribution
    #out_hist = vertex_hist(g, "out")

    #print('degree max : %s, min : %s'%(max(in_hist), min(in_hist)))

    
    cascade_centrality_analysis(g, vprop, eweight)
    #rumor_centrality_analysis(g, vprop)
    return 
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
    #edge_count = my_util.ncr(v_count,2)
    #weight_distribution.extend([0] * (edge_count - len(weight_distribution)))
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

#tweet initiation ratio : the number of users who initate the tweet 
#retweeted ratio : the number of tweets which are retweeted 
def network_analysis():
    files = ['Data/ranked_weight2_echo_chamber.json', 'Data/ranked_weight5_echo_chamber.json', 'Data/ranked_weight10_echo_chamber.json', 'Data/ranked_weight50_echo_chamber.json', 'Data/ranked_weight100_echo_chamber.json']
    for num, filename in enumerate(files):
        print(filename)
        
        with open(filename, 'r') as f:
            echo_chamber = json.load(f)

            for postid in echo_chamber:
                depth = []
                child = []
                all_depth = []
                all_child = []
                users = echo_chamber[postid]

                with open('RetweetNew/'+ postid, 'r') as fe:
                    tweets = json.load(fe)

                    for tweet in tweets.values():
                        d = tweet['depth']
                        c = tweet['child']
                        all_depth.append(d)
                        all_child.append(c)
                        if tweet['user'] in users:
                            depth.append(d)         
                            child.append(c)

                #count of depth 
                print(postid, 'depth 1 count : %s / %s, %s / %s, %s / %s'%(depth.count(1)/len(depth), all_depth.count(1)/len(all_depth), depth.count(1), len(depth), all_depth.count(1), len(all_depth))) 

        #CDF?
        cdf = CDFPlot()
        cdf.set_label('Depth', 'CDF')
        cdf.set_log(True)
        cdf.set_data(depth, 'Depth')
        cdf.set_data(all_depth, 'Depth')
        cdf.set_legends(['Ranked', 'All'], 'Depth')
        cdf.save_image('%s/depth_cdf_%s.png'%(folder_name, num))

        #CDF?
        cdf = CDFPlot()
        cdf.set_label('Child', 'CDF')
        cdf.set_log(True)
        cdf.set_data(child, 'Depth')
        cdf.set_data(all_child, 'Depth')
        cdf.set_legends(['Ranked', 'All'], 'Child')
        cdf.save_image('%s/child_cdf_%s.png'%(folder_name, num))

def rank_depth_distribution():
    files = ['Data/pagerank_ranked_users.json', 'Data/betweenness_ranked_users.json', 'Data/closeness_ranked_users.json', 'Data/degree_ranked_users.json', 'Data/weighted_degree_ranked_users.json']   
    all_postid = {}
    rank_root_ratio = {}
    for num, filename in enumerate(files):
        print(filename)
        rank_root_ratio[num] = []
        
        with open(filename, 'r') as f:
            echo_chamber = json.load(f)

            for postid in echo_chamber:
                all_postid[postid] = 1
                depth = []
                child = []
                users = echo_chamber[postid]

                with open('RetweetNew/'+ postid, 'r') as fe:
                    tweets = json.load(fe)

                    for tweet in tweets.values():
                        d = tweet['depth']
                        c = tweet['child']
                        if tweet['user'] in users:
                            depth.append(d)         
                            child.append(c)
                print(depth.count(1)/len(depth))
                rank_root_ratio[num].append(depth.count(1)/len(depth))

    all_root_ratio = []
    for postid in all_postid.keys():
        depth = []
        child = []
        with open('RetweetNew/'+ postid, 'r') as fe:
            tweets = json.load(fe)

            for tweet in tweets.values():
                d = tweet['depth']
                c = tweet['child']
                depth.append(d)         
                child.append(c)
            all_root_ratio.append(depth.count(1)/len(depth))

    cdf = CDFPlot()
    cdf.set_label('Depth', 'CDF')
    for num in rank_root_ratio.keys():
        print(num)
        cdf.set_data(rank_root_ratio[num], 'Depth')

    cdf.set_data(all_root_ratio, 'Depth')
    cdf.set_legends(['Pagerank', 'Betweenness', 'Closeness', 'Degree', 'W-Degree', 'All'], 'Depth')
    cdf.save_image('%s/depth_cdf_rank.png'%(folder_name))

#correlation between polarity and weight 
#correlation between weight and category sim.
def polarity_weight_correlation():
    g = load_graph(graph_name)
    vprop = g.vertex_properties['vertex']
    eprop = g.edge_properties['edge']
    eweight = g.edge_properties['weight']

    f = open('Data/network_key.json', 'r') 
    v_keys = json.load(f)
    f.close()

    filename = 'Data/echo_chamber_polarization.json'
    if os.path.exists(filename):
        f = open(filename) 
        json_data = json.load(f)
        d_mean = json_data['mean']
        d_median = json_data['median']
        f.close()
    else:
        f = open('Data/echo_chamber2.json', 'r') 
        echo_chamber = json.load(f)
        f.close()

        d_median = {}
        d_mean = {}
        for key in echo_chamber:
            users = echo_chamber[key]
            #users = echo_chamber[key].keys()

            if len(users) < 2:
                continue
            
            mean_p, median_p = polar.median_polarity(users)

            d_mean[key] = mean_p
            d_median[key] = median_p
            
        with open(filename, 'w') as f:
            json.dump({'mean' : d_mean, 'median' : d_median}, f)
   
    dkeys = d_mean.keys() 

    print('polarity calculation done for echo chambers')
    f = open('Data/ranked_echo_chambers%s.json'%weight_filter, 'r') 
    ranked_echo_chamber = json.load(f)
    f.close()
    print('ranked echo chamber : %s'%len(ranked_echo_chamber))
    
    echo_chamber_categories = {}
    polar_mean_list = []
    polar_median_list = []
    weight_list = []
    common_category_num_list = []
    ranked_keys = ranked_echo_chamber['d']
    category_mean_weight = {}
    category_median_weight = {}
    category_mean_polar = {}
    category_median_polar = {}
    is_politics = {}
    median_v1 = []; median_v2 = []
    mean_v1 = []; mean_v2 = []
    """
    for key in d_mean.keys():
        p1 = key.split('_')
        #if not my_util.is_politics(p1[0]) and not my_util.is_politics(p1[1]):
        #    is_politics[key] = 0
        #else :
        #    is_politics[key] = 1
        if my_util.is_politics(p1[0]) and my_util.is_politics(p1[1]):
            is_politics[key] = 1
        else :
            is_politics[key] = 0

    print('politics key fetch done')
    """

    for i in range(3):
        category_mean_weight[i] = []
        category_median_weight[i] = []
        category_mean_polar[i] = []
        category_median_polar[i] = []

    if os.path.exists('Data/echo_chamber_categories.json'):
        f = open('Data/echo_chamber_categories.json', 'r') 
        echo_chamber_categories = json.load(f)
        f.close()
    else:
        f = open('Data/echo_chamber2.json', 'r') 
        echo_chamber_keys = json.load(f)
        f.close()
        for key in echo_chamber_keys:
            echo_chamber_categories[key] = [my_util.get_category(item) for item in key.split('_')]

        with open('Data/echo_chamber_categories.json', 'w') as f:
            json.dump(echo_chamber_categories, f)
    
    print('category fetch done')

    round_num = 1
    for v in g.vertices():

        v_string = vprop[v]
#        print(v_string)
        if v_string not in ranked_keys:
            continue

        postids = v_string.split('_')
        for e in v.out_edges():

            weight = eweight[e]
            if weight < int(weight_filter):
                continue
            keys = eprop[e].split('_')
            #print(v_keys[keys[0]], v_keys[keys[1]], eweight[e])
        
            key1 = v_keys[keys[0]]
            key2 = v_keys[keys[1]]

            #if not is_politics[key1] or not is_politics[key2]:
            #    continue
            
            p_median = round(d_median[key1] * d_median[key2],round_num)
            p_mean = round(d_mean[key1] * d_mean[key2],round_num)

            median_v1.append(d_median[key1])
            median_v2.append(d_median[key2])
            mean_v1.append(d_mean[key1])
            mean_v2.append(d_mean[key2])
            #print(d_mean[key1], d_mean[key2])
            polar_mean_list.append(p_mean)
            polar_median_list.append(p_median)
            weight_list.append(weight)

            #category compare intersection of set (0 , 1, 2)
            intersection = set(echo_chamber_categories[key1]) & set(echo_chamber_categories[key2])
            common_category_num_list.append(len(intersection))
            #print(len(intersection), weight)

            category_median_weight[len(intersection)].append(weight)
            category_mean_weight[len(intersection)].append(weight)

            category_median_polar[len(intersection)].append(p_mean)
            category_mean_polar[len(intersection)].append(p_median)

        #weighted_degree.append([eweight[e] for e in v.out_edges()])
    #print(polar_mean_list)
    #print(weight_list)

    print('median, mean weight')
    print([np.median(category_median_weight[i]) for i in range(3)])
    print([np.mean(category_mean_weight[i]) for i in range(3)])

    print('median, mean polarity')
    print([np.median(category_median_polar[i]) for i in range(3)])
    print([np.mean(category_mean_polar[i]) for i in range(3)])

    
    numbers = np.arange(-1.1, 1.1, 0.01)
    median_median = {}
    mean_mean = {}
    weight_polar = {}
    weight_pearson_median = {}
    weight_pearson_mean = {}
    for key in weight_list:
        weight_pearson_mean[key] = []
        weight_pearson_median[key] = []
        key = int(key / 10) * 10
        weight_polar[key] = []

    for num in numbers:
        median_median[round(num,round_num)] = []
        mean_mean[round(num,round_num)] = []
    
    #median of median
    for i in range(len(polar_mean_list)):
        median_median[polar_median_list[i]].append(weight_list[i])
        mean_mean[polar_median_list[i]].append(weight_list[i])
        weight_pearson_median[weight_list[i]].append((median_v1[i], median_v2[i]))
        weight_pearson_mean[weight_list[i]].append((mean_v1[i], mean_v2[i]))
        w_key = int(weight_list[i] / 10) * 10
        weight_polar[w_key].append(polar_median_list[i])

    pearson_list = []
    for key in weight_pearson_mean.keys():
        vectors = weight_pearson_mean[key]
        v1 = [item[0] for item in vectors]
        v2 = [item[1] for item in vectors]
        #print(key, stats.pearsonr(v1, v2))
        pearson_list.append(stats.pearsonr(v1, v2)[0])
    print(weight_pearson_median.keys())
    print(pearson_list)
    print(len(weight_pearson_median.keys()), len(pearson_list))
    scatter = ScatterPlot()
    #scatter.set_log(True)
    scatter.set_ylog()
    scatter.set_label('Weight', 'Pearson Correlation')
    scatter.set_data(weight_pearson_median.keys(), pearson_list)
    scatter.save_image('%s/echo_chamber_polarity_weight_pearson_median_%s.png'%(folder_name, weight_filter))
    
    #print(median_median)
    #print(mean_mean)

    scatter = ScatterPlot()
    #scatter.set_log(True)
    scatter.set_ylog()
    scatter.set_label('Median Polarity', 'Median Weight')
    scatter.set_data(median_median.keys(), [np.median(item) for item in median_median.values()])
    scatter.save_image('%s/echo_chamber_polarity_weight_median_median_%s.png'%(folder_name, weight_filter))
    
    scatter = ScatterPlot()
    #scatter.set_log(True)
    #scatter.set_ylog()
    scatter.set_label('Average Polarity', 'Mean Weight')
    scatter.set_data(median_median.keys(), [np.median(item) for item in median_median.values()])
    scatter.set_data(mean_mean.keys(), [np.mean(item) for item in mean_mean.values()])
    scatter.set_legends(['Median', 'Mean'],'')
    scatter.save_image('%s/echo_chamber_polarity_weight_mean_mean_%s.png'%(folder_name, weight_filter))

    #print(weight_polar.keys())
    #print([item for item in weight_polar.values()])
    scatter = ScatterPlot()
    scatter.set_log(True)
    #scatter.set_ylog()
    scatter.set_label('Weight', 'Mean Polarity')
    scatter.set_data(weight_polar.keys(), [np.mean(item) for item in weight_polar.values()])
    scatter.save_image('%s/echo_chamber_polarity_weight_transpose_mean_%s.png'%(folder_name, weight_filter))

    scatter = ScatterPlot()
    scatter.set_log(True)
    #scatter.set_ylog()
    scatter.set_label('Weight', 'Mean Polarity')
    scatter.set_data(weight_polar.keys(), [np.median(item) for item in weight_polar.values()])
    scatter.save_image('%s/echo_chamber_polarity_weight_transpose_median_%s.png'%(folder_name, weight_filter))

    draw_cdf_graph([category_mean_polar[0], category_mean_polar[1], category_mean_polar[2]], 'Homophily', ['num 0', 'num 1', 'num 2'], 'common category', 'echo_chamber_polarity_category_%s_cdf'%(weight_filter), log_scale=False)

    scatter = ScatterPlot()
    #scatter.set_log(True)
    scatter.set_ylog()
    scatter.set_ylim(0, 1000)
    scatter.set_label('Polarity', 'Mean Weight')
    scatter.set_data(polar_mean_list, weight_list)
    scatter.save_image('%s/echo_chamber_polarity_weight_mean.png'%folder_name)
    
    scatter = ScatterPlot()
    #scatter.set_log(True)
    scatter.set_ylog()
    scatter.set_ylim(0, 1000)
    scatter.set_label('Polarity', 'Median Weight')
    scatter.set_data(polar_median_list, weight_list)
    scatter.save_image('%s/echo_chamber_polarity_weight_median.png'%folder_name)
 
    polar_weight_file = 'Data/polarity_weight_correlation.json'
    if os.path.exists(polar_weight_file):
        with open(polar_weight_file, 'r') as f:
            polar_weight_aggre = json.load(f)
    else : 
        polar_weight_aggre = {}
    
    polar_weight_aggre[weight_filter] = {'keys' : mean_mean.keys(), 'weight' : [np.mean(item) for item in mean_mean.values()]}
    with open(polar_weight_file, 'w') as f:
        json.dump(polar_weight_aggre, f)

    print('polar aggre : %s'%len(polar_weight_aggre))
    scatter = ScatterPlot()
    #scatter.set_log(True)
    scatter.set_ylog()
    scatter.set_label('Mean Polarity', 'Mean Weight')
    for key in polar_weight_aggre.keys():
        scatter.set_data(polar_weight_aggre[key]['keys'], polar_weight_aggre[key]['weight'])
    scatter.set_legends([key for key in polar_weight_aggre.keys()], '')
    scatter.save_image('%s/echo_chamber_polarity_weight_mean_aggre.png'%(folder_name))

   

if __name__ == "__main__":
    folder_name = 'Image/20181023'
    graph_name = 'Data/graph%s.xml.gz'
    start = time()
    #find_echo_chamber_network()
    #jaccard_distribution()
    if len(sys.argv) > 1:
        weight_filter = sys.argv[1]
        graph_name = graph_name%weight_filter
        print('load ', graph_name)
    #analyze_echo_chamber_network()
    #network_analysis()
    #rank_depth_distribution()
    polarity_weight_correlation()
    end = time()
    print('%s takes'%(end - start))

