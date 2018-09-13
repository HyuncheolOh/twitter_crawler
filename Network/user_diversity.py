#user's polarity diversity 
import os, sys, time
import json
import entropy
from draw_tools.box_plot import BoxPlot
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
def diversity():

    with open('Data/echo_chamber2.json') as f:
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

    dir_name = 'RetweetNew/'
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
    box.save_image('Image/diversity_box.png')


if __name__ == "__main__":
    diversity()
