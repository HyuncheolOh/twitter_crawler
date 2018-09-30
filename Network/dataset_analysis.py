import MySQLdb 
import os, sys, json
import fileinput
import bot_detect as bot
import unicodecsv as csv
import pandas as pd
from dateutil import parser
from tweet_parser.tweet import Tweet
from tweet_parser.tweet_parser_errors import NotATweetError
from draw_tools.cdf_plot import CDFPlot
from draw_tools.ccdf_plot import CCDFPlot
from draw_tools.bar_plot import BarPlot

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def get_veracity(postid):
    conn, cursor = sql_connect()
    if int(postid) < 100000:
    #factchecking
        sql = """
        SELECT veracity, title
        FROM factchecking_data
        WHERE id = %s
        """

    else:
    #snopes
        sql = """
        SELECT veracity, title
        FROM snopes_set
        WHERE post_id = %s
        """

    cursor.execute(sql, [postid])
    rs = cursor.fetchall()
    sql_close(cursor, conn)
    return rs[0][0], rs[0][1]

def get_category(postid):
    conn, cursor = sql_connect()
    if int(postid) < 100000:
    #factchecking
        sql = """
        SELECT category
        FROM factchecking_data
        WHERE id = %s
        """

    else:
    #snopes
        sql = """
        SELECT category
        FROM snopes_set
        WHERE post_id = %s
        """

    cursor.execute(sql, [postid])
    rs = cursor.fetchall()
    sql_close(cursor, conn)
    return rs[0][0]

def screen_name(userid):
    dir_name = "Retweet/"
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

    top_0_1 = []
    top_1 = []
    for i, item in enumerate(sort):
        #print(item, screen_name(item), len(user_participation[item]), bot.check_bot(Bot, item))

        if bot.check_bot(Bot, item) == 0:
            if i < 200:
                top_0_1.append(item)

            if i < 2000:
                top_1.append(item)

    with open('top_users.json', 'w') as f:
        json.dump({'top_0_1':top_0_1, 'top_1': top_1}, f)


def retweet_graph_info(path):
    postid = path.split('/')[-1]
    with open(path, 'r') as f:
        tweets = json.load(f)

    max_cascade = 0
    max_depth = 0
    max_breadth = 0
    claim_unique_user = {}
    breadth_size = {}
    unique_cascade = {}
    time = {}
    for tid in tweets:
        tweet = tweets[tid]
        cascade_num[tweet['origin_tweet']] = 1
        unique_cascade[tweet['origin_tweet']] = 1
        uid = tweet['user']
        unique_user[uid] = 1
        claim_unique_user[uid] = 1
        b_size = breadth_size.get(tweet['depth'], 0) + 1
        breadth_size[tweet['depth']] = b_size
        user_participation[uid] = user_participation.get(uid, {})
        user_participation[uid][postid] = 1
        time[tid] = parser.parse(tweets[tid]['time'])
        if tweet['depth'] > max_depth:
            max_depth = tweet['depth']
            max_depth_user = tweet['origin']

        if tweet['cascade'] > max_cascade:
            max_cascade = tweet['cascade']
            max_cascade_user = tweet['origin']
            
        if b_size > max_breadth:
            max_breadth = b_size
            max_breadth_user = tweet['origin']
    
    times = [parser.parse(tid['time']) for tid in tweets.values() if tid['origin'] == max_cascade_user]
    cascade_period = max(times) - min(times)
    #time_diff = (times[i] - times[1]).total_seconds() / 60
    #cascade size (max), cascade num, unique users, max depth, max_breadth, echo chamber formed?, root spreader name , veracity 
    veracity, title = get_veracity(postid)
    unique_users = len(claim_unique_user)
    c_num = len(unique_cascade)
    print("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"%(postid,  c_num, max_cascade, screen_name(max_cascade_user),max_depth, screen_name(max_depth_user),max_breadth, screen_name(max_breadth_user), unique_users, veracity,   max(time.values()) - min(time.values()), cascade_period))
    cwriter.writerow([postid, len(tweets), max_cascade, max_depth, max_breadth, c_num, unique_users, veracity, screen_name(max_cascade_user), screen_name(max_depth_user), screen_name(max_breadth_user), max(time.values()) - min(time.values()), cascade_period])


