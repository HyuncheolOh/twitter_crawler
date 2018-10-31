import os, sys, json 
import numpy as np
import draw_tools.pdf as pdf
from draw_tools.cdf_plot import CDFPlot
from draw_tools.ccdf_plot import CCDFPlot
from draw_tools.line_plot import LinePlot
from draw_tools.box_plot import BoxPlot

def draw_cdf_plot(datas, datatype, legend, legend_type, filename, log_scale=True):
    cdf = CDFPlot()
    cdf.set_label(datatype, 'CDF')
    cdf.set_log(log_scale)
    for i in range(len(datas)):
        cdf.set_data(datas[i], '')
    if len(legend) > 1:
        cdf.set_legends(legend, legend_type)
    cdf.save_image(filename)

def draw_4_2_1_figures():
    #with open('Data/Figure/4_2_1.json', 'r') as f:
    #    data= json.load(f)
    
    #pdf.draw_pdf(data, 'Mean Edge Homogeneity', ['Echo Chambers' , 'Non Echo Chambers'], 'Image/Figure/4_2_3.png')
    #draw_cdf_plot([data['e'], data['ne']], 'Mean Edge Homogeneity', ['Echo chamber', 'Non echo chamber'], '', 'Image/Figure/4_2_3_2.png')
    draw_cdf_plot([[0.5, 0.4, 0.9],[-0.3, 0.4, 0.6]], 'Mean Edge Homogeneity', ['Echo chamber', 'Non echo chamber'], '', 'Image/Figure/4_2_3_2.png')

def draw_4_2_2_figures():
    with open('Data/Figure/4_2_2.json', 'r') as f:
        data = json.load(f)

    #pdf.draw_pdf(data, 'Homogeneity', ['Echo Chamber', 'Random Sampling'], 'Image/Figure/4_2_4.png')
    #draw_cdf_plot([data['e'], data['ne']], 'Group Homogeneity', ['Echo chamber', 'Non echo chamber'], '', 'Image/Figure/4_2_4_2.png')


def draw_5_1_1_figures():
    with open('Data/Figure/5_1_1.json', 'r') as f:
        data= json.load(f)
    
    echo = data['echo']
    non_echo = data['necho']

    draw_cdf_plot([echo[0], non_echo[0]], 'Depth', ['Echo chamber', 'Non echo Chamber'], '', 'Image/Figure/5_1_1_1.png', log_scale=False)
    draw_cdf_plot([echo[2], non_echo[2]], 'Child', ['Echo chamber', 'Non echo chamber'], '', 'Image/Figure/5_1_1_2.png')

def draw_5_1_1_2_figures():
    with open('Data/Figure/5_1_1_2.json', 'r') as f:
        data = json.load(f)
    
    e_depth = data['e_depth']
    e_child = data['e_child']
    ne_depth = data['ne_depth']
    ne_child = data['ne_child']
    
    print('Data load from  Data/Figure/5_1_1_2.json')
    draw_cdf_plot([e_depth, ne_depth], 'Depth', ['Echo Chamber', 'Non Echo Chamber'], '', 'Image/Figure/5_1_1_3.png', log_scale=False)
    draw_cdf_plot([e_child, ne_child], 'Child', ['Echo Chamber', 'Non Echo Chamber'], '', 'Image/Figure/5_1_1_4.png')

 

def draw_5_1_2_figures():
    with open('Data/Figure/5_1_2.json', 'r') as f:
        data= json.load(f)

    echo = data['echo']
    non_echo = data['necho']
    draw_cdf_plot([echo['max_depth'].values(), non_echo['max_depth'].values()], 'Depth',[], '', 'Image/Figure/5_1_2_1.png') 
    draw_cdf_plot([echo['max_breadth'].values(), non_echo['max_breadth'].values()], 'Breadth',[], 'User Type', 'Image/Figure/5_1_2_2.png') 
    draw_cdf_plot([echo['cascade'].values(), non_echo['cascade'].values()], 'Cascade',[], 'User Type', 'Image/Figure/5_1_2_3.png') 
    draw_cdf_plot([echo['unique_users'].values(), non_echo['unique_users'].values()], 'Number of users',[], 'User Type', 'Image/Figure/5_1_2_4.png') 
 

def draw_5_2_1_figures():
    with open('Data/Figure/5_2_1.json', 'r') as f:
        data = json.load(f)

    #print(data)
    #draw_time_to_depth_echo_chamber([echo_chamber_values['time_depth'], non_echo_chamber_values['time_depth']], ['echo chamber', 'no echo chamber'], 'median minutes', 'time_depth_echo_chamber_line')
    x_ticks = np.arange(1,20)
    line = LinePlot()
    line.set_ylog()
    line.set_label('Depth', 'Median Time')
    for item in data:
        #yticks = [np.mean(item[depth]) for depth in x_ticks]
        yticks = [np.median(item[str(depth)]) for depth in x_ticks]
        #u_ticks1 = [np.mean(outlier.remove_outlier(item[depth])) for depth in x_ticks]
        line.set_plot_data(yticks, x_ticks)
    line.set_legends(['Echo chambers', 'Non-echo chambers'])
    line.set_xticks(x_ticks)
    line.save_image('Image/Figure/5_2_1.png')


        

if __name__ == "__main__":
    #draw_4_2_1_figures()
    #draw_4_2_2_figures()
    #draw_5_1_1_figures()
    draw_5_1_1_2_figures()
    #draw_5_1_2_figures()
    #draw_5_2_1_figures()
