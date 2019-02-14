import numpy as np

def Poisson(lam=2, noise=0):
    '''
    The function used to create the actual device performance data

    :param lambda: Mean of the normal distribution to draw the metric from
    :param noise: Added noise, (Drawn from distribution of Normal(0, noise)
    :return: Metric
    '''
    # while True:
    added_noise = 0
    if noise is not 0:
        added_noise = np.random.normal(loc=0, scale=noise, size=1)
    tick = np.random.poisson(lam=lam, size=1) + added_noise
    return tick