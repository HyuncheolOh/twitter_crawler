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

    def set_data(self, data):
       	if CCDFPlot.is_log == True: 
            self.ax.set_xscale('log')

        x_ccdf, y_ccdf = self.get_ccdf(data)
        self.ax.set_yscale('log')
        #ax.step(x_ccdf, y_ccdf, lw=1.5)
        self.ax.step(x_ccdf, y_ccdf)


    def get_ccdf(self, degree_sequence):
        """
        Function to get CCDF of the list of degrees.

        Args:
            degree_sequence: numpy array of nodes' degrees.
        Returns:
            uniques: unique degree values met in the sequence.
            1-CDF: CCDF values corresponding to the unique values
                   from the 'uniques' array.
        """
        degree_sequence = np.array(degree_sequence)
        uniques, counts = np.unique(degree_sequence, return_counts=True)
        cumprob = np.cumsum(counts).astype(np.double) / (degree_sequence.size)
        return uniques[::-1], (1. - cumprob)[::-1]

    def set_xlim(self, min_value, max_value):
        self.ax.set_xlim(min_value, max_value)
        
    def set_legends(self, legends, title=""):
        plt.legend(legends, title=title, fontsize=9)

    def set_label(self, x, y):
        self.ax.set_xlabel(x, fontsize=16);
        self.ax.set_ylabel(y, fontsize=16);

    def set_log(self, log):
	CCDFPlot.is_log = log;

    def save_image(self, path):
	self.fig.savefig(path, bbox_inches='tight')
	self.fig.savefig(path + '.eps', bbox_inches='tight')
