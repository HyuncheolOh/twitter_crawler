import MySQLdb 
import itertools
import os, sys, json 
import bot_detect as bot 
import numpy as np
import itertools
import echo_chamber_util as e_util
import util
import pandas as pd
from dateutil import parser
import draw_tools.cdf_plot as cdf_plot
from draw_tools.cdf_plot import CDFPlot
from draw_tools.ccdf_plot import CCDFPlot
from draw_tools.line_plot import LinePlot
from draw_tools.box_plot import BoxPlot
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
 
#remove or not? 
def time_to_depth():
    #index = filename.replace(".json", "").split('echo_chamber')
    #print(index)
    _, _, time_depth_cascade, user_ids, cascade_depth_users = get_depth_time_series('True')    
    _, _, time_depth_cascade2, user_ids2, cascade_depth_users2 = get_depth_time_series('False')    
    _, _, time_depth_cascade3, user_ids3, cascade_depth_users3 = get_depth_time_series('Mixture,Mostly True,Mostly False')    


    t = {}; e = {}; u_all = {}
    #true, false, mixture time to depth
    t_td = {}; f_td = {}; m_td = {};
    #true, false, mixture user to depth
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

    x_ticks = np.arange(1,20)
    """
    depth_list = []
    veracity_list = []
    time_list = []
    for depth in x_ticks:
        for value in t_td[depth]:
            depth_list.append(depth)
            time_list.append(value)
            veracity_list.append('True')
        
        for value in f_td[depth]:
            depth_list.append(depth)
            time_list.append(value)
            veracity_list.append('False')

        for value in m_td[depth]:
            depth_list.append(depth)
            time_list.append(value)
            veracity_list.append('Mixed')

    df = pd.DataFrame({'time':time_list, 'depth':depth_list, 'type':veracity_list}) 
    line = LinePlot()
    line.set_sns_plot(df)
    """
    y_ticks1 = [np.median(t_td[depth]) for depth in x_ticks]
    y_ticks2 = [np.median(f_td[depth]) for depth in x_ticks]
    y_ticks3 = [np.median(m_td[depth]) for depth in x_ticks]

    print(y_ticks1)
    print(y_ticks2)
    print(y_ticks3)
   
    line = LinePlot()
    line.set_ylog()
    line.set_label('Depth', 'Median Minutes')
    line.set_plot_data(y_ticks1, x_ticks)
    line.set_plot_data(y_ticks2, x_ticks)
    line.set_plot_data(y_ticks3, x_ticks)
    line.set_legends(['True', 'False', 'Mixed'])
    line.set_xticks(x_ticks)
    line.save_image('%s/time_depth_line_echo_chamber.png'%(foldername))
    
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
    line.save_image('%s/user_depth_line_echo_chamber.png'%(foldername))


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

def get_depth(politic=None, veracity=None, echo_chamber=False):
    print(politic, veracity, echo_chamber)
    dir_name = "RetweetNew/"
    files = os.listdir(dir_name)
    unique_d = {}
    count = 0
    if echo_chamber == True:
        echo_chamber_users = e_util.get_echo_chamber_users('Data/echo_chamber2.json')
        e_d = {}
        ne_d = {}

    breadth, depth, unique_users = e_util.get_cascade_max_breadth()
    for postid in files:
        if veracity != None:
            if not get_veracity(postid,  veracity):
                continue
        ##print(postid, veracity)

        if politic == True:
            if util.is_politics(postid) == False:
                continue

        if politic == False:
            if util.is_non_politics(postid) == False:
                continue

        echo_chamber_cascade_root = {}
        unique_root = {}
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
                    
        
            for tweet in tweets.values():
                
                if tweet['user'] in echo_chamber_users[postid].keys():
                    echo_chamber_cascade_root[tweet['origin_tweet']] = 1

                unique_root[tweet['origin_tweet']] = 1
                #unique_d[postid][tweet['origin_tweet']] = tweet['depth']

            print(len(unique_root), len(echo_chamber_cascade_root))
            echo_chamber_cascades = echo_chamber_cascade_root.keys()
            for key in unique_root.keys():
                unique_d[key] = depth[key]

                if key in echo_chamber_cascades:        
                    e_d[key] = depth[key]
                else:
                    ne_d[key] = depth[key]
                    
        #count += 1
        #if count > 4 :
        #    break

    return unique_d, e_d, ne_d


