from __future__ import division
import os, sys, json 
import numpy as np
import draw_tools.pdf as pdf
from draw_tools.cdf_plot import CDFPlot
from draw_tools.ccdf_plot import CCDFPlot
from draw_tools.line_plot import LinePlot
from draw_tools.box_plot import BoxPlot
from draw_tools.cdf_complex import CDFCCDFPlot
from draw_tools.scatter_plot import ScatterPlot
from draw_tools.bar_plot import BarPlot

def draw_cdf_plot(datas, datatype, legend, legend_type, filename, log_scale=True):
    cdf = CDFPlot()
    cdf.set_label(datatype, 'CDF')
    cdf.set_log(log_scale)
    for i in range(len(datas)):
        cdf.set_data(datas[i], '')
    #ticks = np.arange(-1, 1.1, 0.1)
    #ticks = [round(item,1) for item in ticks]
    #print(ticks)
    #cdf.set_xticks(ticks, index=ticks)
    cdf.set_xticks([-1, 0, 1],index = [-1, 0, 1])
    #cdf.set_xticks(['0', '1m', '5m', '1h', '1d', '30d', '6m'], index=[0,1,5,60, 24*60, 24*30*60, 24*30*6*60])
    if len(legend) > 1:
        cdf.set_legends(legend, legend_type)
    cdf.save_image(filename)

def draw_ccdf_plot(datas, datatype, legend, legend_type, filename, log_scale=True):
    cdf = CCDFPlot()
    cdf.set_label(datatype, 'CCDF')
    cdf.set_log(log_scale)
    for i in range(len(datas)):
        cdf.set_data(datas[i])
    if len(legend) > 1:
        cdf.set_legends(legend, legend_type)
    cdf.save_image('%s'%filename)


def draw_cdf_complex_plot(datas, datatype, legend, legend_type, filename, log_scale=True):
    cdf = CDFCCDFPlot()
    cdf.set_label(datatype, 'CDF')
    if log_scale:
        cdf.set_xlog()
    for i in range(len(datas)):
        cdf.set_data(datas[i])
    if len(legend) > 1:
        cdf.set_legends(legend, legend_type)
    cdf.save_image(filename)


def draw_4_2_1_figures():
    with open('Data/Figure/4_2_1.json', 'r') as f:
        data= json.load(f)
    

    #pdf.draw_pdf(data, 'Mean Edge Homogeneity', ['Echo Chambers' , 'Non Echo Chambers'], 'Image/Figure/4_2_3.png')
    #Mean edge homogeneity
    draw_cdf_plot([data['e'], data['ne']], '', ['Echo chamber', 'Non-echo chamber'], '', 'Image/Figure/4_2_3_2.png')

def draw_4_2_2_figures():
    with open('Data/Figure/4_2_2.json', 'r') as f:
        data = json.load(f)

    #pdf.draw_pdf(data, 'Homogeneity', ['Echo Chamber', 'Random Sampling'], 'Image/Figure/4_2_4.png')
    items1 = [item for item in data['e'] if item > 0]   
    items2 = [item for item in data['e'] if item > 0.5]   

    #print(len(items1), len(items2), len(data['e']))
    
    draw_cdf_plot([data['e'], data['ne']], 'User Homogeneity', ['Echo chamber', 'Random'], '', 'Image/Figure/4_2_4_2.png')


def draw_5_1_1_figures():
    with open('Data/Figure/5_1_1.json', 'r') as f:
        data= json.load(f)
    
    echo = data['echo']
    non_echo = data['necho']

    draw_cdf_plot([echo[0], non_echo[0]], 'Depth', ['Echo chamber', 'Non-echo chamber'], '', 'Image/Figure/5_1_1_1.png', log_scale=False)
    draw_cdf_plot([echo[2], non_echo[2]], 'Child', ['Echo chamber', 'Non-echo chamber'], '', 'Image/Figure/5_1_1_2.png')

