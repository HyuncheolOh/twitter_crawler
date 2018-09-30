#user's polarity diversity 
import os, sys, time
import json
import entropy
import pandas as pd
import numpy as np
from draw_tools.box_plot import BoxPlot
from draw_tools.cdf_plot import CDFPlot
from draw_tools.line_plot import LinePlot
import random 

P = None
def get_polarity(userid):
    global P
    global error
    if P == None:
        with open('Data/polarization.json', 'r') as f:
            P = json.load(f)
    
    try:
        #put in the bucket
        p = float(P[userid])
        """
        if p < -1.2:
            return -2
        elif p < -0.4:
            return -1
        elif p < 0.4:
            return 0
        elif p < 1.2:
            return 1
        else:
            return 2
        """
        """
        if p < 0:
            return -1
        else:
            return 1
        """
        if p > 2:
            p = 2
        elif p < -2:
            p = -2

        return p / 2 #return -1 ~ 1 
    except KeyError as e:
        return -999

def get_random_user(users, num):
    user_list = []
    max_num = len(users)
    user1 = users[random.randrange(0,max_num)]
    while(True):
        user2 = users[random.randrange(0,max_num)]
        if user2 not in user_list:
            user_list.append(user2)
            if len(user_list) == num:
                break
    return user_list
 
#find mutual follower or have common friends 
def diversity(filename):
    index = filename.replace(".json", "").split('echo_chamber')
    print(index)

    with open(filename) as f:
        echo_chambers = json.load(f)

    print('total ', len(echo_chambers))
    friends_cache = {}
    postid = {}
    count = 0
    echo_diversity = {}

    for key in echo_chambers:
        #print(key)
        users = echo_chambers[key]
        #print(users)
       
        count += 1 
        if count % 100 == 0:
            print(count)
            #break
        
        if len(users) < 2:
            continue
        
        postids = key.split('_')
        for k in postids:
            postid[k] = 1


        #print(len(users))
        polars = []
        user_count = 0
        #polarity scores 
        for userid in users:
            score = get_polarity(userid)
            if score != -999:
                polars.append(score)
                user_count += 1
        postid[postids[0]] = user_count
        postid[postids[1]] = user_count
        if 1 in postid.values():
            break
        diversity = entropy.eta(polars)
        echo_diversity[key] = diversity

    dir_name = 'Retweet/'
    random_diversity = {}
   
    for key in postid.keys():
        #number of users 
        user_num = postid[key]
        #print(user_num)
        with open(dir_name + key, 'r') as f:
            tweets = json.load(f)
        users = [tweet['user']for tweet in tweets.values()]
        users = get_random_user(users, user_num)

        polars = []
        #polarity scores 
        for userid in users:
            score = get_polarity(userid)
            if score != -999:
                polars.append(score)
        diversity = entropy.eta(polars)
        random_diversity[key] = diversity
        #print(users)
        print(polars)
        print(diversity)
    
    with open('Data/echo_chamber_diversity.json', 'w') as f:
        json.dump({'echo_chamber':echo_diversity, 'random':random_diversity}, f)

    box = BoxPlot(1)
    box.set_data([random_diversity.values(), echo_diversity.values()],'')
    box.set_xticks(['Random', 'Echo chamber'])
    box.save_image('Image/diversity_box_%s.png'%index[1])

