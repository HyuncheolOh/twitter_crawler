#graph analysis
#depth, common follower, mutual friends, cascade structural virality
#time series analysis

import os, sys, json 
import bot_detect as bot 

def update():
    """ Update retweet graph with 
        Cascade, Bot information
    """
    #cascade calculation
    cascade = {}
    for postid in files:
        cascade = [postid] = {}
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)

            for key in tweets.keys():
                tweet = tweets[key]
                origin = tweet['origin_tweet']
                cascade[postid][origin] = cascade.get(origin, 0) + 1

    #update
    Bot = bot.load_bot()
    for postid in files:
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
            for tweet in tweets.values():
                tweet['cascade'] = cascade[tweet['origin_tweet']]
                tweet['bot'] = bot.check_bot(Bot, tweet['user'])

    
if __name__ == "__main__":
    dir_name = 'Retweet_New/'
    files = os.listdir(dir_name)

    update()