def draw_5_1_1_2_figures():
    with open('Data/Figure/5_1_1_2.json', 'r') as f:
        data = json.load(f)
    
    e_depth = data['e_depth']
    e_child = data['e_child']
    ne_depth = data['ne_depth']
    ne_child = data['ne_child']
    
    print('Data load from  Data/Figure/5_1_1_2.json')
    draw_ccdf_plot([e_depth, ne_depth], '', ['Echo chamber', 'Non-echo chamber'], '', 'Image/Figure/5_1_1_3.png', log_scale=False)
    draw_ccdf_plot([e_child, ne_child], '', ['Echo chamber', 'Non-echo chamber'], '', 'Image/Figure/5_1_1_4.png')
    #draw_cdf_complex_plot([e_depth, ne_depth], '', ['Echo Chamber', 'Non Echo Chamber'], '', 'Image/Figure/5_1_1_3_1.png', log_scale=False)
    #draw_cdf_complex_plot([e_child, ne_child], '', ['Echo Chamber', 'Non Echo Chamber'], '', 'Image/Figure/5_1_1_4_1.png')
     

def draw_5_1_2_figures():
    with open('Data/Figure/5_1_2.json', 'r') as f:
        data= json.load(f)

    echo = data['echo']
    non_echo = data['necho']

    #size 1 cascade size
    print(non_echo['cascade'].values().count(1), len(non_echo['cascade']), non_echo['cascade'].values().count(1) / len(non_echo['cascade']))
    print(echo['cascade'].values().count(1), len(echo['cascade']), echo['cascade'].values().count(1) / len(echo['cascade']))

    #top 1% size, depth, members, width
    e_depth = sorted(echo['max_depth'].values(), reverse=True)
    e_breadth = sorted(echo['max_breadth'].values(), reverse=True)
    e_size = sorted(echo['cascade'].values(), reverse=True)
    e_users = sorted(echo['unique_users'].values(), reverse=True)
    ne_depth = sorted(non_echo['max_depth'].values(), reverse=True)
    ne_breadth = sorted(non_echo['max_breadth'].values(), reverse=True)
    ne_size = sorted(non_echo['cascade'].values(), reverse=True)
    ne_users = sorted(non_echo['unique_users'].values(), reverse=True)
    e_top = int(len(e_depth) * 0.01)
    ne_top = int(len(ne_depth) * 0.01)

    print('top num')
    print(e_top, ne_top)
    print('echo')
    print(e_depth[:100])
    print(e_size[:100])
    print('non echo')
    
    print(ne_depth[:200])
    print(ne_size[:100])
    print('echo : %s / %s'%(e_top, len(e_depth)))
    print('non echo : %s / %s'%(ne_top, len(ne_depth)))

    print('echo chamber / non-echo chamber')
    print('depth %s : %s'%(e_depth[e_top], ne_depth[ne_top]))
    print('breadth %s : %s'%(e_breadth[e_top], ne_breadth[ne_top]))
    print('size %s : %s'%(e_size[e_top], ne_size[ne_top]))
    print('user %s : %s'%(e_users[e_top], ne_users[e_top]))
    draw_cdf_plot([echo['max_depth'].values(), non_echo['max_depth'].values()], '',['Echo chamber', 'Non-echo chamber'], '', 'Image/Figure/5_1_2_1.png') 
    draw_cdf_plot([echo['max_breadth'].values(), non_echo['max_breadth'].values()], '',['Echo chamber', 'Non-echo chamber'], '', 'Image/Figure/5_1_2_2.png') 
    draw_cdf_plot([echo['cascade'].values(), non_echo['cascade'].values()], '',['Echo chamber', 'Non-echo chamber'], '', 'Image/Figure/5_1_2_3.png') 
    draw_cdf_plot([echo['unique_users'].values(), non_echo['unique_users'].values()], '',['Echo chamber', 'Non-echo chamber'], '', 'Image/Figure/5_1_2_4.png') 
 
