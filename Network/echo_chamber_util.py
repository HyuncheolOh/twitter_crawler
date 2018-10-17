import json, os, sys
import bot_detect as bot

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

# max breadth, depth, cascade from a cascade
def get_cascade_max_breadth():
    dir_name = "RetweetNew/"
    files = os.listdir(dir_name)
    c_breadth = {}
    c_depth = {}
    c_unique_users = {}
    max_depth = 0
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

                if tweet['depth'] > max_depth:
                    max_depth = tweet['depth']

            
        for key in u.keys():
            c_unique_users[key] = len(u[key])
    
    print("Max cascade, max depth, unique users of cascade calculation done")
    print('max_depth : %s'%max_depth)
    return c_breadth, c_depth, c_unique_users


# max breadth, depth, cascade from a rumor 
def get_rumor_max_properties():
    dir_name = "RetweetNew/"
    files = os.listdir(dir_name)
    c_breadth = {}
    c_depth = {}
    c_unique_users = {}
    c_cascade = {}
    for postid in files:
        #cascade_breadth[postid] = {} #origin tweet + max_breadth
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
        
        b = {}
        d = {}
        u = {}
        c = {}
        for tweet in tweets.values():
            #same origin tweet, number of same depth node means breadth
            origin_tweet = postid
            b[origin_tweet] = b.get(origin_tweet, {})
            breadth = b[origin_tweet].get(tweet['depth'], 0) + 1 
            b[origin_tweet][tweet['depth']] = breadth
            c_breadth[origin_tweet] = c_breadth.get(origin_tweet, 0)
            c_depth[origin_tweet] = c_depth.get(origin_tweet, 1)
            c_cascade[origin_tweet] = c_cascade.get(origin_tweet, 0) 
            #unique users of a cascade
            u[origin_tweet] = u.get(origin_tweet, {})
            u[origin_tweet][tweet['user']] = 1
            if c_breadth[origin_tweet] < breadth:
                c_breadth[origin_tweet] = breadth
       
            if c_depth[origin_tweet] < tweet['depth']:
                c_depth[origin_tweet] = tweet['depth']
        
            if c_cascade[origin_tweet] < tweet['cascade']:
                c_cascade[origin_tweet] = tweet['cascade']

        for key in u.keys():
            c_unique_users[key] = len(u[key])
    
    print("Max cascade, max depth, unique users of cascade calculation done")
    return c_breadth, c_depth, c_unique_users, c_cascade

