import json, os, sys
from time import time 
def find_echo_chamber(num):
    #select number of rumors and compare user intersection
    print('find echo chamber %s'%num)
    start_time = time()
    dir_name = 'Retweet_New/'
    files = os.listdir(dir_name)

    users = {}
    for postid in files:

        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
            users[postid] = set([item['user'] for item in tweets.values()])

    #find echo chamber (intersection) between rumor spreaders
    echo_chamber = {}
    for i in range(len(files)):
        names = []
        p1 = files[i]
        names.append(p1)
        
        for j in range(i+1, len(files)):
            p2 = files[j]
            names.append(p2)
            if num == 2:
                echo = users[p1] & users[p2]
                echo_chamber['_'.join(names)] = list(echo)
                names.pop()
                continue
            
            for k in range(j+1, len(files)):
                p3 = files[k]
                names.append(p3)
                if num == 3:
                    echo = users[p1] & users[p2] & users[p3]
                    echo_chamber['_'.join(names)] = list(echo)
                    names.pop()
                    continue
                
                for l in range(k+1, len(files)):
                    p4 = files[l]
                    names.append(p4)
                    if num == 4:
                        echo = users[p1] & users[p2] & users[p3] & users[p4]
                        echo_chamber['_'.join(names)] = list(echo)
                        names.pop()
                        continue
                names.pop()
            names.pop()
        names.pop()

    end_time = time()
    print('%s taken'%(end_time-start_time))
    with open('Data/echo_chamber%s.json'%num, 'w') as f:
        json.dump(echo_chamber, f)




if __name__ == "__main__":
    find_echo_chamber(2)
    find_echo_chamber(3)
    find_echo_chamber(4)
