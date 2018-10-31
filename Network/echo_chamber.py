from __future__ import division
import json, os, sys
import MySQLdb 
import numpy as np
import random
import itertools
import bot_detect as bot
import util
import echo_chamber_util as e_util
from time import time 
from draw_tools.cdf_plot import CDFPlot
from draw_tools.ccdf_plot import CCDFPlot
from draw_tools.box_plot import BoxPlot

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def get_veracity(postid, veracity):
    conn, cursor = sql_connect()
    if int(postid) < 100000:
    #factchecking
        sql = """
        SELECT veracity
        FROM factchecking_data
        WHERE id = %s and ({0})
        """

    else:
    #snopes
        sql = """
        SELECT veracity
        FROM snopes_set
        WHERE post_id = %s and ({0})
        """

    veracity = veracity.split(',')
    if len(veracity) == 1:
        sql = sql.format("veracity = '%s'"%veracity[0])
    else:
        v_list = ["veracity = '%s'"%item for item in veracity]
        condition = " or ".join(v_list)
        sql = sql.format(condition)
    cursor.execute(sql, [postid])
    rs = cursor.fetchall()
    sql_close(cursor, conn)
    #return rs[0][0]
    if len(rs) == 0:
        return False
    else:
        return True



def find_echo_chamber(num):
    #select number of rumors and compare user intersection
    print('find echo chamber %s'%num)
    start_time = time()
    dir_name = 'RetweetNew/'
    files = os.listdir(dir_name)
    
    #with open('Data/top_users.json', 'r') as f:
    #    top_users = json.load(f)

    #print(top_users.keys())
    #top_users = top_users['top_1']
    #print(len(top_users))
    users = {}
    for postid in files:

        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
            #remove bots 
            
            users[postid] = set([item['user'] for item in tweets.values() if item['bot'] == 0])
            #print(users[postid]) 

    print('total_users', len(users))
    #find echo chamber (intersection) between rumor spreaders
    echo_chamber = {}
    count = 0
    for i in range(len(files)):
        names = []
        p1 = files[i]
        names.append(p1)
        
        for j in range(i+1, len(files)):
            p2 = files[j]
            names.append(p2)
            if num == 2:
                echo = users[p1] & users[p2]
                echo_chamber['_'.join(names)] = list(echo)
                names.pop()
                continue
            
            for k in range(j+1, len(files)):
                p3 = files[k]
                names.append(p3)
                if num == 3:
                    echo = users[p1] & users[p2] & users[p3]
                    echo_chamber['_'.join(names)] = list(echo)
                    names.pop()
                    continue
                
                for l in range(k+1, len(files)):
                    p4 = files[l]
                    names.append(p4)
                    if num == 4:
                        echo = users[p1] & users[p2] & users[p3] & users[p4]
                        echo_chamber['_'.join(names)] = list(echo)
                        names.pop()
                        continue

                    for m in range(l+1, len(files)):
                        count += 1 
                        if count % 100000 == 0:
                            print(count)
                        p5 = files[m]
                        names.append(p5)
                        if num == 5:
                            echo = users[p1] & users[p2] & users[p3] & users[p4] & users[p5]
                            echo_chamber['_'.join(names)] = list(echo)
                            names.pop()
                            continue
                    names.pop()
                names.pop()
            names.pop()
        names.pop()

    end_time = time()
    print('%s taken'%(end_time-start_time))
    print('number of echo chambers %s'%(len(echo_chamber)))
    with open('Data/echo_chamber%s.json'%num, 'w') as f:
        json.dump(echo_chamber, f)


# breadth, depth
def get_cascade_max_breadth():
    dir_name = "RetweetNew/"
    files = os.listdir(dir_name)
    c_breadth = {}
    c_depth = {}
    c_unique_users = {}
    for postid in files:
        #cascade_breadth[postid] = {} #origin tweet + max_breadth
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
        
        b = {}
        d = {}
        u = {}
        for tweet in tweets.values():
            #same origin tweet, number of same depth node means breadth
            origin_tweet = tweet['origin_tweet']
            b[origin_tweet] = b.get(origin_tweet, {})
            breadth = b[origin_tweet].get(tweet['depth'], 0) + 1 
            b[origin_tweet][tweet['depth']] = breadth
            c_breadth[origin_tweet] = c_breadth.get(origin_tweet, 0)
            c_depth[origin_tweet] = c_depth.get(origin_tweet, 1)

            #unique users of a cascade
            u[origin_tweet] = u.get(origin_tweet, {})
            u[origin_tweet][tweet['user']] = 1
            if c_breadth[origin_tweet] < breadth:
                c_breadth[origin_tweet] = breadth
       
            if c_depth[origin_tweet] < tweet['depth']:
                c_depth[origin_tweet] = tweet['depth']
        
        for key in u.keys():
            c_unique_users[key] = len(u[key])
    
    print("Max cascade, max depth, unique users of cascade calculation done")
    return c_breadth, c_depth, c_unique_users

#find echo chamber users'depth, cascade, breadth and those of non echo chamber users 
def echo_chamber_anlysis(file_name, veracity):
    cache = {}
    echo_chamber_depth = {}
    echo_chamber_cascade = {}
    echo_chamber_child = {}
    echo_chamber_breadth = {}
    count = 0

    with open(file_name) as f:
        echo_chambers = json.load(f)

    cascade_breadth = get_cascade_max_breadth()

    echo_chamber_users = {}
    print('total ', len(echo_chambers))
    for key in echo_chambers:
        #print(key)
        
        count += 1 
       # if count % 100 == 0:
      #      print(count)
            #break

        users = echo_chambers[key]
        if len(users) < 2:
            continue
        postids = key.split('_')
        #if not get_veracity(postids[0], veracity) or not  get_veracity(postids[1], veracity):
        #    continue 
        
        for postid in postids:
            echo_chamber_users[postid] = echo_chamber_users.get(postid, {})
            for user in users:
                echo_chamber_users[postid][user] = 1

    #check all tweets in RetweetNew network 
    dir_name = "RetweetNew/"
    files = os.listdir(dir_name)
    e_depth = []; e_cascade = []; e_breadth = []; e_child = [];
    ne_depth = []; ne_cascade = []; ne_breadth = []; ne_child = [];

    for ccc ,  postid in enumerate(files):
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)

        for tweet in tweets.values():
            if tweet['user'] in echo_chamber_users[postid]:
                #echo chamber users characteristics
                e_depth.append(tweet['depth'])
                e_cascade.append(tweet['cascade'])
                e_child.append(tweet['child'])
            else:
                ne_depth.append(tweet['depth'])
                ne_cascade.append(tweet['cascade'])
                ne_child.append(tweet['child'])
   
        #if ccc == 10:
        #    break
    return ((e_depth, e_cascade, e_child), (ne_depth, ne_cascade, ne_child))
   
