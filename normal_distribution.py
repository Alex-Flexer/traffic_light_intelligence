from scipy.stats import norm


SIGMA = 3
CITIZENS_MU = 6
GUESTS_MU = 18


def get_leaving_citizens_factor(time: int) -> float:
    return norm.pdf(time % 24, loc=CITIZENS_MU_MU, scale=SIGMA)


def get_leaving_guests_factor(time: int) -> float:
    return norm.pdf(time % 24, loc=GUESTS_MU, scale=SIGMA)
