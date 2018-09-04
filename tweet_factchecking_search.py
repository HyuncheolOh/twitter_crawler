import tweepy
from tweepy import OAuthHandler
import json
import datetime as dt
import time
import os
import sys


'''
In order to use this script you should register a data-mining application
with Twitter.  Good instructions for doing so can be found here:
http://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/

After doing this you can copy and paste your unique consumer key,
consumer secret, access token, and access secret into the load_api()
function below.

The main() function can be run by executing the command: 
python twitter_search.py

I used Python 3 and tweepy version 3.5.0.  You will also need the other
packages imported above.
'''

def load_api():
    ''' Function that loads the twitter API after authorizing the user. '''

    consumer_key = 'vqjpsBtqeyH2eNm0n8FdPfJJb'
    consumer_secret = 'n6e481fnVD6Hs58gGHzGIkyWPaK3yNbDI2vo3XBVnIH5FfMJ25'
    access_token = '970481481087774726-V8vi36RxAJM3ImG6NG5fv6ydoR8M9DN'
    access_secret = 'fsroQTMnvysMDGKy70slOKLENYQTcZCwkwFXIAB7tFe1p'
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    # load the twitter API via tweepy
    return tweepy.API(auth, wait_on_rate_limit=True)

    
def tweet_search(api, query, max_tweets, max_id, since_id, geocode):
    ''' Function that takes in a search string 'query', the maximum
        number of tweets 'max_tweets', and the minimum (i.e., starting)
        tweet id. It returns a list of tweepy.models.Status objects. '''

    searched_tweets = []
    while len(searched_tweets) < max_tweets:
        remaining_tweets = max_tweets - len(searched_tweets)
        try:
            new_tweets = api.search(q=query, count=remaining_tweets,
                                    since_id=str(since_id),
				                    max_id=str(max_id-1))
#                                    geocode=geocode)
            print('found',len(new_tweets),'tweets')
            if not new_tweets:
                print('no tweets found')
                break
            searched_tweets.extend(new_tweets)
            max_id = new_tweets[-1].id
        except tweepy.TweepError:
            print('exception raised, waiting 15 minutes')
            print('(until:', dt.datetime.now()+dt.timedelta(minutes=15), ')')
            time.sleep(15*60)
            break # stop the loop
    return searched_tweets, max_id


def get_tweet_id(api, date='', days_ago=10, query='ab'):
    ''' Function that gets the ID of a tweet. This ID can then be
        used as a 'starting point' from which to search. The query is
        required and has been set to a commonly used word by default.
        The variable 'days_ago' has been initialized to the maximum
        amount we are able to search back in time (9).'''

    if date:
        # return an ID from the start of the given day
        td = date + dt.timedelta(days=1)
        tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
        tweet = api.search(q=query, count=1, until=tweet_date)
    else:
        # return an ID from __ days ago
        td = dt.datetime.now() - dt.timedelta(days=days_ago)
        tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
        print(tweet_date)
        # get list of up to 10 tweets
        tweet = api.search(q=query, count=10, until=tweet_date)
        print('search limit (start/stop):',tweet[0].created_at)
        # return the id of the first tweet in the list
        return tweet[0].id


def write_tweets(tweets, filename):
    ''' Function that appends tweets to a file. '''

    with open(filename, 'a') as f:
        for tweet in tweets:
            json.dump(tweet._json, f)
            f.write('\n')


def search(post_id, query):
    ''' This is a script that continuously searches for tweets
        that were created over a given number of days. The search
        dates and search phrase can be changed below. '''



    ''' search variables: '''
    time_limit = 1.5                           # runtime limit in hours
    max_tweets = 100                           # number of tweets per search (will be
                                               # iterated over) - maximum is 100
    min_days_old, max_days_old = 0, 10         # search limits e.g., from 7 to 8
                                               # gives current weekday from last week,
                                               # min_days_old=0 will search from right now
    USA = '39.8,-95.583068847656,2500km'       # this geocode includes nearly all American
                                               # states (and a large portion of Canada)
    

    # loop over search items,
    # creating a new file for each
    print('Search phrase =', query )

    ''' other variables '''
    name = post_id
    json_file_root = 'Data/'  + str(name)

    try :
        if not os.path.exists(os.path.dirname(json_file_root)):
            os.makedirs(os.path.dirname(json_file_root))
    except OSError as err:
        print(err)
        
    read_IDs = False
        
    # open a file in which to store the tweets
    '''
    if max_days_old - min_days_old == 1:
        d = dt.datetime.now() - dt.timedelta(days=min_days_old)
        day = '{0}-{1:0>2}-{2:0>2}'.format(d.year, d.month, d.day)
    else:
        d1 = dt.datetime.now() - dt.timedelta(days=max_days_old-3)
        d2 = dt.datetime.now() - dt.timedelta(days=min_days_old)
        day = '{0}-{1:0>2}-{2:0>2}_to_{3}-{4:0>2}-{5:0>2}'.format(
              d1.year, d1.month, d1.day, d2.year, d2.month, d2.day)
    json_file = json_file_root + '_' + day + '.json'
    '''
    json_file = json_file_root +'.json'
    if os.path.isfile(json_file):
        print('Appending tweets to file named: ',json_file)
        read_IDs = True
        
    # authorize and load the twitter API
    api = load_api()
        
    # set the 'starting point' ID for tweet collection
    if read_IDs:
        # open the json file and get the latest tweet ID
        with open(json_file, 'r') as f:
            lines = f.readlines()
            since_id = json.loads(lines[-1])['id']
            print('Searching from the bottom ID in file')
        max_id = get_tweet_id(api, days_ago=(min_days_old-1))
    else:
        # get the ID of a tweet that is min_days_old
        if min_days_old == 0:
            max_id = -1
        else:
            max_id = get_tweet_id(api, days_ago=(min_days_old-1))
            # set the smallest ID to search for
        since_id = get_tweet_id(api, days_ago=(max_days_old-1))

    print('max id (starting point) =', max_id)
    print('since id (ending point) =', since_id)
        
    ''' tweet gathering loop  '''
    start = dt.datetime.now()
    end = start + dt.timedelta(hours=time_limit)
    count, exitcount = 0, 0
    while dt.datetime.now() < end:
        count += 1
        print('count =',count)
        # collect tweets and update max_id
        tweets, max_id = tweet_search(api, query, max_tweets,
                                      max_id=max_id, since_id=since_id,
                                      geocode=USA)
        # write tweets to file in JSON format
        if tweets:
            write_tweets(tweets, json_file)
            exitcount = 0
        else:
            exitcount += 1
            if exitcount == 1:
                print('Maximum number of empty tweet strings reached - breaking')
                break


#if __name__ == "__main__":
    #search()