def get_list(data, key):
    return list(itertools.chain(*[item.values() for item in data[key].values()]))[0]

#echo chamber and non echo chamber depth, breadth distribution from echo chamber participated cascades
def echo_chamber_user_characteristics():
    echo_chamber_users = e_util.get_echo_chamber_users('Data/echo_chamber2.json')

    #find cascades that echo chamber users participated (root id)
    tweet_cache = {}
    echo_chamber_cascades = {}
    for postid in echo_chamber_users.keys():
        
        users = echo_chamber_users[postid] #echo chamber users 

        with open('RetweetNew/' + postid, 'r') as f:
            tweets = json.load(f)
            tweet_cache[postid] = tweets
            
            for tweet in tweets.values():
                if tweet['user'] in users:
                    root_id = tweet['origin_tweet'] #root tweet id 
                    echo_chamber_cascades[root_id] = 1
        
    echo_chamber_cascades_ids = echo_chamber_cascades.keys()
    e_depth = []; e_child = []; ne_depth = []; ne_child = [];
    for postid in echo_chamber_users.keys():
        tweets = tweet_cache[postid]
        users = echo_chamber_users[postid]

        for tweet in tweets.values():
            if tweet['origin_tweet'] not in echo_chamber_cascades_ids:
                continue

            if tweet['user'] in users:
                e_depth.append(tweet['depth'])
                e_child.append(tweet['child'])
            else:
                ne_depth.append(tweet['depth'])
                ne_child.append(tweet['child'])

    print('Data save in Data/Figure/5_1_1_2.json')
    with open('Data/Figure/5_1_1_2.json', 'w') as f:
        json.dump({'e_depth':e_depth, 'e_child' : e_child, 'ne_depth':ne_depth, 'ne_child':ne_child}, f)

    draw_cdf_plot([e_depth, ne_depth], 'Depth', ['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/echo_depth_user_distribution'%folder, log_scale=False)
    draw_cdf_plot([e_child, ne_child], 'Child', ['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/echo_child_user_distribution'%folder)

    

#echo chamber and non echo chamber depth, breadth distribution
def draw_echo_chamber_true_false():
    echo_chamber, non_echo_chamber = echo_chamber_anlysis('Data/echo_chamber2.json', 'All')

    with open('Data/Figure/5_1_1.json', 'w') as f:
        json.dump({'echo' : echo_chamber, 'necho' : non_echo_chamber}, f)

    #draw_cdf_plot([path_distribution, path_distribution2], 'Ratio', ['type1', 'type2'], '', 'Image/%s/echo_chamber_path_ratio2')
    draw_cdf_plot([echo_chamber[0], non_echo_chamber[0]], 'Depth', ['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/echo_depth'%folder, log_scale=False)
    draw_cdf_plot([echo_chamber[1], non_echo_chamber[1]], 'Cascade', ['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/echo_cascade'%folder)
    draw_cdf_plot([echo_chamber[2], non_echo_chamber[2]], 'Child', ['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/echo_child'%folder)
    
    draw_ccdf_plot([echo_chamber[0], non_echo_chamber[0]], 'Depth',['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/echo_depth_ccdf'%folder, log_scale=False) 
    draw_ccdf_plot([echo_chamber[2], non_echo_chamber[2]], 'Child',['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/echo_child_ccdf'%folder) 
    print(echo_chamber[0].count(1), echo_chamber[0].count(2), echo_chamber[0].count(3), echo_chamber[0].count(4), len(echo_chamber[0]))
    print(non_echo_chamber[0].count(1), non_echo_chamber[0].count(2), non_echo_chamber[0].count(3), non_echo_chamber[0].count(4), len(non_echo_chamber[0]))

    #draw_cdf_plot([path_distribution, path_distribution2], 'Ratio', ['type1', 'type2'], '', 'Image/%s/echo_chamber_path_ratio2')
    non_echo_chamber[0].extend(echo_chamber[0])
    non_echo_chamber[1].extend(echo_chamber[1])
    non_echo_chamber[2].extend(echo_chamber[2])

    draw_cdf_plot([echo_chamber[0], non_echo_chamber[0]], 'Depth', ['Echo Chamber', 'All'], 'User Type', 'Image/%s/echo_depth_all'%folder, log_scale=False)
    draw_cdf_plot([echo_chamber[1], non_echo_chamber[1]], 'Cascade', ['Echo Chamber', 'All'], 'User Type', 'Image/%s/echo_cascade_all'%folder)
    draw_cdf_plot([echo_chamber[2], non_echo_chamber[2]], 'Child', ['Echo Chamber', 'All'], 'User Type', 'Image/%s/echo_child_all'%folder)

    echo_chamber3, non_echo_chamber = echo_chamber_anlysis('Data/echo_chamber3.json', 'All')
    echo_chamber4, non_echo_chamber = echo_chamber_anlysis('Data/echo_chamber4.json', 'All')
    
    #compare echo chambers by strength
    draw_cdf_plot([echo_chamber[0], echo_chamber3[0], echo_chamber4[0]], 'Depth', ['Echo Chamber 2', 'Echo Chamber 3', 'Echo Chamber 4'], 'Echo Chamber Types', 'Image/%s/echo_depth_4'%folder, log_scale=False)
    draw_cdf_plot([echo_chamber[1], echo_chamber3[1], echo_chamber4[1]], 'Cascade', ['Echo Chamber 2', 'Echo Chamber 3', 'Echo Chamber 4'], 'Echo Chamber Types', 'Image/%s/echo_cascade_4'%folder)
    draw_cdf_plot([echo_chamber[2], echo_chamber3[2], echo_chamber4[2]], 'Child', ['Echo Chamber 2', 'Echo Chamber 3', 'Echo Chamber 4'], 'Echo Chamber Types', 'Image/%s/echo_child_4'%folder)

def get_random_user(users):
    max_num = len(users)
    user1 = users[random.randrange(0,max_num)]
    while(True):
        user2 = users[random.randrange(0,max_num)]
        if user1 != user2:
            break

    return user1, user2 
    
def sub_tree_num(tweets, root_tweet):
    cascade = []
    for tweet in tweets.values():
        if tweet['origin_tweet'] == root_tweet:
            tweet['sub_tree_confirm'] = False
            tweet['sub_tree_num'] = 0
            cascade.append(tweet)
            tweets[tweet['tweet']] = tweet

    #print(len(cascade))
    for item in cascade:
        if item['child'] == 0 and item['sub_tree_confirm'] == False:
            if item['parent_tweet'] != item['tweet']:
                tweets[item['parent_tweet']]['sub_tree_num'] += 1
            item['sub_tree_confirm'] = True

    while(True):
        count =0 
        for item in cascade:
            if item['sub_tree_confirm'] == True:
                count +=1 

        #all calculation done 
        if count == len(cascade):
            break
 
   
        for item in cascade:
            if item['child'] != 0 and item['sub_tree_confirm'] == False and item['sub_tree_num'] != 0:
                if item['parent_tweet'] != item['tweet']:
                    tweets[item['parent_tweet']]['sub_tree_num'] += 1 + item['child']
                item['sub_tree_confirm'] = True

    
def child_speed(tweets, parent_tweet):
    if parent_tweet['child'] == 0:
        return flaot('Inf')
    else:
        children = []
        for tweet in tweets.values():
            if tweet['parent_tweet'] == parent_tweet['tweet'] and tweet['parent_tweet'] != tweet['tweet']:
                children.append(parser.parser(tweet['time']))

        return (min(children) - parser.parse(parent_tweet['time'])).total_seconds() / 60 # minutes 

#get all echo chamber users per postid
def get_echo_chamber_users(file_name):
    #file_name = 'Data/echo_chamber2.json'
    with open(file_name) as f:
        echo_chambers = json.load(f)

    Bot = bot.load_bot()
    echo_chamber_users = {}
    count = 0
    for key in echo_chambers:
        #print(key)
        users = echo_chambers[key]

        postids = key.split('_')
        
        #bot check
        for postid in postids:
            for user in users:
                if bot.check_bot(Bot, user) == 0:
                    echo_chamber_users[postid] = echo_chamber_users.get(postid, {})
                    echo_chamber_users[postid][user] = 1
        count += 1

    print('echo chamber size %s'%count)
    return echo_chamber_users


#cascade : origin tweet for echo chamber user participated or not participated 
def echo_chamber_cascade_analysis(file_name, veracity=None, echo_chamber_users=None):
    #get all echo chamber users per postid
    #file_name = 'Data/echo_chamber2.json'
    #with open(file_name) as f:
    #    echo_chambers = json.load(f)

    print('file name', file_name)

    Bot = bot.load_bot()
    cascade_breadth, cascade_max_depth, cascade_unique_users = e_util.get_cascade_max_breadth()

    if echo_chamber_users == None:
        echo_chamber_users = get_echo_chamber_users(file_name)
    ccc = 0
    echo_chamber_values = {}
    non_echo_chamber_values = {} 
    depth = {}; child = {}; cascade = {}; subtree = {}; breadth = {}; propagate_time = {};
    for item in ['max_depth', 'max_breadth', 'cascade', 'unique_users']:
        echo_chamber_values[item] = {}
        non_echo_chamber_values[item] = {}

    dir_name = 'RetweetNew/'
    for postid in echo_chamber_users.keys():
        users = echo_chamber_users[postid].keys()
        echo_chamber_values[postid] = {}
        if len(users) == 0:
            continue

        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)

        #find cascade information
        unique_users = {}
        unique_tweets = {}
        max_depth = 0

        if veracity != None:
            if not get_veracity(postid, veracity):
                continue
        #print(postid, 'echo chamber users : %s'%len(users))

        echo_chamber_origin = {}
        for tweet in tweets.values():
            #if tweet['user'] in users and tweet['depth'] == 1:
            if tweet['user'] in users:
            #from echo chamber root 
                origin_tweet = tweet['origin_tweet']
                echo_chamber_origin[origin_tweet] = 1
                echo_chamber_values['max_depth'][origin_tweet] = cascade_max_depth[origin_tweet]
                echo_chamber_values['cascade'][origin_tweet] = tweet['cascade']
                echo_chamber_values['max_breadth'][origin_tweet] = cascade_breadth[origin_tweet]
                echo_chamber_values['unique_users'][origin_tweet] = cascade_unique_users[origin_tweet]


        #non echo chamber cascade which do not contain origin tweet of echo chamber 
        for tweet in tweets.values():
            if bot.check_bot(Bot, tweet['user']) != 0:
                continue
            origin_tweet = tweet['origin_tweet']
            if not origin_tweet in echo_chamber_origin.keys():
                non_echo_chamber_values['max_depth'][origin_tweet] = cascade_max_depth[origin_tweet]
                non_echo_chamber_values['cascade'][origin_tweet] = tweet['cascade']
                non_echo_chamber_values['max_breadth'][origin_tweet] = cascade_breadth[origin_tweet]
                non_echo_chamber_values['unique_users'][origin_tweet] = cascade_unique_users[origin_tweet]

        #print(len(echo_chamber_values['max_depth']))
        ccc +=1
        #if ccc > 5:
        #    break
    

    return echo_chamber_values, non_echo_chamber_values

def echo_chamber_political_cascade_analysis(veracity=None):
    #get all echo chamber users per postid
    file_name = 'Data/echo_chamber2.json'
    Bot = bot.load_bot()
    cascade_breadth, cascade_max_depth, cascade_unique_users = get_cascade_max_breadth()
    echo_chamber_users = get_echo_chamber_users(file_name)

    ccc = 0
    echo_chamber_values = {}
    non_echo_chamber_values = {} 
    politics = {}
    non_politics = {}
    p_e = {}; p_ne = {}; np_e = {}; np_ne = {}; #political echo chamber, non echo chamber / non political echo chamber, non echo chamber 
    depth = {}; child = {}; cascade = {}; subtree = {}; breadth = {}; propagate_time = {};
    characteristics = ['max_depth', 'max_breadth', 'cascade', 'unique_users']
    for item in characteristics:
        echo_chamber_values[item] = {}
        non_echo_chamber_values[item] = {}
        politics[item] = {}
        non_politics[item] = {}
        p_e[item] = {}
        p_ne[item] = {}
        np_e[item] = {}
        np_ne[item] = {}

    dir_name = 'RetweetNew/'
   
    for postid in echo_chamber_users.keys():
        users = echo_chamber_users[postid].keys()
        echo_chamber_values[postid] = {}
        non_echo_chamber_values = {} 
        if len(users) == 0:
            continue

        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)

        #find cascade information
        unique_users = {}
        unique_tweets = {}
        max_depth = 0

        if veracity != None:
            if not get_veracity(postid, veracity):
                continue
        print(postid, 'echo chamber users : %s'%len(users))

        max_depth = {}; cascade = {}; max_breadth = {}; unique_users = {};
        e_max_depth = {}; e_cascade = {}; e_max_breadth = {}; e_unique_users = {};
        ne_max_depth = {}; ne_cascade = {}; ne_max_breadth = {}; ne_unique_users = {};
        for tweet in tweets.values():
            origin_tweet = tweet['origin_tweet']
            max_depth[origin_tweet] = cascade_max_depth[origin_tweet]
            cascade[origin_tweet] = tweet['cascade']
            max_breadth[origin_tweet] = cascade_breadth[origin_tweet]
            unique_users[origin_tweet] = cascade_unique_users[origin_tweet]

        echo_chamber_origin = {}
        for tweet in tweets.values():
            if tweet['user'] in users:
                origin_tweet = tweet['origin_tweet']
                echo_chamber_origin[origin_tweet] = 1
                e_max_depth[origin_tweet] = cascade_max_depth[origin_tweet]
                e_cascade[origin_tweet] = tweet['cascade']
                e_max_breadth[origin_tweet] = cascade_breadth[origin_tweet]
                e_unique_users[origin_tweet] = cascade_unique_users[origin_tweet]

        #non echo chamber cascade which do not contain origin tweet of echo chamber 
        for tweet in tweets.values():
            origin_tweet = tweet['origin_tweet']
            if not origin_tweet in echo_chamber_origin.keys():
                ne_max_depth[origin_tweet] = cascade_max_depth[origin_tweet]
                ne_cascade[origin_tweet] = tweet['cascade']
                ne_max_breadth[origin_tweet] = cascade_breadth[origin_tweet]
                ne_unique_users[origin_tweet] = cascade_unique_users[origin_tweet]

        if util.is_politics(postid):
            politics['max_depth'].update(max_depth)
            politics['max_breadth'].update(max_breadth)
            politics['cascade'].update(cascade)
            politics['unique_users'].update(unique_users)
            p_e['max_depth'].update(e_max_depth)
            p_e['max_breadth'].update(e_max_breadth)
            p_e['cascade'].update(e_cascade)
            p_e['unique_users'].update(e_unique_users)
            p_ne['max_depth'].update(ne_max_depth)
            p_ne['max_breadth'].update(ne_max_breadth)
            p_ne['cascade'].update(ne_cascade)
            p_ne['unique_users'].update(ne_unique_users)

        elif util.is_non_politics(postid):
            non_politics['max_depth'].update(max_depth)
            non_politics['max_breadth'].update(max_breadth)
            non_politics['cascade'].update(cascade)
            non_politics['unique_users'].update(unique_users)
            np_e['max_depth'].update(e_max_depth)
            np_e['max_breadth'].update(e_max_breadth)
            np_e['cascade'].update(e_cascade)
            np_e['unique_users'].update(e_unique_users)
            np_ne['max_depth'].update(ne_max_depth)
            np_ne['max_breadth'].update(ne_max_breadth)
            np_ne['cascade'].update(ne_cascade)
            np_ne['unique_users'].update(ne_unique_users)

    print('Politic Rumors ', len(politics['max_depth']))
    print('Non Politic Rumors', len(non_politics['max_depth']))
    print('Politic Rumor Echo Chamber Participation', len(p_e['max_depth']), len(p_ne['max_depth']))
    print('Non Politic Rumor Echo Chamber Participation', len(np_e['max_depth']), len(np_ne['max_depth']))
    #political vs. non-political
    draw_cdf_plot([politics['max_depth'].values(), non_politics['max_depth'].values()], 'Depth',['Politics', 'Non Politics'], 'Category', 'Image/%s/politic_depth'%folder, log_scale=False) 
    draw_cdf_plot([politics['max_breadth'].values(), non_politics['max_breadth'].values()], 'Breadth',['Politics', 'Non Politics'], 'Category', 'Image/%s/politic_breadth'%folder) 
    draw_cdf_plot([politics['cascade'].values(), non_politics['cascade'].values()], 'Cascade',['Politics', 'Non Politics'], 'Category', 'Image/%s/politic_cascade'%folder) 
    draw_cdf_plot([politics['unique_users'].values(), non_politics['unique_users'].values()], 'Number of users',['Politics', 'Non Politics'], 'Category', 'Image/%s/politic_unique_users'%folder) 

    #ccdf for political vs. non-political
    draw_ccdf_plot([politics['max_depth'].values(), non_politics['max_depth'].values()], 'Depth',['Politics', 'Non Politics'], 'Category', 'Image/%s/politic_depth_ccdf'%folder, log_scale=False) 
    draw_ccdf_plot([politics['max_breadth'].values(), non_politics['max_breadth'].values()], 'Breadth',['Politics', 'Non Politics'], 'Category', 'Image/%s/politic_breadth_ccdf'%folder) 
    draw_ccdf_plot([politics['cascade'].values(), non_politics['cascade'].values()], 'Cascade',['Politics', 'Non Politics'], 'Category', 'Image/%s/politic_cascade_ccdf'%folder) 
    draw_ccdf_plot([politics['unique_users'].values(), non_politics['unique_users'].values()], 'Number of users',['Politics', 'Non Politics'], 'Category', 'Image/%s/politic_unique_users_ccdf'%folder) 



    #political echo vs. non echo 
    draw_cdf_plot([p_e['max_depth'].values(), p_ne['max_depth'].values()], 'Depth',['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/politic_depth_e'%folder, log_scale=False) 
    draw_cdf_plot([p_e['max_breadth'].values(), p_ne['max_breadth'].values()], 'Breadth',['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/politic_breadth_e'%folder) 
    draw_cdf_plot([p_e['cascade'].values(), p_ne['cascade'].values()], 'Cascade',['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/politic_cascade_e'%folder) 
    draw_cdf_plot([p_e['unique_users'].values(), p_ne['unique_users'].values()], 'Number of users',['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/politic_unique_users_e'%folder) 

    #non political echo vs. non echo 
    draw_cdf_plot([np_e['max_depth'].values(), np_ne['max_depth'].values()], 'Depth',['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/politic_depth_e2'%folder, log_scale=False) 
    draw_cdf_plot([np_e['max_breadth'].values(), np_ne['max_breadth'].values()], 'Breadth',['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/politic_breadth_e2'%folder) 
    draw_cdf_plot([np_e['cascade'].values(), np_ne['cascade'].values()], 'Cascade',['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/politic_cascade_e2'%folder) 
    draw_cdf_plot([np_e['unique_users'].values(), np_ne['unique_users'].values()], 'Number of users',['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/politic_unique_users_e2'%folder) 

#    return politics, non_politics

def draw_echo_chamber_cascade_chracteristics():
   
    start_time = time()
    echo_chamber_values, non_echo_chamber_values = echo_chamber_cascade_analysis('Data/echo_chamber2.json')
    end_time = time()
    print('echo chamber2 takes %s'%(end_time - start_time))
    with open('Data/Figure/5_1_2.json', 'w') as f:
        json.dump({'echo':echo_chamber_values, 'necho':non_echo_chamber_values}, f)

    #echo_chamber_values, non_echo_chamber_values = echo_chamber_cascade_analysis('Data/echo_chamber2.json')
    draw_cdf_plot([echo_chamber_values['max_depth'].values(), non_echo_chamber_values['max_depth'].values()], 'Depth',[], '', 'Image/%s/echo_depth3'%folder) 
    draw_cdf_plot([echo_chamber_values['max_breadth'].values(), non_echo_chamber_values['max_breadth'].values()], 'Breadth',[], 'User Type', 'Image/%s/echo_breadth3'%folder) 
    draw_cdf_plot([echo_chamber_values['cascade'].values(), non_echo_chamber_values['cascade'].values()], 'Cascade',[], 'User Type', 'Image/%s/echo_cascade3'%folder) 
    draw_cdf_plot([echo_chamber_values['unique_users'].values(), non_echo_chamber_values['unique_users'].values()], 'Number of users',[], 'User Type', 'Image/%s/echo_unique_users3'%folder) 
   
    draw_ccdf_plot([echo_chamber_values['max_depth'].values(), non_echo_chamber_values['max_depth'].values()], 'Depth',['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/echo_depth3_ccdf'%folder) 
    draw_ccdf_plot([echo_chamber_values['max_breadth'].values(), non_echo_chamber_values['max_breadth'].values()], 'Breadth',['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/echo_breadth3_ccdf'%folder) 
    draw_ccdf_plot([echo_chamber_values['cascade'].values(), non_echo_chamber_values['cascade'].values()], 'Cascade',['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/echo_cascade3_ccdf'%folder) 
    draw_ccdf_plot([echo_chamber_values['unique_users'].values(), non_echo_chamber_values['unique_users'].values()], 'Number of users',['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/%s/echo_unique_users3_ccdf'%folder) 

    return 
    #degree ranked cascade 
    with open('Data/degree_ranked_users.json', 'r') as f:
        ranked_users = json.load(f)
    ranked_echo, non_echo = echo_chamber_cascade_analysis(None, echo_chamber_users = ranked_users)

    with open('Data/ranked_weight2_echo_chamber.json', 'r') as f:
        ranked_users2 = json.load(f)
    
    with open('Data/ranked_weight5_echo_chamber.json', 'r') as f:
        ranked_users5 = json.load(f)

    with open('Data/ranked_weight10_echo_chamber.json', 'r') as f:
        ranked_users10 = json.load(f)
    
    ranked_echo2, non_echo = echo_chamber_cascade_analysis(None, echo_chamber_users = ranked_users2)
    ranked_echo5, non_echo = echo_chamber_cascade_analysis(None, echo_chamber_users = ranked_users5)
    ranked_echo10, non_echo = echo_chamber_cascade_analysis(None, echo_chamber_users = ranked_users10)

    draw_cdf_plot([echo_chamber_values['max_depth'].values(), non_echo_chamber_values['max_depth'].values(), ranked_echo2['max_depth'].values(), ranked_echo5['max_depth'].values(), ranked_echo10['max_depth'].values()],
            'Depth',['Echo Chamber', 'Non Echo Chamber', 'Ranked Weight 2', 'Ranked Weight 5', 'Ranked Weight 10'], 'User Type', 'Image/%s/echo_depth_ranked'%folder, log_scale=False) 
    draw_cdf_plot([echo_chamber_values['max_breadth'].values(), non_echo_chamber_values['max_breadth'].values(), ranked_echo2['max_breadth'].values(), ranked_echo5['max_breadth'].values(), ranked_echo10['max_breadth'].values()], 
            'Breadth',['Echo Chamber', 'Non Echo Chamber','Ranked Weight 2', 'Ranked Weight 5', 'Ranked Weight 10'], 'User Type', 'Image/%s/echo_breadth_ranked'%folder) 
    draw_cdf_plot([echo_chamber_values['cascade'].values(), non_echo_chamber_values['cascade'].values(), ranked_echo2['cascade'].values(), ranked_echo5['cascade'].values(), ranked_echo10['cascade'].values()], 'Cascade',
        ['Echo Chamber', 'Non Echo Chamber','Ranked Weight 2', 'Ranked Weight 5', 'Ranked Weight 10'], 'User Type', 'Image/%s/echo_cascade_ranked'%folder) 
    draw_cdf_plot([echo_chamber_values['unique_users'].values(), non_echo_chamber_values['unique_users'].values(), ranked_echo2['unique_users'].values(), ranked_echo5['unique_users'].values(), ranked_echo10['unique_users'].values() ], 
        'Number of users',['Echo Chamber', 'Non Echo Chamber','Ranked Weight 2', 'Ranked Weight 5', 'Ranked Weight 10'], 'User Type', 'Image/%s/echo_unique_users_ranked'%folder) 
    
    print('ranked cascade calculation done')
   
    
    start_time = time()
    echo_chamber_values2, non_echo_chamber_values = echo_chamber_cascade_analysis('Data/echo_chamber3.json')
    end_time = time()
    print('echo chamber3 takes %s'%(end_time - start_time))
    start_time = time()
    echo_chamber_values3, non_echo_chamber_values = echo_chamber_cascade_analysis('Data/echo_chamber4.json')
    end_time = time()
    print('echo chamber4 takes %s'%(end_time - start_time))

    draw_cdf_plot([echo_chamber_values['max_depth'].values(), echo_chamber_values2['max_depth'].values(), echo_chamber_values3['max_depth'].values()], 'Depth',['Echo Chamber2', 'Echo Chamber3', 'Echo Chamber4'], 'User Type', 'Image/%s/echo_depth2'%folder, log_scale=False) 
    draw_cdf_plot([echo_chamber_values['max_breadth'].values(), echo_chamber_values2['max_breadth'].values(), echo_chamber_values3['max_breadth'].values()], 'Breadth',['Echo Chamber2', 'Echo Chamber3', 'Echo Chamber4'], 'User Type', 'Image/%s/echo_breadth2'%folder) 
    draw_cdf_plot([echo_chamber_values['cascade'].values(), echo_chamber_values2['cascade'].values(), echo_chamber_values3['cascade'].values()], 'Cascade',['Echo Chamber2', 'Echo Chamber3', 'Echo Chamber4'], 'User Type', 'Image/%s/echo_cascade2'%folder) 
    draw_cdf_plot([echo_chamber_values['unique_users'].values(), echo_chamber_values2['unique_users'].values(), echo_chamber_values3['unique_users'].values()], 'Number of users',['Echo Chamber2', 'Echo Chamber3', 'Echo Chamber4'], 'User Type', 'Image/%s/echo_unique_users2'%folder) 
    
    

def echo_chamber_user_analysis():
    #get all echo chamber users per postid
    file_name = 'Data/echo_chamber2.json'
    with open(file_name) as f:
        echo_chambers = json.load(f)

    Bot = bot.load_bot()
    cascade_breadth, cascade_max_depth, cascade_unique_users = get_cascade_max_breadth()

    echo_chamber_users = {}
    for key in echo_chambers:
        #print(key)
        users = echo_chambers[key]

        postids = key.split('_')
        
        #bot check
        for postid in postids:
            for user in users:
                if bot.check_bot(Bot, user) == 0:
                    echo_chamber_users[postid] = echo_chamber_users.get(postid, {})
                    echo_chamber_users[postid][user] = 1

    #with open('Data/echo_chamber_user.json', 'r') as f:
        #echo_chamber_user = json.load(f)


    #import csv
    #f = open('Data/echo_characteristics_cascade.csv', 'w')
    #cwriter = csv.writer(f, delimiter='\t')
    #cwriter.writerow(['postid', 'all depth', 'all child', 'all subtree', 'all propagation time', 'echo depth', 'echo child', 'echo sub_tree', 'echo propagation time'])
    ccc = 0
    echo_chamber_values = {}
    non_echo_chamber_values = {} 
    depth = {}; child = {}; cascade = {}; subtree = {}; breadth = {}; propagate_time = {};
    for item in ['max_depth', 'max_breadth', 'cascade', 'unique_users']:
        echo_chamber_values[item] = {}
        non_echo_chamber_values[item] = {}

    for item in ['False', 'True','Mixed', 'e', 'n']:
        depth[item] = []
        child[item] = []
        cascade[item] = []
        subtree[item] = []
        breadth[item] = []
        propagate_time[item] = []
    dir_name = 'RetweetNew/'
    for postid in echo_chamber_users.keys():
        users = echo_chamber_users[postid].keys()
        echo_chamber_values[postid] = {}
        if len(users) == 0:
            continue

        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)

        #find cascade information
        unique_users = {}
        unique_tweets = {}
        max_depth = 0

        print(postid, 'echo chamber users : %s'%len(users))
    
        echo_depth = []
        echo_cascade = []
        echo_child = []
        echo_sub_tree = []
        echo_propagation_time = []
        echo_breadth = []
        all_depth = []
        all_cascade = []
        all_child = []
        all_sub_tree = []
        all_propagation_time = []

        
        #echo chamber characteristics per veracity
        if get_veracity(postid, 'True'):
            v= 'True'
        elif get_veracity(postid, 'False'):
            v = 'False'
        else:
            v = 'Mixed'

        for tweet in tweets.values():
            if tweet['user'] in users:
                unique_tweets[tweet['origin_tweet']] = 1 
                unique_tweet = tweet['origin_tweet']
                echo_depth.append(tweet['depth'])
                echo_cascade.append(tweet['cascade'])
                echo_child.append(tweet['child'])
                #echo_sub_tree.append(tweet['sub_tree_num'])
                echo_breadth.append(cascade_breadth[tweet['origin_tweet']])
                
                depth[v].append(tweet['depth'])
                cascade[v].append(tweet['cascade'])
                child[v].append(tweet['child'])
                #subtree[v].append(tweet['sub_tree_num'])
                breadth[v].append(cascade_breadth[tweet['origin_tweet']])
                
                #if tweet['propagate_time'] != float('Inf'):
                #    echo_propagation_time.append(float(tweet['propagate_time']))
                #    propagate_time[v].append(float(tweet['propagate_time']))
        
        
        #print(np.mean(echo_depth), np.mean(echo_child), np.mean(echo_sub_tree), np.mean(echo_propagation_time))
        #print(np.mean(all_depth), np.mean(all_child), np.mean(all_sub_tree), np.mean(all_propagation_time))
        #cwriter.writerow([postid, np.mean(all_depth), np.mean(all_child), np.mean(all_sub_tree), np.mean(all_propagation_time), np.mean(echo_depth), np.mean(echo_child), np.mean(echo_sub_tree), np.mean(echo_propagation_time)])
        ccc +=1
        #if ccc > 5:
        #    break
    

    draw_cdf_plot(depth['True'], depth['False'], depth['Mixed'], 'Depth',['True', 'False', 'Mixed'], 'Image/%s/echo_depth'%folder, log_scale=False) 
    draw_cdf_plot(child['True'], child['False'], child['Mixed'], 'Child',['True', 'False', 'Mixed'], 'Image/%s/echo_child'%folder) 
    draw_cdf_plot(subtree['True'], subtree['False'], subtree['Mixed'], 'Sub Tree Size',['True', 'False', 'Mixed'], 'Image/%s/echo_subtree'%folder) 
    draw_cdf_plot(breadth['True'], breadth['False'], breadth['Mixed'], 'Breadth',['True', 'False', 'Mixed'], 'Image/%s/echo_breadth'%folder) 
    draw_cdf_plot(cascade['True'], cascade['False'], cascade['Mixed'], 'Cascade',['True', 'False', 'Mixed'], 'Image/%s/echo_cascade'%folder) 
    #draw_cdf_plot(propagate_time['True'], propagate_time['False'], propagate_time['Mixed'], 'Propagation Time',['True', 'False', 'Mixed'], 'Image/%s/echo_propagate_time'%folder) 
    #f.close()
    #with open('Data/echo_chamber_user.json', 'w') as f:
        #json.dump({'all':{'depth':all_depth, 'child':all_child, 'sub_tree':all_sub_tree, 'propagation_time' : all_propagation_time, 'cascade':all_cascade}, 'echo':{'depth':echo_depth, 'child':echo_child, 'sub_tree':echo_sub_tree, 'propagation_time':echo_propagation_time, 'cascade':echo_cascade}}, f)

#draw graph from saved data
def draw_echo_chamber_user_characteristics():
    with open('Data/echo_chamber_user.json', 'r') as f:
        data = json.load(f)

    echo_depth = data['all']['depth']
    echo_cascade = data['all']['cascade']
    echo_child = data['all']['child']
    echo_sub_tree = data['all']['sub_tree']
    echo_propagation_time = data['all']['propagation_time']
    
    all_depth = data['echo']['depth']
    all_cascade = data['echo']['cascade']
    all_child = data['echo']['child'] 
    all_sub_tree = data['echo']['sub_tree']
    all_propagation_time = data['echo']['propagation_time']

    draw_cdf_plot(all_cascade, echo_cascade, 'Cascade Size', 'All', 'Echo', 'Image/%s/cascade_all'%folder)
    draw_cdf_plot(all_depth, echo_depth, 'Depth', 'All', 'Echo', 'Image/%s/depth_all'%folder, log_scale=False)
    draw_cdf_plot(all_child, echo_child, 'Child', 'All', 'Echo', 'Image/%s/child_all'%folder)
    draw_cdf_plot(all_sub_tree, echo_sub_tree, 'Sub Tree Size', 'All', 'Echo', 'Image/%s/sub_tree_all'%folder)
    draw_cdf_plot(all_propagation_time, echo_propagation_time, 'Propagation Time', 'All', 'Echo', 'Image/%s/propagation_time_all'%folder)


#mean value analysis
def draw_echo_chamber_user_analysis():
    import csv
    with open('Data/echo_characteristics_cascade.csv', 'r') as f:
        creader = csv.reader(f, delimiter = '\t') 

        echo_depth = []
        echo_cascade = []
        echo_child = []
        echo_sub_tree = []
        echo_propagation_time = []
        
        all_depth = []
        all_cascade = []
        all_child = []
        all_sub_tree = []
        all_propagation_time = []

        f_d = []; f_c = []; f_s = []; f_p = [];
        t_d = []; t_c = []; t_s = []; t_p = [];
        m_d = []; m_c = []; m_s = []; m_p = [];

        for i, row in enumerate(creader):
            if i == 0:
                continue
            
            all_depth.append(row[1])
            all_child.append(row[2])
            all_sub_tree.append(row[3])
            all_propagation_time.append(float(row[4]))
            echo_depth.append(row[5])
            echo_child.append(row[6])
            echo_sub_tree.append(row[7])
            echo_propagation_time.append(float(row[8]))

            if get_veracity(row[0], 'True'):
                t_d.append(row[5])
                t_c.append(row[6])
                t_s.append(row[7])
                t_p.append(float(row[8]))

            if get_veracity(row[0], 'False'):
                f_d.append(row[5])
                f_c.append(row[6])
                f_s.append(row[7])
                f_p.append(float(row[8]))

            if get_veracity(row[0], 'Mixture,Mostly True,Mostly False'):
                m_d.append(row[5])
                m_c.append(row[6])
                m_s.append(row[7])
                m_p.append(float(row[8]))

        draw_cdf_plot(t_d, f_d, m_d, 'Depth', ['True', 'False','Mixed'], 'Image/%s/depth_veracity'%folder, log_scale=False)
        draw_cdf_plot(t_c, f_c, m_c, 'Child', ['True', 'False','Mixed'], 'Image/%s/child_veracity'%folder)
        draw_cdf_plot(t_s, f_s, m_s, 'Sub Tree Size', ['True', 'False','Mixed'], 'Image/%s/sub_tree_veracity'%folder)
        draw_cdf_plot(t_p, f_p, m_p, 'Propagation Time', ['True', 'False','Mixed'], 'Image/%s/propagation_time_veracity'%folder)




#how many users in echo chamber - distribution
def statistics(filename):
    with open(filename, 'r') as f:
        echo_chamber = json.load(f)

    users = []
    echo_exist = 0 
    unique_users = {}
    for key in echo_chamber.keys():
        user_num = len(echo_chamber[key]) # users 
        for user in echo_chamber[key]:
            unique_users[user] = 1
        if user_num > 1:
            echo_exist += 1 

        users.append(user_num)

    print('echo chamber exists in %s / %s combination'%(echo_exist, len(echo_chamber)))
    print('unique user : %s'%len(unique_users))
    print(min(users))
    return users

def draw_statistics():
    user2 = statistics('Data/echo_chamber2.json')
    user3 = statistics('Data/echo_chamber3.json')
    user4 = statistics('Data/echo_chamber4.json')
    #user5 = statistics('Data/echo_chamber5.json')

    #draw_cdf_plot([user2, user3, user4, user5], 'Number of Users', ['2', '3', '4', '5'], 'Echo Chamber', 'Image/%s/echo_chamber_statistics')
    draw_cdf_plot([user2, user3, user4], 'Number of Users', ['Strength 2', 'Strength 3', 'Strength 4'], 'Echo Chamber', 'Image/%s/echo_chamber_statistics'%folder)
   

#show echo chamber users get information from whom  (echo chamber or non echo chamber user)
def propagation_within_echo_chamber():
    filename = 'Data/echo_chamber2.json'
    with open(filename, 'r') as f:
        echo_chambers = json.load(f)

    #echo chamber users in a rumor
    Bot = bot.load_bot()
    
    #cascade that echo chamber users particiate in
    cascade_size = {}
    cascade_path = {}
    cascade_node = {} #echo chamber node count in a cascade
    cascade_depth = {}
   
    #non echo chamber 
    ne_cascade_path = {}
    ne_cascade_node = {} 
    ne_cascade_depth = {}

    ccc = 0
    retweet_cache = {}
    path_distribution = []
    path_distribution2 = []
    #calculate echo chamber users in one echo chamber independently 
    for key in echo_chambers:
        #print(key)
        users = echo_chambers[key]

        postids = key.split('_')
        
        #bot check
        for postid in postids:
            echo_users = {}
            for user in users:
                if bot.check_bot(Bot, user) == 0:
                    echo_users[user] = 1

            if len(echo_users) < 1:
                continue

            #load retweet graph 
            if retweet_cache.get(postid, -1) == -1:
                with open('RetweetNew/%s'%postid, 'r') as f:
                    tweets = json.load(f)
                    retweet_cache[postid] = tweets
            else:
                tweets = retweet_cache[postid]
            cascade_size[key] = {}
            cascade_path[key] = {}
            cascade_node[key] = {}
            cascade_depth[key] = {}
            ne_cascade_path[key] = {}
            ne_cascade_node[key] = {}
            ne_cascade_depth[key] = {}


            #check a node is from whom (for echo chamber, non echo chamber node)
            for tweet in tweets.values():
                if tweet['cascade'] == 1:
                    continue

                cascade_size[key][tweet['origin_tweet']] = tweet['cascade']
                if tweet['user'] in echo_users:
                    #check the parent is echo chamber user 
                    if tweet['user'] != tweet['parent'] and tweet['parent'] in echo_users.keys() and tweet['depth'] != 1:
                        cascade_path[key][tweet['origin_tweet']] = cascade_path[key].get(tweet['origin_tweet'], 0) + 1 
                    
                    #node count in the cascade. if a node is not a root node, then increase the count
                    if tweet['depth'] != 1:
                        cascade_node[key][tweet['origin_tweet']] = cascade_node[key].get(tweet['origin_tweet'], 0) + 1 
                        
                    if cascade_depth[key].get(tweet['origin_tweet'], 0) < tweet['depth']: # max depth
                        cascade_depth[key][tweet['origin_tweet']] = tweet['depth']
                else:
                    #check the parent is echo chamber user 
                    if tweet['user'] != tweet['parent'] and tweet['parent'] in echo_users.keys() and tweet['depth'] != 1:
                        ne_cascade_path[key][tweet['origin_tweet']] = ne_cascade_path[key].get(tweet['origin_tweet'], 0) + 1 
                    
                    if tweet['depth'] != 1:
                        ne_cascade_node[key][tweet['origin_tweet']] = ne_cascade_node[key].get(tweet['origin_tweet'], 0) + 1 
                        
                    if ne_cascade_depth[key].get(tweet['origin_tweet'], 0) < tweet['depth']: # max depth
                        ne_cascade_depth[key][tweet['origin_tweet']] = tweet['depth']
        ccc += 1 
        #if ccc > 100:
        #    break

    for postid in cascade_path.keys(): #echo chamber
    #    print(postid)
        for cascade in cascade_path[postid].keys(): #cascade id
            #print(cascade)
            #path_num : number of node receive rumors from echo chamber nodes 
            #node_num : number of node in the cascade
            path_num = cascade_path[postid][cascade]
            node_num = cascade_node[postid][cascade]
            #if node_num == 1:
            #    continue
            #print('Path : %s / %s, Size : %s'%(path_num, node_num , cascade_size[postid][cascade])) # if they are same then, all rumor propagate within echo chambers 
            """
            try :
                path_num2 = ne_cascade_path[postid][cascade]
                node_num2 = ne_cascade_node[postid][cascade]
            except KeyError:
                pass
            print('%s / %s, %s / %s, Size : %s'%(path_num, node_num, path_num2, node_num2, cascade_size[postid][cascade]))
            """


            #print(path_num / node_num, round(path_num / node_num, 1))
            #path_distribution.append(round(path_num/node_num, 3))
            path_distribution.append(path_num/node_num)
     
    for postid in ne_cascade_path.keys(): #rumor
        #print(postid)
        for cascade in ne_cascade_path[postid].keys(): #cascade
            path_num = ne_cascade_path[postid][cascade]
            node_num = ne_cascade_node[postid][cascade]
            if node_num == 1:
                continue
            #path_distribution2.append(round(path_num/node_num, 3))
            path_distribution2.append(path_num/node_num)
    
    #draw_cdf_plot([path_distribution], 'Ratio', [''], '', 'Image/%s/echo_chamber_path_ratio')
    #draw_cdf_plot([path_distribution2], 'Ratio', [''], '', 'Image/%s/echo_chamber_path_ratio2'%folder)
    with open('Data/Figure/5_1_3_2.json', 'w') as f:
        json.dump([path_distribution, path_distribution2], f)
    draw_cdf_plot([path_distribution, path_distribution2], 'Ratio', ['Echo Chamber', 'Non Echo chamber'], '', 'Image/%s/echo_chamber_path_ratio2'%folder, log_scale=False)

#search how many nodes (tweets) receive from echo chamber users 
def echo_chamber_rumor_spread():
    files = ['Data/echo_chamber2.json', 'Data/echo_chamber3.json', 'Data/echo_chamber4.json']
    for filename in files:
        echo_chamber_users = e_util.get_echo_chamber_users(filename)
        
        all_node = 0
        from_echo = 0
        is_echo = 0
        files = os.listdir(dirname)
        for i, postid in enumerate(files):
            #print(i, postid)
            with open(dirname + postid, 'r') as f:
                tweets = json.load(f)
        
                for tweet in tweets.values():
                    all_node += 1 
                    if tweet['parent'] in echo_chamber_users[postid].keys():
                        from_echo += 1
                        if tweet['user'] in echo_chamber_users[postid].keys():
                            is_echo += 1


        print('Nodes receive rumors from echo chambers users : %s, child : %s all tweets : %s'%(is_echo, from_echo, all_node))

#distribution of cascade per depth 
#1,2,3,4,5
#1~2, 3~maximum
def depth_analysis():
    echo_chamber_users = e_util.get_echo_chamber_users('Data/echo_chamber2.json')
    files = os.listdir('RetweetNew')
    follower_path = '../Data/followers/followers/'

    d = {}
    n = {}
    for i in range(1, 20):
        d[i] = []
        n[i] = []

    for ccc, postid in enumerate(files):
        users = echo_chamber_users[postid]

        with open('RetweetNew/' + postid, 'r') as f:
            tweets = json.load(f)

            for tweet in tweets.values():
                user = tweet['user']
                with open(follower_path + user, 'r') as f:
                    followers = json.load(f)
                if user in users:
                    d[tweet['depth']].append(tweet['cascade'])
                    d[tweet['depth']].append(len(followers))
                else:
                    n[tweet['depth']].append(len(followers))

        if ccc == 100:
            break

    draw_cdf_plot([d[i] for i in range(1,6)], 'Follower Size', ['1', '2', '3', '4', '5'], 'Depth', 'Image/%s/follower_num_per_depth_cdf'%folder)
 
    box = BoxPlot(1)
    box.set_multiple_data([d, n])
    box.set_ylog()
    box.set_label('Depth', 'Follower Count')
    box.save_image('Image/%s/follower_num_per_depth_box.png'%folder)



    a = []; b = []
    a.extend(d[1])
    a.extend(d[2])
    for i in range(3,15):
        b.extend(d[i]) 
    draw_cdf_plot([a, b], 'Cascade Size', ['1-2', '3-max'], 'Depth', 'Image/%s/cascade_size_per_depth2'%folder)


    draw_cdf_plot([d[i] for i in range(1,5)], 'Cascade Size', ['1', '2', '3', '4'], 'Depth', 'Image/%s/cascade_size_per_depth'%folder)
    a = []; b = []
    a.extend(d[1])
    a.extend(d[2])
    for i in range(3,15):
        b.extend(d[i]) 
    draw_cdf_plot([a, b], 'Cascade Size', ['1-2', '3-max'], 'Depth', 'Image/%s/cascade_size_per_depth2'%folder)


    draw_ccdf_plot([d[i] for i in range(1,5)], 'Cascade Size', ['1', '2', '3', '4'], 'Depth', 'Image/%s/cascade_size_per_depth_ccdf'%folder)
    draw_ccdf_plot([a, b], 'Cascade Size', ['1-2', '3-max'], 'Depth', 'Image/%s/cascade_size_per_depth2_ccdf'%folder)

    print('done')
    
def draw_cdf_plot(datas, datatype, legend, legend_type, filename, log_scale=True):
    cdf = CDFPlot()
    cdf.set_label(datatype, 'CDF')
    cdf.set_log(log_scale)
    for i in range(len(datas)):
        cdf.set_data(datas[i], legend[i])
    if len(legend) > 1:
        cdf.set_legends(legend, legend_type)
    cdf.save_image('%s.png'%filename)

def draw_ccdf_plot(datas, datatype, legend, legend_type, filename, log_scale=True):
    cdf = CCDFPlot()
    cdf.set_label(datatype, 'CCDF')
    cdf.set_log(log_scale)
    for i in range(len(datas)):
        cdf.set_data(datas[i])
    if len(legend) > 1:
        cdf.set_legends(legend, legend_type)
    cdf.save_image('%s.png'%filename)

if __name__ == "__main__":
    #following_anlysis()
    folder = '20181031' 
    dirname = 'RetweetNew/'
    start = time()
    #find_echo_chamber(2)
    #find_echo_chamber(3)
    #find_echo_chamber(4)
    #find_echo_chamber(5)  not working because of memory problem
    
    #draw_statistics()
    #draw_echo_chamber_true_false()
    propagation_within_echo_chamber()
    #draw_echo_chamber_cascade_chracteristics()
    #echo_chamber_rumor_spread()
    #echo_chamber_political_cascade_analysis('False')
    #echo_chamber_user_characteristics()
    #depth_analysis()

    #echo_chamber_anlysis('Data/echo_chamber2.json', 'True')
    #echo_chamber_user_analysis()
    #draw_echo_chamber_user_characteristics()
    #draw_echo_chamber_user_analysis()

    end = time()
    print('%s taken'%(end-start))
