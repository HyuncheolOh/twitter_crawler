import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

class CDFCCDFPlot():

    def __init__(self):
        self.fig = plt.figure(figsize=(5,5));
	self.ax = self.fig.add_subplot(1,1,1);
        #self.axin = inset_axes(self.ax, width='40%', height='40%', loc=2, bbox_to_anchor=(0.5, 0, 1,1))
        #self.axin = inset_axes(self.ax, width='40%', height='40%', loc=4, bbox_to_anchor=(-0.1, .9, 1, 1), bbox_transform=self.ax.transAxes)
        #self.axin = inset_axes(self.ax, width='50%', height='50%', loc=4, bbox_to_anchor=(-0.1, .1, 1, 1), bbox_transform=self.ax.transAxes)
        self.axin = inset_axes(self.ax, width='40%', height='40%', loc=4, bbox_to_anchor=(-0.05, .1, 1, 1), bbox_transform=self.ax.transAxes)
        self.count = 0
        #self.colors = ['#1f78b4', '#33a02c']
        #self.colors = ['#377eb8', '#4daf4a']  #blue, green
        self.colors = ['r', 'b'] #green ,orange 

    def plot_cdf(self, data, ax):
        sorted_vals = np.sort(data)
        p = 1. * np.arange(len(data)) / (len(data) - 1)
        if self.count == 1:
            ax.plot(sorted_vals, p, self.colors[self.count], linewidth=2, linestyle='--')   
        else:
            ax.plot(sorted_vals, p, self.colors[self.count], linewidth=2)   
        #ax.set_ticks
        #ax.set_xticks(np.arange(len([0,1,10,100,1000])), [0,1,10,100,1000])
    
    def plot_ccdf(self, data, ax):
        degree_sequence = np.array(data)
        uniques, counts = np.unique(degree_sequence, return_counts=True)
        cumprob = np.cumsum(counts).astype(np.double) / (degree_sequence.size)
    
        x_ccdf, y_ccdf = uniques[::-1], (1. - cumprob)[::-1]
        ax.set_yscale('log')
        ax.set_ylabel('CCDF');
        #ax.step(x_ccdf, y_ccdf, lw=1.5)
        if self.count == 1:
            ax.step(x_ccdf, y_ccdf, self.colors[1],linewidth=2, linestyle='--')
        else:
            ax.step(x_ccdf, y_ccdf, self.colors[1], linewidth=2)
        
        #ax.set_xticks(np.arange(len([0,1,10,100,1000])), [0,1,10,100,1000])
        #for tick in ax.xaxis.get_major_ticks():
        #    tick.label.set_fontsize(10)
        #for tick in ax.yaxis.get_major_ticks():
        #    tick.label.set_fontsize(10)

    def set_data(self, data):
	self.plot_cdf(data, self.ax)
	self.plot_ccdf(data, self.axin)
        self.count += 1


    def set_title(self, title):
        #self.ax.title.set_text(title, fontsize=20)
        self.ax.set_title(title, fontsize=20, y=1.02)

    def set_legends(self, legends, title=""):
        #plt.legend(legends, loc=2,  title=title, fontsize=12, bbox_to_anchor=(0.5, 1.75))
        legend = plt.legend(legends, loc=2,  title=title, fontsize=12, bbox_to_anchor=(-0.1, 1.7), framealpha=1, fancybox=True)
        legend.get_frame().set_edgecolor('grey')

    def set_label(self, x, y):
        self.ax.set_xlabel(x, fontsize=16);
        self.ax.set_ylabel(y, fontsize=16);

    def set_xticks(self, xticks):
        self.ax.set_xticklabels(xticks, fontsize=12)
        #plt.xticks(np.arange(len(xticks)), xticks, fontsize=12)

    def set_ylog(self):
        self.ax.set_yscale('symlog')
                
    def set_xlog(self):
        self.ax.set_xscale('symlog')
        self.axin.set_xscale('symlog')

    def set_xlim(self, minimum, maximum):
        self.ax.set_xlim(minimum, maximum)

    def save_image(self, path):
        self.fig.savefig(path, bbox_inches='tight')
        self.fig.savefig(path + '.eps', bbox_inches='tight', format='eps', dpi=600)