#echo chamber characteristics 
#number of echo chambers in a rumor 
#number of users in an echo chamber 2, 3, 4 
#polarity scores 
def echo_chamber_statistics():
    with open('Data/echo_chamber2.json') as f:
        echo_chamber = json.load(f)

    echo_chamber_num = {} 
    unique_user = {}
    unique_user_per_cascade = {}
    for key in echo_chamber:
        users = echo_chamber[key]

        if len(users) < 2:
            continue 

        postids = key.split('_')
        for postid in postids:
            if unique_user.get(postid, -1) == -1:
                unique_user[postid] = {}

            echo_chamber_num[postid] = echo_chamber_num.get(postid, 0) + 1

            for user in users:
                unique_user[postid][user] = 1

    for postid in unique_user.keys():
        users = unique_user[postid]

        with open('Retweet/%s'%postid, 'r') as f:
            tweets = json.load(f)

        for tweet in tweets.values():
            if tweet['user'] in users:
                unique_user_per_cascade[tweet['origin_tweet']] = unique_user_per_cascade.get(tweet['origin_tweet'], [])
                unique_user_per_cascade[tweet['origin_tweet']].append(tweet['user'])


    #for postid in unique_user.keys():
    #    print(postid, echo_chamber_num[postid], len(unique_user[postid]))
    users = [len(unique_user[postid]) for postid in unique_user.keys()]
    echo_num = [echo_chamber_num[postid] for postid in unique_user.keys()]
    users_cascade = [len(item) for item in unique_user_per_cascade.values()]

    print('users')
    print(pd.Series(users).describe())
    print('users cascade')
    print(pd.Series(users_cascade).describe())
    print('echo numbers')
    print(pd.Series(echo_num).describe())
    draw_cdf_plot([users], 'Number of Users', ['Echo Chamber'], '', 'echo_chamber_statistics_user_num_rumor')
    draw_cdf_plot([users_cascade], 'Number of Users', ['Echo Chamber'], '', 'echo_chamber_statistics_user_num_cascade')
    draw_cdf_plot([echo_num], 'Number of Echo Chambers', ['Echo Chamber'], '', 'echo_chamber_statistics_echo_num')
    

def draw_cdf_plot(datas, datatype, legend, legend_type, filename):
    cdf = CDFPlot()
    cdf.set_label(datatype, 'CDF')
    cdf.set_log(True)
    for i in range(len(datas)):
        cdf.set_data(datas[i], legend[i])
    cdf.set_legends(legend, legend_type)
    cdf.save_image('Image/20180927/%s.png'%filename)

def category_analysis():
    dirname = 'Retweet'
    files = os.listdir(dirname)
    categories = []
    titles = []
    for postid in files:
        categories.append(get_category(postid))
        _, title = get_veracity(postid)
        titles.append(title)
        #print(postid, get_category(postid))

    #bar chart?
    #print(categories)
    c_set = set(categories)
    category_num = []
    for item in c_set:
        category_num.append(categories.count(item))
        print(item, categories.count(item))
    #show distribution with bar plot
    barplot = BarPlot(1)
    barplot.set_data(c_set, category_num, 'Categories', 'vertical')
    barplot.set_ylim(80)
    barplot.save_image('Image/20180928/categories_bar.png')
    #show politics and non-politics 
    Politics = ['Politics', 'Politicians'] 
    Other = ['Fake News', 'Fauxtography']

    p_count = 0
    np_count = 0 
    o_count = 0
    for item in categories:
        #print(item)
        if item in Politics:
            p_count += 1 
        elif item in Other:
            o_count += 1
        else : 
            np_count += 1

    print("Politics : %s, Non-Politics : %s"%(p_count, np_count))


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
        retweet_graph_info(path + 'Network/Retweet/'+postid)
    return len(unique_user), len(cascade_num)

def analysis():
    print("Veracity : True, False, Mixture, Mostly True, Mostly False")
    print("At least 100 tweets collected since Mar. 2018")
    print("Number of rumors : %s / %s"%(len(rumors), len(files)))
    #users, cascade, = tweet_anlysis()
    #print("Unique users : %s"%users)
    #print("Number of cascades : %s"%cascade)

    #draw_graph()
    #print("User participation CDF saved. /Image/user_participation_cdf.png")
    category_analysis()
    #echo_chamber_statistics()

if __name__ == "__main__":
    f = open('Data/rumors.csv', 'w')
    cwriter = csv.writer(f, delimiter='\t')
    cwriter.writerow(['postid', '# tweets', 'max_cascade', 'max_depth', 'max_breadth', '# cascade', 'unique users', 'veracity', 'max_cascade_user', 'max_depth_user', 'max_breadth_user', 'all period', 'cascade period']) 
    path = '/media1/Fakenews/Twitter/crawler/TwitterAPI/'
    files = os.walk(path + 'Data').next()[2]
    rumors = os.walk(path + 'Network/Retweet').next()[2]
    unique_user = {}
    cascade_num = {}
    user_participation = {}
    analysis()

    f.close()



