import MySQLdb 
import itertools
import os, sys, json 
import bot_detect as bot 
import numpy as np
import itertools
import outlier
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

def veracity_type(postid):
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
    dir_name = "Retweet/"
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

                if tweet['origin'] != '14294848':
                    continue
                unique_d[postid][tweet['origin_tweet']] = unique_d[postid].get(tweet['origin_tweet'], [])
                unique_d[postid][tweet['origin_tweet']].append(tweet['depth'])

        #count += 1
        #if count > 4 :
        #    break
    return unique_d

def get_depth_time_series(veracity):
    dir_name = "Retweet/"
    files = os.listdir(dir_name)
    unique_d = {}
    count = 0
    depth_time = {}
    depth_user = {}
    cascade_depth_users = {}
    cascade_depth = {}
    userid_cascade= {} #user <-> origin_tweet for cascade depth
    cascade_unique_users = {} #root user
    Bot = bot.load_bot()
    for postid in files:
        if veracity != None:
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
        #new_list = sorted(sort.items(), key=lambda x: x[1])
        new_list = sorted(sort.items(), key=lambda x: x)
        start_time = new_list[0][1]
        sorted_ids = [item[0] for item in new_list]
        cascade_unique_users[postid] = {} 
        unique_users = {}
        max_depth = 0
        cascade_tweet = {}
        cascade_max_depth = {}
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
            #if bot.check_bot(Bot, tweet['origin']) == 1:
            #    continue

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
    
            cascade_unique_users[postid][origin_tweet] = cascade_unique_users[postid].get(origin_tweet, {})
            cascade_unique_users[postid][origin_tweet][tweet['user']] = 1
            cascade_max_depth[origin_tweet] = cascade_max_depth.get(origin_tweet, 0)
            if cascade_max_depth[origin_tweet] < tweet['depth']:
                cascade_max_depth[origin_tweet] = tweet['depth']
                cascade_depth_users[origin_tweet] = cascade_depth_users.get(origin_tweet, {})
                cascade_depth_users[origin_tweet][tweet['depth']] = len(cascade_unique_users[postid][origin_tweet])

            #if origin_tweet == '1008855051895476225':
            #    print(tweet['user'], origin_tweet, len(cascade_unique_users[origin_tweet]))
            #    print(cascade_depth_users[origin_tweet])
            #    from time import sleep
            #    sleep(0.3)
        count += 1
        #if count > 5 :
            #break
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
            time_diff = (times[i] - times[1]).total_seconds() / 60
            if (time_diff) < 0:
                print(key)
                print(times[i], times[i-1])
            times[i] = time_diff
        cascade_depth[key] = times
    #print(cascade_depth)
    return depth_time, depth_user, cascade_depth, userid_cascade, cascade_depth_users

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

