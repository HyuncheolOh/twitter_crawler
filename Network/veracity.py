import MySQLdb 
import os, sys, json 

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
        WHERE id = %s and (veracity = 'True' or veracity = 'False' or veracity = 'Mixture' or veracity = 'Mostly True' or veracity = 'Mostly False')
        """

    else:
    #snopes
        sql = """
        SELECT veracity
        FROM snopes_set
        WHERE post_id = %s and (veracity = 'True' or veracity = 'False' or veracity = 'Mixture' or veracity = 'Mostly True' or veracity = 'Mostly False')
        """
    cursor.execute(sql, [postid])
    rs = cursor.fetchall()
    sql_close(cursor, conn)

    if len(rs) == 0:
        return False
    else:
        return True

def check(postid):
    return get_veracity(postid)

if __name__ == "__main__":
    files = os.listdir('Retweet')

    all_list = [check(postid) for postid in files]
    print(len(all_list))
    print(all_list.count(True), all_list.count(False))

