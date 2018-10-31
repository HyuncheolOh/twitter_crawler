import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math
from numpy import ma
from matplotlib import scale as mscale
from matplotlib import transforms as mtransforms
from matplotlib.ticker import FixedFormatter, FixedLocator
class CDFPlot:
    is_log = False;

    def __init__(self):
	self.fig = plt.figure(figsize=(5,5));
	self.ax = self.fig.add_subplot(1,1,1);
        self.x_label = 'x';
	self.y_label = 'y';

    def plot_cdf(self, data, ax, label):
        """
        Plot CDF(x) on the axes object
        Note that this way of computing and plotting the CDF is not
        the best approach for a discrete variable, where many
        observations can have exactly same value!
        """
        # Note that, here we use the convention for presenting an
        # empirical 1-CDF (ccdf) as discussed
        # a quick way of computing a ccdf (valid for continuous data):
        sorted_vals = np.sort(data)
        #print(sorted_vals)
        p = 1. * np.arange(len(data)) / (len(data) - 1)
        #ax.plot(sorted_vals, p, label=label, linewidth = 2.0)
        ax.plot(sorted_vals, p, label=label)
        
	if CDFPlot.is_log == True: 
#	    ax.set_xscale('log')
            ax.set_xscale('symlog')
      
    def set_data(self, data, label):
	self.plot_cdf(data, self.ax, label)

    def set_subplot_data(self, data, label):
        self.ax = self.fig.add_subplot(self.subplot_x, self.subplot_y, self.fig_num)
        #self.ax.set_xscale('log', nonpox='clip')
        self.fig_num += 1
        self.plot_cdf(data, self.ax, label)


    def set_xlim(self, min_value, max_value):
        self.ax.set_xlim(min_value, max_value)
        
    def set_plot_data(self, data, label):
        #self.ax.set_xscale('log', nonpox='clip')
        self.plot_cdf(data, self.ax, label)

    def set_title(self, title):
        #self.ax.title.set_text(title, fontsize=20)
        self.ax.set_title(title, fontsize=20, y=1.02)

    def set_legends(self, legends, title=""):
        plt.legend(legends, loc=2,  title=title, fontsize=12)

    def set_label(self, x, y):
        self.ax.set_xlabel(x, fontsize=16);
        self.ax.set_ylabel(y, fontsize=16);

    def set_xticks(self, xticks):
        self.ax.set_xticklabels(xticks, fontsize=12)
        #plt.xticks(np.arange(len(xticks)), xticks, fontsize=12)

    def set_ylog(self):
        #self.ax.set_yscale('symlog')
        self.ax.set_yscale('close_to_one')
                
    def set_log(self, log):
	CDFPlot.is_log = log;

    def set_xlim(self, minimum, maximum):
        self.ax.set_xlim(minimum, maximum)

    def save_image(self, path):
	self.fig.savefig(path, bbox_inches='tight')
        self.fig.savefig(path + '.eps', bbox_inches='tight', format='eps', dpi=600)