#echo chamber cascade about  size, depth, users, width for the number of rumors 2,3,4 
def draw_5_1_2_2_figures():
    with open('Data/Figure/5_1_2_2.json', 'r') as f:
        data = json.load(f)
    echo_1 = data['echo_2']
    echo_2 = data['echo_3']
    echo_3 = data['echo_4']

    draw_cdf_plot([echo_1['max_depth'].values(), echo_2['max_depth'].values(), echo_3['max_depth'].values()], '',['Relevance 2', 'Relevance 3', 'Relevance 4'], 'User Type', 'Image/Figure/5_1_2_2_1.png') 
    draw_cdf_plot([echo_1['max_breadth'].values(), echo_2['max_breadth'].values(), echo_3['max_breadth'].values()], '',['Relevance 2', 'Relevance 3', 'Relevance 4'], 'User Type', 'Image/Figure/5_1_2_2_2.png') 
    draw_cdf_plot([echo_1['cascade'].values(), echo_2['cascade'].values(), echo_3['cascade'].values()], '',['Relevance 2', 'Relevance 3', 'Relevance 4'], 'User Type', 'Image/Figure/5_1_2_2_3.png') 
    draw_cdf_plot([echo_1['unique_users'].values(), echo_2['unique_users'].values(), echo_3['unique_users'].values()], '',['Relevance 2', 'Relevance 3', 'Relevance 4'], 'User Type', 'Image/Figure/5_1_2_2_4.png') 



def draw_5_2_1_figures():
    with open('Data/Figure/5_2_1.json', 'r') as f:
        data = json.load(f)

    #print(data)
    #draw_time_to_depth_echo_chamber([echo_chamber_values['time_depth'], non_echo_chamber_values['time_depth']], ['echo chamber', 'no echo chamber'], 'median minutes', 'time_depth_echo_chamber_line')
    #x_ticks = np.arange(1,18)
    x_ticks = range(1, 18)
    line = LinePlot()
    line.set_ylog()
    line.set_label('Depth', 'Depth Increment Time')
    xtick_labels = []
    print('sadfasdfasdfasdf')
    print(len(data))
    x_tickslabel = range(0,17)
    x_tickslabel.append('')
    for item in data:
        #yticks = [np.mean(item[depth]) for depth in x_ticks]
        yticks = [np.median(item[str(depth)]) for depth in x_ticks]
        #u_ticks1 = [np.mean(outlier.remove_outlier(item[depth])) for depth in x_ticks]
        print(yticks)
        line.set_plot_data(yticks, x_tickslabel)
    print(x_ticks)
    #print(x_ticks[0]['time_depth'])
    #print(x_ticks[1]['time_depth'])
    line.set_legends(['Echo chamber', 'Non-echo chamber'])
    line.set_xticks(x_tickslabel)
    line.set_yticks(['0', '1 m', '5 m', '1 h', '1 day', '10 day'], index=[0,1,5,60, 24*60, 24*10*60])
    line.save_image('Image/Figure/5_2_1.png')
    print(xtick_labels)