#depth cdf for every tweet
def depth_cdf():
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

def depth_politics_cdf():
    depth, echo_depth, necho_depth = get_depth(politic=True, veracity='False', echo_chamber=True)
    depth2, echo_depth2, necho_depth2 = get_depth(politic=False, veracity='False', echo_chamber=True)

    """
    depth = list(itertools.chain(*list(itertools.chain(*[item.values() for item in depth.values()]))))
    echo_depth = list(itertools.chain(*list(itertools.chain(*[item.values() for item in echo_depth.values()]))))
    necho_depth = list(itertools.chain(*list(itertools.chain(*[item.values() for item in necho_depth.values()]))))

    depth2 = list(itertools.chain(*list(itertools.chain(*[item.values() for item in depth2.values()]))))
    echo_depth2 = list(itertools.chain(*list(itertools.chain(*[item.values() for item in echo_depth2.values()]))))
    necho_depth2 = list(itertools.chain(*list(itertools.chain(*[item.values() for item in necho_depth2.values()]))))
    """
    depth = depth.values()
    echo_depth = echo_depth.values()
    necho_depth = necho_depth.values()

    depth2 = depth2.values()
    echo_depth2 = echo_depth2.values()
    necho_depth2 = necho_depth2.values()

    #print(depth)
    cdf = CDFPlot()
    cdf.set_label('Depth', 'CDF')
    cdf.set_data(depth, 'Politics')
    cdf.set_data(depth2, 'Other')
    cdf.set_legends(['Politics', 'Other'], 'Category')
    cdf.save_image('Image/20181002/depth_cdf.png')

    cdf = CDFPlot()
    cdf.set_label('Depth', 'CDF')
    cdf.set_data(echo_depth, 'Echo Chamber')
    cdf.set_data(necho_depth, 'Non Echo Chamber')
    cdf.set_title('Politics')
    cdf.set_legends(['Echo Chamber', 'Non Echo Chamber'], 'User Type')
    cdf.save_image('Image/20181002/echo_depth_cdf.png')

    cdf = CDFPlot()
    cdf.set_label('Depth', 'CDF')
    cdf.set_data(echo_depth2, 'Echo Chamber')
    cdf.set_data(necho_depth2, 'Non Echo Chamber')
    cdf.set_title('Non Politics')
    cdf.set_legends(['Echo Chamber', 'Non Echo Chamber'], 'User Type')
    cdf.save_image('Image/20181002/echo_depth_cdf2.png')

    cdf = CCDFPlot()
    cdf.set_label('Depth', 'CCDF')
    #cdf.set_log(True)
    #cdf.set_ylog()
    cdf.set_data(depth)
    cdf.set_data(depth2)
    cdf.set_legends(['Politics', 'Other'], 'Category')
    cdf.save_image('Image/20181002/depth_ccdf.png')
  
def get_depth_time_series(veracity):
    dir_name = "RetweetNew/"
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
        #if postid != '126119':
        #    continue
        if veracity != None:
            if not get_veracity(postid,  veracity):
                continue

        #print(postid)
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

            #if origin_tweet != '1018876220480606208':
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

                #if tweet['depth'] == 17:
                #    print(postid, origin_tweet, 17)
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
    #print(cascade_depth)
    #depth_time, depth_user - time or user to depth of rumor 
    #cascade_depth, cascade_depth_users - time or user to depth of cascade 
    return depth_time, depth_user, cascade_depth, userid_cascade, cascade_depth_users

