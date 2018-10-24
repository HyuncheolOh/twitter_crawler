import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json
from scipy.stats.kde import gaussian_kde
from scipy.stats import norm



def draw_multiline_pdf(data, xlabel, legends, path):
    fig = plt.figure(figsize=(7,7));
    ax = fig.add_subplot(1,1,1);
    x = np.arange(-1, 1.1, 0.1)
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    for i in range(len(data)):
        d1_np = np.array(data[i])
        #print(d1_np)
        KDEpdf = gaussian_kde(d1_np)
        ax.plot(x, KDEpdf(x), 'r', label=legends[i], color=colors[i])

    plt.legend(loc=4)
    ax.set_ylabel('PDF', fontsize=20);
    ax.set_xlabel(xlabel, fontsize=20);
    plt.savefig(path, bbox_inches='tight')
    plt.savefig(path+'.eps', bbox_inches='tight')


def draw_pdf(data, xlabel, legends, path):
#    plt.style.use("ggplot")

    #f = open("Data/homogeneity.json","r")
    #data = json.load(f)
    e_homogeneity = data['e']
    ne_homogeneity = data['ne']
    
    legend1 = legends[0]
    legend2 = legends[1]
    
    #f.close()

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
    fig = plt.figure(figsize=(7,7));
    ax = fig.add_subplot(1,1,1);
    ax.plot(x,KDEpdf(x),'r',label=legend1,color="blue")
    ax.plot(x,KDEpdf2(x),'r',label=legend2,color="green")
    #plt.hist(d1_np,normed=1,color="cyan",alpha=.8)
    #plt.plot(x,norm.pdf(x,mu,stdv),label="parametric distribution",color="red")
    plt.legend(loc=4)
    ax.set_ylabel('PDF', fontsize=20);
    ax.set_xlabel(xlabel, fontsize=20);

    plt.savefig(path, bbox_inches='tight')
    plt.savefig(path+'.eps', bbox_inches='tight')
