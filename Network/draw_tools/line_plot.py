import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from cycler import cycler

class LinePlot:
    is_log = False;

    def __init__(self):
	self.fig = plt.figure(figsize=(10,5));
	self.ax = self.fig.add_subplot(1,1,1);
        self.x_label = 'x';
	self.y_label = 'y';

    def plot_line(self, data, ax, label):
        if type(data[0]) is not list:
            ax.plot(data, label=label, linewidth=2.0)
        else:
            for i in range(len(data)):
                ax.plot(data[i], label=label, linewidth=2.0)
        ax.set_xlabel(self.x_label, fontsize=16);
        ax.set_ylabel(self.y_label, fontsize=16);

    def set_sns_plot(self, data):
        sns.set_style("darkgrid")
        self.ax = sns.lineplot(x="depth", y="time", hue="type", data=data)
	self.fig.savefig('Image/20181017/line22222.png', bbox_inches='tight')

    def set_plot_data(self, data, label):
        #self.ax.set_xscale('log', nonpox='clip')
        #colors = [plt.cm.spectral(i) for i in np.linspace(0, 1, len(data))]
        #self.ax.set_prop_cycle(cycler('color', colors))
        self.plot_line(data, self.ax, label)

    def set_xticks(self, xticks, rotation = 'horizontal'):
        plt.xticks(np.arange(len(xticks)), xticks, rotation=rotation)

    def set_legends(self, legends, title=""):
        box = self.ax.get_position()
        self.ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        #plt.legend(legends, loc='center left', title=title, fontsize=10, bbox_to_anchor=(1, 0.5))
        #plt.legend(legends, loc=4, title=title, fontsize=10, bbox_to_anchor=(1, 0.5))
        plt.legend(legends, loc=4, title=title, fontsize=14)

    def set_label(self, x, y):
	self.x_label = x;
	self.y_label = y;

    def set_ylim(self, value):
        self.ax.set_ylim(0, value)

    def set_ylog(self):
        self.ax.set_yscale('symlog')

    def set_xlog(self):
        self.ax.set_xscale('symlog')
    
    def set_axvline(self, lines, published_date):
        for line in lines:
            plt.axvline(x=line, color='r', linestyle='--', linewidth=1)
            
        plt.axvline(x=published_date, color='g', linestyle='--', linewidth=2)
    
    def set_hline(self, lines, start, end):
        for line in lines:
            plt.hlines(line, start, end,  color='r', linestyle='--', linewidth=1)

    def save_image(self, path):
	self.fig.savefig(path, bbox_inches='tight')
	self.fig.savefig(path + '.eps', bbox_inches='tight')
