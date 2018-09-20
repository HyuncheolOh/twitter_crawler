import MySQLdb 
import os, sys, json 
import bot_detect as bot 
import numpy as np
import itertools
import dataset_analysis as da
import datetime
import pytz
from dateutil import parser
import draw_tools.cdf_plot as cdf_plot
from draw_tools.line_plot import LinePlot
from draw_tools.cdf_plot import CDFPlot
from draw_tools.scatter_plot import ScatterPlot
from draw_tools.bar_plot import BarPlot

#number of cascade per veraqcity
#true, false, mixed (mixture, mostly true, mostly false)

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def get_tz(fact_checker):
    if fact_checker == 'Kim LaCapria':
        tz = pytz.timezone('America/New_York') #change later
    elif fact_checker == 'Dan MacGuill':
        tz = pytz.timezone('America/New_York') #change later
    else:
        tz = pytz.timezone('America/Los_Angeles') #change later
        
    return tz


def created_time(postid):
    conn, cursor = sql_connect()
    if int(postid) < 100000:
    #factchecking
        sql = """
        SELECT dates
        FROM factchecking_data
        WHERE id = %s
        """

    else:
    #snopes
        sql = """
        SELECT published_date, fact_checker
        FROM snopes_set
        WHERE post_id = %s
        """

    cursor.execute(sql, [postid])
    rs = cursor.fetchall()
    sql_close(cursor, conn)
    tz = pytz.timezone('America/Los_Angeles') #change later
    local_dt = rs[0][0].replace(tzinfo=pytz.utc).astimezone(tz)
    published_time = tz.normalize(local_dt)
    return published_time


def veracity(postid):
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

