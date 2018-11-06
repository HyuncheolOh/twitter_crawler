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
    plt.savefig(filename + '.eps', bbox_inches='tight', format='eps', dpi=600)

def draw_echo_plot(x, y, x2, y2, filename):
    plt.style.use("ggplot")
    
    x_all = list(x)
    x_all.extend(x2)
    y_all = list(y)
    y_all.extend(y2)
    user_type = ['non echo chamber'] * len(x)
    user_type.extend(['echo chamber'] * len(x2))
    df = pd.DataFrame({'User Polarity':x_all, 'Content Polarity':y_all, 'user type' : user_type})
    df1 = pd.DataFrame({'User Polarity':x, 'Content Polarity':y})
    df2 = pd.DataFrame({'User Polarity':x2, 'Content Polarity':y2})

    c1 = 'g'
    c2 = 'b'
    height = 10
    ratio = 10 
    f = plt.figure(figsize=(height, height))
    gs = plt.GridSpec(ratio + 1, ratio + 1)

    ax_joint = f.add_subplot(gs[3:, :-3])
    ax_marg_x = f.add_subplot(gs[:2, :-3], sharex=ax_joint)
    ax_marg_y = f.add_subplot(gs[3:, -2:], sharey=ax_joint)

    #set label
    ax_marg_x.set_xlabel('User Polarity', fontsize = 16, color='black')
    ax_marg_y.set_ylabel('Content Polarity', fontsize = 16, color='black')
    ax_joint.set_xlabel('User Polarity', fontsize = 20, color='black')
    ax_joint.set_ylabel('Content Polarity', fontsize = 20, color='black')
    ax_joint.set_xticklabels(['', '0.0', '0.2', '0.4', '0.6', '0.8', '1.0'], fontdict={'fontsize':14})
    ax_joint.set_yticklabels(['', '0.0', '0.2', '0.4', '0.6', '0.8', '1.0'], fontdict={'fontsize':14})
    #ax_marg_x.set_xticklabels(['', '0.0', '0.2', '0.4', '0.6', '0.8', '1.0'], fontdict={'fontsize':12})
    #ax_marg_y.set_xticklabels(['', '0.0', '0.2', '0.4', '0.6', '0.8', '1.0'], fontdict={'fontsize':12})

    ax_joint.grid(True)
    g = sns.regplot(x="User Polarity", y="Content Polarity", data = df1, ax=ax_joint, color=c1, scatter_kws={'alpha':0.5}, label='Non-echo chamber')
    g = sns.regplot(x="User Polarity", y="Content Polarity", data = df2, ax=ax_joint, color=c2, scatter_kws={'alpha':0.5}, label='Echo chamber')
    g.set(ylim=(0,1))
    g.set(xlim=(0,1))
    ax_joint.legend(loc=2)
    #ax_marg_y.set_xticks([0,1,2,3,4], [0,1,2,3,4])
    ax_marg_y.set_xticks([0,1,2,3,4,5,6])
    ax_marg_y.set_xticklabels([0,1,2,3,4,5,6]) 
    ax_marg_y.set_xlim(0, 6)
    ax_marg_x.set_ylim(0, 3.5)
    #f.legend((g1, g2), ('Non Echo Chamber', 'Echo Chamber'))
    sns.kdeplot(df1['User Polarity'], ax=ax_marg_x, shade=True, color=c1, legend=False)
    sns.kdeplot(df2['User Polarity'], ax=ax_marg_x, shade=True, color=c2, legend=False)
    
    sns.kdeplot(df1['Content Polarity'], ax=ax_marg_y, shade=True, color=c1, vertical=True, legend=False)
    sns.kdeplot(df2['Content Polarity'], ax=ax_marg_y, shade=True, color=c2, vertical=True, legend=False)

    #f = plot.figure
    plt.savefig(filename, bbox_inches='tight')
    plt.savefig(filename + '.eps', bbox_inches='tight', format='eps')
    plt.savefig(filename + '.pdf', bbox_inches='tight',  dpi=600)
