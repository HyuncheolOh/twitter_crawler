#group analysis for echo chamber 
import os, json
import numpy as np
import echo_chamber_util as e_util
import bot_detect as bot
from dateutil import parser
from draw_tools.box_plot import BoxPlot
#echo chamber rumor propagation velocity 
#calculate distribution of rumor propagation from parent(echo chamber or not ) to child 

def rumor_propagation_velocity(filename):
    #get all echo chamber users
    #filename = 'Data/echo_chamber2.json'
    Bot = bot.load_bot()
    dirname = 'Retweet/'
    files = os.listdir(dirname)
    
    if filename == None:
        echo_chamber_users = {}
        for postid in files:
            echo_chamber_users[postid] = {}
    else:
        echo_chamber_users = e_util.get_echo_chamber_users(filename)


    echo_v = []
    necho_v = []
        
    for ccc, postid in enumerate(files):
        with open(dirname + postid, 'r') as f:
            tweets = json.load(f)

        #order by timeline 
        sort = {}
        for key in tweets.keys():
            tweet = tweets[key]
            sort[key] = parser.parse(tweet['time'])

        #sort by time
        new_list = sorted(sort.items(), key=lambda x: x[1])
        sorted_ids = [item[0] for item in new_list]

        #make one dictionary parent - children 
        parent_child = {} 
        echo_chamber_parent = {}
        for i, tid in enumerate(sorted_ids):
            tweet = tweets[tid]['tweet']
            parent = tweets[tid]['parent_tweet']
            cascade = tweets[tid]['cascade']
            if cascade < 2:
                continue
 
            #bot filter
            if bot.check_bot(Bot, tweets[tid]['user']) != 0:
                continue 
               
            if tweet != parent: 
                    
                parent_child[parent] = parent_child.get(parent, [])
                #parent comes always earlier then child
                if len(parent_child[parent]) == 0:
                    #add parent time into index 0 
                    parent_child[parent].append(parser.parse(tweets[parent]['time']))
                #time or tweet? 
                
                parent_child[parent].append(new_list[i][1])
            else:
                #root tweet of cascade 
                parent_child[parent] = [new_list[i][1]]
            
            if len(tweets[parent]) != 0:
                #parent is echo chamber or not
                if tweets[tid]['parent'] in echo_chamber_users[postid]:
                    echo_chamber_parent[parent] = 1
        

        #insert time diff from start time 
        parent_child_diff = {}
        for key in parent_child.keys():
            parent_child_diff[key] = []
            times = parent_child[key]
            for i, time in enumerate(times):
                if i == 0 :
                    start_time = time
                    continue
                parent_child_diff[key].append((time-start_time).total_seconds() / 60)

        echo_parent = 0
        necho_parent =0 
        for key in parent_child_diff:
            if key in echo_chamber_parent.keys():
#                print('echo', parent_child_diff[key])
                echo_parent += 1
                if len(parent_child_diff[key]) == 0:
                    continue
                echo_v.append(np.mean(parent_child_diff[key]))
            else:
#                print('non echo', parent_child_diff[key])
                necho_parent += 1
                if len(parent_child_diff[key]) == 0:
                    continue

                necho_v.append(np.mean(parent_child_diff[key]))

        #print(postid, echo_parent, necho_parent)
        #if ccc == 10:
        #    break
        #print(echo_v)
        #print(necho_v)
    #return 0
    #print('echo', echo_v)
    #print('necho', necho_v)
    return echo_v, necho_v

#check the taken time to the specific group (all users in the group)
#taken time from root to a user OR 
#taken time from parent to a user 
def propagation_time_to_group(filename):
    #get all echo chamber users
    #filename = 'Data/echo_chamber2.json'
    Bot = bot.load_bot()
    dirname = 'Retweet/'
    files = os.listdir(dirname)
    
    if filename == None:
        echo_chamber_users = {}
        for postid in files:
            echo_chamber_users[postid] = {}
    else:
        echo_chamber_users = e_util.get_echo_chamber_users(filename)


    echo_p = []; echo_r = [];
    necho_p = []; necho_r = [];
    for ccc, postid in enumerate(files):
        #if postid != '150232' and  postid != '29947':
        #    continue 
        with open(dirname + postid, 'r') as f:
            tweets = json.load(f)

        #order by timeline 
        sort = {}
        for key in tweets.keys():
            tweet = tweets[key]
            sort[key] = parser.parse(tweet['time'])

        #sort by time
        new_list = sorted(sort.items(), key=lambda x: x[1])
        sorted_ids = [item[0] for item in new_list]

        parent_child = {} 
        parent_start = {}
        root_start = {}
        #make one dictionary parent - children 
        echo_chamber_parent = {}
        echo_chamber_root = {}
        echo_chamber_tweet = {}    
        #print('echo_chamber user num ', len(echo_chamber_users[postid]))
        for i, tid in enumerate(sorted_ids):
            tweet = tweets[tid]['tweet']
            parent = tweets[tid]['parent_tweet']
            root = tweets[tid]['origin_tweet']
            cascade = tweets[tid]['cascade']
            if cascade < 2:
                continue
 
            #bot filter
            if bot.check_bot(Bot, tweets[tid]['user']) != 0:
                continue 
            
            #save all the parent, root start time 
            
            if root_start.get(root, None) == None:
                root_start[root] = new_list[i][1]

            if parent_start.get(parent, None) == None:
                parent_start[parent] = new_list[i][1]

    
            if tweets[tid]['user'] in echo_chamber_users[postid]:
                echo_chamber_tweet[tid] = 1
            #if tweets[tid]['parent'] in echo_chamber_users[postid]:
            #    echo_chamber_parent[parent] = 1
       
            #if tweets[tid]['origin'] in echo_chamber_users[postid]:
            #    echo_chamber_root[root] = 1


        #parent_child_diff[key].append((time-start_time).total_seconds() / 60)
        echo_parent = 0
        necho_parent =0 
        for tweet in tweets.values():
            tid = tweet['tweet']
            pid = tweet['parent_tweet']
            rid = tweet['origin_tweet']

            #bot filter
            if bot.check_bot(Bot, tweets[tid]['user']) != 0:
                continue 

            if tid != pid:
                #not root 
                r_time = (parser.parse(tweets[tid]['time']) - parser.parse(tweets[rid]['time'])).total_seconds() / 60
                p_time = (parser.parse(tweets[tid]['time']) - parser.parse(tweets[pid]['time'])).total_seconds() / 60
                
                if tweet['parent_tweet'] in echo_chamber_tweet.keys():
                    echo_p.append(p_time)
                else:
                    necho_p.append(p_time)

                if tweet['origin_tweet'] in echo_chamber_tweet.keys():
                    echo_r.append(r_time)
                else:
                    necho_r.append(r_time)

        if ccc % 10 == 0:
            print(ccc)
    return echo_p, necho_p, echo_r, necho_r


