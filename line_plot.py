import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler

class LinePlot:
    is_log = False;

    def __init__(self):
	self.fig = plt.figure(figsize=(10,10));
	self.ax = self.fig.add_subplot(1,1,1);
        self.x_label = 'x';
	self.y_label = 'y';

    def plot_line(self, data, ax, label):
        if type(data[0]) is not list:
            ax.plot(data, label=label, linewidth=2.0)
        else:
            for i in range(len(data)):
                ax.plot(data[i], label=label, linewidth=2.0)
        if LinePlot.is_log == True: 
#	    ax.set_xscale('log')
            ax.set_xscale('symlog')
        ax.set_xlabel(self.x_label);
        ax.set_ylabel(self.y_label);

    def set_plot_data(self, data, label):
        #self.ax.set_xscale('log', nonpox='clip')
        colors = [plt.cm.spectral(i) for i in np.linspace(0, 1, len(data))]
        self.ax.set_prop_cycle(cycler('color', colors))
        self.plot_line(data, self.ax, label)

    def set_xticks(self, xticks, rotation = 'horizontal'):
        plt.xticks(np.arange(len(xticks)), xticks, rotation=rotation)

    def set_legends(self, legends, title=""):
        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        plt.legend(legends, loc='center left', title=title, fontsize=10, bbox_to_anchor=(1, 0.5))

    def set_label(self, x, y):
	self.x_label = x;
	self.y_label = y;

    def set_ylim(self, value):
        self.ax.set_ylim(0, value)

    def set_log(self, log):
        LinePlot.is_log = log;

    def save_image(self, path):
	self.fig.savefig(path, bbox_inches='tight')