def draw_5_3_1_figures():
    with open('Data/Figure/5_3_1_2.json', 'r') as f:
        data = json.load(f)

    e_child = data['e_child']
    ne_child = data['ne_child']
    e_time = data['e_time']
    ne_time = data['ne_time']
    ne_time2 = data['ne_time2']

    e_c = {}; e_t = {}; ne_c = {}; ne_t = {}; ne_t2 = {};
    for i in range(1, 11):
        e_c[i] = e_child[str(i)]
        e_t[i] = e_time[str(i)]
        ne_c[i] = ne_child[str(i)]
        ne_t[i] = ne_time[str(i)]
        ne_t2[i] = ne_time2[str(i)]
        
        #if i > 6:
        #    print(e_t[i])
        #    print(e_c[i])

    box = BoxPlot(1)
    box.set_multiple_data([e_c, ne_c])
    box.set_ylog()
    box.set_label('Depth', 'Child Count')
    box.save_image('Image/Figure/5_3_1_2.png')

    print(e_t.keys())
    box = BoxPlot(1)
    box.set_multiple_data([e_t, ne_t])
    box.set_ylog()
    box.set_label('Depth', 'Propagation Time')
    box.set_yticks(['0', '1 m', '5 m', '1 h', '1 day'], index=[0,1,5,60, 24*60])
    #box.set_yticks(['0', '1 m', '10 m', '1 h', '1 day'], index=[0,1,10,60, 24*60])
    box.save_image('Image/Figure/5_3_1_1.png')

    #filter the wrong value is duration over 6 month 
    filter_value = 60 * 24 * 180
    e_time['1'] = [item for item in e_time['1'] if item < filter_value]
    ne_time['1'] = [item for item in ne_time['1'] if item < filter_value]
    print(max(e_time['1']))
    print(max(ne_time['1']))
    e_time['1'] = sorted(e_time['1'])
    ne_time['1'] = sorted(ne_time['1'])
    #print(e_time['1'])
    #print(ne_time['1'])
    draw_cdf_plot([e_time['1'], ne_time['1']], 'Propagation Time', ['Echo chamber', 'Non-echo chamber'], '', 'Image/Figure/5_3_2.png')

    
#degree, weight, weight_degree distribution
def draw_6_1_1_figures():
    with open('Data/Figure/6_1_2.json', 'r') as f:
        data = json.load(f)

    degree = data['degree']
    weight = data['weight']
    weighted_degree = data['weighted_degree']

    degree = [item for item in degree if item > 0]
    #print(degree)
    #np.sort(degree)
    #w_sort = sorted(weight, reverse=True)
    w_sort = sorted(weight)
    print('all weight and weight num below 10')
    print(len(weight), len([item for item in weight if item < 10]))
    #print(w_sort[:10])
    print('all degree and degree num below 10')
    print(degree)
    print(len(degree), len([item for item in degree if item < 10]))
    
    top_one = int(len(weight) * 0.01)
    top_zeroone = int(len(weight) * 0.001)
    top_ten = int(len(weight) * 0.1)
    w_sort = sorted(weight, reverse=True)
    print('top 10%', w_sort[top_ten])
    print('top 1%', w_sort[top_one])
    print('top 0.1%', w_sort[top_zeroone])
    print('max', max(weight))
    print(w_sort[int(len(weight) * 0.95)])
    d_sort = sorted(degree, reverse=True)
    top_one = int(len(degree) * 0.01)
    print('degree all', len(degree), 'degree top 1%', d_sort[top_one])
    #draw_cdf_plot([degree], '', [''], '', 'Image/Figure/6_1_1_1.png')
    #draw_cdf_plot([weight], '', [''], '', 'Image/Figure/6_1_1_2.png')
    #draw_cdf_plot([weighted_degree], '', [''], '', 'Image/Figure/6_1_1_3.png')
    #draw_ccdf_plot([degree], '', [''], '', 'Image/Figure/6_1_1_4.png')
    #draw_ccdf_plot([weight], '', [''], '', 'Image/Figure/6_1_1_5.png')
    #draw_ccdf_plot([weighted_degree], '', [''], '', 'Image/Figure/6_1_1_6.png')

    #draw_cdf_complex_plot([e_depth, ne_depth], '', ['Echo Chamber', 'Non Echo Chamber'], '', 'Image/Figure/5_1_1_3_1.png', log_scale=False)
    draw_cdf_complex_plot([weight], '', [''], '', 'Image/Figure/6_1_1_7.png')
    draw_cdf_complex_plot([degree], '', [''], '', 'Image/Figure/6_1_1_8.png')


def draw_6_2_1_figures():
    with open('Data/Figure/6_2_1.json', 'r') as f:
        data = json.load(f)

    ranklist = data['ranklist']
    topuserlist = data['topuserlist']
    
    scatter = ScatterPlot()
    scatter.set_log(True)
    scatter.set_ylog()
    scatter.set_ylim(1, 1000)
    scatter.set_xlim(1, max(ranklist))
    scatter.set_label('Rank', 'Number of Top Spreaders')
    scatter.set_data(ranklist, topuserlist)
    scatter.set_xticks(['1', '10', '100', '1K'])
    scatter.set_yticks(['1', '10', '100', '1K'])

    scatter.save_image('Image/Figure/6_2_1.png')

