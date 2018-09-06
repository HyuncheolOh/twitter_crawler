import json
import os
import fileinput
import time
import veracity
from random import shuffle
from tweet_parser.tweet import Tweet
from tweet_parser.tweet_parser_errors import NotATweetError

f_cache = {}
fr_cache = {}
def retweet_network(t):
    #extract retweet network
    start_time = time.time()
    global f_cache
    dir_name = '../Data/followers/followers/'
    confirm = {}
    unconfirm = {}
    confirm_new = {}
    count = 0
    for tid in t.keys():
        if t[tid]['confirm'] == True: #origin tweet
            confirm[tid] = t[tid] 
        else:
            uid = t[tid]['user']
            #check tweet is retweeted from origin
            origin_user = t[tid]['origin']
            if f_cache.get(origin_user, -1) == -1:
                path = dir_name + origin_user
                with open(path, 'r') as f:
                    followers = json.load(f)
                    f_cache[origin_user] = followers
            else:
                followers = f_cache[origin_user]

            #check uid is origin's follower
            if int(uid) in followers:
                t[tid]['confirm'] = True
                t[tid]['depth'] = 2
                #confirm[tid] = t[tid]
                confirm_new[tid] = t[tid]
            else:
                unconfirm[tid] = t[tid]
                count += 1
                    
    print('unconfirmed %s'%count)
    #sub_retweet_network(confirm, unconfirm)
    confirm.update(confirm_new)
    print('confirm : %s, confirm_new : %s, unconfirm : %s'%(len(confirm), len(confirm_new), len(unconfirm)))
    if count > 0:
        r_network = sub_retweet_network2(confirm, confirm_new, unconfirm)
        #r_network = sub_retweet_network(confirm, unconfirm)
    else:
        r_network = confirm.update(unconfirm)

    end_time = time.time()
    #print(len(r_network))
    print('%s taken'%(end_time - start_time))
    return r_network
    

def sub_retweet_network(confirm, unconfirm):
    change_count = 0
    confirm_new = confirm.copy()
    unconfirm_new = {}
    global f_cache
    dir_name = '../Data/followers/followers/'
    count = 0
    for tid in unconfirm.keys():
        tweet1 = unconfirm[tid]
        user1 = tweet1['user']
        for tid2 in confirm_new.keys():
            tweet2 = confirm_new[tid2]

            if tweet1['confirm'] == False and tweet1['origin_tweet'] == tweet2['origin_tweet'] and tid2 != tweet1['origin']:

                #if user1 in user2's followers
                origin_user = tweet2['user']
                if f_cache.get(origin_user, -1) == -1:
                    path = dir_name + origin_user
                    with open(path, 'r') as f:
                        followers = json.load(f)
                        f_cache[origin_user] = followers
                else:
                    followers = f_cache[origin_user]
                
                if int(user1) in followers:
                    tweet1['confirm'] = True
                    tweet1['parent'] = origin_user
                    tweet1['depth'] = tweet2['depth'] + 1 
                    tweet1['parent_tweet'] = tid2
                    confirm_new[tid] = tweet1
                    change_count += 1
                    break
        if tweet1['confirm'] == False:
           unconfirm_new[tid] = tweet1
    print('change count : %s'%change_count, count)
    print('confirm : %s, unconfirm : %s'%(len(confirm_new), len(unconfirm_new)))
    if change_count != 0:
        sub_retweet_network(confirm_new, unconfirm_new)

    confirm_new.update(unconfirm_new)
    return confirm_new


def sub_retweet_network2(confirm, newconfirm, unconfirm):
    change_count = 0
    #confirm_new = confirm.copy()
    confirm_new = {}
    unconfirm_new = {}
    global f_cache
    dir_name = '../Data/followers/followers/'
    count = 0
    for tid in unconfirm.keys():
        tweet1 = unconfirm[tid]
        user1 = tweet1['user']
        for tid2 in newconfirm.keys():
            tweet2 = newconfirm[tid2]

            if tweet1['confirm'] == False and tweet1['origin_tweet'] == tweet2['origin_tweet'] and tid2 != tweet1['origin']:

                #if user1 in user2's followers
                origin_user = tweet2['user']
                if f_cache.get(origin_user, -1) == -1:
                    path = dir_name + origin_user
                    with open(path, 'r') as f:
                        followers = json.load(f)
                        f_cache[origin_user] = followers
                else:
                    followers = f_cache[origin_user]
                
                if int(user1) in followers:
                    tweet1['confirm'] = True
                    tweet1['parent'] = origin_user
                    tweet1['depth'] = tweet2['depth'] + 1 
                    tweet1['parent_tweet'] = tid2
                    confirm_new[tid] = tweet1
                    change_count += 1
                    break
        if tweet1['confirm'] == False:
           unconfirm_new[tid] = tweet1

    #join confirm and new confirm
    confirm.update(confirm_new)
    print('change count : %s'%change_count, count)
    print('confirm : %s, confirm_new : %s, unconfirm : %s'%(len(confirm), len(confirm_new), len(unconfirm_new)))
    if change_count != 0:
        sub_retweet_network2(confirm, confirm_new, unconfirm_new)

    confirm.update(unconfirm_new)
    return confirm


