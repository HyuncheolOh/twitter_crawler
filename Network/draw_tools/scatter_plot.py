import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np

class ScatterPlot:

    def __init__(self, subplot_num=1):
        self.fig_num = 1
        self.is_log = False
        self.fig = plt.figure(figsize=(30,15))
	self.ax = self.fig.add_subplot(1,1,1);
        self.subplot_x = subplot_num
        self.subplot_y = subplot_num

    def set_data(self, x, y):
        #self.ax = self.fig.add_subplot(self.subplot_x, self.subplot_y, self.fig_num)
        if self.is_log == True:
            self.ax.set_yscale('symlog')
        #c = ['g' for i in range(5)]
        #for i in range(len(x)):
        #    self.ax.scatter(x[i], y[i], c = colors[i], s = 100, marker = markers[i])
        self.ax.scatter(x, y)
        #self.ax.scatter(x, y, c = colors, s = 80, marker = markers)
#        plt.legend(legends)
        
    def set_data(self, x, y, e):
        if self.is_log == True:
            self.ax.set_yscale('symlog')
        #c = ['g' for i in range(5)]
        for i in range(len(x)):
            if e[i] == 1:
                self.ax.scatter(x[i], y[i], c = 'r', s = 300)
            else :
                self.ax.scatter(x[i], y[i], c = 'b', s = 100)

        #self.ax.scatter(x, y)
        #self.ax.scatter(x, y, c = colors, s = 80, marker = markers)

    def set_label(self, x,y):
        self.ax.set_xlabel(x);
        self.ax.set_ylabel(y);


    def set_xticks(self, xticks):
        plt.xticks(np.arange(len(xticks)), xticks)

    def set_yticks(self, yticks):
        plt.yticks(np.arange(len(yticks)), yticks)

    def set_ylim(self, value):
        self.ax.set_ylim(10000, value)
        self.ax.set_xlim(0,100)

    def set_title(self, title):
        self.ax.title.set_text(title)

    def set_ylog(self):
        self.ax.set_yscale('symlog')

    def set_log(self, log):
        self.is_log = log

    def save_image(self, path):
        plt.hold(False)
        plt.axis('tight')
        self.ax.legend()
        plt.savefig(path, bbox_inches='tight')


