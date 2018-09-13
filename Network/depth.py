import MySQLdb 
import itertools
import os, sys, json 
import bot_detect as bot 
import numpy as np
import itertools
from dateutil import parser
import draw_tools.cdf_plot as cdf_plot
from draw_tools.cdf_plot import CDFPlot
from draw_tools.line_plot import LinePlot

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def get_veracity(postid, veracity):
    conn, cursor = sql_connect()
    if int(postid) < 100000:
    #factchecking
        sql = """
        SELECT veracity
        FROM factchecking_data
        WHERE id = %s and ({0})
        """

    else:
    #snopes
        sql = """
        SELECT veracity
        FROM snopes_set
        WHERE post_id = %s and ({0})
        """

    veracity = veracity.split(',')
    if len(veracity) == 1:
        sql = sql.format("veracity = '%s'"%veracity[0])
    else:
        v_list = ["veracity = '%s'"%item for item in veracity]
        condition = " or ".join(v_list)
        sql = sql.format(condition)
    cursor.execute(sql, [postid])
    rs = cursor.fetchall()
    sql_close(cursor, conn)
    #return rs[0][0]
    if len(rs) == 0:
        return False
    else:
        return True

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def get_veracity(postid, veracity):
    conn, cursor = sql_connect()
    if int(postid) < 100000:
    #factchecking
        sql = """
        SELECT veracity
        FROM factchecking_data
        WHERE id = %s and ({0})
        """

    else:
    #snopes
        sql = """
        SELECT veracity
        FROM snopes_set
        WHERE post_id = %s and ({0})
        """

    veracity = veracity.split(',')
    if len(veracity) == 1:
        sql = sql.format("veracity = '%s'"%veracity[0])
    else:
        v_list = ["veracity = '%s'"%item for item in veracity]
        condition = " or ".join(v_list)
        sql = sql.format(condition)
    cursor.execute(sql, [postid])
    rs = cursor.fetchall()
    sql_close(cursor, conn)
    #return rs[0][0]
    if len(rs) == 0:
        return False
    else:
        return True


def get_depth(veracity):
    dir_name = "RetweetNew/"
    files = os.listdir(dir_name)
    unique_d = {}
    count = 0
    for postid in files:
        if not get_veracity(postid,  veracity):
            continue
        ##print(postid, veracity)
        unique_d[postid] = {}
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
            
            for tweet in tweets.values():
                #unique_d[postid][tweet['origin_tweet']] = tweet['depth']
                unique_d[postid][tweet['origin_tweet']] = unique_d[postid].get(tweet['origin_tweet'], [])
                unique_d[postid][tweet['origin_tweet']].append(tweet['depth'])

        #count += 1
        #if count > 4 :
        #    break
    return unique_d

def get_depth_time_series(veracity):
    dir_name = "RetweetNew/"
    files = os.listdir(dir_name)
    unique_d = {}
    count = 0
    depth_time = {}
    depth_user = {}
    cascade_depth = {}
    userid_cascade= {} #user <-> origin_tweet for cascade depth
    for postid in files:
        if not get_veracity(postid,  veracity):
            continue
        print(postid)

        unique_d[postid] = {}
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
 
        sort = {}
        for key in tweets.keys():
            tweet = tweets[key]
            sort[key] = parser.parse(tweet['time'])

        #sort by time
        new_list = sorted(sort.items(), key=lambda x: x[1])
        start_time = new_list[0][1]
        sorted_ids = [item[0] for item in new_list]

        unique_users = {}
        max_depth = 0
        cascade_tweet = {}
        for i, tid in enumerate(sorted_ids):
            tweet = tweets[tid]
            unique_users[tweet['user']] = 1
            #order by depth can decrease time 
            #time to get to the depth in a rumor. not care about which cascade is in 
            if max_depth < tweet['depth']:
                max_depth = tweet['depth']
                depth_time[max_depth] = depth_time.get(max_depth, {})
                elapsed_time = (new_list[i][1] - start_time).total_seconds() / 60 #min
                depth_time[max_depth][postid] = elapsed_time
                depth_user[max_depth] = depth_user.get(max_depth, {})
                depth_user[max_depth][postid] = len(unique_users)

            #time to get to the depth in a cascade.
            #depth by cascade
            origin_tweet = tweet['origin_tweet']
            #userid_cascade[tweet['user']] = origin_tweet
            userid_cascade[tweet['user']] = userid_cascade.get(tweet['user'], [])
            userid_cascade[tweet['user']].append(origin_tweet)
            cascade_tweet[origin_tweet] = 1
            t_depth = tweet['depth']
            cascade_depth[origin_tweet] = cascade_depth.get(origin_tweet, {})
            if len(cascade_depth[origin_tweet]) == 0:
                cascade_depth[origin_tweet][t_depth] = new_list[i][1] #depth 1, start time of cascade 

            if cascade_depth[origin_tweet].get(t_depth, -1) == -1:
                cascade_depth[origin_tweet][t_depth] = new_list[i][1]
    
            #print('------')
            #print(set(userid_cascade.values()))
            #a = set(itertools.chain(*[item for item in userid_cascade.values()]))
            #print(set(cascade_depth.keys()))
            #print(userid_cascade)
            #print(len(a), len(set(cascade_depth.keys())))

    
        #calculate time diff in cascade_depth
        for origin_tweet in cascade_tweet.keys():
            times = cascade_depth[origin_tweet]
            depth_all = times.keys()
            max_depth = max(depth_all)
            if max_depth == 1:
                times[1] = 0
            for i in range(max_depth, 0, -1):
                if i == 1:
                    times[i] = 0
                    break
                time_diff = (times[i] - times[i-1]).total_seconds() / 60
                if (time_diff) < 0:
                    print(key, 'depth %s'%i)
                    print(times[i], times[i-1])
                times[i] = time_diff
            cascade_depth[origin_tweet] = times
            count += 1
        #break
        #if count > 2 :
        #    break
    """
    for key in cascade_depth.keys():
        times = cascade_depth[key]
        depth_all = times.keys()
        max_depth = max(depth_all)
        if max_depth == 1:
            times[1] = 0
        for i in range(max_depth, 0, -1):
            if i == 1:
                times[i] = 0
                break
            time_diff = (times[i] - times[i-1]).total_seconds() / 60
            if (time_diff) < 0:
                print(key)
                print(times[i], times[i-1])
            times[i] = time_diff
        cascade_depth[key] = times
    """
    return depth_time, depth_user, cascade_depth, userid_cascade

