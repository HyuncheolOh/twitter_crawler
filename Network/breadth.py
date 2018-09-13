import MySQLdb 
import os, sys, json 
import bot_detect as bot 
import numpy as np
import itertools
from dateutil import parser
import draw_tools.cdf_plot as cdf_plot
from draw_tools.line_plot import LinePlot
from draw_tools.cdf_plot import CDFPlot

def get_breadth_time_series(keys, users):
    dir_name = "RetweetNew/"
    files = os.listdir(dir_name)
    unique_d = {}
    count = 0
    breadth_size = {}
    breadth_time = {}
    breadth_user = {}
    files = keys.split('_')
    user_index = {}
    for postid in files:
        #if not get_veracity(postid,  veracity):
        #    continue

        unique_d[postid] = {}
        breadth_time[postid] = []
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

        breadth_size[postid] = {}
        unique_users = {}
        max_breadth = 0
        for i, tid in enumerate(sorted_ids):
            tweet = tweets[tid]
            unique_users[tweet['user']] = 1
            #order by breadth can decrease time 

            #time to get to the breadth in a rumor. not care about which breadth is in 
            b_size = breadth_size[postid].get(tweet['depth'], 0) + 1
            breadth_size[postid][tweet['depth']] = b_size
            print(tweet['user'], tweet['depth'])
            if max_breadth < b_size:
                max_breadth = b_size
            #    breadth_time[max_breadth] = breadth_time.get(max_breadth, {})
            #    elapsed_time = (new_list[i][1] - start_time).total_seconds() / 60 #min
            #    breadth_time[max_breadth][postid] = elapsed_time
            #    breadth_user[max_breadth] = breadth_user.get(max_breadth, {})
            #    breadth_user[max_breadth][postid] = len(unique_users)
            if tweet['user'] in users:
                user_index[postid].append(i)
            breadth_time[postid].append(max_breadth)
            #time to get to the breadth in a breadth.
        count += 1
        #if count > 10 :
        #    break
    return breadth_time, user_index
#observe the change of breadth size with emergence of echo chamber users 
def breadth_change():
    
    with open('Data/echo_chamber2.json', 'r') as f:
        echo_chambers = json.load(f)

    count = 0
    for keys in echo_chambers.keys():
        users = echo_chambers[keys]
        breadth_series, user_index = get_breadth_time_series(keys, users)    

        for key in breadth_series.keys():
            breadth = breadth_series[key]
            user = user_index[key]
            line = LinePlot()
            #line.set_ylog()
            line.set_label('Users', 'Breadth')
            line.set_plot_data(breadth, np.arange(1, len(breadth) + 1, 1))
            line.set_axvline(user)
            #line.set_legends(['True', 'False', 'Mixed'])
            #line.set_xticks(x_ticks)
            line.save_image('Image/Breadth/breadth_change_line_%s_%s.png'%(keys, key))

        count += 1 
        if count > 0:
            break

if __name__ == "__main__":
    #breadth_cdf()
    #breadth_num()
    breadth_change()



