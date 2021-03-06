#!/usr/bin/env python
# coding: utf-8

import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from profit.sur.backend.gp import GPSurrogate


#%% Define some model f(u, v)
def rosenbrock(x, y, a, b):
    return (a - x)**2 + b * (y - x**2)**2
def f(r, u, v):
    return rosenbrock((r - 0.5) + u - 5, 1 + 3 * (v - 0.6), a=1, b=3)/20

u = np.linspace(4.7, 5.3, 20)
v = np.linspace(0.55, 0.6, 20)
y = np.fromiter((f(0.25, uk, vk) for vk in v for uk in u), float)
[U,V] = np.meshgrid(u, v)
Y = y.reshape(U.shape)

plt.figure()
plt.contour(U,V,Y)
plt.colorbar()
plt.show()

#%% Generate training data
utrain = u[::5]
vtrain = v[::5]
xtrain = np.array([[uk, vk] for vk in vtrain for uk in utrain])
ytrain = np.fromiter((f(0.25, uk, vk) for vk in vtrain for uk in utrain), float)
ntrain = len(ytrain)


#%% Create and train surrogate
sur = GPSurrogate()
sur.train(xtrain, ytrain)

#%% Compute surrogate predictor for test input
xtest = np.array([[uk, vtrain[1]] for uk in u])
ftest = sur.predict(xtest)

# reference for checking only:
ytest = np.fromiter((f(0.25, xk[0], xk[1]) for xk in xtest), float)

plt.figure()
plt.errorbar(xtrain[4:8,0], ytrain[4:8], sur.sigma*1.96, capsize=2, fmt='.')
plt.plot(xtest[:,0], ytest)
plt.plot(xtest[:,0], ftest)
plt.xlabel('u')
plt.ylabel('f(u,v0)')

#%% Plot likelihood over hyperparameters
from profit.sur.backend.gp import gp_nll

hypaplot = np.empty([100,2])
hypaplot[:,0] = np.linspace(1.0,4.0,100)
hypaplot[:,1] = 1.0
nlls = np.fromiter(
        (gp_nll(hyp, xtrain, ytrain, sur.sigma) for hyp in hypaplot), float)
plt.figure()
plt.title('Negative log likelihood in kernel hyperparameters')
plt.plot(hypaplot[:,0], nlls)
plt.xlabel('l')
plt.ylabel('-log p(y|u,v0) + C')
plt.show()


sigplot = np.linspace(1e-2*(np.max(ytrain)-np.min(ytrain)),1e-3,40)
nlls = np.fromiter(
        (gp_nll([2.08,1.0], xtrain, ytrain, sig) for sig in sigplot), float)
plt.figure()
plt.title('Negative log likelihood in kernel hyperparameters')
plt.plot(sigplot, nlls)
plt.xlabel('sigma')
plt.ylabel('-log p(y|u,v0) + C')
plt.show()



# %%
