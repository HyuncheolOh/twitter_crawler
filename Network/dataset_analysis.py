import os, sys, json
import fileinput
import bot_detect as bot
from tweet_parser.tweet import Tweet
from tweet_parser.tweet_parser_errors import NotATweetError
from draw_tools.cdf_plot import CDFPlot
from draw_tools.ccdf_plot import CCDFPlot

def screen_name(userid):
    dir_name = "RetweetNew/"
    files = os.listdir(dir_name)
    for postid in files:
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
        for tweet in tweets.values():
            if tweet['user'] == userid:
                return tweet['screen_name']
def top_participated_users(users):
    Bot = bot.load_bot()
    for key in user_participation:
        user_participation[key] #postids 

    sort = sorted(user_participation, key = lambda k : len(user_participation[k]), reverse=True)

    for i, item in enumerate(sort):
        if i == 20:
            break
        print(item, screen_name(item), len(user_participation[item]), bot.check_bot(Bot, item))

def retweet_graph_info(path):
    postid = path.split('/')[-1]
    with open(path, 'r') as f:
        tweets = json.load(f)

    for tid in tweets:
        tweet = tweets[tid]
        cascade_num[tweet['origin_tweet']] = 1
        uid = tweet['user']
        unique_user[uid] = 1
        user_participation[uid] = user_participation.get(uid, {})
        user_participation[uid][postid] = 1

def draw_graph():
    #user participation
    user_part_num = [len(rumor_num) for rumor_num in user_participation.values()]
    cdf = CDFPlot()
    cdf.set_label('Number of rumors', 'CDF')
    cdf.set_data(user_part_num, 'CDF')
    cdf.save_image('Image/user_participation_cdf.png')

    ccdf = CCDFPlot()
    ccdf.set_label('Number of rumors', 'CDF')
    ccdf.set_data(user_part_num, 'CCDF')
    ccdf.save_image('Image/user_participation_ccdf.png')

    top_participated_users(user_part_num)

def tweet_anlysis():
    for postid in rumors:
        retweet_graph_info(path + 'Network/RetweetNew/'+postid)
    return len(unique_user), len(cascade_num)

def analysis():
    print("Veracity : True, False, Mixture, Mostly True, Mostly False")
    print("At least 100 tweets collected since Mar. 2018")
    print("Number of rumors : %s / %s"%(len(rumors), len(files)))
    users, cascade, = tweet_anlysis()
    print("Unique users : %s"%users)
    print("Number of cascades : %s"%cascade)

    draw_graph()
    print("User participation CDF saved. /Image/user_participation_cdf.png")
    

if __name__ == "__main__":
    path = '/media1/Fakenews/Twitter/crawler/TwitterAPI/'
    files = os.walk(path + 'Data').next()[2]
    rumors = os.walk(path + 'Network/RetweetNew').next()[2]
    unique_user = {}
    cascade_num = {}
    user_participation = {}
    analysis()






