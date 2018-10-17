import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

sns.set_style("darkgrid")
plt.plot(np.cumsum(np.random.randn(1000,1)))
plt.savefig('Image/20181017/test222.png')
