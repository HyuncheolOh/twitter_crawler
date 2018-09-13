import MySQLdb 
import os, sys, json 
import bot_detect as bot 
import numpy as np
import itertools
from dateutil import parser
import draw_tools.cdf_plot as cdf_plot
from draw_tools.line_plot import LinePlot
from draw_tools.cdf_plot import CDFPlot
from draw_tools.scatter_plot import ScatterPlot

#number of cascade per veraqcity
#true, false, mixed (mixture, mostly true, mostly false)

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


def get_cascades(veracity):
    dir_name = "RetweetNew/"
    files = os.listdir(dir_name)
    unique_c = {}
    for postid in files:
        if not get_veracity(postid,  veracity):
            continue
        ##print(postid, veracity)
        unique_c[postid] = {}
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
            
            for tweet in tweets.values():
                unique_c[postid][tweet['origin_tweet']] = tweet['cascade']
                #combine depth and cascade
    return unique_c

def get_depth_cascade(keys, users):
    dir_name = "RetweetNew/"
    #files = os.listdir(dir_name)
    unique_c = {}
    files = keys.split('_')
    echo_users = {}
    for postid in files:
        ##print(postid, veracity)
        unique_c[postid] = {}
        echo_users[postid] = {}
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
            
            for tweet in tweets.values():
                #combine depth and cascade
                if unique_c[postid].get(tweet['origin_tweet'], -1) == -1:
                    unique_c[postid][tweet['origin_tweet']] = {'cascade': tweet['cascade'], 'max_depth' : tweet['depth']}
                else :
                    if unique_c[postid][tweet['origin_tweet']]['max_depth'] < tweet['depth']:
                        unique_c[postid][tweet['origin_tweet']] = {'cascade': tweet['cascade'], 'max_depth' : tweet['depth']}

                if tweet['user'] in users:
                    echo_users[postid][tweet['origin_tweet']] = 1
                else :
                    echo_users[postid][tweet['origin_tweet']] = 0
    
    return unique_c, echo_users

def get_cascade_time_series(keys, users):
    dir_name = "RetweetNew/"
    files = os.listdir(dir_name)
    unique_d = {}
    count = 0
    cascade_size = {}
    cascade_time = {}
    cascade_user = {}
    files = keys.split('_')
    user_index = {}
    for postid in files:
        #if not get_veracity(postid,  veracity):
        #    continue

        unique_d[postid] = {}
        cascade_time[postid] = []
        user_index[postid] = []
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
        max_cascade = 0
        for i, tid in enumerate(sorted_ids):
            tweet = tweets[tid]
            unique_users[tweet['user']] = 1
            #order by cascade can decrease time 

            #time to get to the cascade in a rumor. not care about which cascade is in 
            c_size = cascade_size.get(tweet['origin_tweet'], 0) + 1
            cascade_size[tweet['origin_tweet']] = c_size
            if max_cascade < c_size:
                max_cascade = c_size
            #    cascade_time[max_cascade] = cascade_time.get(max_cascade, {})
            #    elapsed_time = (new_list[i][1] - start_time).total_seconds() / 60 #min
            #    cascade_time[max_cascade][postid] = elapsed_time
            #    cascade_user[max_cascade] = cascade_user.get(max_cascade, {})
            #    cascade_user[max_cascade][postid] = len(unique_users)
            if tweet['user'] in users:
                user_index[postid].append(i)
            cascade_time[postid].append(max_cascade)
            #time to get to the cascade in a cascade.
        count += 1
        #if count > 10 :
        #    break
    return cascade_time, user_index

def cascade_cdf():
    cascades = get_cascades('True')
    cascades = list(itertools.chain(*[item.values() for item in get_cascades('True').values()]))
    #cascades = list(itertools.chain(*cascades))
    cascades2 = list(itertools.chain(*[item.values() for item in get_cascades('False').values()]))
    cascades3 = list(itertools.chain(*[item.values() for item in get_cascades('Mixture,Mostly False,Mostly True').values()]))
    cdf = CDFPlot()
    cdf.set_label('Cascade Size', 'CDF')
    cdf.set_log(True)
    cdf.set_ylog()
    cdf.set_data(cascades, 'True')
    cdf.set_data(cascades2, 'False')
    cdf.set_data(cascades3, 'Mixed')
    cdf.set_legends(['True', 'False', 'Mixed'], '')
    cdf.save_image('Image/cascades_cdf.png')

#number of cascade per rumor
def cascade_num():
    cascades = [len(item) for item in get_cascades('True').values()]
    #print(cascades)
    cascades2 = [len(item) for item in get_cascades('False').values()]
    cascades3 = [len(item) for item in get_cascades('Mixture,Mostly False,Mostly True').values()]
    print(len(cascades), len(cascades2), len(cascades3))
    cdf_plot.set_label_num(2)
    cdf = CDFPlot()
    #cdf.set_label('Number of Cascades', 'CDF')
    cdf.set_log(True)
    cdf.set_ylog()
    cdf.set_data(cascades, 'True')
    cdf.set_data(cascades2, 'False')
    cdf.set_data(cascades3, 'Mixed')
    cdf.set_legends(['True', 'False', 'Mixed'], '')
    cdf.save_image('Image/cascades_number_cdf.png')


#observe the change of cascade size with emergence of echo chamber users 
def cascade_change():
    
    with open('Data/echo_chamber2.json', 'r') as f:
        echo_chambers = json.load(f)

    count = 0
    for keys in echo_chambers.keys():
        users = echo_chambers[keys]
        cascade_series, user_index = get_cascade_time_series(keys, users)    

        for key in cascade_series.keys():
            cascade = cascade_series[key]
            user = user_index[key]
            line = LinePlot()
            line.set_ylog()
            line.set_label('Cascade', 'User')
            line.set_xlog()
            line.set_axvline(user)
            line.set_plot_data(cascade, np.arange(1, len(cascade) + 1, 1))
            #line.set_plot_data(np.arange(1, len(cascade) + 1, 1), cascade)
            #line.set_hline(user, 0, len(cascade))
            #line.set_legends(['True', 'False', 'Mixed'])
            #line.set_xticks(x_ticks)
            line.save_image('Image/Cascade/cascade_change_line_%s_%s.png'%(keys, key))

        count += 1 
        if count > 10:
            break

#see the relation between depth and cascade and echo chamber users. scatter 
def cascade_and_depth():
    with open('Data/echo_chamber2.json', 'r') as f:
        echo_chambers = json.load(f)

    count = 0
            
    d = []; c = []; u = []
    for keys in echo_chambers.keys():
        users = echo_chambers[keys]

        cascade_series, user_index = get_depth_cascade(keys, users)    
        for key in cascade_series.keys():
            cascade = cascade_series[key]
            user = user_index[key]
            for key in cascade.keys():
                d.append(cascade[key]['max_depth'])
                c.append(cascade[key]['cascade'])
                u.append(user[key])
            #scatter = ScatterPlot()
            #scatter.set_label('Depth', 'Cascade')
            #scatter.set_data(d, c)
            #scatter.save_image('Image/CascadeDepth/depth_cascade_%s_%s.png'%(keys, key))

        count += 1 
        if count > 1000:
            break
    scatter = ScatterPlot()
    scatter.set_label('Depth', 'Cascade')
    scatter.set_ylog()
    scatter.set_data(d, c, u)
    scatter.save_image('Image/CascadeDepth/depth_cascade.png')



if __name__ == "__main__":
    #cascade_cdf()
    #cascade_num()
    #cascade_change()
    cascade_and_depth()



