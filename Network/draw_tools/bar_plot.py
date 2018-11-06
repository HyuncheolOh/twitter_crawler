import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np

class BarPlot:

    def __init__(self, subplot_num):
        self.fig_num = 1
        self.fig = plt.figure(figsize=(8,3))
        #self.fig = plt.figure(figsize=(10,5))
        self.fig, self.ax = plt.subplots()
        self.subplot_x = subplot_num
        self.subplot_y = subplot_num

    def set_data(self, ticks, data, name, rotation='horizontal'):
        #self.ax = self.fig.add_subplot(self.subplot_x, self.subplot_y, self.fig_num)
        y_pos = np.arange(len(data))
        self.ax.bar(y_pos, data, align='center', color='#2d7cb5', width=0.3)
        plt.xticks(y_pos, ticks, rotation=rotation)
        self.ax.title.set_text(name)
        #self.ax.set_yscale('symlog')
        #plt.axis('tight')
        self.fig_num += 1
 
    def set_multiple_data(self, data1, data2):
        #self.ax = self.fig.add_subplot(self.subplot_x, self.subplot_y, self.fig_num)
        wth = 0.3
        spc = 0.2
        y_pos = np.arange(len(data1))
        rect1 = self.ax.bar(y_pos+spc, data1, color='#2d7cb5', width=wth)
        #self.ax.bar(y_pos+0.4, data2, align='center', color='#b30000', width=0.4)
        ax2 = self.ax.twinx()
        rect2 = ax2.bar(y_pos+wth+spc, data2, color='#b30000', width=wth)
        ax2.set_ylabel('Cumulative Portion of Retweet Count (%)', fontsize=16) 
        #ax2.set_yscale('symlog')
        #ax2.tick_params('y', colors='r')
        #self.ax.set_yscale('symlog')
        #plt.axis('tight')
        self.ax.legend((rect1, rect2), ('Cascade', 'Retweet'), loc=2, fontsize=12)
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
 
    def set_axvline(self, published_date):
        plt.axvline(x=published_date, color='g', linestyle='--', linewidth=2)
   
    def set_legends(self, legends, title=""):
        print(legends)
        plt.legend(legends, loc=2, title=title, fontsize=12)

    def set_label(self, x,y):
        self.ax.set_xlabel(x, fontsize=16);
        self.ax.set_ylabel(y, fontsize=16);

    def set_ylog(self):
        self.ax.set_yscale('symlog')

    def set_xticks(self, xticks):
        plt.xticks(np.arange(len(xticks)) + 0.3 + 0.2, xticks, fontsize=12)

    def set_x_bins(self, bins):
        self.ax.locator_params(nbins=bins, axis='x')
        #plt.locator_params(nbins=bins, axis='x')

    def set_xticklabels(self, labels):
        self.ax.set_xticklabels(labels)

    def set_ylim(self, value):
        self.ax.set_ylim(0, value)

    def set_width(self, width):
        self.ax.plot(width = width)

    def save_image(self, path):
        plt.savefig(path, bbox_inches='tight')
        self.fig.savefig(path + '.eps', bbox_inches='tight', format='eps', dpi=600)


