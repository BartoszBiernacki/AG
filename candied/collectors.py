"""Defines data collector functions.

All functions take a single argument - `model` or `agent` and return a number
that represents some meaningful value we wish to collect.
"""


def total_energy(model):
    """Returns total energy of the population."""
    return sum(map(lambda a: a.energy, model.creatures))


def avg_speed(model):
    """Returns the average speed of the current population."""
    creatures = list(model.creatures)
    if len(creatures) > 0:
        return sum(map(lambda a: a.speed, creatures)) / len(creatures)
    return 0


def avg_view_range(model):
    """Returns the average view range of the current population."""
    creatures = list(model.creatures)
    if len(creatures) > 0:
        return sum(map(lambda a: a.view_range, creatures), ) / len(creatures)
    return 0


def avg_focus_angle(model):
    """Returns the average focus angle of the current population."""
    creatures = list(model.creatures)
    if len(creatures) > 0:
        return sum(map(lambda a: a.focus_angle, creatures), ) / len(creatures)
    return 0


def avg_mut_rate(model):
    """Returns the average mutation rate of the current population."""
    creatures = list(model.creatures)
    if len(creatures) > 0:
        return sum(map(lambda a: a.mut_rate, creatures), ) / len(creatures)
    return 0


def count_zero_eaters(model):
    """Returns the number of creatures which have eaten `0` candies."""
    return len(list(filter(lambda c: c.eaten_candies == 0, model.creatures)))


def count_one_eaters(model):
    """Returns the number of creatures which have eaten `1` candy."""
    return len(list(filter(lambda c: c.eaten_candies == 1, model.creatures)))


def count_two_eaters(model):
    """Returns the number of creatures which have eaten `2` candies."""
    return len(list(filter(lambda c: c.eaten_candies == 2, model.creatures)))


def count_creatures(model):
    """Return num of creatures in model."""
    return len(list(model.creatures))


def count_candies(model):
    """Return num of candies in model."""
    return len(list(model.candies))