#depth cdf for every tweet
def depth_cdf():
    depth = get_depth('True')
    depth = list(itertools.chain(*list(itertools.chain(*[item.values() for item in get_depth('True').values()]))))
    #depth = list(itertools.chain(*depth))
    depth2 = list(itertools.chain(*list(itertools.chain(*[item.values() for item in get_depth('False').values()]))))
    depth3 = list(itertools.chain(*list(itertools.chain(*[item.values() for item in get_depth('Mixture,Mostly False,Mostly True').values()]))))
    cdf = CDFPlot()
    cdf.set_label('Depth', 'CDF')
    cdf.set_log(True)
    cdf.set_ylog()
    cdf.set_data(depth, 'True')
    cdf.set_data(depth2, 'False')
    cdf.set_data(depth3, 'Mixed')
    cdf.set_legends(['True', 'False', 'Mixed'], '')
    cdf.save_image('Image/depth_cdf.png')

#max depth per cascade
def max_depth_per_rumor():
    #a = [item.values() for item in depth.values()]
    #print([max(item) for item in a[0]])    
    #print([max(item) for item in [item.values() for item in depth.values()][0]])
    
    depth = []; depth2 = []; depth3 = []
    for item in get_depth('True').values():
        for t in item.values():
            depth.append(max(t))
    
    for item in get_depth('False').values():
        for t in item.values():
            depth2.append(max(t))

    for item in get_depth('Mixture,Mostly False,Mostly True').values():
        for t in item.values():
            depth3.append(max(t))


    #depth = [max(item) for item in [item.values() for item in get_depth('True').values()][0]]
    #depth2 = [max(item) for item in [item.values() for item in get_depth('True').values()][0]]
    #depth2 = [max(t) for t in item.values() for item in get_depth('False').values()]
    #depth3 = [max(item) for item in [item.values() for item in get_depth('Mixture,Mostly False,Mostly True').values()][0]]


    #cdf_plot.set_label_num(3)
    cdf = CDFPlot()
    cdf.set_label('Cascade Max Depth', 'CDF')
    cdf.set_log(True)
    cdf.set_ylog()
    cdf.set_data(depth, 'True')
    cdf.set_data(depth2, 'False')
    cdf.set_data(depth3, 'Mixed')
    cdf.set_legends(['True', 'False', 'Mixed'], '')
    cdf.save_image('Image/depth_per_cascade_cdf.png')
    for i in range(1, 20):
        print(i, depth.count(i), depth2.count(i), depth3.count(i))

def time_to():
    time_depth, user_depth = get_depth_time_series('True')    
    time_depth2, user_depth2 = get_depth_time_series('False')    
    time_depth3, user_depth3 = get_depth_time_series('Mixture,Mostly True,Mostly False')    

    time_to_depth(time_depth, time_depth2, time_depth3)
    user_to_depth(user_depth, user_depth2, user_depth3)

