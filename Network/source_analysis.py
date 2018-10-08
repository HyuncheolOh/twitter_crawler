import os, json
import util 
import bot_detect as bot
import echo_chamber_util as e_util
from operator import itemgetter
from draw_tools.cdf_plot import CDFPlot
from draw_tools.box_plot import BoxPlot

#return origin screen name diversity, url diversity 
def get_diversity(user_tweets):
    source = []
    urls = []

    #remove empty tweets
    if len(user_tweets) == 0:
        return None, None

    for tweet in user_tweets:
        user = tweet['user']['screen_name']
        if tweet.get('retweeted_status', None) != None:
            tweet = tweet['retweeted_status']
        elif tweet.get('quoted_status', None) != None:
            tweet = tweet['quoted_status']
    
        #source[tweet['user']['screen_name']] = source.get(tweet['user']['screen_name'], 0) + 1
        if user != tweet['user']['screen_name']:
            source.append(tweet['user']['screen_name'])
        if len(tweet['entities']['urls']) != 0:
            expanded_url = tweet['entities']['urls'][0]['expanded_url']
            display_url = tweet['entities']['urls'][0]['display_url']
            
            if display_url != None:
                url = display_url.split('/')[0]
                if 'twitter' not in url:
                    #print(url)
                    urls.append(url)

    #print(util.eta(source), util.eta(urls))
    return util.eta(source), util.eta(urls)

#compare echo chamber users' source diversity and non echo chamber users' diversity
def echo_chamber_diversity(filename):
    Bot = bot.load_bot()
    dirname = 'Retweet/'
    files = os.listdir(dirname)
    
    if filename == None:
        echo_chamber_users = {}
        for postid in files:
            echo_chamber_users[postid] = {}
    else:
        echo_chamber_users = e_util.get_echo_chamber_users(filename)


    
    echo_tweet_diversity = []; echo_source_diversity = [];
    necho_tweet_diversity = []; necho_source_diversity = [];
    for postid in files:

        with open(dirname + postid) as f:
            tweets = json.load(f)

        non_echo_users = {}
        for tweet in tweets.values():
            user = tweet['user']

            #non echo chamber collect
            if not user in echo_chamber_users[postid]:
                non_echo_users[user] = 1

        print(len(echo_chamber_users[postid]), len(non_echo_users))

        timeline_dir = '../Timeline/'
        #collect echo chamber users' source diversity
        err = 0; nerr = 0
        for user in echo_chamber_users[postid]:
            try:
                with open(timeline_dir + user, 'r') as f:
                    user_tweets = json.load(f)
            except IOError as e:
                #print(e)
                err +=1
                continue
            tweet_diversity, source_diversity = get_diversity(user_tweets)

            if tweet_diversity != None:
                echo_tweet_diversity.append(tweet_diversity)
            if source_diversity != None:
                echo_source_diversity.append(source_diversity)

        for user in non_echo_users:
            try:
                with open(timeline_dir + user, 'r') as f:
                    user_tweets = json.load(f)
            except IOError as e:
                #print(e)
                nerr += 1
                continue

            tweet_diversity, source_diversity = get_diversity(user_tweets)
            if tweet_diversity != None:
                necho_tweet_diversity.append(tweet_diversity)
            if source_diversity != None:
                necho_source_diversity.append(source_diversity)

        #print(err, nerr)
        #break
                
    #CDF
    cdf = CDFPlot()
    cdf.set_label('Retweet Origin Diversity', 'CDF')
    #cdf.set_log(True)
    cdf.set_data(echo_tweet_diversity, 'Echo Chamber')
    cdf.set_data(necho_tweet_diversity, 'Non Echo Chamber')
    cdf.set_legends(['Echo CHamber', 'Non Echo CHamber'], 'User Type')
    cdf.save_image('Image/20181002/source_diversity_retweet_cdf.png')

    cdf = CDFPlot()
    cdf.set_label('Source News Diversity', 'CDF')
    #cdf.set_log(True)
    cdf.set_data(echo_source_diversity, 'Echo Chamber')
    cdf.set_data(necho_source_diversity, 'Non Echo Chamber')
    cdf.set_legends(['Echo CHamber', 'Non Echo CHamber'], 'User Type')
    cdf.save_image('Image/20181002/source_diversity_news_cdf.png')

    #BoxPlot
    box = BoxPlot(1)
    box.set_data([echo_tweet_diversity, necho_tweet_diversity],'')
    box.set_xticks(['Echo Chamber', 'Non Echo Chamber', 'All'])
    box.set_label('', 'Retweet Origin Diversity')
    box.save_image('Image/20181002/source_diversity_retweet.png')

    box = BoxPlot(1)
    box.set_data([echo_source_diversity, necho_source_diversity],'')
    box.set_xticks(['Echo Chamber', 'Non Echo Chamber', 'All'])
    box.set_label('', 'Source News Diversity')
    box.save_image('Image/20181002/source_diversity_news.png')


if __name__ == "__main__":
    echo_chamber_diversity('Data/echo_chamber2.json')
