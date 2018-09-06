import os, sys, time
import json
import unicodecsv as csv
import pandas as pd
import numpy as np
import fileinput
from tweet_parser.tweet import Tweet
from tweet_parser.tweet_parser_errors import NotATweetError


header = ['id', 'id_str', 'screen_name', 'location', 'description', 'url',
            'followers_count', 'friends_count', 'listed_count', 'created_at',
            'favourites_count', 'verified', 'statuses_count', 'lang', 'status',
            'default_profile','default_profile_image', 'has_extended_profile',
            'name', 'bot']

def createOutput(data):

    d = {}
    for key in header:
        if key == 'status':
            d[key] = ''
        elif key not in data['user'].keys():
            d[key] = ""
        else:
            d[key] = data['user'][key]

    #df = pd.DataFrame(d, columns= header, index=np.arange(1))
    d['bot'] = ''
    #return df
    return d


def convert_json_csv():
    df = pd.DataFrame()
    
    filename = 'Data/Bot_info/'
    
    dir_name = "../Data/"
    
    files = os.listdir('Retweet_New')
    
    for postid in files:
        #if os.path.exists(filename + postid):
        #    continue
        print(postid)
        f = open(filename + postid + '.csv', 'w') 
        cwriter = csv.writer(f, delimiter=',')
        cwriter.writerow(header)
        path = dir_name + postid + '.json'

        
        with open(path, 'r') as f:
            lines = fileinput.FileInput(path)
            
            for line in lines:
                tweet_dict = json.loads(line)
                output = createOutput(tweet_dict)
                cwriter.writerow([output[key] for key in header])

                try:
                    retweet = tweet_dict['retweeted_status']
                    output = createOutput(retweet)
                    cwriter.writerow([output[key] for key in header])
                except KeyError:
                    pass
        #break       
        #postid = postid.replace(".json", "")
        #df.to_csv(filename+postid, encoding='utf-8')
        #df = df.iloc[0:0]
    #df.to_csv(filename + 'bot_user_info.csv', encoding='utf-8', sep='\t')

def load_bot():
    with open('Data/bot.json', 'r') as f:
        bot = json.load(f)
    return bot

def check_bot(Bot, uid):
    try:
        return Bot[uid]
    except KeyError:
        return '0'

def bot_validation():
    filename = 'Data/Bot_info/'
    
    files = os.listdir(filename)

    for postid in files:
        with open(filename + postid, 'r') as f : 
            reader = csv.reader(f)

            for i, row in enumerate(reader):
                if i == 0:
                    continue
                int(row[0])

def bot_patch():
    dir_name = 'Retweet_New/'

    files = os.listdir(dir_name)
    Bot = load_bot()

    for postid in files:
        with open(dir_name + postid) as f:
            tweets = json.load(f)

            for item in tweets.values():
                item['bot'] = check_bot(Bot, item['user'])

        #with open(dir_name + postid) as f:
        #    json.dump(tweets, f)


if __name__ == "__main__":
    #convert_json_csv()
    #bot_validation()
    bot_patch()