def time_to_depth(time_depth, time_depth2, time_depth3):
    #time_depth = get_depth_time_series('True')    
    #time_depth2 = get_depth_time_series('False')    
    #time_depth3 = get_depth_time_series('Mixture,Mostly True,Mostly False')    

    #mean time to get to depth

    x_ticks1 = time_depth.keys()
    x_ticks2 = time_depth2.keys()
    x_ticks3 = time_depth3.keys()
    y_ticks1 = [np.mean(time_depth[depth].values()) for depth in x_ticks1]
    y_ticks2 = [np.mean(time_depth2[depth].values()) for depth in x_ticks2]
    y_ticks3 = [np.mean(time_depth3[depth].values()) for depth in x_ticks3]
    if len(x_ticks1) > len(x_ticks2) and len(x_ticks1) > len(x_ticks2):
        x_ticks = x_ticks1
    elif len(x_ticks2) > len(x_ticks1) and len(x_ticks2) > len(x_ticks3):
        x_ticks = x_ticks2
    else:
        x_ticks = x_ticks3
    line = LinePlot()
    line.set_ylog()
    line.set_label('Depth', 'Mean Minutes')
    line.set_plot_data(y_ticks1, x_ticks)
    line.set_plot_data(y_ticks2, x_ticks)
    line.set_plot_data(y_ticks3, x_ticks)
    line.set_legends(['True', 'False', 'Mixed'])
    line.set_xticks(x_ticks)
    line.save_image('Image/time_depth_line.png')

def time_to_depth_echo_chamber():
    _, _, time_depth_cascade, user_ids = get_depth_time_series('True,False,Mixture,Mostly True,Mostly False')    

    #get echo chamber cascade only 
    with open('Data/echo_chamber2.json', 'r') as f:
        echo_chambers = json.load(f)

    t = {}
    e = {}
    for i in range(1,15):
        t[i] = []
        e[i] = []

    for times in time_depth_cascade.values():
        for i in range(1, max(times.keys())+1):
            t[i].append(times[i]) # 1 ~ max_depth 
        #break

    #a = set(itertools.chain(*[item for item in userid_cascade.values()]))
    echo_chamber_cascade_ids = {}
    for key in echo_chambers.keys():
        postids = key.split('_')
        for uid in echo_chambers[key]: 
            for item in user_ids[uid]: #all unique root which user participate in 
                echo_chamber_cascade_ids[item] = 1

    echo_time_depth_cascade = {}
    for eid in echo_chamber_cascade_ids: #unique tweetid 
        #print(time_depth_cascade)
        #print(eid)
        #print(time_depth_cascade[eid])
        for times in time_depth_cascade[eid]:
            e[times].append(time_depth_cascade[eid][times])


    #print(e)

    #x_ticks1 = time_depth.keys()
    x_ticks = np.arange(1,15)
    y_ticks2 = [e[depth] for depth in x_ticks]
    y_ticks1 = [np.mean(t[depth]) for depth in x_ticks]
    y_ticks2 = [np.mean(e[depth]) for depth in x_ticks]
    print(y_ticks1)
    #print(y_ticks2)
    line = LinePlot()
    line.set_ylog()
    line.set_label('Depth', 'Mean Minutes')
    line.set_plot_data(y_ticks1, x_ticks)
    line.set_plot_data(y_ticks2, x_ticks)
    line.set_legends(['All', 'Echo chambers'])
    line.set_xticks(x_ticks)
    line.save_image('Image/time_depth_line_echo_chamber.png')


def user_to_depth(user_depth, user_depth2, user_depth3):
    #time_depth = get_depth_time_series('True')    
    #time_depth2 = get_depth_time_series('False')    
    #time_depth3 = get_depth_time_series('Mixture,Mostly True,Mostly False')    

    #mean time to get to depth
    print(user_depth)
    x_ticks = np.arange(0, 20, 1)
    x_ticks1 = user_depth.keys()
    x_ticks2 = user_depth2.keys()
    x_ticks3 = user_depth3.keys()
    y_ticks1 = [np.mean(user_depth[depth].values()) for depth in x_ticks1]
    y_ticks2 = [np.mean(user_depth2[depth].values()) for depth in x_ticks2]
    y_ticks3 = [np.mean(user_depth3[depth].values()) for depth in x_ticks3]
    if len(x_ticks1) > len(x_ticks2) and len(x_ticks1) > len(x_ticks2):
        x_ticks = x_ticks1
    elif len(x_ticks2) > len(x_ticks1) and len(x_ticks2) > len(x_ticks3):
        x_ticks = x_ticks2
    else:
        x_ticks = x_ticks3
    line = LinePlot()
    line.set_ylog()
    line.set_label('Depth', 'Mean Unique Users')
    line.set_plot_data(y_ticks1, x_ticks)
    line.set_plot_data(y_ticks2, x_ticks)
    line.set_plot_data(y_ticks3, x_ticks)
    line.set_legends(['True', 'False', 'Mixed'])
    line.set_xticks(x_ticks)
    line.save_image('Image/user_depth_line.png')


    


if __name__ == "__main__":
    #depth_cdf()
    #max_depth_per_rumor()
    #time_to()
    #time_to_depth()    
    time_to_depth_echo_chamber()



