from __future__ import division
import os, sys, time
import json
import unicodecsv as csv
import pandas as pd
import numpy as np
import bot_detect as bot
from draw_tools.box_plot import BoxPlot

def bot_participation():
    Bot = bot.load_bot()

    dir_name = "RetweetNew/"
    files = os.listdir(dir_name)
    bot_list = []
    for postid in files:
        with open(dir_name + postid, 'r') as f:
            tweets = json.load(f)
        users = [tweet['user'] for tweet in tweets.values()]
        bots = [bot.check_bot(Bot, user) for user in users]
        bot_list.append(bots.count(1)/ bots.count(0))


    box = BoxPlot(1)
    box.set_data(bot_list,'')
    box.set_xticks('bot_ratio')
    box.save_image('Image/bot_ratio_box.png')



if __name__ == "__main__":
    bot_participation()
