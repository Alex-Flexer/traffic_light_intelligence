from datetime import timedelta
from scipy.stats import norm


SIGMA = 1.8
CITIZENS_MU = 8
GUESTS_MU = 18

HOUR = 3600


def get_leaving_citizens_factor(time: timedelta, delta: timedelta) -> float:
    hours = time.seconds / HOUR
    dx = delta.seconds / HOUR
    return norm.pdf(hours, loc=CITIZENS_MU, scale=SIGMA) * dx


def get_leaving_guests_factor(time: timedelta, delta: timedelta) -> float:
    hours = time.seconds / HOUR
    dx = delta.seconds / HOUR
    return norm.pdf(hours, loc=GUESTS_MU, scale=SIGMA) * dx
