import MySQLdb 
import os, sys, json
import fileinput
import bot_detect as bot
import unicodecsv as csv
import pandas as pd
import operator as op
import numpy as np
from dateutil import parser
import math
from collections import Counter
from math import log, e

def sql_connect():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="mmlab", db="fake_news", use_unicode=True, charset='utf8')
    cursor = conn.cursor()
    return conn, cursor

def sql_close(cursor, conn):
    cursor.close()
    conn.close()

def is_veracity(postid, veracity):
    conn, cursor = sql_connect()
    if int(postid) < 100000:
    #factchecking
        sql = """
        SELECT veracity
        FROM factchecking_data
        WHERE id = %s and ({0})
        """

    else:
    #snopes
        sql = """
        SELECT veracity
        FROM snopes_set
        WHERE post_id = %s and ({0})
        """

    veracity = veracity.split(',')
    if len(veracity) == 1:
        sql = sql.format("veracity = '%s'"%veracity[0])
    else:
        v_list = ["veracity = '%s'"%item for item in veracity]
        condition = " or ".join(v_list)
        sql = sql.format(condition)
    cursor.execute(sql, [postid])
    rs = cursor.fetchall()
    sql_close(cursor, conn)
    #return rs[0][0]
    if len(rs) == 0:
        return False
    else:
        return True

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

def get_category(postid):
    conn, cursor = sql_connect()
    if int(postid) < 100000:
    #factchecking
        sql = """
        SELECT category
        FROM factchecking_data
        WHERE id = %s
        """

    else:
    #snopes
        sql = """
        SELECT category
        FROM snopes_set
        WHERE post_id = %s
        """

    cursor.execute(sql, [postid])
    rs = cursor.fetchall()
    sql_close(cursor, conn)
    return rs[0][0]

def is_politics(postid):
    category = get_category(postid)

    if category == 'Politics' or category == 'Politicians':
        return True
    else:
        return False

def is_non_politics(postid):
    category = get_category(postid)

    condition = ['Politics', 'Politicians', 'Fauxtography', 'Fake News']
    if category in condition:
        return False
    else:
        return True


#shannon entropy 
def eta(data, unit='natural'):
    base = {
        'shannon' : 2.,
        'natural' : math.exp(1),
        'hartley' : 10.
    }

    if len(data) <= 1:
        return 0

    counts = Counter()

    for d in data:
        counts[d] += 1

    probs = [float(c) / len(data) for c in counts.values()]
    probs = [p for p in probs if p > 0.]

    ent = 0

    for p in probs:
        if p > 0.:
            ent -= p * math.log(p, base[unit])

    return ent
	


def remove_outlier(arr):
    if len(set(arr)) == 1 or len(arr) == 1:
        return arr

    elements = np.array(arr)

    mean = np.mean(elements, axis=0)
    sd = np.std(elements, axis=0)

    final_list = [x for x in arr if (x > mean - 2 * sd)]
    final_list = [x for x in final_list if (x < mean + 2 * sd)]

    return final_list
#combination function
def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, xrange(n, n-r, -1), 1)
    denom = reduce(op.mul, xrange(1, r+1), 1)
    return numer//denom

def gini(x):
# (Warning: This is a concise implementation, but it is O(n**2)
# in time and memory, where n = len(x).  *Don't* pass in huge
# samples!)

# Mean absolute difference
    mad = np.abs(np.subtract.outer(x, x)).mean()
    # Relative mean absolute difference
    rmad = mad/np.mean(x)
    # Gini coefficient
    g = 0.5 * rmad
    return g


def gini2(array):
    """Calculate the Gini coefficient of a numpy array."""
    # based on bottom eq: http://www.statsdirect.com/help/content/image/stat0206_wmf.gif
    # from: http://www.statsdirect.com/help/default.htm#nonparametric_methods/gini.htm
    array = array.flatten() #all values are treated equally, arrays must be 1d
    if np.amin(array) < 0:
        array -= np.amin(array) #values cannot be negative
    array += 0.0000001 #values cannot be 0
    array = np.sort(array) #values must be sorted
    index = np.arange(1,array.shape[0]+1) #index per array element
    n = array.shape[0]#number of array elements
    return ((np.sum((2 * index - n  - 1) * array)) / (n * np.sum(array))) #Gini coefficient
