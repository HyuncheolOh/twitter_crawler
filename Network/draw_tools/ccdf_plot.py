from __future__ import division
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math 

class CCDFPlot:
    is_log = False;

    def __init__(self):
	self.fig = plt.figure(figsize=(5,5));
	self.ax = self.fig.add_subplot(1,1,1);
        self.x_label = 'x';
	self.y_label = 'y';

    def plot_ccdf(self, data, ax, label):
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
        logcdfy = [-math.log10(1.0 - (float(idx) / len(data)))
                           for idx in range(len(data))]
        print(max(logcdfy))
        #labels = ['0.0001', '0.001', '0.01', '0.10', '1', '10', '100']
        labels = ['', '90', '99', '99.9', '99.99', '99.999', '99.9999', '99.99999']

        #labels = ['0.10', '1', '10', '100']
        max_num = int(math.ceil(max(logcdfy))+1)
        labels = labels[0 : max_num]
        print(labels)
        #ax.plot(sorted_vals, max_num - np.array(logcdfy), label=label)
        ax.plot(sorted_vals, np.array(logcdfy), label=label)
        ax.set_xlim(min(data), max(data) * 1.01)
        ax.set_ylim(0, math.ceil(max(logcdfy)))
        ax.set_yticklabels(labels)
       	if CCDFPlot.is_log == True: 
            ax.set_xscale('symlog')
        ax.set_xlabel(self.x_label);
        ax.set_ylabel(self.y_label);

    def set_data(self, data, label):
	self.plot_ccdf(data, self.ax, label)

    def set_subplot_data(self, data, label):
        self.ax = self.fig.add_subplot(self.subplot_x, self.subplot_y, self.fig_num)
        #self.ax.set_xscale('log', nonpox='clip')
        self.fig_num += 1
        self.plot_ccdf(data, self.ax, label)


    def set_xlim(self, min_value, max_value):
        self.ax.set_xlim(min_value, max_value)
        
    def set_plot_data(self, data, label):
        #self.ax.set_xscale('log', nonpox='clip')
        self.plot_ccdf(data, self.ax, label)

    def set_legends(self, legends, title=""):
        plt.legend(legends, loc=4, title=title, fontsize=9)

    def set_label(self, x, y):
	self.x_label = x;
	self.y_label = y;

    def set_log(self, log):
	CCDFPlot.is_log = log;

    def set_xlim(self, minimum, maximum):
        self.ax.set_xlim(minimum, maximum)

    def save_image(self, path):
	self.fig.savefig(path, bbox_inches='tight')