#check cascade polarity similarity
def polarity_diversity():
    #check rumor polarity similarity
    #check cascade polarity similarity
    files = os.listdir('Retweet')
    users_polarity = {}
    users_polarity_cascade = {}
    retweet_cache = {}
    for ccc, postid in enumerate(files):
        users_polarity[postid] = {}
        with open('Retweet/%s'%postid, 'r') as f:
            tweets = json.load(f)
            retweet_cache[postid] = tweets

        for tweet in tweets.values():
            p_score = get_polarity(tweet['user'])
            users_polarity[postid][tweet['user']] = p_score
            users_polarity_cascade[tweet['origin_tweet']] = users_polarity_cascade.get(tweet['origin_tweet'], {})
            users_polarity_cascade[tweet['origin_tweet']][tweet['user']] = p_score

        #if ccc == 10:
        #    break

    r_diversity = []
    for key in users_polarity.keys():
        r_diversity.append(entropy.eta([score for score in users_polarity[key].values()]))
    
    print(pd.Series(r_diversity).describe())
    c_diversity = []
    for key in users_polarity_cascade.keys():
        if len(users_polarity_cascade[key]) < 2:
            continue
        c_diversity.append(entropy.eta([score for score in users_polarity_cascade[key].values()]))

    print(pd.Series(c_diversity).describe())
    box = BoxPlot(1)
    box.set_data([r_diversity, c_diversity],'')
    box.set_xticks(['Rumor', 'Cascade'])
    box.save_image('Image/20180927/diversity_box.png')

    #check echo chamber users' poarltiy similarity
    e_diversity = []
    echo_chamber_users = {}
    with open('Data/echo_chamber2.json') as f:
        echo_chamber = json.load(f)

    for key in echo_chamber:
        users = echo_chamber[key]

        if len(users) < 2:
            continue

        polar = []
        e_diversity.append(entropy.eta([get_polarity(user) for user in users]))

        #get all echo chamber users for cascade characteristics
        for postid in key.split('_'):
            echo_chamber_users[postid] = echo_chamber_users.get(postid, {})
            for user in users:
                echo_chamber_users[postid][user] = 1 
        
    print(pd.Series(e_diversity).describe())

    #check echo chamber user pariticpate polarity similarity and non-echo chamber user participate polarity similarity 
    echo_cascade = {}
    cascade_users = {}
    for postid in files:
        tweets = retweet_cache[postid]

        #get echo chamber cascade 
        for tweet in tweets.values():
            if tweet['user'] in echo_chamber_users[postid].keys(): 
                echo_cascade[tweet['origin_tweet']] = 1
            cascade_users[tweet['origin_tweet']] = cascade_users.get(tweet['origin_tweet'], {})
            cascade_users[tweet['origin_tweet']][tweet['user']] = get_polarity(tweet['user'])

    echo_cascade = echo_cascade.keys()
    echo_cascade_diversity = []
    echo_cascade_size = []
    non_echo_cascade_diversity = []
    non_echo_cascade_size = []
    for cascade in cascade_users.keys():
        #echo chamber user participated cascade
        if cascade in echo_cascade:
            echo_cascade_diversity.append(entropy.eta([score for score in cascade_users[cascade].values()]))
            echo_cascade_size.append(len(cascade_users[cascade]))
        #non echo chamber user participated cascade
        else:
            non_echo_cascade_diversity.append(entropy.eta([score for score in cascade_users[cascade].values()]))
            non_echo_cascade_size.append(len(cascade_users[cascade]))

    print('echo chamber cascade')
    print(pd.Series(echo_cascade_diversity).describe())
    print(pd.Series(echo_cascade_size).describe())
    print('non echo chamber cascade')
    print(pd.Series(non_echo_cascade_diversity).describe())
    print(pd.Series(non_echo_cascade_size).describe())

    box = BoxPlot(1)
    box.set_data([echo_cascade_diversity, non_echo_cascade_diversity],'')
    box.set_xticks(['Echo Chamber', 'Non Echo Chamber'])
    box.save_image('Image/20180927/diversity_echo_cascade_box.png')

    box = BoxPlot(1)
    box.set_data([echo_cascade_size, non_echo_cascade_size],'')
    box.set_xticks(['Echo Chamber', 'Non Echo Chamber'])
    box.save_image('Image/20180927/diversity_echo_cascade_size_box.png')

