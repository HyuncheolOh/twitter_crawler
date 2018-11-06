import os, json
import util 
import bot_detect as bot
import echo_chamber_util as e_util
from time import time
from operator import itemgetter
from draw_tools.cdf_plot import CDFPlot
from draw_tools.box_plot import BoxPlot
import draw_tools.sns_plot as snsplot
from scipy import stats

def get_polarity(userid):
    with open('Data/polarization.json', 'r') as f:
        P = json.load(f)
    
    try:
        #put in the bucket
        p = float(P[userid])
        if p > 2:
            p = 2
        elif p < -2:
            p = -2
        p += 2
        return p / 4 #return -1 ~ 1 
    except KeyError as e:
        return None

#return source urls
def timeline_urls(user_tweets):
    urls = []
    expanded_urls = []

    #remove empty tweets
    if len(user_tweets) == 0:
        return urls, expanded_urls

    for tweet in user_tweets:
        user = tweet['user']['screen_name']
        if tweet.get('retweeted_status', None) != None:
            tweet = tweet['retweeted_status']
        elif tweet.get('quoted_status', None) != None:
            tweet = tweet['quoted_status']
    
        if len(tweet['entities']['urls']) != 0:
            expanded_url = tweet['entities']['urls'][0]['expanded_url']
            display_url = tweet['entities']['urls'][0]['display_url']
            if display_url != None:
                url = display_url.split('/')[0]
                if 'twitter' not in url:
                    #print(url)
                    urls.append(url)
  
            if expanded_url != None:
                if not 'twitter.com' in expanded_url:
                    expanded_urls.append(expanded_url)

    return urls, expanded_urls

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


#show user's consuming content (source) is aligned to their ideological position
def political_alignment():
    source_politic_score = {}
    echo_chamber_users = e_util.get_echo_chamber_users(filename)

    #load source information file
    with open('Data/top500.tab', 'r') as f:
        i = 0
        for row in f:
            if i != 0:
                items = row.split('\t')
                items[0] = items[0].replace("www.", "")
                source_politic_score[items[0]] = (float(items[1]) + 1) / 2 
            i += 1
    #print(source_politic_score.keys())
    source_list = source_politic_score.keys()
    #check users political score in the rumor propagation
    files = os.listdir(dir_name)
    timeline_dir = '../Timeline/'

    user_content_polarity = {} #user - polarity 
    postid_content_polarity = {}
    all_echo_user_score = []; all_non_echo_user_score = []
    all_echo_source_score = []; all_non_echo_source_score = []       

    for postid in files:
        user_score = []; echo_user_score = []; non_echo_user_score = []
        source_score = []; echo_source_score = []; non_echo_source_score = []       

        path = '%s/selective_exposure_%s'%(folder, postid)
        if postid != '142256':
            continue
        postid_content_polarity[postid] = {}
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)

        #if len(tweets) > 3000 or len(tweets) < 70:
        #    continue
        print(postid, len(tweets))
        users = list(set([tweet['user'] for tweet in tweets.values()]))
        #collect echo chamber users' source diversity
        err = 0; nerr = 0
        count_zero_users = 0
        for user in users:

            if user_content_polarity.get(user, None) != None:
                postid_content_polarity[postid][user] = user_content_polarity.get(user)
                continue

            try:
                with open(timeline_dir + user, 'r') as f:
                    user_tweets = json.load(f)
            except IOError as e:
                #print(e)
                err +=1
                continue
            except ValueError as e:
                err += 1
                continue
            
            urls, expanded_urls = timeline_urls(user_tweets)
            if len(urls) == 0:
                continue 

            count =0 
            p_sum = 0 
            for url in urls:
                if url in source_list:
                    count += 1
                    idx = source_list.index(url)
                    #print(url, source_politic_score.keys()[idx], source_politic_score[source_politic_score.keys()[idx]])
                    p_sum += source_politic_score[source_list[idx]]
            if count == 0:
                count_zero_users += 1
                continue
            p_mean = round(p_sum / count, 4)
            user_politic_score = round(get_polarity(user),4)
            if user_politic_score != None:
                user_score.append(user_politic_score)
                source_score.append(p_mean)
                if user in echo_chamber_users[postid]:
                    echo_user_score.append(user_politic_score)
                    echo_source_score.append(p_mean)
                    all_echo_user_score.append(user_politic_score)
                    all_echo_source_score.append(p_mean)

                else:
                    non_echo_user_score.append(user_politic_score)
                    non_echo_source_score.append(p_mean)
                    all_non_echo_user_score.append(user_politic_score)
                    all_non_echo_source_score.append(p_mean)


            user_content_polarity[user] = p_mean            
            postid_content_polarity[postid][user] = p_mean
            #calculate until 1000 users cause it takes too much time 
            #if len(user_score) > 1500:
            #    break

        print('count zero users : %s'%count_zero_users)
        print('save selective exposure file')
        filefolder = 'Data/SelectiveExposure/'
        if not os.path.exists(filefolder):
           os.makedirs(filefolder)

    
        print('echo', stats.pearsonr(echo_user_score, echo_source_score)[0])
        print('necho', stats.pearsonr(non_echo_user_score, non_echo_source_score)[0])
    #    break
        datapath = filefolder + postid + '_polarity'
        with open(datapath, 'w') as f :
            json.dump({'necho_user' : non_echo_user_score, 'necho_source' : non_echo_source_score, 'echo_user' : echo_user_score, 'echo_source' : echo_source_score}, f)

        snsplot.draw_echo_plot(non_echo_user_score, non_echo_source_score, echo_user_score, echo_source_score, path)
    
        with open(filefolder + postid, 'w') as f:
            json.dump(postid_content_polarity[postid], f)
       
    print('echo', stats.pearsonr(all_echo_user_score, all_echo_source_score))
    print('necho', stats.pearsonr(all_non_echo_user_score, all_non_echo_source_score))

    with open('Data/user_content_polarity.json', 'w') as f:
        json.dump(user_content_polarity, f)
    with open('Data/user_content_polarity_postid.json', 'w') as f:
        json.dump(postid_content_polarity, f)