#correlation with cascade size, numbers, unique users 
def cascade_correlation(v_condition):
    #load data
    dir_name = 'Retweet/'
    files = os.listdir(dir_name)
    cascade_size = []
    cascade_num = []
    unique_users = []
    total_period = []
    ccc = 0
    max_follower_num = [] #max cascade origin's follower count
    all_values = {}
    all_values['False'] = {}
    all_values['True'] = {}
    all_values['Mixture'] = {}
    
    for key in all_values.keys():
        all_values[key]['cascade_size'] = []
        all_values[key]['follower_num'] = []
        all_values[key]['tweet_num'] = []
        all_values[key]['cascade_num'] = []
        all_values[key]['user_num'] = []


    for postid in files:

        #if postid != '153932':
        #    continue
        if not get_veracity(postid, v_condition):
            continue 

        print(postid, veracity(postid))
        published_date = created_time(postid)       
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
        
        #compute all period
        sort = {}
        for tweet in tweets.values():
            sort[tweet['tweet']] = parser.parse(tweet['time'])

        new_list = sorted(sort.items(), key=lambda x: x[1])
        sorted_tweets = [time[0] for time in new_list]
        times = [time[1] for time in new_list]
        period = times[len(times)-1] - times[0]
        #divide by 100 (min)
        #print(period / 100)
        #period = period.total_seconds() / 60
        #bin_minute = period / 100 #change to 24 hours 
        bin_minute = datetime.timedelta(days=1)
        #print(bin_minute)
        bin_count = {}
        for i in range(250):
            bin_count[i] = 0

        start_time = times[0]
        #count number of cascade per bin 
        count = 0
        idx = 0
        max_cascade = 0
        unique_cascade = {}
        unique_user = {}
        tweets_per_day = {} #for max cascade size tweets 

        for tweet in tweets.values():
            if max_cascade < tweet['cascade']:
                max_cascade = tweet['cascade'] 
                max_cascade_user = tweet['origin']
            unique_cascade[tweet['origin_tweet']] = 1
            unique_user[tweet['user']] = 1

        published_index = -1
        print(min(times), max(times), published_date)
        while(True):
            if times[idx] <= start_time + bin_minute * count:
                tweet = tweets[sorted_tweets[idx]]
                if tweet['origin'] == max_cascade_user:
                    bin_count[count] = bin_count.get(count, 0) + 1
                #from time import sleep
                #sleep(1.0)
                idx += 1 
            else:
                count += 1
                
            if published_date < start_time + bin_minute * count and published_index == -1:
                published_index = count
            if idx == len(times):
                break
        if published_index == 0:
            published_index += 1

        print(published_index)
        """
        while(True):
            if times[idx] <= start_time + bin_minute * count:
                bin_count[count] = bin_count.get(count, 0) + 1
                tweet = tweets[sorted_tweets[idx]]
                if max_cascade < tweet['cascade']:
                    max_cascade = tweet['cascade']
                    max_cascade_user = tweet['origin']
                unique_cascade[tweet['origin_tweet']] = 1
                unique_user[tweet['user']] = 1
                idx += 1 
            else:
                count += 1
            if idx == len(times):
                break

        """
        
        bar = BarPlot(1)
        bar.set_data(range(1,251), [bin_count[i] for i in range(250)], '')
        bar.set_axvline(published_index)
        bar.set_x_bins(5)
        labels = []
        for i in range(1, 101):
            if i % 50 == 0:
                labels.extend([get_time_label(bin_minute * i)])
            else:
                labels.extend([''])
        #print(labels)
        bar.set_xticklabels([0,50,100,150,200])
        bar.set_ylog()
        bar.set_ylim(10000)
        bar.set_label('Period', 'Cascade Size')
        #bar.set_xticks([0,50,100,150,200])
        bar.save_image('Image/Cascade/%s/%s'%(veracity(postid).title(), postid))

        #cascade_size[postid] = max_cascade
        #cascade_num[postid] = len(unique_cascade)
        #unique_users[postid] = len(unique_users)
        #total_period[postid] = int(period.total_seconds() / 3600*24)
        #if len(unique_cascade.keys()) > 10000:
        #    print(postid, 'continue')
        #    continue
        cascade_size.append(max_cascade)
        cascade_num.append(len(unique_cascade.keys()))
        unique_users.append(len(unique_user.keys()))
        total_period.append(int(period.total_seconds() / (3600*24)))
        with open('../Data/followers/followers/%s'%max_cascade_user, 'r') as f:
            followers = json.load(f)
        max_follower_num.append(len(followers))
        #print(da.screen_name(max_cascade_user), len(followers))
        v_name = veracity(postid).title()
        if v_name == 'Mostly False' or v_name == 'Mostly True':
            v_name = 'Mixture'
        all_values[v_name]['follower_num'].append(len(followers))
        all_values[v_name]['cascade_size'].append(max_cascade)
        all_values[v_name]['tweet_num'].append(len(tweets))
        all_values[v_name]['cascade_num'].append(len(unique_cascade.keys()))
        all_values[v_name]['user_num'].append(len(unique_user.keys()))

        ccc += 1
        #if ccc > 5:
        #    break
    print('cascade', cascade_size)
    print('period', total_period)
    print('number of cascade', cascade_num)
    print('unique users', unique_users)
    print('max follower num', max_follower_num)
    #correlation with cascade size and period 
    scatter = ScatterPlot()
    scatter.set_label('Period', 'Cascade Size')
    scatter.set_data(total_period, cascade_size)
    scatter.save_image('Image/cascade_period_%s_scatter.png'%v_condition)

    #correlation with cascade size and cascade num
    scatter = ScatterPlot()
    scatter.set_label('Number of Cascade', 'Cascade Size')
    scatter.set_data(cascade_num, cascade_size)
    scatter.save_image('Image/cascade_num_%s_scatter.png'%v_condition)

    #correlation with cascade size and unique users 
    scatter = ScatterPlot()
    scatter.set_label('Number of Users', 'Cascade Size')
    scatter.set_data(unique_users, cascade_size)
    scatter.save_image('Image/cascade_user_%s_scatter.png'%v_condition)

    #correlation with tweet num and cascade num
    scatter = ScatterPlot()
    scatter.set_label('Number of Cascade', 'Number of Tweet')
    scatter.set_log(True)
    scatter.set_ylog()

    legends = []
    for key in all_values:
        item = all_values[key]
        legends.append(key)
        scatter.set_data(item['cascade_num'], item['tweet_num'])
    scatter.set_legends(legends)
    scatter.save_image('Image/cascade_tweet_num_%s_scatter.png'%v_condition)

    #correlation with cascade size and number of followers 
    scatter = ScatterPlot()
    scatter.set_label('Number of Followers', 'Cascade Size')
    scatter.set_log(True)
    scatter.set_ylog()
    scatter.set_ylim(20000)
    scatter.set_xlim(10000000)
    legends = []
    for key in all_values:
        item = all_values[key]
        legends.append(key)
        scatter.set_data(item['follower_num'], item['cascade_size'])
    scatter.set_legends(legends)
    #scatter.set_data(max_follower_num, cascade_size)
    scatter.save_image('Image/cascade_follower_%s_scatter.png'%v_condition)

    #correlation with tweet num and number of followers 
    scatter = ScatterPlot()
    scatter.set_label('Number of Followers', 'Number of Tweet')
    scatter.set_log(True)
    scatter.set_ylog()
    scatter.set_ylim(1000000)
    scatter.set_xlim(10000000)
    legends = []
    for key in all_values:
        item = all_values[key]
        legends.append(key)
        scatter.set_data(item['follower_num'], item['tweet_num'])
    scatter.set_legends(legends)
    #scatter.set_data(max_follower_num, cascade_size)
    scatter.save_image('Image/cascade_tweet_follower_%s_scatter.png'%v_condition)


def get_time_label(time_delta):
    #if time_delta > day then return #d
    if time_delta.total_seconds() > (3600 * 24):
        return '%sd'%(int(time_delta.total_seconds() / (3600 * 24)))
    elif time_delta.total_seconds() > 3600:
    #if time_delta > hour then return #h
        return '%sh'%(int(time_delta.total_seconds() / 3600))
    else:
    #if tiume delta > min then return #m
        return '%sm'%(int(time_delta.total_seconds() / 60))


if __name__ == "__main__":
    #cascade_cdf()
    #cascade_num()
    #cascade_change()
    #cascade_and_depth()
    cascade_correlation('True,False,Mixture,Mostly False,Mostly True')
    #cascade_correlation('True')
    #cascade_correlation('False')
    #cascade_correlation('Mixture,Mostly False,Mostly True')



