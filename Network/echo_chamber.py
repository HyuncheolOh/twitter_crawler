from __future__ import division
import json, os, sys
import MySQLdb 
import numpy as np
import random
import itertools
import bot_detect as bot
from time import time 
from draw_tools.cdf_plot import CDFPlot

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
    dir_name = 'Retweet/'
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
    dir_name = "Retweet/"
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
        if count % 100 == 0:
            print(count)
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

    #check all tweets in retweet network 
    dir_name = "Retweet/"
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
    """
    files = os.listdir('Retweet')
    depth_all = []
    cascade_all = []
    child_all = []
    for postid in files:
        if cache.get(postid, -1) == -1:
            with open('Retweet/' + postid, 'r') as f:
                tweets = json.load(f)
                cache[postid] = tweets
        else:
            tweets = cache[postid]

        for td in tweets:
            try:
                depth_all.append(tweets[td]['depth'])
                cascade_all.append(tweets[td]['cascade'])
                child_all.append(tweets[td]['child'])
            except KeyError as e:
                print(postid)
    """
    return {'depth':echo_chamber_depth, 'child':echo_chamber_child, 'cascade':echo_chamber_cascade, 'breadth':echo_chamber_breadth}
    
    #with open('Data/depth_echochamber3.json', 'w') as f:
    #    #json.dump({'echo_chamber':echo_chamber_depth, 'all': depth_all} , f)
    #    json.dump({'echo_chamber': {'depth':echo_chamber_depth, 'child':echo_chamber_child, 'cascade':echo_chamber_cascade, 'breadth':echo_chamber_breadth}, 'all': {'depth':depth_all, 'cascade':cascade_all, 'child':child_all, 'breadth':cascade_breadth}}, f)
def get_list(data, key):
    return list(itertools.chain(*[item.values() for item in data[key].values()]))[0]

