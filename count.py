import json
import os
import sys
from tweet_parser.tweet import Tweet
from tweet_parser.tweet_parser_errors import NotATweetError
from cdf_plot import CDFPlot
import fileinput


if __name__ == "__main__":

    # folder check 

    # read file 
    '''
    dirname = './Data/'
    files = os.listdir(dirname)
    count_list = []
    #tweet count
    for file_name in files:
        if file_name == 'followers' or file_name == 'friends':
            continue
        #read json and count len 
        path = os.path.join(dirname, file_name)
        count = 0
        for line in fileinput.FileInput(path):
            count += 1
            try:
                tweet_dict = json.loads(line)
                tweet = Tweet(tweet_dict)
            except (json.JSONDecodeError, NotATweetError):
                pass
            """ 
            try:
                print(tweet.created_at_string, tweet.text)
            except KeyError as e:
                print(tweet)
            """
        count_list.append(count)

    Cdf = CDFPlot()
    Cdf.set_label('# tweets', 'CDF')
    Cdf.set_log(True)
    Cdf.set_data(count_list, '')
    Cdf.save_image('./cdf.png')
    '''

    #follower count
    follower_path = './Data/followers/list.json'
    follower_json = json.load(open(follower_path))
    
    #friends count
    friends_path = './Data/friends/list.json'
    friends_json = json.load(open(friends_path))

    Cdf = CDFPlot()
    Cdf.set_label('','')
    Cdf.set_log(True)
    Cdf.set_data(follower_json.values(), '')
    Cdf.set_data(friends_json.values(), 'friends')
    Cdf.set_legends(['# followers', '# friends'])
    Cdf.save_image('./follower_cdf.png')

        
    Cdf = CDFPlot()
    Cdf.set_label('# friends', 'CDF')
    Cdf.set_log(True)
    Cdf.set_data(friends_json.values(), '')
    Cdf.save_image('./friends_cdf.png')


