import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

class BoxPlot:
    '''
    def __init__(self, data):
        self.data = data
        plt.boxplot(data, showfliers=False)
    '''
    def __init__(self, subplot_num):
        self.fig_num = 1
        self.fig = plt.figure(figsize=(10,10))
        self.subplot_x = subplot_num
        self.subplot_y = subplot_num

    def set_data(self, data, label):
        self.ax = self.fig.add_subplot(self.subplot_x, self.subplot_y, self.fig_num)
        self.ax.boxplot(data, showfliers = False)
        #self.fig_num += 1

    def set_box_color(self, bp, color):
        plt.setp(bp['boxes'], color=color)
        plt.setp(bp['whiskers'], color=color)
        plt.setp(bp['caps'], color=color)
        plt.setp(bp['medians'], color=color)


    def set_multiple_data(self, data):
        self.ax = self.fig.add_subplot(self.subplot_x, self.subplot_y, self.fig_num)

        #for i, item in enumerate(data):
            #self.ax.boxplot(item, positions = [i*5+1, i*5+2], showfliers = False, widths=0.6)
        bpl = self.ax.boxplot(data[0].values(), positions=np.array(xrange(len(data[0])))*2.0-0.4, sym='', widths=0.6, showfliers = False)
        bpr = self.ax.boxplot(data[1].values(), positions=np.array(xrange(len(data[1])))*2.0+0.4, sym='', widths=0.6, showfliers = False)
        self.set_box_color(bpl, '#b2182b') # colors are from http://colorbrewer2.org/
        self.set_box_color(bpr, '#084081')

        # draw temporary red and blue lines and use them to create a legend
        plt.plot([], c='#b2182b', label='Echo Chamber')
        plt.plot([], c='#084081', label='Non Echo Chamber')
        plt.legend(fontsize=20)
        ticks = np.arange(1,11)
        plt.xticks(xrange(0, len(ticks) * 2, 2), ticks, fontsize=20)
        plt.xlim(-2, len(ticks)*2)
        #plt.ylim(0, 8)

    def set_data_with_position(self, data, lebel, grid):
        self.ax = self.fig.add_subplot(grid)
        self.ax.boxplot(data, showfliers = True)

    def set_title(self, title):
        #self.ax.title.set_text(title, fontsize=20)
        self.ax.set_title(title, fontsize=24, y=1.02)

    def set_xticks(self, x_ticks):
        #plt.xticks(np.arange(len(x_ticks))+1, x_ticks) 
        #plt.xticks(np.arange(len(x_ticks))+1, x_ticks) 
        self.ax.set_xticklabels(x_ticks, fontsize=20)

    def set_yticks(self, y_ticks):
        self.ax.set_yticklabels(y_ticks, fontsize=20)

    def set_label(self, x, y):
        self.ax.set_xlabel(x, fontsize=24);
        self.ax.set_ylabel(y, fontsize=24);

    def set_ylim(self, value):
        self.ax.set_ylim(0, value)

    def set_ylog(self):
        self.ax.set_yscale('symlog')

    def set_xlog(self):
        self.ax.set_xscale('symlog')

    def save_image(self, path):
        plt.savefig(path, bbox_inches='tight')
        plt.savefig(path + '.eps', bbox_inches='tight')