def time_to_depth_echo_chamber(filename):
    
    _, _, time_depth, _, user_depth = get_depth_time_series(None)    
    print(len(time_depth))
    #with open('Data/time_series_data.json', 'w') as f:
    #    json.dump({'time_depth' : time_depth, 'user_depth' : user_depth}, f)
    #with open('Data/time_series_data.json', 'r') as f:
    #    data = json.load(f)

    #time_depth = data['time_depth']
    #user_depth = data['user_depth']

    print("time series data load done ")
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
    echo_chamber_users = e_util.get_echo_chamber_users(filename)
   
    files = os.listdir('RetweetNew')
    #collect echo chamber user participate cascade 
    #for postid in echo_chamber_users.keys():
    for postid in files:
        v = veracity_type(postid).title()
        
        #get origin tweet of echo chamber user 
        with open('RetweetNew/%s'%postid, 'r') as f:
            tweets = json.load(f)

            for tweet in tweets.values():
                try:
                    #if tweet['user'] in echo_chamber_users[postid].keys():
                    origin = tweet['origin']
                    otid = tweet['origin_tweet']
                    #if origin in echo_chamber_users[postid].keys():
                    if tweet['user'] in echo_chamber_users[postid].keys():
                        echo_chamber_cascade_root[tweet['origin_tweet']] = 1
                except KeyError :
                    pass

                cascade_veracity[tweet['origin_tweet']] = v
    
    print("echo chamber cascade extraction done")

    echo_chamber_cascades = echo_chamber_cascade_root.keys()

    print('echo chamber cascades')
    #print(echo_chamber_cascades)

    e = {};  n = {}; r = {}; #echo, non echo, ranked echo 
    for item in ['True', 'False', 'Mixed']:
        e[item] = {}
        n[item] = {}
        r[item] = {}
        
        for d_type in ['user_depth', 'time_depth']:
            e[item][d_type] = {}
            n[item][d_type] = {}
            r[item][d_type] = {}

            for i in range(1, 20):
                e[item][d_type][i] = []
                n[item][d_type][i] = []
                r[item][d_type][i] = []

    for key in time_depth.keys():
        v = cascade_veracity[key]
        if v !='True' and  v != 'False':
            v = 'Mixed'

        if key in echo_chamber_cascades:
            #for i in range(1, max(time_depth[key].keys())+1):
            for i in range(1, max(time_depth[key].keys())+1):
                try:
                    echo_chamber_values['time_depth'][i].append(time_depth[key][i])
                    echo_chamber_values['user_depth'][i].append(user_depth[key][i])
                    e[v]['time_depth'][i].append(time_depth[key][i])
                    e[v]['user_depth'][i].append(user_depth[key][i])

                except KeyError:
                    pass
        else:
            for i in range(1, max(time_depth[key].keys())+1):
                try :
                    non_echo_chamber_values['time_depth'][i].append(time_depth[key][i])
                    non_echo_chamber_values['user_depth'][i].append(user_depth[key][i])
                    n[v]['time_depth'][i].append(time_depth[key][i])
                    n[v]['user_depth'][i].append(user_depth[key][i])

                except KeyError:
                    pass

    box = BoxPlot(1)
    box.set_multiple_data([echo_chamber_values['time_depth'], non_echo_chamber_values['time_depth']])
    box.set_ylog()
    box.set_label('Depth', 'Minutes to Depth')
    box.save_image('%s/time_depth_echo_chamber_box.png'%foldername)
    print(echo_chamber_values['time_depth'])    

    #draw time to depth, user to depth of cascade for echo chamber users participated or non echo chamer users participated 
    with open('Data/Figure/5_2_1.json', 'w') as f:
        json.dump([echo_chamber_values['time_depth'], non_echo_chamber_values['time_depth']], f)

    
    draw_time_to_depth_echo_chamber([echo_chamber_values['time_depth'], non_echo_chamber_values['time_depth']], ['echo chamber', 'no echo chamber'], 'median minutes', 'time_depth_echo_chamber_line')
    draw_time_to_depth_echo_chamber([echo_chamber_values['user_depth'], non_echo_chamber_values['user_depth']], ['echo chamber', 'no echo chamber'], 'median unique users', 'user_depth_echo_chamber_line')
    
    with open('Data/Figure/5_2_time.json', 'w') as f:
        json.dump({'e':echo_chamber_values['time_depth'][1], 'ne':non_echo_chamber_values['time_depth'][1]}, f)

    #draw cdf with top retweet 
    cdf = CDFPlot()
    cdf.set_label('Propagation Time', 'CDF')
    cdf.set_log(True)
    #cdf.set_ylog()
    cdf.set_data(echo_chamber_values['time_depth'][1], '')
    cdf.set_data(non_echo_chamber_values['time_depth'][1], '')
    cdf.save_image('Image/20181105/depth_propagation_time_cdf.png')

    """
    draw_time_to_depth_echo_chamber([e['True']['time_depth'], n['True']['time_depth']], ['echo chamber', 'no echo chamber'], 'median minutes', 'time_depth_echo_chamber_line_t')
    draw_time_to_depth_echo_chamber([e['False']['time_depth'], n['False']['time_depth']], ['echo chamber', 'no echo chamber'],'median minutes', 'time_depth_echo_chamber_line_f')
    draw_time_to_depth_echo_chamber([e['Mixed']['time_depth'], n['Mixed']['time_depth']], ['echo chamber', 'no echo chamber'],'median minutes', 'time_depth_echo_chamber_line_m')

    draw_time_to_depth_echo_chamber([e['True']['time_depth'], n['True']['time_depth'], r['True']['time_depth']], ['echo chamber', 'no echo chamber', 'ranked echo chamber'], 'median minutes', 'time_depth_echo_chamber_line_t_ranked')
    draw_time_to_depth_echo_chamber([e['False']['time_depth'], n['False']['time_depth'], r['False']['time_depth']], ['echo chamber', 'no echo chamber', 'ranked echo chamber'],'median minutes', 'time_depth_echo_chamber_line_f_ranked')
    draw_time_to_depth_echo_chamber([e['Mixed']['time_depth'], n['Mixed']['time_depth'], r['Mixed']['time_depth']], ['echo chamber', 'no echo chamber', 'ranked echo chamber'],'median minutes', 'time_depth_echo_chamber_line_m_ranked')

    draw_time_to_depth_echo_chamber([e['True']['user_depth'], n['True']['user_depth']], ['echo chamber', 'no echo chamber'],'median unique users', 'user_depth_echo_chamber_line_t')
    draw_time_to_depth_echo_chamber([e['False']['user_depth'], n['False']['user_depth']], ['echo chamber', 'no echo chamber'],'median unique users', 'user_depth_echo_chamber_line_f')
    draw_time_to_depth_echo_chamber([e['Mixed']['user_depth'], n['Mixed']['user_depth']], ['echo chamber', 'no echo chamber'],'median unique users', 'user_depth_echo_chamber_line_m')
    """
