import MySQLdb 
import json
import codecs
import os
import tweet_factchecking_search 
import tweepy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def data_trim(data):
    data = data.replace('"', '\\"')
    return data

def call_script(words, post_id):
    query = ''
    for item in words:
        if "'" in item or "`" in item or ")" in item or "(" in item or "&" in item:
            continue
        query += item + ','
    query = query[:-1]
    tweet_factchecking_search.search(post_id, query)



if __name__ == '__main__':
    import sys
    conn, cursor, = sql_connect()

    sql = """
        SELECT id, title
        FROM factchecking_data
        WHERE dates >= '2018-07-01'
        """
    cursor.execute(sql)
    rs = cursor.fetchall()
    
    
    for i, item in enumerate(rs):
        post_id, title, = item
        #check folder already exists
        #if os.path.exists('./Data/'+post_id) == True:
        #    continue

        tokenizer = RegexpTokenizer(r'\w+')
        word_tokens = tokenizer.tokenize(title.lower())
        
        #stopwords remove
        stop_words = set(stopwords.words('english'))
        word_tokens = [w for w in word_tokens if not w in stop_words]
        
        if len(word_tokens) <= 3:
            continue
            
        print("##################", post_id, title, "###################")       

        call_script(word_tokens, post_id)
    sql_close(cursor, conn)



