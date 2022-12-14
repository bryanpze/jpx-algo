# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 17:08:58 2018

@author: Ernest
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt # For debug only


def genhurst(z):
    z = pd.DataFrame(z)
    taus = list(range(1, int(len(z) / 10)))
    logVar = np.array([np.log(z.diff(tau).var(ddof=0)) for tau in taus])

    X = np.log(taus)
    y = logVar

    X = sm.add_constant(X)
    model = sm.OLS(y, X)
    results = model.fit()
    H = results.params[1] / 2
    pVal = results.pvalues[1]
    return H, pVal


def genhurst1(z):
# =============================================================================
# calculation of Hurst exponent given log price series z
# =============================================================================
    z=pd.DataFrame(z)
    
    # We cannot use tau that is of same magnitude of time series length
    taus = np.arange(np.round(len(z)/10)).astype(int)
    logVar = np.empty(len(taus)) # log variance

    for tau in taus:
        logVar[tau] = np.log(z.diff(int(tau)).var(ddof=0))
        
    X=np.log(taus)
    Y=logVar[:len(taus)]
    X=X[np.isfinite(logVar)]
    Y=Y[np.isfinite(logVar)]
    # pd.DataFrame(np.asmatrix([X, Y]).T).to_csv('XY.csv')

    X = sm.add_constant(X)
    # plt.scatter(X[:,1], Y) # for debug only
    model=sm.OLS(Y, X)
    results=model.fit()
    H=results.params[1]/2
    pVal=results.pvalues[1]
    return H, pVal