#upper-class / lower-class political homophily
def draw_6_2_2_figures():


    with open('Data/Figure/6_2_2.json', 'r') as f:
        data = json.load(f)

    print('user homogeneity')
    upper_class = data[0]
    lower_class = data[1]
    up1 = [item for item in upper_class if item < 0]
    lw1 = [item for item in lower_class if item < 0]
    print(len(up1), len(upper_class), len(up1)/len(upper_class))
    print(len(lw1),len(lower_class), len(lw1)/len(lower_class))

    #pdf.draw_multiline_pdf(data, 'Homogeneity', ['Upper Class', 'Lower Class'], 'Image/Figure/6_2_2.png')
    draw_cdf_plot(data, '', ['Top 10%', 'Bottom 10%'], '', 'Image/Figure/6_2_2_1.png')
    
    with open('Data/Figure/6_2_2_2.json', 'r') as f:
        data = json.load(f)

    #pdf.draw_multiline_pdf(data, 'Mean Edge Homogeneity', ['Upper Class', 'Lower Class'], 'Image/Figure/6_2_2_2.png')

    upper_class = data[0]
    lower_class = data[1]

    print('mean edge homogeneity')
    print('all upper ', len(upper_class))
    print('all lower ', len(lower_class))
    up1 = [item for item in upper_class if item > 0]
    up2 = [item for item in upper_class if item > 0.9]
    lw1 = [item for item in lower_class if item > 0]
    lw2 = [item for item in lower_class if item > 0.9]
    print(len(up1), len(upper_class), len(up1)/len(upper_class))
    print(len(lw1), len(lower_class), len(lw1)/len(lower_class))

    draw_cdf_plot([upper_class, lower_class], '', ['Top 10%', 'Bottom 10%'], '', 'Image/Figure/6_2_2_2.png')


