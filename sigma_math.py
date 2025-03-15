from scipy.stats import norm


SIGMA = 1
MU = 0


def Phi(mu, sigma, x):
    return norm.cdf(x, loc=mu, scale=sigma)


def get_sigma(k: float, p: float, l, r):
    return (k*p)/(Phi(MU, SIGMA, r) - Phi(MU, SIGMA, l))

def calc_leaving_people(time: int, k: float, p: float):
    sigma = get_sigma(k, p, 0, 12)
    return get_sigma()