def time_to_depth_echo_chamber(filename):
    #get echo chamber cascade only 
    with open(filename, 'r') as f:
        echo_chambers = json.load(f)

    echo_chamber_values = {}
    non_echo_chamber_values = {} 
    for item in ['time_depth', 'user_depth']:
        echo_chamber_values[item] = {}
        non_echo_chamber_values[item] = {}

        for i in range(1,20):
            echo_chamber_values[item][i] = []
            non_echo_chamber_values[item][i] = []
    
    Bot = bot.load_bot()
    echo_chamber_cascade_root = {}
    cascade_veracity = {}
    echo_chamber_users = {}
    #keys = sorted(echo_chambers)
    #keys.reverse()
    #print(keys)
    #print(echo_chambers.keys())
    out = False
    for key in echo_chambers.keys():
        users = echo_chambers[key]

        postids = key.split('_')
        
        #bot check
        for postid in postids:
            for user in users:
                if bot.check_bot(Bot, user) == 0:
                    echo_chamber_users[postid] = echo_chamber_users.get(postid, {})
                    echo_chamber_users[postid][user] = 1

    files = os.listdir('Retweet')
    #for postid in echo_chamber_users.keys():
    for postid in files:

        v = veracity_type(postid).title()
        
        #get origin tweet of echo chamber user 
        with open('Retweet/%s'%postid, 'r') as f:
            tweets = json.load(f)

            for tweet in tweets.values():
                try:
                    if tweet['user'] in echo_chamber_users[postid].keys():
                        echo_chamber_cascade_root[tweet['origin_tweet']] = 1
                except KeyError :
                    pass

                cascade_veracity[tweet['origin_tweet']] = v
                    
    print(set(cascade_veracity.values()))

    if cascade_veracity.values()[0] == 'True':
        print('True')
    elif cascade_veracity.values()[0] == 'False':
        print('False')
    else:
        print('Mixed')
        
    print("echo chamber cascade extraction done")

    _, _, time_depth, _, user_depth = get_depth_time_series(None)    

    print("time series data load done ")
    echo_chamber_cascades = echo_chamber_cascade_root.keys()
    print('echo chamber cascades')
    #print(echo_chamber_cascades)

    e = {}; n = {};
    for item in ['True', 'False', 'Mixed']:
        e[item] = {}
        n[item] = {}
        
        for d_type in ['user_depth', 'time_depth']:
            e[item][d_type] = {}
            n[item][d_type] = {}

            for i in range(1, 20):
                e[item][d_type][i] = []
                n[item][d_type][i] = []

    for key in time_depth.keys():
        v = cascade_veracity[key]
        if v !='True' and  v != 'False':
            v = 'Mixed'

        if key in echo_chamber_cascades:
            for i in range(1, max(time_depth[key].keys())):
                try:
                    echo_chamber_values['time_depth'][i].append(time_depth[key][i])
                    echo_chamber_values['user_depth'][i].append(user_depth[key][i])
                    e[v]['time_depth'][i].append(time_depth[key][i])
                    e[v]['user_depth'][i].append(user_depth[key][i])

                except KeyError:
                    pass
        else:
            for i in range(1, max(time_depth[key].keys())):
                try :
                    non_echo_chamber_values['time_depth'][i].append(time_depth[key][i])
                    non_echo_chamber_values['user_depth'][i].append(user_depth[key][i])
                    n[v]['time_depth'][i].append(time_depth[key][i])
                    n[v]['user_depth'][i].append(user_depth[key][i])

                except KeyError:
                    pass

    draw_time_to_depth_echo_chamber([echo_chamber_values['time_depth'], non_echo_chamber_values['time_depth']], ['Echo Chamber', 'No Echo Chamber'], 'Mean Minutes', 'time_depth_echo_chamber_line')
    draw_time_to_depth_echo_chamber([echo_chamber_values['user_depth'], non_echo_chamber_values['user_depth']], ['Echo Chamber', 'No Echo Chamber'], 'Mean Unique Users', 'user_depth_echo_chamber_line')
    draw_time_to_depth_echo_chamber([e['True']['time_depth'], n['True']['time_depth']], ['Echo Chamber', 'No Echo Chamber'], 'Mean Minutes', 'time_depth_echo_chamber_line_t')
    draw_time_to_depth_echo_chamber([e['False']['time_depth'], n['False']['time_depth']], ['Echo Chamber', 'No Echo Chamber'],'Mean Minutes', 'time_depth_echo_chamber_line_f')
    draw_time_to_depth_echo_chamber([e['Mixed']['time_depth'], n['Mixed']['time_depth']], ['Echo Chamber', 'No Echo Chamber'],'Mean Minutes', 'time_depth_echo_chamber_line_m')
    draw_time_to_depth_echo_chamber([e['True']['user_depth'], n['True']['user_depth']], ['Echo Chamber', 'No Echo Chamber'],'Mean Unique Users', 'user_depth_echo_chamber_line_t')
    draw_time_to_depth_echo_chamber([e['False']['user_depth'], n['False']['user_depth']], ['Echo Chamber', 'No Echo Chamber'],'Mean Unique Users', 'user_depth_echo_chamber_line_f')
    draw_time_to_depth_echo_chamber([e['Mixed']['user_depth'], n['Mixed']['user_depth']], ['Echo Chamber', 'No Echo Chamber'],'Mean Unique Users', 'user_depth_echo_chamber_line_m')

def draw_time_to_depth_echo_chamber(data, legend, data_type, filename):
    x_ticks = np.arange(1,20)
    line = LinePlot()
    line.set_ylog()
    line.set_label('Depth', data_type)
    for item in data:
        yticks = [np.mean(item[depth]) for depth in x_ticks]
        #u_ticks1 = [np.mean(outlier.remove_outlier(item[depth])) for depth in x_ticks]
        line.set_plot_data(yticks, x_ticks)
    line.set_legends(legend)
    line.set_xticks(x_ticks)
    line.save_image('Image/20180919/%s.png'%filename)

