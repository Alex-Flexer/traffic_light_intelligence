from datetime import timedelta
from scipy.stats import norm


SIGMA = 1.8
CITIZENS_MU = 8
GUESTS_MU = 18

HOUR = 3600


def get_leaving_citizens_factor(time: timedelta) -> float:
    hours = time.seconds / HOUR
    return norm.pdf(hours, loc=CITIZENS_MU, scale=SIGMA)


def get_leaving_guests_factor(time: timedelta) -> float:
    hours = time.seconds / HOUR
    return norm.pdf(hours, loc=GUESTS_MU, scale=SIGMA)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    xs = [x/10 for x in range(241)]

    ys = [get_leaving_citizens_factor(x) for x in xs]
    plt.plot(xs, ys)

    ys = [-get_leaving_guests_factor(x) for x in xs]
    plt.plot(xs, ys)

    plt.show()