#time, user to depth of political, non political rumors 
def propagation_to_depth_politic(filename):
    #get echo chamber cascade only 
    echo_chamber_values = {}
    non_echo_chamber_values = {} 
    echo_politics = {}; echo_non_politics = {}; non_echo_politics = {}; non_echo_non_politics = {};
    ranked_echo_politics = {}; ranked_echo_non_politics = {}
    politics = {}
    non_politics = {}
    for item in ['time_depth', 'user_depth']:
        echo_chamber_values[item] = {}
        non_echo_chamber_values[item] = {}
        politics[item] = {}
        non_politics[item] = {}
        echo_politics[item] = {}
        echo_non_politics[item] = {}
        non_echo_politics[item] = {}
        non_echo_non_politics[item] = {}
        ranked_echo_politics[item] = {}
        ranked_echo_non_politics[item] = {}


        for i in range(1,20):
            echo_chamber_values[item][i] = []
            non_echo_chamber_values[item][i] = []
            politics[item][i] = []
            non_politics[item][i] = []
            echo_politics[item][i] = []
            echo_non_politics[item][i] = []
            non_echo_politics[item][i] = []
            non_echo_non_politics[item][i] = []
            ranked_echo_politics[item][i] = []
            ranked_echo_non_politics[item][i] = []

   
    echo_chamber_cascade_root = {} #cascade which echo chamber users participated in 
    ranked_echo_chamber_cascade_root = {} #cascade which echo chamber users participated in 
    cascade_veracity = {}
    echo_chamber_users = {}
    politic_cascade = {} #contain cascade root of political rumors
    non_politic_cascade = {}
   
    echo_chamber_users = e_util.get_echo_chamber_users(filename)
    with open('Data/degree_ranked_users.json', 'r') as f:
        ranked_echo_chamber_users = json.load(f)
    print(ranked_echo_chamber_users.keys())

    files = os.listdir('RetweetNew')
    #for postid in echo_chamber_users.keys():
    for postid in files:
        
        #if not get_veracity(postid, 'Mixture,Mostly True,Mostly False'):
        #if not get_veracity(postid, 'False'):
        #    continue

        v = veracity_type(postid).title()
        #get origin tweet of echo chamber user 

        politic_num = 0 
        if util.is_politics(postid):
            politic_num = 1
        elif util.is_non_politics(postid):
            politic_num = 2

        with open('RetweetNew/%s'%postid, 'r') as f:
            tweets = json.load(f)

            for tweet in tweets.values():
                try:
                    if tweet['user'] in echo_chamber_users[postid].keys():
                        echo_chamber_cascade_root[tweet['origin_tweet']] = 1
                except KeyError :
                    pass

                try:
                    if tweet['user'] in ranked_echo_chamber_users[postid].keys():
                        ranked_echo_chamber_cascade_root[tweet['origin_tweet']] = 1
                except KeyError :
                    pass

                cascade_veracity[tweet['origin_tweet']] = v
                if politic_num == 1:
                    politic_cascade[tweet['origin_tweet']] = 1
                elif politic_num ==2 :
                    non_politic_cascade[tweet['origin_tweet']] = 1

    #print(set(cascade_veracity.values()))
    print("echo chamber cascade extraction done")

    _, _, time_depth, _, user_depth = get_depth_time_series('False') 

    print("time series data load done ")
    echo_chamber_cascades = echo_chamber_cascade_root.keys()
    ranked_echo_chamber_cascades = ranked_echo_chamber_cascade_root.keys()

    print(len(ranked_echo_chamber_cascades))
    political_cascades = politic_cascade.keys()
    non_political_cascades = non_politic_cascade.keys()
    #print('echo chamber cascades')
    #print(echo_chamber_cascades)

    for key in time_depth.keys():

        if key in political_cascades:
            #political rumors
            if key in echo_chamber_cascades:
                echo = 1
            else : 
                echo = 0 

            if key in ranked_echo_chamber_cascades:
                ranked = 1
            else:
                ranked = 0
            for i in range(1, max(time_depth[key].keys())):
                try:
                    politics['time_depth'][i].append(time_depth[key][i])
                    politics['user_depth'][i].append(user_depth[key][i])
                    if echo == 1:
                        #echo political
                        echo_politics['time_depth'][i].append(time_depth[key][i])
                        echo_politics['user_depth'][i].append(user_depth[key][i])
                    else: 
                        #non echo political
                        non_echo_politics['time_depth'][i].append(time_depth[key][i])
                        non_echo_politics['user_depth'][i].append(user_depth[key][i])

                    if ranked == 1:
                        #echo political
                        ranked_echo_politics['time_depth'][i].append(time_depth[key][i])
                        ranked_echo_politics['user_depth'][i].append(user_depth[key][i])


                except KeyError :
                    pass

        if key in non_political_cascades:
            if key in echo_chamber_cascades:
                echo = 1
            else : 
                echo = 0 
            if key in ranked_echo_chamber_cascades:
                ranked = 1
                print(222)
            else:
                ranked = 0

            for i in range(1, max(time_depth[key].keys())):
                try:
                    non_politics['time_depth'][i].append(time_depth[key][i])
                    non_politics['user_depth'][i].append(user_depth[key][i])
                   
                    if echo == 1:
                        #echo political
                        echo_non_politics['time_depth'][i].append(time_depth[key][i])
                        echo_non_politics['user_depth'][i].append(user_depth[key][i])
                    else: 
                        #non echo political
                        non_echo_non_politics['time_depth'][i].append(time_depth[key][i])
                        non_echo_non_politics['user_depth'][i].append(user_depth[key][i])

                    if ranked == 1:
                        #echo non political
                        print(222)
                        ranked_echo_non_politics['time_depth'][i].append(time_depth[key][i])
                        ranked_echo_non_politics['user_depth'][i].append(user_depth[key][i])

                except KeyError :
                    pass
       
       
    #draw time to depth, user to depth of cascade for echo chamber users participated or non echo chamer users participated 
    draw_time_to_depth_echo_chamber([politics['time_depth'], non_politics['time_depth']], ['Politics', 'Other'], 'Median Minutes', 'time_depth_politics_line')
    draw_time_to_depth_echo_chamber([politics['user_depth'], non_politics['user_depth']], ['Politics', 'Other'], 'Median Unique Users', 'user_depth_politics_line')
    
    #compare echo chamber users participated cascades and non echo chamber users participated cascades for politics and others 
    draw_time_to_depth_echo_chamber([echo_politics['time_depth'], non_echo_politics['time_depth']], ['Echo Chamber', 'Non Echo Chamber'], 'Median Minutes', 'time_depth_politics_echo_line')
    draw_time_to_depth_echo_chamber([echo_politics['user_depth'], non_echo_politics['user_depth']], ['Echo Chamber', 'Non Echo Chamber'], 'Median Unique Users', 'user_depth_politics_echo_line')
    draw_time_to_depth_echo_chamber([echo_non_politics['time_depth'], non_echo_non_politics['time_depth']], ['Echo Chamber', 'Non Echo Chamber'], 'Median Minutes', 'time_depth_non_politics_echo_line')
    draw_time_to_depth_echo_chamber([echo_non_politics['user_depth'], non_echo_non_politics['user_depth']], ['Echo Chamber', 'Non Echo Chamber'], 'Median Unique Users', 'user_depth_non_politics_echo_line')

    draw_time_to_depth_echo_chamber([echo_politics['time_depth'], non_echo_politics['time_depth'], ranked_echo_politics['time_depth']], ['Echo Chamber', 'Non Echo Chamber', 'Ranked Echo Chamber'], 'Median Minutes', 'time_depth_politics_echo_line_ranked')
    draw_time_to_depth_echo_chamber([echo_non_politics['time_depth'], non_echo_non_politics['time_depth'], ranked_echo_non_politics['time_depth']], ['Echo Chamber', 'Non Echo Chamber', 'Ranked Echo Chamber'], 'Median Minutes', 'time_depth_non_politics_echo_line_ranked')


def draw_time_to_depth_echo_chamber(data, legend, data_type, filename):
    x_ticks = np.arange(1,20)
    line = LinePlot()
    line.set_ylog()
    line.set_label('Depth', data_type)
    for item in data:
        #yticks = [np.mean(item[depth]) for depth in x_ticks]
        yticks = [np.median(item[depth]) for depth in x_ticks]
        #u_ticks1 = [np.mean(outlier.remove_outlier(item[depth])) for depth in x_ticks]
        line.set_plot_data(yticks, x_ticks)
    line.set_legends(legend)
    line.set_xticks(x_ticks)
    line.save_image('%s/%s.png'%(foldername, filename))

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
    foldername = 'Image/20181104'
    if not os.path.exists(foldername):
        os.makedirs(foldername)
    #depth_cdf()
   # max_depth_per_rumor()
    #time_to_depth()    
    #propagation_to_depth_politic('Data/echo_chamber2.json')
    time_to_depth_echo_chamber('Data/echo_chamber2.json')

    #depth_politics_cdf()





