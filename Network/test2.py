import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json
from scipy.stats.kde import gaussian_kde
from scipy.stats import norm

plt.style.use("ggplot")

f = open("Data/homogeneity.json","r")
data = json.load(f)
e_homogeneity = data['e']
ne_homogeneity = data['ne']
f.close()

d1 = []

mu = np.mean(e_homogeneity)
stdv = np.std(e_homogeneity)

d1_np = np.array(e_homogeneity)
d2_np = np.array(ne_homogeneity)

# Estimating the pdf and plotting
KDEpdf = gaussian_kde(d1_np)
KDEpdf2 = gaussian_kde(d2_np)
#x = np.linspace(-1.0, 1, 20)
x = np.arange(-1, 1.1, 0.1)
fig = plt.figure(figsize=(5,5));
ax = fig.add_subplot(1,1,1);
ax.plot(x,KDEpdf(x),'r',label="Echo Chamber",color="blue")
ax.plot(x,KDEpdf2(x),'r',label="Non Echo Chamber",color="green")
#plt.hist(d1_np,normed=1,color="cyan",alpha=.8)
#plt.plot(x,norm.pdf(x,mu,stdv),label="parametric distribution",color="red")
plt.legend(loc=4)
ax.set_ylabel('PDF', fontsize=20);
ax.set_xlabel('Edge Homogeneity', fontsize=20);

plt.savefig('Image/20180927/aaaa.png', bbox_inches='tight')
