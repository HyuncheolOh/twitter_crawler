import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import math
from numpy import ma
from matplotlib import scale as mscale
from matplotlib import transforms as mtransforms
from matplotlib.ticker import FixedFormatter, FixedLocator



num = 5
def set_label_num(value):
    global num
    num = value

class CloseToOne(mscale.ScaleBase):
    name = 'close_to_one'

    def __init__(self, axis, **kwargs):
        mscale.ScaleBase.__init__(self)
        self.nines = kwargs.get('nines', num)

    def get_transform(self):
        return self.Transform(self.nines)
        #return self.InvertedTransform(self.nines)

    def set_default_locators_and_formatters(self, axis):
        axis.set_major_locator(FixedLocator(
                np.array([1-10**(-k) for k in range(1+self.nines)])))
        axis.set_major_formatter(FixedFormatter(
                [str(1-10**(-k)) for k in range(1+self.nines)]))


    def limit_range_for_scale(self, vmin, vmax, minpos):
        return vmin, min(1 - 10**(-self.nines), vmax)

    class Transform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def __init__(self, nines):
            mtransforms.Transform.__init__(self)
            self.nines = nines

        def transform_non_affine(self, a):
            masked = ma.masked_where(a > 1-10**(-1-self.nines), a)
            if masked.mask.any():
                return -ma.log10(1-a)
            else:
                return -np.log10(1-a)

        def inverted(self):
            return CloseToOne.InvertedTransform(self.nines)

    class InvertedTransform(mtransforms.Transform):
        input_dims = 1
        output_dims = 1
        is_separable = True

        def __init__(self, nines):
            mtransforms.Transform.__init__(self)
            self.nines = nines

        def transform_non_affine(self, a):
            return 1. - 10**(-a)

        def inverted(self):
            return CloseToOne.Transform(self.nines)

mscale.register_scale(CloseToOne)


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
        ax.plot(sorted_vals, p, label=label, linewidth = 2.0)
        
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

    def set_legends(self, legends, title=""):
        plt.legend(legends, loc=4, title=title, fontsize=9)

    def set_label(self, x, y):
        self.ax.set_xlabel(x);
        self.ax.set_ylabel(y);


    def set_ylog(self):
        #self.ax.set_yscale('symlog')
        self.ax.set_yscale('close_to_one')
                
    def set_log(self, log):
	CDFPlot.is_log = log;

    def set_xlim(self, minimum, maximum):
        self.ax.set_xlim(minimum, maximum)

    def save_image(self, path):
	self.fig.savefig(path, bbox_inches='tight')