#draw graph from saved datafile 
def draw_political_alignment():
    
    filefolder = 'Data/SelectiveExposure/'
    postid = '142256'
    #postid = '142264'
    path = folder  + '/' + postid
    datapath = filefolder + postid + '_polarity'
    
    print(datapath)
    with open(datapath, 'r') as f : 
        dataset = json.load(f)
    
    print(dataset.keys())
    non_echo_user_score = dataset['necho_user']
    non_echo_source_score = dataset['necho_source']
    echo_user_score = dataset['echo_user']
    echo_source_score = dataset['echo_source']

    print(path)
    snsplot.draw_echo_plot(non_echo_user_score, non_echo_source_score, echo_user_score, echo_source_score, path)


#compare ranked echo chamber user's political diversity 
def source_diversity_rank_comparison(filename):
    source_politic_score = {}

    #load source information file
    with open('Data/top500.tab', 'r') as f:
        i = 0
        for row in f:
            if i != 0:
                items = row.split('\t')
                items[0] = items[0].replace("www.", "")
                source_politic_score[items[0]] = (float(items[1]) + 1) / 2 
            i += 1
    #print(source_politic_score.keys())
    source_list = source_politic_score.keys()
    #check users political score in the rumor propagation
    timeline_dir = '../Timeline/'

    with open(filename, 'r') as f:
        echo_chambers = json.load(f)

    for postid in echo_chambers:
        users = echo_chambers[postid]

        user_score = []
        source_score = []
        for user in users: 
            try:
                with open(timeline_dir + user, 'r') as f:
                    user_tweets = json.load(f)
            except IOError as e:
                #print(e)
                err +=1
                continue
            except ValueError as e:
                err += 1
                continue
     
            urls, expanded_urls = timeline_urls(user_tweets)
            if len(urls) == 0:
                continue 

            count =0 
            p_sum = 0 
            for url in urls:
                if url in source_list:
                    count += 1
                    idx = source_list.index(url)
                    #print(url, source_politic_score.keys()[idx], source_politic_score[source_politic_score.keys()[idx]])
                    p_sum += source_politic_score[source_list[idx]]
            if count == 0:
                continue
            p_mean = round(p_sum / count, 4)
            user_politic_score = round(get_polarity(user),4)
            if user_politic_score != None:
                user_score.append(user_politic_score)
                source_score.append(p_mean)
          
        path = '%s/SourcePolarity/%s'%(folder, postid)
        if not os.path.exists('%s/SourcePolarity'%folder):
            os.makedirs('%s/SourcePolarity'%folder)
        snsplot.draw_plot(user_score, source_score, path)

def political_alignment_pearson():
    with open('Data/user_content_polarity.json', 'r') as f:
        content_polarity = json.load(f)

    echo_chamber_users = e_util.get_echo_chamber_users('Data/echo_chamber2.json')

    files = os.listdir('RetweetNew')
    e_user = {}
    ne_user = {}
    e_source = {}
    ne_source = {}
    Bot = bot.load_bot()
    for ccc, postid in enumerate(files):
        with open('RetweetNew/' + postid, 'r') as f:
            tweets = json.load(f)
        print(ccc, postid, len(tweets))
        echo_users = echo_chamber_users[postid]
        for tweet in tweets.values():
            user = tweet['user']

            
            if bot.check_bot(Bot, user) == 1:
                continue
            
            if e_user.get(user, None) != None or ne_user.get(user, None) != None:
                continue

            user_politic_score = round(get_polarity(user),4)
            content_politic_score = content_polarity.get(user, None)

            if user_politic_score != None and content_politic_score != None:

                if user in echo_users:
                    e_user[user] = user_politic_score
                    e_source[user] = content_politic_score
                else:
                    ne_user[user] = user_politic_score
                    ne_source[user] = content_politic_score
    
        #if ccc == 10:
        #    break
    #    break
    e_keys = e_user.keys()
    ne_keys = ne_user.keys()
    #print('echo', stats.pearsonr(e_user.values(), e_source.values()))
    #print('necho', stats.pearsonr(ne_user.values(), ne_source.values()))
    print('echo', stats.pearsonr([e_user[key] for key in e_keys], [e_source[key] for key in e_keys]))
    print('necho', stats.pearsonr([ne_user[key] for key in ne_keys], [ne_source[key] for key in ne_keys]))

    with open('Data/user_polarity_content_polarity.json', 'w') as f:
        json.dump({'e_user':e_user, 'ne_user' : ne_user, 'e_source' : e_source, 'ne_source' : ne_source},f)

if __name__ == "__main__":
    folder = 'Image/20181105'
    start = time()
    dir_name = 'RetweetNew/'
    #echo_chamber_diversity('Data/echo_chamber2.json')
    
    filename = 'Data/echo_chamber2.json'
    #echo_chamber_users = e_util.get_echo_chamber_users(filename)
    #political_alignment()
    #political_alignment_pearson()
    draw_political_alignment()
    #source_diversity_rank_comparison('Data/ranked_weight2_echo_chamber.json')
    end = time()
    print('%s taken'%(end-start))
