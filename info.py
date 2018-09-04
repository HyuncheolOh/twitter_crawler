import MySQLdb
import json
import os
import sys
from tweet_parser.tweet import Tweet
from tweet_parser.tweet_parser_errors import NotATweetError
from cdf_plot import CDFPlot
import fileinput

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()


def get_info(post_id):
    conn, cursor = sql_connect()

    sql = """
        SELECT category, title, veracity
        FROM snopes_set
        WHERE post_id = %s and (veracity = 'true' or veracity = 'false' or veracity = 'mixture')
        """
    cursor.execute(sql, [post_id])
    rs = cursor.fetchall()
    if len(rs) == 0:
        return None

    d = {}
    for item in rs:
        d['category'] = item[0]
        d['title'] = item[1]

    sql_close(cursor, conn)

    return d

if __name__ == "__main__":

    dirname = './Data/'
    files = os.listdir(dirname)
    count_list = []
    #tweet count
    for file_name in files:
        if file_name == 'followers' or file_name == 'friends':
            continue
        #read json and count len
        print(file_name)
        path = os.path.join(dirname, file_name)
        post_id = file_name.replace(".json", "")
        d = get_info(post_id)
        if d == None:
            continue
        count = 0
        for line in fileinput.FileInput(path):
            count += 1
            try:
                tweet_dict = json.loads(line)
                tweet = Tweet(tweet_dict)
            except (json.JSONDecodeError, NotATweetError):
                pass
             
            #try:
            #    print(tweet.created_at_string, tweet.text)
            #except KeyError as e:
            #    print(tweet)
        d['count'] = count
        count_list.append(d)
#   print(count_list)
    with open('tweet_data2.json', 'w') as f:
        json.dump(count_list, f)

    # rumor categories and # articles

    # category and tweet count 

    # tweet count and titles 



    # user info