def edge_homogeneity():
    files = os.listdir('Retweet')
    
    retweet_cache = {}
    homogeneity = []
    for ccc, postid in enumerate(files):
        #users_polarity[postid] = {}
        with open('Retweet/%s'%postid, 'r') as f:
            tweets = json.load(f)
            retweet_cache[postid] = tweets

        for tweet in tweets.values():
            p_score = get_polarity(tweet['user'])

            #calculate edge homogeneity
            if tweet['depth'] != 1:
                #compare with parents if parent is not root node 
                p_score2 = get_polarity(tweet['parent'])

                if p_score == -999 or p_score2 == -999:
                    continue
                e = p_score * p_score2

                #print(p_score, p_score2, round(e, 1))
                homogeneity.append(round(e, 1))
        

    #    if ccc == 10:
    #        break

    #compare with echo chamber node's edge homogeneity
    echo_chamber_users = {}
    e_homogeneity = []
    ne_homogeneity = []
    with open('Data/echo_chamber2.json') as f:
        echo_chamber = json.load(f)

    for key in echo_chamber:
        users = echo_chamber[key]

        if len(users) < 1:
            continue

        for postid in key.split('_'):
            echo_chamber_users[postid] = echo_chamber_users.get(postid, {})
            for user in users:
                echo_chamber_users[postid][user] = 1 
 
    for postid in echo_chamber_users.keys():
        tweets = retweet_cache[postid]

        for tweet in tweets.values():
            #echo chamber user's edge homogeneity
            if tweet['depth'] != 1:
                p_score = get_polarity(tweet['user'])
                p_score2 = get_polarity(tweet['parent'])

                if p_score == -999 or p_score2 == -999:
                    continue
            
                e = p_score * p_score2

                #print(p_score, p_score2, round(e, 1))
                if tweet['user'] in echo_chamber_users[postid].keys():
                    e_homogeneity.append(e)
                    #e_homogeneity.append(round(e, 1))
                else:
                    ne_homogeneity.append(e)
                    #ne_homogeneity.append(round(e, 1))

        


    draw_cdf_plot([e_homogeneity, ne_homogeneity], 'Homogenety', ['Echo Chambers', 'Non-Echo Chambers'], 'User type', 'homogeneity')

    with open('Data/homogeneity.json', 'w') as f:
        json.dump({'e':e_homogeneity, 'ne' : ne_homogeneity}, f)

    x_ticks = np.arange(-1,1.1, 0.1)
    x_ticks = np.around(x_ticks, decimals=1)
    e_count = []
    ne_count = []
    for x in x_ticks:
        e_count.append(e_homogeneity.count(x))
        ne_count.append(ne_homogeneity.count(x))
    line = LinePlot()
    line.set_ylog()
    line.set_label('Homogeneity', 'Number of Homogeneity')
    line.set_plot_data(e_count, x_ticks)
    line.set_plot_data(ne_count, x_ticks)
    line.set_legends(['Echo Chambers', 'Non-Echo Chambers'])
    line.set_xticks(x_ticks)
    line.save_image('Image/20180927/homogeneity_line.png')

    

def draw_cdf_plot(datas, datatype, legend, legend_type, filename):
    cdf = CDFPlot()
    cdf.set_label(datatype, 'CDF')
    #cdf.set_log(True)
    for i in range(len(datas)):
        cdf.set_data(datas[i], legend[i])
    if len(legend) > 1:
        cdf.set_legends(legend, legend_type)
    cdf.save_image('Image/20180927/%s.png'%filename)


def echo_chamber_diversity():
    filename = 'Data/echo_chamber2_0_1.json'
    diversity(filename)

    filename = 'Data/echo_chamber2_1.json'
    diversity(filename)
    filename = 'Data/echo_chamber2.json'
    diversity(filename)
    filename = 'Data/echo_chamber2_m_1.json'
    diversity(filename)
    filename = 'Data/echo_chamber2_m_0_1.json'
    diversity(filename)

if __name__ == "__main__":
    #echo_chamber_diversity()
    #polarity_diversity()
    edge_homogeneity()
