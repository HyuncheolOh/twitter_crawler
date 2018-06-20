import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
class CDFPlot:
    is_log = False;

    def __init__(self):
	self.fig = plt.figure(figsize=(5,5));
	self.ax = self.fig.add_subplot(1,1,1);
        self.x_label = 'x';
	self.y_label = 'y';

    '''
    #for the subplot
    def __init__(self, subplot_x, subplot_y):
        self.fig_num = 1 
	self.fig = plt.figure(figsize=(20,20));
        self.x_label = 'x';
	self.y_label = 'y';
        self.subplot_x = subplot_x
        self.subplot_y = subplot_y
    '''
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
        p = 1. * np.arange(len(data)) / (len(data) - 1)
        ax.plot(sorted_vals, p, label=label)
	if CDFPlot.is_log == True: 
#	    ax.set_xscale('log')
            ax.set_xscale('symlog')
        ax.set_xlabel(self.x_label);
        ax.set_ylabel(self.y_label);

    def set_data(self, data, label):
	self.plot_cdf(data, self.ax, label)

    def set_subplot_data(self, data, label):
        self.ax = self.fig.add_subplot(self.subplot_x, self.subplot_y, self.fig_num)
        #self.ax.set_xscale('log', nonpox='clip')
        self.fig_num += 1
        self.plot_cdf(data, self.ax, label)

    def set_plot_data(self, data, label):
        #self.ax.set_xscale('log', nonpox='clip')
        self.plot_cdf(data, self.ax, label)

    def set_legends(self, legends, title=""):
        plt.legend(legends, loc=4, title=title, fontsize=9)

    def set_label(self, x, y):
	self.x_label = x;
	self.y_label = y;

    def set_log(self, log):
	CDFPlot.is_log = log;

    def save_image(self, path):
	self.fig.savefig(path, bbox_inches='tight')