def extract_friends(t):
    start_time = time.time()
    global fr_cache
    dir_name = '../Data/friends/friends/'
    for tid in t.keys():
        uid = t[tid]['user']
        if fr_cache.get(uid, -1) == -1:
            path = dir_name + uid
            with open(path, 'r') as f:
                friends = json.load(f)
                fr_cache[uid] = friends
        else:
            friends = fr_cache[uid]
    #not implemented yet 
    return friends 

def get_tweet(path):
    ready = False
    with open(path, 'r') as f:
        lines = fileinput.FileInput(path)
           
    t = {}
    unique_u = {}
    unique_f = {}

    for line in lines:
        #print(line)
        tweet_dict = json.loads(line)
        tweet = Tweet(tweet_dict)
        t_id1 = tweet['id_str']
        u_id1 = tweet['user']['id_str']
        tweet1 = tweet['text']
        screen_name = tweet['user']['screen_name']
        time1 = tweet['created_at']
        unique_u[u_id1] = 1
        unique_f[u_id1] = 1
        
        #isretweeted
        try:
            retweet = tweet['retweeted_status']
            tweet2 = retweet['text']
            t_id2 = retweet['id_str']
            u_id2 = retweet['user']['id_str']
            origin_name = retweet['user']['screen_name']
            time2 = retweet['created_at']
            t[t_id1] = {'user' : u_id1, 'parent':u_id2, 'origin':u_id2, 'confirm': False, 'text' :  tweet1, 'origin_tweet':t_id2, 'parent_tweet' : t_id2, 'tweet':t_id1, 'screen_name':screen_name, 'origin_name':origin_name, 'time':time1, 'depth': 2}
            t[t_id2] = {'user' : u_id2, 'parent':u_id2, 'origin':u_id2, 'confirm': True, 'text' :  tweet2, 'origin_tweet':t_id2, 'parent_tweet' : t_id2, 'tweet':t_id2, 'screen_name':origin_name, 'origin_name':origin_name, 'time':time2, 'depth': 1}
            unique_u[u_id2] = 1
        except KeyError as e:
            #no retweeted
            t[t_id1] = {'user' : u_id1, 'parent':u_id1, 'origin':u_id1, 'confirm': True, 'text' :tweet1, 'origin_tweet':t_id1, 'parent_tweet' : t_id1, 'tweet':t_id1, 'screen_name':screen_name,'origin_name':screen_name, 'time':time1, 'depth': 1}
        #print(tweet.created_at_string, tweet.all_text)
    
    # if follower, origin_follwer, friends counts are same as unique users, then struct retweet networks
    # and the number of tweets are more than 100, else return None

    f_count = 0
    fr_count = 0
    for uid in unique_u.keys():
        path = '../Data/followers/followers/' + uid
        if os.path.exists(path):
            f_count += 1
            
    #for uid in unique_f.keys():
    #    path = '../Data/friends/friends/' + uid
    #    if os.path.exists(path):
    #        fr_count += 1

    #print('unique_users : %s , collected users : %s'%(len(unique_u), f_count))
    if len(t) <= 100:
        return 0, None
        
    if f_count == len(unique_u) and fr_count == len(unique_u):
        print('%s : %s tweets'%(path, len(t)))
        return 1, t
    elif f_count == len(unique_u):
        print('%s : %s tweets'%(path, len(t)))
        return 2, t
    elif fr_count == len(unique_u):
        return 3, t
    else:
        return 0, t


if __name__ == "__main__":

    dir_name = '../Data/'
    files = os.listdir(dir_name)

    shuffle(files)
    for file_name in files:   
        if file_name == "followers" or file_name == "friends":
            continue

        postid = file_name.replace('.json', '')

        #if postid != '143241':
        #    continue
        #check retweet , friends already collected
        Retweet = 'RetweetNew/'
        Friends = 'PolarFriends/'
        if os.path.exists(Retweet + postid) and os.path.exists(Friends + postid):
            continue

        if veracity.check(postid) == False:
            continue

        result, t = get_tweet(dir_name + file_name)
        if result == 1 or result == 2:
            if os.path.exists(Retweet + postid):
                continue
    
            print(postid)
            r_network = retweet_network(t)
            
            #with open(Retweet + postid, 'w') as f:
            with open(Retweet + postid, 'w') as f:
                json.dump(r_network, f)
            #break
        
        if result == 1 or result == 3:
            if os.path.exists(Friends + postid):
                continue

            #print(postid)
            #extracted_friends = extract_friends(t)

            #with open(postid, 'w') as f:
            #    json.dump(extract_friends, f)


