import json, os, sys
import numpy as np
import random
from time import time 
from draw_tools.cdf_plot import CDFPlot


def find_echo_chamber(num):
    #select number of rumors and compare user intersection
    print('find echo chamber %s'%num)
    start_time = time()
    dir_name = 'RetweetNew/'
    files = os.listdir(dir_name)

    users = {}
    for postid in files:

        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
            #remove bots 
            users[postid] = set([item['user'] for item in tweets.values() if item['bot'] == 0])
            #print(users[postid]) 

    #find echo chamber (intersection) between rumor spreaders
    echo_chamber = {}
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
                names.pop()
            names.pop()
        names.pop()

    end_time = time()
    print('%s taken'%(end_time-start_time))
    print('number of echo chambers %s'%(len(echo_chamber)))
    with open('Data/echo_chamber%s.json'%num, 'w') as f:
        json.dump(echo_chamber, f)

def get_cascade_max_breadth():
    dir_name = "RetweetNew/"
    files = os.listdir(dir_name)
    c_breadth = {}
    for postid in files:
        #cascade_breadth[postid] = {} #origin tweet + max_breadth
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
        
        b = {}
        for tweet in tweets.values():
            #same origin tweet, number of same depth node means breadth
            origin_tweet = tweet['origin_tweet']
            b[origin_tweet] = b.get(origin_tweet, {})
            breadth = b[origin_tweet].get(tweet['depth'], 0) + 1 
            b[origin_tweet][tweet['depth']] = breadth
            c_breadth[origin_tweet] = c_breadth.get(origin_tweet, 0)
            if c_breadth[origin_tweet] < breadth:
                c_breadth[origin_tweet] = breadth
        
    return c_breadth