#core echo chamber rumor participation
def draw_6_3_1_figures():
    with open('Data/Figure/6_3.json', 'r') as f:
        data = json.load(f)
        #json.dump({'rumor' : rumor_num, 'cascade_num' : cascade_num}, f)

    all_cascade_num = 48644
    all_tweet_num = 310545 
    all_retweet_count = 264653
    rumor_num = data['rumor']
    cascade_num = data['cascade_num']
    all_retweet_num = data['all_user']
    all_retweet_median_num = data['all_median']
    all_retweet_mean_num = data['all_mean']

    x_ticks = range(0, len(rumor_num))

    print('top 10% echo chamber ', len(rumor_num))
    #print(x_ticks)
    #print(rumor_num)
    line = LinePlot()
    line.set_ylog()
    line.set_label('Rank', 'Number of Rumors')
    yticks = [rumor_num[i] for i in x_ticks]
    line.set_plot_data(yticks, x_ticks)
    #line.set_yticks(['0', '1 m', '5 m', '1 h', '1 day', '10 day'], index=[0,1,5,60, 24*60, 24*10*60])
    line.save_image('Image/Figure/6_3_1.png')

    x_ticks = range(0, len(rumor_num))
    line = LinePlot()
    line.set_ylog()
    line.set_label('Rank', 'Number of Cascades')
    yticks = [cascade_num[i] for i in x_ticks]
    line.set_plot_data(yticks, x_ticks)
    #line.set_yticks(['0', '1 m', '5 m', '1 h', '1 day', '10 day'], index=[0,1,5,60, 24*60, 24*10*60])
    line.save_image('Image/Figure/6_3_2.png')

    print('all', len(x_ticks))
    #portion of cascades
    echo_num = len(cascade_num)
    top_01 = int(echo_num * 0.01)
    top_1 = int(echo_num * 0.1)
    top_5 = int(echo_num * 0.5)
    top_10 = -1
    top01_p = cascade_num[top_01] / all_cascade_num * 100
    top1_p = cascade_num[top_1] / all_cascade_num * 100
    top5_p = cascade_num[top_5] / all_cascade_num * 100
    top10_p = cascade_num[top_10] / all_cascade_num * 100
    #print(cascade_num)
    print(top01_p, top1_p, top5_p, top10_p)
    barplot = BarPlot(1)
    barplot.set_data([0,1,2,3], [top01_p, top1_p, top5_p, top10_p], '')
    barplot.set_xticks(['0.1%', '1%', '5%', '10%'])
    #barplot.set_ylim(100)
    barplot.set_label('Hub Echo Chambers', 'Participation of Cascades (%)')
    barplot.save_image('Image/Figure/6_3_3.png')

    print(top_01, top_1, top_5)
    top01_n = all_retweet_num[top_01] / all_retweet_count * 100
    top1_n = all_retweet_num[top_1] / all_retweet_count * 100
    top5_n = all_retweet_num[top_5] / all_retweet_count * 100
    top10_n = all_retweet_num[top_10] / all_retweet_count * 100
    print(all_retweet_num[top_10])
    print(top01_n, top1_n, top5_n, top10_n)
    barplot = BarPlot(1)
    barplot.set_multiple_data([top01_p, top1_p, top5_p, top10_p], [top01_n, top1_n, top5_n, top10_n])
    barplot.set_xticks(['0.1%', '1%', '5%', '10%'])
    barplot.set_ylim(50)
    barplot.set_label('Hub Echo Chambers', 'Portion of Cascades (%)')
    #barplot.set_legends(['Cascade', 'Retweet'], '')
    barplot.save_image('Image/Figure/6_3_4.png')

    """
    top01_n = all_retweet_median_num[top_01] / all_tweet_num * 100
    top1_n = all_retweet_median_num[top_1] / all_tweet_num * 100
    top5_n = all_retweet_median_num[top_5] / all_tweet_num * 100
    top10_n = all_retweet_median_num[top_10] / all_tweet_num * 100
    print(top01_n, top1_n, top5_n, top10_n)
    barplot = BarPlot(1)
    barplot.set_multiple_data([top01_p, top1_p, top5_p, top10_p], [top01_n, top1_n, top5_n, top10_n])
    barplot.set_xticks(['0.1%', '1%', '5%', '10%'])
    #barplot.set_ylim(50)
    barplot.set_label('Hub Echo Chambers', 'Participation of Cascades (%)')
    barplot.save_image('Image/Figure/6_3_5.png')

    top01_n = all_retweet_mean_num[top_01] / all_tweet_num * 100
    top1_n = all_retweet_mean_num[top_1] / all_tweet_num * 100
    top5_n = all_retweet_mean_num[top_5] / all_tweet_num * 100
    top10_n = all_retweet_mean_num[top_10] / all_tweet_num * 100
    print(top01_n, top1_n, top5_n, top10_n)
    barplot = BarPlot(1)
    barplot.set_multiple_data([top01_p, top1_p, top5_p, top10_p], [top01_n, top1_n, top5_n, top10_n])
    barplot.set_xticks(['0.1%', '1%', '5%', '10%'])
    #barplot.set_ylim(100)
    barplot.set_label('Hub Echo Chambers', 'Cumulative Portion of Cascades (%)')
    barplot.save_image('Image/Figure/6_3_6.png')
    """
if __name__ == "__main__":
    #draw_4_2_1_figures()
    #draw_4_2_2_figures()
    #draw_5_1_1_figures()
    #draw_5_1_1_2_figures()
    #draw_5_1_2_2_figures()
    #draw_5_1_2_figures()
    #draw_5_2_1_figures()
    #draw_5_3_1_figures()
    draw_6_1_1_figures()
    #draw_6_2_1_figures()
    #draw_6_2_2_figures()
    #draw_6_3_1_figures()

