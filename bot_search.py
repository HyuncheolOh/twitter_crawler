import sys, os, json, csv
import botometer
import botornot
from time import time
from random import shuffle
token_list = []
def load_key_list():
    with open('key.csv', 'r') as csvfile:
        keyread = csv.reader(csvfile, delimiter=',')
        for row in keyread:
            token = []
            if 'consumer' not in row[0]:
                token.append(row[0])
                token.append(row[1])
                token.append(row[2])
                token.append(row[3])
                token_list.append(token)


def search_bot():
    token = token_list[key_num]
    mashape_key = "u1kNOtrKczmshxJRKCPky57YO3Tpp12IfbqjsnN1R7EOzZ6w7o"
    twitter_app_auth = {
                'consumer_key': token[0],
                'consumer_secret': token[1],
                'access_token': token[2],
                'access_token_secret': token[3],
    }
    bom = botometer.Botometer(wait_on_ratelimit=True,
                              mashape_key=mashape_key,
                              **twitter_app_auth)

    #result = bom.check_account('@TBTimes_Opinion')
    #print(result)

    files = os.listdir('Timeline')
    print('all files ', len(files))
    shuffle(files)
    isbot = lambda x : 1 if x >= 0.5 else 0
    for userid in files:
        try:
            if os.path.exists('BotResult/'+userid):
                continue
            result = bom.check_account(userid)
            f = open('BotResult/' + userid, 'w')
            bot_result = isbot(result['scores']['universal'])
            json.dump(bot_result, f)
            print(userid, bot_result)
            f.close()
        except BaseException as e:
            print(e)
            f = open('BotResult/' + userid, 'w')
            json.dump(1, f)
            f.close()

    """
    all_users = {}    
    count =0 
    for userid, result in bom.check_accounts_in(files):
        try:
            print(count, userid, result['scores']['universal'])
            all_users[userid] = f(result['scores']['universal'])
        except KeyError as e:
            print(result, e)

        count += 1
    
    with open('botornot.json', 'w') as f:
        json.dump(all_users, f)
    # Check a single account by id
    #result = bom.check_account(1548959833)
    """
# Check a sequence of accounts
    #accounts = ['@clayadavis', '@onurvarol', '@jabawack', '@TBTimes_Opinion']
    #for screen_name, result in bom.check_accounts_in(accounts):
            # Do stuff with `screen_name` and `result`
    #    print(screen_name, result)

def botornot_search():
    token = token_list[key_num]
    twitter_app_auth = {
                'consumer_key': token[0],
                'consumer_secret': token[1],
                'access_token': token[2],
                'access_token_secret': token[3],
    }
    
    bon = botornot.BotOrNot(**twitter_app_auth)
    start = time()
    #bon.check_account('@TBTimes_Opinion')
    bon.check_account('@clayadavis')
    end = time()
    print('%s takes'%(end-start))


if __name__ == '__main__':
    #get folders
    key_num = 3
    if len(sys.argv) >=2:
        key_num = int(sys.argv[1])
    print(key_num)

    load_key_list()
    search_bot()
    #botornot_search()

