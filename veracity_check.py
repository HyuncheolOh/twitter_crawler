import MySQLdb 
import json
import codecs
import os


def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

#if veracity is in condition, then return
#true, false, mixture, mostly false, mostly true
def check_veracity(post_id):
    conn, cursor = sql_connect()

    pids = json.load(open('pids.json', 'r'))
    try:
        tweet_num = pids[post_id]
        print("tweet num : %s"%tweet_num)
    except KeyError as e:
        return False

    sql = """
        SELECT veracity
        FROM snopes_set
        WHERE (veracity = "true" or veracity = "false" or veracity = "mixture" or veracity = "mostly false" or veracity = "mostly true") and post_id = %s
        """
        #WHERE (veracity = "true" or veracity = "false") and post_id = %s
    cursor.execute(sql, [post_id])
    rs = cursor.fetchall()

    if len(rs) == 0:
        return False
    else :
        return True

if __name__ == "__main__":
    print(check_veracity("123"))
    print(check_veracity("122922"))




