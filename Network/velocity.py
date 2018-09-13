import MySQLdb 
import os, sys, json 
import bot_detect as bot 
import numpy as np
import itertools
import pytz
from datetime import datetime
from dateutil import parser
import draw_tools.cdf_plot as cdf_plot
from draw_tools.line_plot import LinePlot
from draw_tools.cdf_plot import CDFPlot


#number of velocity per veraqcity
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

def get_tz(fact_checker):
    if fact_checker == 'Kim LaCapria':
        tz = pytz.timezone('America/New_York') #change later
    elif fact_checker == 'Dan MacGuill':
        tz = pytz.timezone('America/New_York') #change later
    else:
        tz = pytz.timezone('America/Los_Angeles') #change later
        
    return tz

def created_time(postid, veracity):
    conn, cursor = sql_connect()
    if int(postid) < 100000:
    #factchecking
        sql = """
        SELECT dates
        FROM factchecking_data
        WHERE id = %s and ({0})
        """

    else:
    #snopes
        sql = """
        SELECT published_date, fact_checker
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
        return None
    else:
        tz = pytz.timezone('America/Los_Angeles') #change later
        local_dt = rs[0][0].replace(tzinfo=pytz.utc).astimezone(tz)
        published_time = tz.normalize(local_dt)
        return published_time

def get_velocity(veracity):
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
                unique_c[postid][tweet['origin_tweet']] = tweet['velocity']
    print(len(unique_c))
    return unique_c


def get_velocity_time_series(keys, users, veracity):
    dir_name = "RetweetNew/"
    files = os.listdir(dir_name)
    unique_d = {}
    count = 0
    velocity_size = {}
    velocity_time = {}
    velocity_user = {}
    files = keys.split('_')
    user_index = {}
    published_index = {}
    for postid in files:
        print(postid)
        published_time = created_time(postid,  veracity)
        
        print("Published date", published_time)
        unique_d[postid] = {}
        velocity_time[postid] = []
        user_index[postid] = []
        published_index[postid] = -1
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
 
        sort = {}
        for key in tweets.keys():
            tweet = tweets[key]
            sort[key] = parser.parse(tweet['time'])

        #sort by time
        new_list = sorted(sort.items(), key=lambda x: x[1])
        #start_time = new_list[0][1]
        sorted_ids = [item[0] for item in new_list]

        unique_users = {}
        max_velocity = 0
        for i, tid in enumerate(sorted_ids):
            if i == 0 :
                continue
            tweet = tweets[tid]
            unique_users[tweet['user']] = 1
            #order by velocity can decrease time 

            #time to get to the velocity in a rumor. not care about which velocity is in 
            c_size = velocity_size.get(tweet['origin_tweet'], 0) + 1
            
            elapsed_time = (new_list[i][1] - new_list[i-1][1]).total_seconds() / 60 #min
            velocity_time[postid].append(elapsed_time)
            #time to get to the velocity in a velocity.
            if tweet['user'] in users:
                user_index[postid].append(i)
            #print(new_list[i][1])        
            if published_time < new_list[i][1] and published_index[postid] == -1:
                published_index[postid] = i

        count += 1
        #if count > 10 :
        #    break
    return velocity_time, user_index, published_index

#observe the change of velocity size with emergence of echo chamber users 
def velocity_change():
    
    with open('Data/echo_chamber2.json', 'r') as f:
        echo_chambers = json.load(f)

    count = 0
    for keys in echo_chambers.keys():
        users = echo_chambers[keys]
        velocity_series, user_index, published_index = get_velocity_time_series(keys, users, 'True,False,Mixture,Mostly False,Mostly True')    

        for key in velocity_series.keys():
            velocity = velocity_series[key]
            user = user_index[key]
            published_date = published_index[key]
            line = LinePlot()
            line.set_ylog()
            line.set_label('User', 'Time Diff')
            line.set_axvline(user, published_date)
            line.set_plot_data(velocity, np.arange(1, len(velocity) + 1, 1))
            #line.set_plot_data(np.arange(1, len(velocity) + 1, 1), velocity)
            #line.set_hline(user, 0, len(velocity))
            #line.set_legends(['True', 'False', 'Mixed'])
            #line.set_xticks(x_ticks)
            line.save_image('Image/Velocity/velocity_change_line_%s_%s.png'%(keys, key))

        count += 1 
        if count > 100:
            break
if __name__ == "__main__":
    #velocity_cdf()
    #velocity_num()
    velocity_change()