def draw_echo_chamber_true_false():
    echo_chamber, non_echo_chamber = echo_chamber_anlysis('Data/echo_chamber2.json', 'All')

    #draw_cdf_plot([path_distribution, path_distribution2], 'Ratio', ['type1', 'type2'], '', 'Image/20180920/echo_chamber_path_ratio2')
    draw_cdf_plot([echo_chamber[0], non_echo_chamber[0]], 'Depth', ['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/20180930/echo_depth')
    draw_cdf_plot([echo_chamber[1], non_echo_chamber[1]], 'Cascade', ['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/20180930/echo_cascade')
    draw_cdf_plot([echo_chamber[2], non_echo_chamber[2]], 'Child', ['Echo Chamber', 'Non Echo Chamber'], 'User Type', 'Image/20180930/echo_child')
    
    #draw_cdf_plot([path_distribution, path_distribution2], 'Ratio', ['type1', 'type2'], '', 'Image/20180920/echo_chamber_path_ratio2')
    non_echo_chamber[0].extend(echo_chamber[0])
    non_echo_chamber[1].extend(echo_chamber[1])
    non_echo_chamber[2].extend(echo_chamber[2])

    draw_cdf_plot([echo_chamber[0], non_echo_chamber[0]], 'Depth', ['Echo Chamber', 'All'], 'User Type', 'Image/20180930/echo_depth_all')
    draw_cdf_plot([echo_chamber[1], non_echo_chamber[1]], 'Cascade', ['Echo Chamber', 'All'], 'User Type', 'Image/20180930/echo_cascade_all')
    draw_cdf_plot([echo_chamber[2], non_echo_chamber[2]], 'Child', ['Echo Chamber', 'All'], 'User Type', 'Image/20180930/echo_child_all')

def get_random_user(users):
    max_num = len(users)
    user1 = users[random.randrange(0,max_num)]
    while(True):
        user2 = users[random.randrange(0,max_num)]
        if user1 != user2:
            break

    return user1, user2 
    
#find mutual follower or have common friends 
def following_anlysis():

    friends_dir = '../Data/friends/friends/'
    with open('Data/echo_chamber2.json') as f:
        echo_chambers = json.load(f)


    print('total ', len(echo_chambers))
    friends_cache = {}
    comm_friends_count = {}
    postid = {}
    count = 0
    for key in echo_chambers:
        #print(key)
        users = echo_chambers[key]
        #print(users)
        postids = key.split('_')
        postid[key] = 1
        
        count += 1 
        if count % 100 == 0:
            #print(count)
            print(count)
            #break
        #print('echo chamber users', len(users))
        if len(users) < 2:
            continue

       
        comm_friends = []
        for i in range(len(users)):
            user1 = users[i]
            
            if friends_cache.get(user1, -1) == -1:
                with open(friends_dir + user1, 'r') as f:
                    user_friends1 = json.load(f)
                    friends_cache[user1] = user_friends1
            else:
                user_friends1 = friends_cache[user1]

            for j in range(i+1, len(users)):
                user2 = users[j]

                if friends_cache.get(user2, -1) == -1:
                    with open(friends_dir + user2, 'r') as f:
                        user_friends2 = json.load(f)
                        friends_cache[user2] = user_friends2
                else:
                    user_friends2 = friends_cache[user2]

                common_friends = set(user_friends1) & set(user_friends2)
                comm_friends.append(len(common_friends))
            #print(comm_friends)
            comm_friends_count[key] = comm_friends
    print(len(comm_friends_count))
    print(len(postid))
    dir_name = 'Retweet/'
    random_friends_count = {}
    for key in postid.keys():
        user_num = len(comm_friends_count[key])
        pids = key.split(',')
        
        for postid in pids:
            r_comm_friends = []
            for _ in range(user_num):
                with open(dir_name + postid, 'r') as f:
                    tweets = json.load(f)
                users = [tweet['user'] for tweet in tweets]
                user1, user2 = get_random_user(users)
                if friends_cache.get(user1, -1) == -1:
                    with open(friends_dir + user1, 'r') as f:
                        user_friends1 = json.load(f)
                        friends_cache[user1] = user_friends1
                else:
                    user_friends1 = friends_cache[user1]

                if friends_cache.get(user2, -1) == -1:
                    with open(friends_dir + user2, 'r') as f:
                        user_friends2 = json.load(f)
                        friends_cache[user2] = user_friends2
                else:
                    user_friends2 = friends_cache[user2]
                
                common_friends = set(user_friends1) & set(user_friends2)
                r_comm_friends.append(len(common_friends))
        random_friends_count[key] = r_comm_friends

    with open('Data/comm_friends.json', 'w') as f:
        json.dump({'echo_chamber':comm_friends_count, 'random':random_friends_count}, f)

    """
    #child
    cdf = CDFPlot()
    cdf.set_data(child_all, 'all')
    cdf.set_label('Friends', 'CDF')
    cdf.set_log(True)
    cdf.set_data(echo_child_all, 'echo chamber')
    cdf.set_legends(['random', 'echo chamber'], 'user type')
    cdf.save_image('Image/echochamber_friends_cdf.png')
    """
    return echo_child_all

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

#analyze cascades which have echo chambers or not

def echo_chamber_cascade_analysis(veracity=None):
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
    ccc = 0
    echo_chamber_values = {}
    non_echo_chamber_values = {} 
    depth = {}; child = {}; cascade = {}; subtree = {}; breadth = {}; propagate_time = {};
    for item in ['max_depth', 'max_breadth', 'cascade', 'unique_users']:
        echo_chamber_values[item] = {}
        non_echo_chamber_values[item] = {}

    dir_name = 'Retweet/'
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
        print(postid, 'echo chamber users : %s'%len(users))

        echo_chamber_origin = {}
        for tweet in tweets.values():
            if tweet['user'] in users:
                origin_tweet = tweet['origin_tweet']
                echo_chamber_origin[origin_tweet] = 1
                echo_chamber_values['max_depth'][origin_tweet] = cascade_max_depth[origin_tweet]
                echo_chamber_values['cascade'][origin_tweet] = tweet['cascade']
                echo_chamber_values['max_breadth'][origin_tweet] = cascade_breadth[origin_tweet]
                echo_chamber_values['unique_users'][origin_tweet] = cascade_unique_users[origin_tweet]


        #non echo chamber cascade which do not contain origin tweet of echo chamber 
        for tweet in tweets.values():
            if bot.check_bot(Bot, user) != 0:
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
    
def draw_echo_chamber_cascade_chracteristics():
    '''
    echo_chamber_values1, _ = echo_chamber_cascade_analysis('True')
    echo_chamber_values2, _ = echo_chamber_cascade_analysis('False')
    echo_chamber_values3, _ = echo_chamber_cascade_analysis('Mixture,Mostly True,Mostly False')

    draw_cdf_plot([echo_chamber_values1['max_depth'].values(), echo_chamber_values2['max_depth'].values(), echo_chamber_values3['max_depth'].values()], 'Depth',['True', 'False', 'Mixed'], 'Veracity','Image/20180919/echo_depth_veracity') 
    draw_cdf_plot([echo_chamber_values1['max_breadth'].values(), echo_chamber_values2['max_breadth'].values(), echo_chamber_values3['max_breadth'].values()], 'Max Breadth',['True', 'False', 'Mixed'], 'Veracity','Image/20180919/echo_breadth_veracity') 
    draw_cdf_plot([echo_chamber_values1['cascade'].values(), echo_chamber_values2['cascade'].values(), echo_chamber_values3['cascade'].values()], 'Cascade',['True', 'False', 'Mixed'], 'Veracity','Image/20180919/echo_cascade_veracity') 
    draw_cdf_plot([echo_chamber_values1['unique_users'].values(), echo_chamber_values2['unique_users'].values(), echo_chamber_values3['unique_users'].values()], 'Numberof Users',['True', 'False', 'Mixed'], 'Veracity','Image/20180919/echo_users_veracity') 
    '''
    echo_chamber_values, non_echo_chamber_values = echo_chamber_cascade_analysis()
    draw_cdf_plot([echo_chamber_values['max_depth'].values(), non_echo_chamber_values['max_depth'].values()], 'Depth',['Echo Chamber', 'No Echo Chamber'], 'User Type', 'Image/20180919/echo_depth2') 
    draw_cdf_plot([echo_chamber_values['max_breadth'].values(), non_echo_chamber_values['max_breadth'].values()], 'Breadth',['Echo Chamber', 'No Echo Chamber'], 'User Type', 'Image/20180919/echo_breadth2') 
    draw_cdf_plot([echo_chamber_values['cascade'].values(), non_echo_chamber_values['cascade'].values()], 'Cascade',['Echo Chamber', 'No Echo Chamber'], 'User Type', 'Image/20180919/echo_cascade2') 
    draw_cdf_plot([echo_chamber_values['unique_users'].values(), non_echo_chamber_values['unique_users'].values()], 'Number of users',['Echo Chamber', 'No Echo Chamber'], 'User Type', 'Image/20180919/echo_unique_users2') 



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
    dir_name = 'Retweet/'
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
                echo_sub_tree.append(tweet['sub_tree_num'])
                echo_breadth.append(cascade_breadth[tweet['origin_tweet']])
                
                depth[v].append(tweet['depth'])
                cascade[v].append(tweet['cascade'])
                child[v].append(tweet['child'])
                subtree[v].append(tweet['sub_tree_num'])
                breadth[v].append(cascade_breadth[tweet['origin_tweet']])
                
                if tweet['propagate_time'] != float('Inf'):
                    echo_propagation_time.append(float(tweet['propagate_time']))
                    propagate_time[v].append(float(tweet['propagate_time']))
        
        
        #print(np.mean(echo_depth), np.mean(echo_child), np.mean(echo_sub_tree), np.mean(echo_propagation_time))
        #print(np.mean(all_depth), np.mean(all_child), np.mean(all_sub_tree), np.mean(all_propagation_time))
        #cwriter.writerow([postid, np.mean(all_depth), np.mean(all_child), np.mean(all_sub_tree), np.mean(all_propagation_time), np.mean(echo_depth), np.mean(echo_child), np.mean(echo_sub_tree), np.mean(echo_propagation_time)])
        ccc +=1
        #if ccc > 5:
        #    break
    

    draw_cdf_plot(depth['True'], depth['False'], depth['Mixed'], 'Depth',['True', 'False', 'Mixed'], 'Image/20180919/echo_depth') 
    draw_cdf_plot(child['True'], child['False'], child['Mixed'], 'Child',['True', 'False', 'Mixed'], 'Image/20180919/echo_child') 
    draw_cdf_plot(subtree['True'], subtree['False'], subtree['Mixed'], 'Sub Tree Size',['True', 'False', 'Mixed'], 'Image/20180919/echo_subtree') 
    draw_cdf_plot(breadth['True'], breadth['False'], breadth['Mixed'], 'Breadth',['True', 'False', 'Mixed'], 'Image/20180919/echo_breadth') 
    draw_cdf_plot(cascade['True'], cascade['False'], cascade['Mixed'], 'Cascade',['True', 'False', 'Mixed'], 'Image/20180919/echo_cascade') 
    draw_cdf_plot(propagate_time['True'], propagate_time['False'], propagate_time['Mixed'], 'Propagation Time',['True', 'False', 'Mixed'], 'Image/20180919/echo_propagate_time') 
    #f.close()
    #with open('Data/echo_chamber_user.json', 'w') as f:
        #json.dump({'all':{'depth':all_depth, 'child':all_child, 'sub_tree':all_sub_tree, 'propagation_time' : all_propagation_time, 'cascade':all_cascade}, 'echo':{'depth':echo_depth, 'child':echo_child, 'sub_tree':echo_sub_tree, 'propagation_time':echo_propagation_time, 'cascade':echo_cascade}}, f)

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

    draw_cdf_plot(all_cascade, echo_cascade, 'Cascade Size', 'All', 'Echo', 'Image/20180918/cascade_all')
    draw_cdf_plot(all_depth, echo_depth, 'Depth', 'All', 'Echo', 'Image/20180918/depth_all')
    draw_cdf_plot(all_child, echo_child, 'Child', 'All', 'Echo', 'Image/20180918/child_all')
    draw_cdf_plot(all_sub_tree, echo_sub_tree, 'Sub Tree Size', 'All', 'Echo', 'Image/20180918/sub_tree_all')
    draw_cdf_plot(all_propagation_time, echo_propagation_time, 'Propagation Time', 'All', 'Echo', 'Image/20180918/propagation_time_all')


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

        #draw_cdf_plot(all_depth, echo_depth, 'Depth', 'All', 'Echo', 'Image/20180919/depth')
        #draw_cdf_plot(all_child, echo_child, 'Child', 'All', 'Echo', 'Image/20180919/child')
        #draw_cdf_plot(all_sub_tree, echo_sub_tree, 'Sub Tree Size', 'All', 'Echo', 'Image/20180919/sub_tree')
        #draw_cdf_plot(all_propagation_time, echo_propagation_time, 'Propagation Time', 'All', 'Echo', 'Image/20180919/propagation_time')

        draw_cdf_plot(t_d, f_d, m_d, 'Depth', ['True', 'False','Mixed'], 'Image/20180919/depth_veracity')
        draw_cdf_plot(t_c, f_c, m_c, 'Child', ['True', 'False','Mixed'], 'Image/20180919/child_veracity')
        draw_cdf_plot(t_s, f_s, m_s, 'Sub Tree Size', ['True', 'False','Mixed'], 'Image/20180919/sub_tree_veracity')
        draw_cdf_plot(t_p, f_p, m_p, 'Propagation Time', ['True', 'False','Mixed'], 'Image/20180919/propagation_time_veracity')

def draw_cdf_plot(datas, datatype, legend, legend_type, filename):
    cdf = CDFPlot()
    cdf.set_label(datatype, 'CDF')
    cdf.set_log(True)
    for i in range(len(datas)):
        cdf.set_data(datas[i], legend[i])
    if len(legend) > 1:
        cdf.set_legends(legend, legend_type)
    cdf.save_image('%s.png'%filename)

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
        if user_num > 0:
            echo_exist += 1 

        users.append(user_num)

    print('echo chamber exists in %s / %s combination'%(echo_exist, len(echo_chamber)))
    print('unique user : %s'%len(unique_users))
    return users

def draw_statistics():
    user2 = statistics('Data/echo_chamber2.json')
    user3 = statistics('Data/echo_chamber3.json')
    user4 = statistics('Data/echo_chamber4.json')
    #user5 = statistics('Data/echo_chamber5.json')

    #draw_cdf_plot([user2, user3, user4, user5], 'Number of Users', ['2', '3', '4', '5'], 'Echo Chamber', 'Image/20180920/echo_chamber_statistics')
    draw_cdf_plot([user2, user3, user4], 'Number of Users', ['2', '3', '4'], 'Echo Chamber', 'Image/20180920/echo_chamber_statistics')
    
def propagation_within_echo_chamber():
    filename = 'Data/echo_chamber2.json'
    with open(filename, 'r') as f:
        echo_chambers = json.load(f)

    #echo chamber users in a rumor
    Bot = bot.load_bot()
    
    #cascade that echo chamber users particiate in
    cascade_path = {}
    cascade_node = {} #echo chamber node count in a cascade
    cascade_depth = {}
    ccc = 0
    """
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

    
    for postid in echo_chamber_users.keys():
        with open('Retweet/%s'%postid, 'r') as f:
            tweets = json.load(f)

            cascade_path[postid] = {}
            cascade_node[postid] = {}
            cascade_depth[postid] = {}
            #if echo chamber users are more than 1, then check 
            user_num = len(echo_chamber_users[postid].keys())
            path_num = 0 
            if user_num < 2 : 
                continue 

            for tweet in tweets.values():
                if tweet['user'] in echo_chamber_users[postid].keys():
                    #check the parent is echo chamber user 
                    if tweet['user'] != tweet['parent'] and tweet['parent'] in echo_chamber_users[postid].keys() and tweet['depth'] != 1:
                        cascade_path[postid][tweet['origin_tweet']] = cascade_path[postid].get(tweet['origin_tweet'], 0) + 1 
                    
                    if tweet['depth'] != 1:
                        cascade_node[postid][tweet['origin_tweet']] = cascade_node[postid].get(tweet['origin_tweet'], 0) + 1 
                    #else:
                    #    print(tweet['user'], tweet['origin'])
                        
                    if cascade_depth[postid].get(tweet['origin_tweet'], 0) < tweet['depth']: # max depth
                        cascade_depth[postid][tweet['origin_tweet']] = tweet['depth']

        ccc += 1 
        #if ccc > 10:
        #    break
    path_distribution = []
    for postid in cascade_path.keys(): #rumor
        print(postid)
        for cascade in cascade_path[postid].keys(): #cascade
            #print(cascade)
            path_num = cascade_path[postid][cascade]
            node_num = cascade_node[postid][cascade]
            #print('Path : %s / %s, Depth : %s'%(path_num, node_num , cascade_depth[postid][cascade])) # if they are same then, all rumor propagate within echo chambers 
            #print(path_num / node_num, round(path_num / node_num, 1))
            path_distribution.append(round(path_num/node_num, 1))
    """
    ccc = 0
    retweet_cache = {}
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

            if len(echo_users) < 2:
                continue

            #load retweet graph 
            if retweet_cache.get(postid, -1) == -1:
                with open('Retweet/%s'%postid, 'r') as f:
                    tweets = json.load(f)
                    retweet_cache[postid] = tweets
            else:
                tweets = retweet_cache[postid]
        
            cascade_path[key] = {}
            cascade_node[key] = {}
            cascade_depth[key] = {}

            for tweet in tweets.values():
                if tweet['user'] in echo_users:
                    #check the parent is echo chamber user 
                    if tweet['user'] != tweet['parent'] and tweet['parent'] in echo_users.keys() and tweet['depth'] != 1:
                        cascade_path[key][tweet['origin_tweet']] = cascade_path[key].get(tweet['origin_tweet'], 0) + 1 
                    
                    if tweet['depth'] != 1:
                        cascade_node[key][tweet['origin_tweet']] = cascade_node[key].get(tweet['origin_tweet'], 0) + 1 
                    #else:
                    #    print(tweet['user'], tweet['origin'])
                        
                    if cascade_depth[key].get(tweet['origin_tweet'], 0) < tweet['depth']: # max depth
                        cascade_depth[key][tweet['origin_tweet']] = tweet['depth']
        ccc += 1 
        #if ccc > 100:
        #    break
    for postid in cascade_path.keys(): #rumor
        #print(postid)
        for cascade in cascade_path[postid].keys(): #cascade
            #print(cascade)
            path_num = cascade_path[postid][cascade]
            node_num = cascade_node[postid][cascade]
            if node_num == 1:
                continue
            print('Path : %s / %s, Depth : %s'%(path_num, node_num , cascade_depth[postid][cascade])) # if they are same then, all rumor propagate within echo chambers 
            #print(path_num / node_num, round(path_num / node_num, 1))
            path_distribution2.append(round(path_num/node_num, 1))
         


    
    #draw_cdf_plot([path_distribution], 'Ratio', [''], '', 'Image/20180920/echo_chamber_path_ratio')
    draw_cdf_plot([path_distribution2], 'Ratio', [''], '', 'Image/20180927/echo_chamber_path_ratio2')
    #draw_cdf_plot([path_distribution, path_distribution2], 'Ratio', ['type1', 'type2'], '', 'Image/20180920/echo_chamber_path_ratio2')


if __name__ == "__main__":
    #following_anlysis()
    

    #find_echo_chamber(2)
    #find_echo_chamber(3)
    #find_echo_chamber(4)
    #find_echo_chamber(5)
    #draw_statistics()
    #propagation_within_echo_chamber()
    #echo_chamber_anlysis('Data/echo_chamber2.json', 'True')
    #echo_chamber_user_analysis()
    #draw_echo_chamber_cascade_chracteristics()
    #draw_echo_chamber_user_characteristics()
    #draw_echo_chamber_user_analysis()
    #draw_echo_chamber_true_false()
    draw_echo_chamber_true_false()
    
