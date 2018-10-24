import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def draw_plot(x, y, filename):
    df = pd.DataFrame({'User Polarity':x, 'Content Polarity':y })

    height = 10
    ratio = 2
    f = plt.figure(figsize=(height, height))
    gs = plt.GridSpec(ratio + 1, ratio + 1)

    ax_joint = f.add_subplot(gs[1:, :-1])
    ax_marg_x = f.add_subplot(gs[0, :-1], sharex=ax_joint)
    ax_marg_y = f.add_subplot(gs[1:, -1], sharey=ax_joint)

    #set label
    #ax_marg_x.set_xlabel('User Polarity', fontsize = 16)
    #ax_marg_y.set_ylabel('Content Polarity', fontsize = 16)
    ax_joint.set_xlabel('User Polarity', fontsize = 20)
    ax_joint.set_ylabel('Content Polarity', fontsize = 20)

    g = sns.regplot(x="User Polarity", y="Content Polarity", data = df, ax=ax_joint, color='g', label='Echo Chamber')
    g.set(ylim=(0,1))
    g.set(xlim=(0,1))
  
    #f.legend((g1, g2), ('Non Echo Chamber', 'Echo Chamber'))
    sns.kdeplot(df['User Polarity'], ax=ax_marg_x, shade=True, color='g', legend=False)
    sns.kdeplot(df['Content Polarity'], ax=ax_marg_y, shade=True, color='g', vertical=True, legend=False)

    #f = plot.figure
    plt.savefig(filename, bbox_inches='tight')  
    plt.savefig(path + '.eps', bbox_inches='tight')

def draw_echo_plot(x, y, x2, y2, filename):
    x_all = list(x)
    x_all.extend(x2)
    y_all = list(y)
    y_all.extend(y2)
    user_type = ['non echo chamber'] * len(x)
    user_type.extend(['echo chamber'] * len(x2))
    df = pd.DataFrame({'User Polarity':x_all, 'Content Polarity':y_all, 'user type' : user_type})
    df1 = pd.DataFrame({'User Polarity':x, 'Content Polarity':y})
    df2 = pd.DataFrame({'User Polarity':x2, 'Content Polarity':y2})

    height = 10
    ratio = 2
    f = plt.figure(figsize=(height, height))
    gs = plt.GridSpec(ratio + 1, ratio + 1)

    ax_joint = f.add_subplot(gs[1:, :-1])
    ax_marg_x = f.add_subplot(gs[0, :-1], sharex=ax_joint)
    ax_marg_y = f.add_subplot(gs[1:, -1], sharey=ax_joint)

    #set label
    #ax_marg_x.set_xlabel('User Polarity', fontsize = 16)
    #ax_marg_y.set_ylabel('Content Polarity', fontsize = 16)
    ax_joint.set_xlabel('User Polarity', fontsize = 20)
    ax_joint.set_ylabel('Content Polarity', fontsize = 20)

    g = sns.regplot(x="User Polarity", y="Content Polarity", data = df1, ax=ax_joint, color='g', label='Non Echo Chamber')
    g = sns.regplot(x="User Polarity", y="Content Polarity", data = df2, ax=ax_joint, color='b', label='Echo Chamber')
    g.set(ylim=(0,1))
    g.set(xlim=(0,1))
  
    #f.legend((g1, g2), ('Non Echo Chamber', 'Echo Chamber'))
    sns.kdeplot(df1['User Polarity'], ax=ax_marg_x, shade=True, color='g', legend=False)
    sns.kdeplot(df2['User Polarity'], ax=ax_marg_x, shade=True, color='b', legend=False)
    
    sns.kdeplot(df1['Content Polarity'], ax=ax_marg_y, shade=True, color='g', vertical=True, legend=False)
    sns.kdeplot(df2['Content Polarity'], ax=ax_marg_y, shade=True, color='b', vertical=True, legend=False)

    #f = plot.figure
    plt.savefig(filename, bbox_inches='tight')
    plt.savefig(path + '.eps', bbox_inches='tight')
