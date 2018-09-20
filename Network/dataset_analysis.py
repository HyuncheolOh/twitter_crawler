import MySQLdb 
import os, sys, json
import fileinput
import bot_detect as bot
import unicodecsv as csv
from dateutil import parser
from tweet_parser.tweet import Tweet
from tweet_parser.tweet_parser_errors import NotATweetError
from draw_tools.cdf_plot import CDFPlot
from draw_tools.ccdf_plot import CCDFPlot

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
    users, cascade, = tweet_anlysis()
    print("Unique users : %s"%users)
    print("Number of cascades : %s"%cascade)

    #draw_graph()
    print("User participation CDF saved. /Image/user_participation_cdf.png")
    

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



