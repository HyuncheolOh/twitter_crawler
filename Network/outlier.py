import numpy
from draw_tools.cdf_plot import CDFPlot

def remove_outlier(arr):
    if len(set(arr)) == 1 or len(arr) == 1:
        return arr

    elements = numpy.array(arr)

    mean = numpy.mean(elements, axis=0)
    sd = numpy.std(elements, axis=0)

    final_list = [x for x in arr if (x > mean - 2 * sd)]
    final_list = [x for x in final_list if (x < mean + 2 * sd)]

    return final_list

'''
cdf = CDFPlot()
cdf.set_log(True)
#cdf.set_ylog()
cdf.set_data(arr, 'True')
cdf.save_image('test1.png')

cdf = CDFPlot()
cdf.set_log(True)
#cdf.set_ylog()
cdf.set_data(final_list, 'True')
cdf.save_image('test2.png')
'''
