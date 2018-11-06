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
        self.fig = plt.figure(figsize=(7,4))
        self.subplot_x = subplot_num
        self.subplot_y = subplot_num
        #self.colors = ['#FC4F30', '#008FD5']
        #self.colors = ['#1f78b4', 'g'] #green, darkblue
        self.colors = ['#e41a1c', '#377eb8'] #green ,orange 

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
        self.set_box_color(bpl, self.colors[0]) # colors are from http://colorbrewer2.org/
        self.set_box_color(bpr, self.colors[1])

        # draw temporary red and blue lines and use them to create a legend
        plt.plot([], c=self.colors[0], label='Echo chamber')
        plt.plot([], c=self.colors[1], label='Non echo chamber')
        legend = plt.legend(fontsize=12, loc='upper center', ncol=2, bbox_to_anchor=(0.5, 1.14), framealpha=1, fancybox=True)
        legend.get_frame().set_edgecolor('grey')
       
        #ax.legend((rects1[0], rects2[0], rects3[0]), ('Fauxtography', 'Politics', 'Combined'), loc='upper center', ncol=3, bbox_to_anchor=(0.5, 1.0))
        ticks = np.arange(1,11)
        plt.xticks(xrange(0, len(ticks) * 2, 2), ticks, fontsize=12)
        plt.xlim(-2, len(ticks)*2)
        #plt.ylim(0, 8)

    def set_data_with_position(self, data, lebel, grid):
        self.ax = self.fig.add_subplot(grid)
        self.ax.boxplot(data, showfliers = True)

    def set_xticks(self, xticks,index = None,  rotation = 'horizontal'):
        if index == None:
            plt.xticks(np.arange(len(xticks)), xticks, rotation=rotation)
        else :
            plt.xticks(index, xticks, rotation=rotation)

        
    def set_yticks(self, yticks, index = None, rotation = 'horizontal'):
        if index == None:
            plt.yticks(np.arange(len(yticks)), yticks, rotation=rotation)
        else:
            plt.yticks(index, yticks, rotation=rotation)
            #plt.locator_params(numticks=len(index))
            plt.minorticks_off()

    def set_label(self, x, y):
        self.ax.set_xlabel(x, fontsize=16);
        self.ax.set_ylabel(y, fontsize=16);

    def set_ylim(self, value):
        self.ax.set_ylim(0, value)

    def set_ylog(self):
        self.ax.set_yscale('symlog')

    def set_xlog(self):
        self.ax.set_xscale('symlog')

    def save_image(self, path):
        plt.savefig(path, bbox_inches='tight')
        plt.savefig(path + '.eps', bbox_inches='tight')

