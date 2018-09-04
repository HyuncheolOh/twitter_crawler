import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np

class BarPlot:

    def __init__(self, subplot_num):
        self.fig_num = 1
        self.fig = plt.figure(figsize=(10,10))
        #self.fig = plt.figure(figsize=(10,5))
        self.fig, self.ax = plt.subplots()
        self.subplot_x = subplot_num
        self.subplot_y = subplot_num

    def set_data(self, ticks, data, name, rotation='horizontal'):
        #self.ax = self.fig.add_subplot(self.subplot_x, self.subplot_y, self.fig_num)
        y_pos = np.arange(len(data))
        self.ax.bar(y_pos, data, align='center')
        plt.xticks(y_pos, ticks, rotation=rotation)
        self.ax.title.set_text(name)
        #self.ax.set_yscale('symlog')
        plt.axis('tight')
        self.fig_num += 1
   
    def set_data_horizontal(self, ticks, data, name, rotation = 'horizontal'):
        #self.ax = self.fig.add_subplot(self.subplot_x, self.subplot_y, self.fig_num)
        y_pos = np.arange(len(data))
        self.ax.barh(y_pos, data, align='center')
        self.ax.invert_yaxis()
        #plt.xticks(y_pos, ticks, rotation=rotation)
        self.ax.set_yticks(y_pos)
        self.ax.set_yticklabels(ticks)
        self.ax.title.set_text(name)
        plt.axis('tight')
        #self.ax.set_yscale('symlog')
        self.fig_num += 1

    def set_bar_line(self, ticks, bar_data, line_data, name, rotation='horizontal'):
        self.ax = self.fig.add_subplot(self.subplot_x, self.subplot_y, self.fig_num)
        y_pos = np.arange(len(bar_data))
        self.ax.bar(y_pos, bar_data, align='center')
        self.ax.plot(line_data)
        plt.xticks(y_pos, ticks, rotation=rotation)
        self.ax.title.set_text(name)
        self.fig_num += 1
    
    def set_legends(self, legends, title=""):
        print(legends)
        plt.legend(legends, loc=1, title=title, fontsize=9)

    def set_label(self, x,y):
        self.x_label = x
        self.y_label = y

    def set_xticks(self, xticks):
        plt.xticks(np.arange(len(xticks)), xticks)

    def set_ylim(self, value):
        self.ax.set_ylim(0, value)

    def set_width(self, width):
        self.ax.plot(width = width)

    def save_image(self, path):
        plt.savefig(path, bbox_inches='tight')


