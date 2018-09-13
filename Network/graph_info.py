#graph analysis
#depth, common follower, mutual friends, cascade structural virality
#time series analysis

import MySQLdb 
import os, sys, json 
import bot_detect as bot 
import numpy as np
from dateutil import parser
from operator import itemgetter
from draw_tools.cdf_plot import CDFPlot
from draw_tools.ccdf_plot import CCDFPlot
from draw_tools.line_plot import LinePlot

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
        SELECT veracity
        FROM factchecking_data
        WHERE id = %s
        """

    else:
    #snopes
        sql = """
        SELECT veracity
        FROM snopes_set
        WHERE post_id = %s
        """
    cursor.execute(sql, [postid])
    rs = cursor.fetchall()
    sql_close(cursor, conn)
    return rs[0][0]

def update():
    """ Update retweet graph with 
        Cascade, Bot information
    """
    #cascade calculation
    cascade = {}
    child = {}
    for postid in files:
        cascade[postid] = {}
        child[postid] = {}
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)

            for key in tweets.keys():
                tweet = tweets[key]
                origin = tweet['origin_tweet']
                cascade[postid][origin] = cascade[postid].get(origin, 0) + 1
                parent_tweet = tweet['parent_tweet']
                child[postid][parent_tweet] = child[postid].get(parent_tweet, 0) + 1 

    #update
    Bot = bot.load_bot()
    for postid in files:
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
            #print(len(tweets))
            #print(cascade[postid])
            for tweet in tweets.values():
                tweet['cascade'] = cascade[postid][tweet['origin_tweet']]
                tweet['bot'] = bot.check_bot(Bot, tweet['user'])
                tweet['child'] = child[postid].get(tweet['tweet'], 0)
        #print(postid)
        with open(dir_name+postid, 'w') as f:
            json.dump(tweets, f)
        print(postid)

def time_series(veracity):
    total_users = {}
    timeseries_data = {}

    depth_time = {} #time to have X depth per rumor depth_time[1][postid] = XX min - Y : mean minutes, X : depth
    depth_user = {} #users to have X depth per rumor 
    unique_user_time = {} #time to have X unique users per rumor   - Y : mean minutes, X : unique users 
    users_count = np.arange(1000, 100000, 1000)
    #print(users_count)
    cascade_all = {}
    cascade_breadth = {}
    cascade_depth = {}
    for num, postid in enumerate(files):
        if veracity != get_veracity(postid):
            continue
        #if veracity != 'True' and veracity != 'False':
        #    continue
        times = []
        path = dir_name + postid
        with open(path, 'r') as f:
            tweets = json.load(f)

        sort = {}
        for key in tweets.keys():
            tweet = tweets[key]
            sort[key] = parser.parse(tweet['time'])
        
        new_list = sorted(sort.items(), key=lambda x: x[1])
        start_time = new_list[0][1]
        sorted_ids = [item[0] for item in new_list]

        max_depth = 0
        max_breadth = 0
        user_num = 0
        unique_users = {}
        #print(start_time)
        ordered_data = []
        cascade_depth[postid] = {}

        b = {}
        user_count_index = 0
        for i, tid in enumerate(sorted_ids):
            tweet = tweets[tid]
            cascade_all[tweet['origin_tweet']] = tweet['cascade']
            unique_users[tweet['user']] = 1
            total_users[tweet['user']] = 1
            user_num = len(unique_users)
            elapsed_time = (new_list[i][1] - start_time).total_seconds() / 60

            #cascade_depth[postid].append(tweet['/depth'])
            #depth from a cascade
            if max_depth < tweet['depth']:
                max_depth = tweet['depth']
                depth_time[max_depth] = depth_time.get(max_depth, {})
                depth_time[max_depth][postid] = elapsed_time
                depth_user[max_depth] = depth_user.get(max_depth, {})
                depth_user[max_depth][postid] = len(unique_users)
            
            #cascade depth
            cascade_depth[postid][tweet['origin_tweet']] = cascade_depth[postid].get(tweet['origin_tweet'], [])
            cascade_depth[postid][tweet['origin_tweet']].append(tweet['depth'])

            #breadth from a cascade 
            b[tweet['origin_tweet']] = b.get(tweet['origin_tweet'], {})
            breadth = b[tweet['origin_tweet']].get(tweet['depth'], 0) + 1 #same origin tweet, number of same depth node means breadth
            b[tweet['origin_tweet']][tweet['depth']] = breadth
            
            c_breadth = cascade_breadth.get(tweet['origin_tweet'], 0)
            if c_breadth < breadth:
                cascade_breadth[tweet['origin_tweet']] = breadth

            if breadth > max_breadth:
                max_breadth = breadth
        
            if user_num >= users_count[user_count_index]:
                unique_user_time[user_num] = unique_user_time.get(user_num, {})
                unique_user_time[user_num][postid] = elapsed_time
                user_count_index += 1 
    
            data = {'elapsed_time' : elapsed_time, 'max_depth' : max_depth, 'max_breadth' : max_breadth, 'unique_users' : user_num}
            #print(data)    
            ordered_data.append(data)
        #if num >= 1000:
        #3    break
        #print(data)

        timeseries_data[postid] = ordered_data
    
    #print(unique_user_time)
    #print(unique_user_time[100])

    #print(np.mean(unique_user_time[100].values()))
    #print(np.mean(unique_user_time[200].values()))

    #print(depth_user)
    #print(depth_user[2])
    #print(np.mean(np.array(depth_user[2].values())))
    #print(np.mean(np.array(depth_user[3].values())))
    
    return depth_time, depth_user, unique_user_time, cascade_depth


def draw_graph():
    depth_time1, depth_user1, unique_user_time1, cascade_depth1 = time_series('True')

    x_ticks1 = depth_time1.keys()
    y_ticks1 = [np.mean(depth_time1[depth].values()) for depth in x_ticks1]

    depth_time2, depth_user2, unique_user_time2, cascade_depth2 = time_series('False')
    
    x_ticks2 = depth_time2.keys()
    y_ticks2 = [np.mean(depth_time2[depth].values()) for depth in x_ticks1]

    #draw mean minutes - depth line plot 
    line = LinePlot()
    line.set_ylog()
    line.set_label('Depth', 'Mean Minutes')
    line.set_plot_data([y_ticks1, y_ticks2], x_ticks1)
    line.set_legends(['True', 'False'])
    line.save_image('Image/time_depth_line.png')

    x_ticks1 = unique_user_time1.keys()
    x_ticks2 = unique_user_time2.keys()
    x_ticks1 = sorted(x_ticks1)
    y_ticks1 = [np.mean(unique_user_time1[num].values()) for num in x_ticks1]
    y_ticks2 = [np.mean(unique_user_time2[num].values()) for num in x_ticks2]
    
    #draw mean minutes - unique users line plot 
    line = LinePlot()
    line.set_ylog()
    line.set_label('Unique Users', 'Mean Minutes')
    line.set_plot_data([y_ticks1, y_ticks2], x_ticks1)
    line.set_xticks(x_ticks1)
    line.set_legends(['True', 'False'])
    line.save_image('Image/time_users_line.png')

    all_depth_true = [[key] * len(depth_time1[key]) for key in depth_time1.keys()] #True
    all_depth_false = [[key] * len(depth_time2[key]) for key in depth_time2.keys()] #True
    all_depth_sum_true = []
    all_depth_sum_false = []

    for item in all_depth_true:
        all_depth_sum_true.extend(item)
    for item in all_depth_false:
        all_depth_sum_false.extend(item)

    #Depth CDF, CCDF
    #cdf = CDFPlot()
    #cdf.set_data(all_depth_sum_true, 'True')
    #cdf.set_data(all_depth_sum_false, 'False')
    #cdf.set_legends(['True', 'False'], '')
    #cdf.save_image('Image/depth_cdf.png')

    true_cascade = []
    false_cascade = []
    for postid in cascade_depth1.keys():
        for depth in cascade_depth1[postid].values(): #origin tweet : depth
            true_cascade.extend(depth)
 
    for postid in cascade_depth2.keys():
        for depth in cascade_depth2[postid].values(): #origin tweet : depth
            false_cascade.extend(depth)
   

    print('true')
    for i in range(1, 15):
        print(i, true_cascade.count(i))
    print('false')
    for i in range(1, 15):
        print(i, false_cascade.count(i))
    
    cdf = CDFPlot()
    cdf.set_legends(['True', 'False'], '')
    cdf.set_xlim(0, 11)
    #cdf.set_log(True)
    #cdf.set_ylog()
    cdf.set_label('Depth', 'CDF')
    cdf.set_data(true_cascade, 'True')
    cdf.set_data(false_cascade, 'False')
    cdf.save_image('Image/depth_cdf.png')



    
if __name__ == "__main__":
    dir_name = 'RetweetNew/'
    files = os.listdir(dir_name)
   
    if len(sys.argv) >= 2:
        update()
        sys.exit()
    draw_graph()
    #tim1e_series('True')
    #update()