def time_to_depth():
    index = filename.replace(".json", "").split('echo_chamber')
    #print(index)
    _, _, time_depth_cascade, user_ids, cascade_depth_users = get_depth_time_series('True')    
    _, _, time_depth_cascade2, user_ids2, cascade_depth_users2 = get_depth_time_series('False')    
    _, _, time_depth_cascade3, user_ids3, cascade_depth_users3 = get_depth_time_series('Mixture,Mostly True,Mostly False')    


    t = {}; e = {}; u_all = {}
    t_td = {}; f_td = {}; m_td = {};
    t_ud = {}; f_ud = {}; m_ud = {};

    for i in range(1,20):
        t[i] = [] 
        e[i] = []
        u_all[i] = []
        t_td[i] = []
        f_td[i] = []
        m_td[i] = []
        t_ud[i] = []
        f_ud[i] = []
        m_ud[i] = []

    for key in time_depth_cascade.keys():
        for i in range(1, max(time_depth_cascade[key].keys())):
            t[i].append(time_depth_cascade[key][i]) # 1 ~ max_depth 
            t_td[i].append(time_depth_cascade[key][i]) # 1 ~ max_depth 
            try:
                u_all[i].append(cascade_depth_users[key][i])
                t_ud[i].append(cascade_depth_users[key][i])
            except KeyError :
                pass 
            
    for key in time_depth_cascade2.keys():
        for i in range(1, max(time_depth_cascade2[key].keys())):
            f_td[i].append(time_depth_cascade2[key][i]) # 1 ~ max_depth 
            try:
                f_ud[i].append(cascade_depth_users2[key][i])
            except KeyError :
                pass 
    for key in time_depth_cascade3.keys():
        for i in range(1, max(time_depth_cascade3[key].keys())):
            m_td[i].append(time_depth_cascade3[key][i]) # 1 ~ max_depth 
            try:
                m_ud[i].append(cascade_depth_users3[key][i])
            except KeyError :
                pass 

    """
    #a = set(itertools.chain(*[item for item in userid_cascade.values()]))
    echo_chamber_cascade_ids = {}
    for key in echo_chambers.keys():
        postids = key.split('_')
        
        if veracity != None:
            if not get_veracity(postids[0], veracity) or not get_veracity(postids[1], veracity):
                continue

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
    """

    x_ticks = np.arange(1,20)
 
    y_ticks1 = [np.mean(t_td[depth]) for depth in x_ticks]
    y_ticks2 = [np.mean(f_td[depth]) for depth in x_ticks]
    y_ticks3 = [np.mean(m_td[depth]) for depth in x_ticks]

    print(y_ticks1)
    print(y_ticks2)
    print(y_ticks3)
   
    y_ticks1 = [np.mean(outlier.remove_outlier(t_td[depth])) for depth in x_ticks]
    y_ticks2 = [np.mean(outlier.remove_outlier(f_td[depth])) for depth in x_ticks]
    y_ticks3 = [np.mean(outlier.remove_outlier(m_td[depth])) for depth in x_ticks]
    print(y_ticks1)
    print(y_ticks2)
    print(y_ticks3)

    line = LinePlot()
    line.set_ylog()
    line.set_label('Depth', 'Mean Minutes')
    line.set_plot_data(y_ticks1, x_ticks)
    line.set_plot_data(y_ticks2, x_ticks)
    line.set_plot_data(y_ticks3, x_ticks)
    line.set_legends(['True', 'False', 'Mixed'])
    line.set_xticks(x_ticks)
    line.save_image('Image/20180919/time_depth_line_echo_chamber_%s_%s.png'%(index[1], veracity))

    #number of users to depth 
    u_ticks1 = [np.mean(t_ud[depth]) for depth in x_ticks]
    u_ticks2 = [np.mean(f_ud[depth]) for depth in x_ticks]
    u_ticks3 = [np.mean(m_ud[depth]) for depth in x_ticks]
    print(u_ticks1)

    line = LinePlot()
    line.set_ylog()
    line.set_label('Depth', 'Mean Unique Users')
    line.set_plot_data(u_ticks1, x_ticks)
    line.set_plot_data(u_ticks2, x_ticks)
    line.set_plot_data(u_ticks3, x_ticks)
    line.set_legends(['True', 'False', 'Mixed'])
    line.set_xticks(x_ticks)
    line.save_image('Image/20180919/user_depth_line_echo_chamber_%s_%s.png'%(index[1], veracity))



def echo_chamber_depth():
    filename = 'Data/echo_chamber2.json'
    time_to_depth_echo_chamber(filename)
    #time_to_depth_echo_chamber(filename, 'True')
    #time_to_depth_echo_chamber(filename, 'False')
    #time_to_depth_echo_chamber(filename, 'Mixture,Mostly True,Mostly False')


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
   # max_depth_per_rumor()
    #time_to()
    #time_to_depth()    
    #time_to_depth_echo_chamber()
    echo_chamber_depth()



