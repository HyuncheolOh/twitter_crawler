#!/usr/bin/env python
# encoding: utf-8

import tweepy #https://github.com/tweepy/tweepy
#import csv
import unicodecsv as csv
import sys 
import os
import json
from tweepy import OAuthHandler
from random import shuffle
#Twitter API credentials
consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""


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


def load_api():
    global key_num 
    if key_num == len(token_list):
        key_num = 0
        print("sleep 900 seconds for rate limit exceeds")
        sleep(900)
    token = token_list[key_num]
    auth = OAuthHandler(token[0], token[1])
    auth.set_access_token(token[2], token[3])

    return tweepy.API(auth, wait_on_rate_limit=True)

def get_url(json_data):
    print(json_data)
    url = ''
    try :
       # print("tweeeeeeeeetttt!!")
       # print(json_data['entities'])
        url = json_data['entities']['urls'][0]['display_url']
    except (KeyError, IndexError) as e:
        try:
        #    print("rettweettttttttt!!")
        #    print(json_data['retweeted_status'])
            #url = json_data['retweeted_status']['quoted_status']['entities']['display_url']
            url = json_data['retweeted_status']['entities']['urls'][0]['display_url']
        except (KeyError, IndexError) as e:
            print(json_data)
            pass
    return url
    
def get_json_info(tweet):
    d = {}
    d['entities'] = tweet._json['entities']
    d['created_at'] = tweet._json['created_at']
    d['user'] = {}
    d['user']['entities'] = tweet._json['user']['entities']
    d['user']['screen_name'] = tweet._json['user']['screen_name']
    d['text'] = tweet._json['text']
    d['retweeted_status'] = {}
    try:
        d['retweeted_status']['entities'] = tweet._json['retweeted_status']['entities']
        d['retweeted_status']['user'] = {}
        d['retweeted_status']['user']['entities'] = tweet._json['retweeted_status']['user']['entities']
    except KeyError as e:
        pass

    return d

def get_all_tweets(userid, screen_name):
    #Twitter only allows access to a users most recent 3240 tweets with this method
    
    #authorize twitter, initialize tweepy
    api = load_api()

    #initialize a list to hold all the tweepy Tweets
    alltweets = []	
    
    #make initial request for most recent tweets (200 is the maximum allowed count)
    try:
        new_tweets = api.user_timeline(screen_name = screen_name,count=200)
    except BaseException as e:
        print(userid, screen_name, e)
 #   except tweepy.error.TweepError as e:
        with open('./Timeline_New/%s'%userid, 'w') as f:
            json.dump([], f)

        return None
    
    alltweets.extend(new_tweets)
    if len(alltweets) == 0:
        with open('./Timeline_New/%s'%userid, 'w') as f:
            json.dump([], f)
        return
 
    #save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1
    
    #keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
            ##print "getting tweets before %s" % (oldest)
            
            #all subsiquent requests use the max_id param to prevent duplicates
            new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
            
            #save most recent tweets
            alltweets.extend(new_tweets)
            
            #update the id of the oldest tweet less one
            oldest = alltweets[-1].id - 1
            
            #print "...%s tweets downloaded so far" % (len(alltweets))
            break
    print(userid, screen_name, len(alltweets))
    #save most recent tweets
   
   
    #transform the tweepy tweets into a 2D array that will populate the csv	| you can comment out data you don't need
           
    #print(alltweets[0]._json)
    '''j
    outtweets = [[tweet.id_str, 
                            tweet.created_at, 
                            tweet.favorite_count, 
                            tweet.retweet_count, 
                            tweet.retweeted, 
                            tweet.source, 
                            get_url(tweet._json),
                            tweet.text,] for tweet in alltweets]
        #write the csv	
    with open('./Timeline/%s.csv' % userid, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(["id",
                            "created_at",
                            "favorites", 
                            "retweets",
                            "retweeted", 
                            "source",
                            "url",
                            "text"])
            writer.writerows(outtweets)
    '''
    outtweets = [get_json_info(tweet) for tweet in alltweets]
    with open('./Timeline_New/%s'%userid, 'w') as f:
        json.dump(outtweets, f)

    pass

def get_all_users():
    
    dirname = './Network/Retweet/'
    files = os.listdir(dirname)
    d = {}
    for postid in files:
        path = dirname + postid
        with open(path, 'r') as f:
            users = json.load(f)

            for user in users.keys():
                d[user] = users[user]['screen_name']

    return d

def is_timeline_exist(userid):
    path = './Timeline_New/%s'%userid
    return os.path.exists(path)


if __name__ == '__main__':
    #pass in the username of the account you want to download
    if len(sys.argv) == 2:
        key_num = int(sys.argv[1])
        print("key num %s"%key_num)

    load_key_list()
    load_api()

    users = get_all_users()
    user_keys = users.keys()
    shuffle(user_keys)
    get_all_tweets('aaaaaaaaaaaaaa', 'gamva2')

    #for userid in user_keys:
    #    if not is_timeline_exist(userid):
    #        get_all_tweets(userid, users[userid])