def draw_propagation_velocity():
    echo_v2, _ = rumor_propagation_velocity('Data/echo_chamber2.json')
    echo_v3, _ = rumor_propagation_velocity('Data/echo_chamber3.json')
    echo_v4, _ = rumor_propagation_velocity('Data/echo_chamber4.json')
    _, non_echo = rumor_propagation_velocity(None)
    print(len(echo_v2), len(echo_v3), len(echo_v4), len(non_echo))

    box = BoxPlot(1)
    box.set_data([echo_v2, echo_v3, echo_v4, non_echo],'')
    box.set_xticks(['Echo Chamber2', 'Echo Chamber3', 'Echo Chamber4', 'All'])
    box.set_label('', 'Mean Propagation Time')
    box.save_image('Image/20181001/propagation_time.png')

def draw_propagation_time_to_group():
    print('echo chamber 2')
    echo_v2, necho_v2, recho_v2, rnecho_v2 = propagation_time_to_group('Data/echo_chamber2.json')
    box = BoxPlot(1)
    box.set_data([echo_v2, necho_v2],'')
    box.set_xticks(['Echo Chamber', 'Non Echo Chamber'])
    box.set_label('', 'Propagation Time')
    box.save_image('Image/20181001/propagation_time_to_group2.png')

    box = BoxPlot(1)
    box.set_data([recho_v2, rnecho_v2],'')
    box.set_xticks(['Echo Chamber', 'Non Echo Chamber'])
    box.set_label('', 'Propagation Time')
    box.save_image('Image/20181001/propagation_time_to_group_r2.png')

    print('echo chamber 3')
    echo_v3, necho_v3, recho_v3, rnecho_v3 = propagation_time_to_group('Data/echo_chamber3.json')
    box = BoxPlot(1)
    box.set_data([echo_v3, necho_v3],'')
    box.set_xticks(['Echo Chamber', 'Non Echo Chamber'])
    box.set_label('', 'Propagation Time')
    box.save_image('Image/20181001/propagation_time_to_group3.png')

    box = BoxPlot(1)
    box.set_data([recho_v3, rnecho_v3],'')
    box.set_xticks(['Echo Chamber', 'Non Echo Chamber'])
    box.set_label('', 'Propagation Time')
    box.save_image('Image/20181001/propagation_time_to_group_r3.png')

    print('echo chamber 4')
    echo_v4, necho_v4, recho_v4, rnecho_v4= propagation_time_to_group('Data/echo_chamber4.json')
    box = BoxPlot(1)
    box.set_data([echo_v4, necho_v4],'')
    box.set_xticks(['Echo Chamber', 'Non Echo Chamber'])
    box.set_label('', 'Propagation Time')
    box.save_image('Image/20181001/propagation_time_to_group4.png')
 
    box = BoxPlot(1)
    box.set_data([recho_v4, rnecho_v4],'')
    box.set_xticks(['Echo Chamber', 'Non Echo Chamber'])
    box.set_label('', 'Propagation Time')
    box.save_image('Image/20181001/propagation_time_to_group_r4.png')
  
    _, non_echo, _, rnon_echo = propagation_time_to_group(None)
    print(len(echo_v2), len(echo_v3), len(echo_v4), len(non_echo))

    box = BoxPlot(1)
    box.set_data([echo_v2, echo_v3, echo_v4, non_echo],'')
    box.set_xticks(['Echo Chamber2', 'Echo Chamber3', 'Echo Chamber4', 'All'])
    box.set_label('', 'Propagation Time')
    box.save_image('Image/20181001/propagation_time_to_group.png')

    box = BoxPlot(1)
    box.set_data([recho_v2, recho_v3, recho_v4, rnon_echo],'')
    box.set_xticks(['Echo Chamber2', 'Echo Chamber3', 'Echo Chamber4', 'All'])
    box.set_label('', 'Propagation Time')
    box.save_image('Image/20181001/propagation_time_to_group_r.png')

if __name__ == "__main__":
    
    #draw_propagation_velocity()
    draw_propagation_time_to_group()

    #propagation_time_to_group('Data/echo_chamber2.json')

