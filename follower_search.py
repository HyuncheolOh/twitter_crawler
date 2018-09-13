#-----------------------------------------------------------------------
# twitter-followers
#  - lists all of a given user's followers (ie, followees)
#-----------------------------------------------------------------------

import os, os.path
import json
import csv
import tweepy
import csv
import sys
from tweepy import OAuthHandler
from time import sleep
from random import shuffle
import veracity_check as vc

#-----------------------------------------------------------------------
# load our API credentials 
#-----------------------------------------------------------------------
config = {}
execfile("config.py", config)
token_list = []
key_num = 2 
#-----------------------------------------------------------------------
# load developer key list 
#-----------------------------------------------------------------------
def load_key_list():
    with open('key.csv', 'rb') as csvfile:
        keyread = csv.reader(csvfile, delimiter=',')
        for row in keyread:
            token = []
            if 'consumer' not in row[0]:
                token.append(row[0])
                token.append(row[1])
                token.append(row[2])
                token.append(row[3])
                token_list.append(token)

#-----------------------------------------------------------------------
# create twitter API object
#-----------------------------------------------------------------------
def load_api():
    global key_num 
    if key_num == len(token_list):
        key_num = 0
        print("sleep 900 seconds for rate limit exceeds")
        sleep(900)
    token = token_list[key_num]
    auth = OAuthHandler(token[0], token[1])
    auth.set_access_token(token[2], token[3])
    key_num += 1
    #return tweepy.API(auth)
    return tweepy.API(auth, wait_on_rate_limit=True)

def get_followers(api, screen_name):

    #-----------------------------------------------------------------------
    # this is the user whose followers we will list
    #-----------------------------------------------------------------------
    username = screen_name

    #-----------------------------------------------------------------------
    # perform a basic search 
    # twitter API docs: https://dev.twitter.com/rest/reference/get/followers/ids
    #-----------------------------------------------------------------------
    #query = twitter.followers.ids(screen_name = username)
    friend_list = []
    try :
        for friend in tweepy.Cursor(api.followers_ids, screen_name=username).items():
                friend_list.append(friend)
    except tweepy.error.RateLimitError:
        print("rate limit error")
        return -1
    except tweepy.error.TweepError:
        print("tweep error")

    print("number of followers : %d"%len(friend_list))
    #-----------------------------------------------------------------------
    # tell the user how many followers we've found.
    # note that the twitter API will NOT immediately give us any more 
    # information about followers except their numeric IDs...
    #-----------------------------------------------------------------------
    #print "found %d followers" % (len(query["ids"]))

    '''
    #-----------------------------------------------------------------------
    # now we loop through them to pull out more info, in blocks of 100.
    #-----------------------------------------------------------------------
    for n in range(0, len(query["ids"]), 100):
        ids = query["ids"][n:n+100]
        #-----------------------------------------------------------------------
        # create a subquery, looking up information about these users
        # twitter API docs: https://dev.twitter.com/rest/reference/get/users/lookup
        #-----------------------------------------------------------------------
        subquery = twitter.users.lookup(user_id = ids)

        for user in subquery:
            #-----------------------------------------------------------------------
            # now print out user info, starring any users that are Verified.
            #-----------------------------------------------------------------------
        print " [%s] %s - %s" % ("*" if user["verified"] else " ", user["screen_name"], user["id_str"])
    '''
    return friend_list

if __name__ == '__main__':
    #get folders
    if len(sys.argv) >=2:
        key_num = int(sys.argv[1])
    print(key_num)

    dirname = './Data/'
    files  = os.listdir(dirname)
    load_key_list()
    api = load_api()
    shuffle(files)
    for post_id in files:
       
        if post_id == "friends" or post_id == "followers":
            continue
        #get user list 
        f = open(os.path.join(dirname, post_id))
        lines = f.readlines()
        follower_list = None
        followers_data = {}
        list_path = './Data/followers/list.json'
        followers_all_path = './Data/followers/all.json'
        #followers_path = './Data/followers/%s'%post_id
        if not os.path.exists('./Data/followers'):
            os.makedirs('./Data/followers')
        pid = post_id.replace(".json", "")
        result = vc.check_veracity(pid)
        #print("%s : %s"%(pid, result))
        if result == "False":
            continue


        if not os.path.exists(list_path):
            follower_list = {}
        #else :
            #follower_list = json.load(open(list_path))

#        if not os.path.exists(followers_all_path):
#            followers_data = {}
#        else : 
#            followers_data = json.load(open(followers_all_path))
        shuffle(lines)
        lines.reverse()
        for line in lines:
            #print(line)
            tweet = json.loads(line)
            
            user = tweet['user']
            user_id = user['id_str']
            screen_name = user['screen_name']
            followers_count = user['followers_count']
            #if followers check already done
        
            followers_path = './Data/followers/followers/%s'%user_id
            if os.path.isfile(followers_path):
                continue

            print("userid : %s, screen_name : %s"%(user_id, screen_name))
    
            followers = []
            if int(followers_count) == 0 :
                print("followers count is zero")
                #follower_list[user_id] = 0
            else:
    
                followers = get_followers(api, screen_name)
                #check rate limit error happened
                if followers == -1:
                    #change access token
                    print("change access token and load_api again")
                    api = load_api()
                    continue
#                follower_list[user_id] = len(followers)
                #save user : file name , followers : content
                #followers_data[user_id] = followers
            
            followers_path = './Data/followers/followers/%s'%user_id
            with open(followers_path, 'w') as f:
                json.dump(followers, f)


#            with open(list_path, 'w') as f:
#                json.dump(follower_list, f)









