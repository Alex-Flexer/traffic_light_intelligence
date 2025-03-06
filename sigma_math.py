from scipy.stats import norm
import math

sigma = 1
mu = 0

def Phi(mu, sigma, x):
    return norm.cdf(x, loc = mu, scale = sigma)


# print(Phi(mu, sigma, 3) - Phi(mu, sigma, -3))

sigmus = (k*pol)/(Phi(mu, sigma, 3) - Phi(mu, sigma, -3))
print(sigmus)
