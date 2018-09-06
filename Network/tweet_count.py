#count information
import MySQLdb 
import os, sys, json 
import bot_detect as bot 
import numpy as np
from dateutil import parser
from operator import itemgetter
from draw_tools.cdf_plot import CDFPlot
from draw_tools.line_plot import LinePlot

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def get_veracity(postid):
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

def tweet_count(veracity):
    tweets_num = []
    for postid in files:
        if veracity != get_veracity(postid):
            continue
        with open(dir_name+postid, 'r') as f:
            tweets = json.load(f)
        tweets_num.append(len(tweets))
    return tweets_num

def count():
    #tweet count
    true = tweet_count('True')
    false = tweet_count('False')

    print('True')
    print(len(true))
    print('False')
    print(len(false))

if __name__ == "__main__":
    dir_name = 'RetweetNew/'
    files = os.listdir(dir_name)
    
    count()