def echo_chamber_anlysis():
    #depth
    #cascade
    #child count 
    #get echo chamber info

    cache = {}
    echo_chamber_depth = {}
    echo_chamber_cascade = {}
    echo_chamber_child = {}
    echo_chamber_breadth = {}
    count = 0

    with open('Data/echo_chamber2.json') as f:
        echo_chambers = json.load(f)

    cascade_breadth = get_cascade_max_breadth()

    print('total ', len(echo_chambers))
    for key in echo_chambers:
        #print(key)
        users = echo_chambers[key]

        postids = key.split('_')
        #print('echo chamber users', len(users))
        count += 1 
        if count % 100 == 0:
            #print(count)
            print(count)
            #break

        if len(users) < 2:
            continue
        for user in users:
            for postid in postids:
                echo_chamber_depth[postid] = echo_chamber_depth.get(postid, {})
                echo_chamber_cascade[postid] = echo_chamber_cascade.get(postid, {})
                echo_chamber_child[postid] = echo_chamber_child.get(postid, {})
                #collect info from echo chamber user 
                if cache.get(postid, -1) == -1:
                    with open('RetweetNew/' + postid, 'r') as f:
                        tweets = json.load(f)
                        cache[postid] = tweets
                else:
                    tweets = cache[postid]

                #get mean of user's depth, cascade in a rumor if he/she spread more than one rumor 
                depth = []
                cascade = []
                child = []
                b = {}
                for tid in tweets:
                    if user == tweets[tid]['user']:
                        depth.append(tweets[tid]['depth'])
                        cascade.append(tweets[tid]['cascade'])
                        child.append(tweets[tid]['child'])
                        echo_chamber_breadth[tweets[tid]['origin_tweet']] = cascade_breadth[tweets[tid]['origin_tweet']]            
 
                echo_chamber_depth[postid][user] = echo_chamber_depth[postid].get(user, [])
                echo_chamber_depth[postid][user].extend(depth)
                
                echo_chamber_cascade[postid][user] = echo_chamber_cascade[postid].get(user, [])
                echo_chamber_cascade[postid][user].extend(cascade)
                
                echo_chamber_child[postid][user] = echo_chamber_child[postid].get(user, [])
                echo_chamber_child[postid][user].extend(child)

            
        #break
    #print(echo_chamber_depth)
    #print(echo_chamber_breadth)
    
    files = os.listdir('RetweetNew')
    depth_all = []
    cascade_all = []
    child_all = []
    for postid in files:
        if cache.get(postid, -1) == -1:
            with open('RetweetNew/' + postid, 'r') as f:
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
    
    with open('Data/depth_echochamber2.json', 'w') as f:
        #json.dump({'echo_chamber':echo_chamber_depth, 'all': depth_all} , f)
        json.dump({'echo_chamber': {'depth':echo_chamber_depth, 'child':echo_chamber_child, 'cascade':echo_chamber_cascade, 'breadth':echo_chamber_breadth}, 'all': {'depth':depth_all, 'cascade':cascade_all, 'child':child_all, 'breadth':cascade_breadth}}, f)
    
    """
        
    with open('Data/depth_echochamber2.json', 'r') as f:
        data = json.load(f)
    echo_chamber_depth = data['echo_chamber']['depth']
    echo_chamber_cascade = data['echo_chamber']['cascade']
    echo_chamber_child = data['echo_chamber']['child']
    
    depth_all = data['all']['depth']
    cascade_all = data['all']['cascade']
    child_all = data['all']['child']
    """

    echo_depth_all = []
    echo_child_all = []
    echo_cascade_all = []
    for item in echo_chamber_depth.values():
        for aaaa in item.values():
            echo_depth_all.extend(aaaa)
    for item in echo_chamber_cascade.values():
        for aaaa in item.values():
            echo_cascade_all.extend(aaaa)
    for item in echo_chamber_child.values():
        for aaaa in item.values():
            echo_child_all.extend(aaaa)

    print(max(echo_child_all))
    print(max(echo_cascade_all))
    #depth
    cdf = CDFPlot()
    cdf.set_data(depth_all, 'all')
    cdf.set_label('Depth', 'CDF')
    cdf.set_data(echo_depth_all, 'echo chamber')
    cdf.set_legends(['all', 'echo chamber'], '')
    cdf.save_image('Image/echochamber_depth_cdf.png')
 
    #cascade
    cdf = CDFPlot()
    cdf.set_data(cascade_all, 'all')
    cdf.set_label('Cascade', 'CDF')
    cdf.set_log(True)
    cdf.set_data(echo_cascade_all, 'echo chamber')
    cdf.set_legends(['all', 'echo chamber'], '')
    cdf.save_image('Image/echochamber_cascade_cdf.png')
    
    #child
    cdf = CDFPlot()
    cdf.set_data(child_all, 'all')
    cdf.set_label('Child', 'CDF')
    cdf.set_log(True)
    cdf.set_data(echo_child_all, 'echo chamber')
    cdf.set_legends(['all', 'echo chamber'], '')
    cdf.save_image('Image/echochamber_child_cdf.png')

    #breadth
    cdf = CDFPlot()
    cdf.set_data(cascade_breadth.values(), 'all')
    cdf.set_label('Breadth', 'CDF')
    cdf.set_log(True)
    cdf.set_data(echo_chamber_breadth.values(), 'echo chamber')
    cdf.set_legends(['all', 'echo chamber'], '')
    cdf.save_image('Image/echochamber_breadth_cdf.png')

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
    dir_name = 'RetweetNew/'
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

    #child
    cdf = CDFPlot()
    cdf.set_data(child_all, 'all')
    cdf.set_label('Friends', 'CDF')
    cdf.set_log(True)
    cdf.set_data(echo_child_all, 'echo chamber')
    cdf.set_legends(['random', 'echo chamber'], 'user type')
    cdf.save_image('Image/echochamber_friends_cdf.png')


            
if __name__ == "__main__":
    #following_anlysis()
    
    echo_chamber_anlysis()

    #find_echo_chamber(2)
    #find_echo_chamber(3)
    #find_echo_chamber(4)


    #breadth = get_cascade_max_breadth()

