import numpy as np

from .agent import Creature, Candy


def total_energy(model):
    """Returns total energy of the population."""
    return sum(map(lambda a: a.energy, model.creatures))


def avg_speed(model):
    """Returns the average speed of the current population."""
    creatures = list(model.creatures)
    if len(creatures) > 0:
        return sum(map(lambda a: a.speed, creatures)) / len(creatures)
    else:
        return 0


def avg_view_range(model):
    """Returns the average view range of the current population."""
    creatures = list(model.creatures)
    if len(creatures) > 0:
        return sum(map(lambda a: a.view_range, creatures), ) / len(creatures)
    else:
        return 0


def avg_focus_angle(model):
    """Returns the average focus angle of the current population."""
    creatures = list(model.creatures)
    if len(creatures) > 0:
        return sum(map(lambda a: a.focus_angle, creatures), ) / len(creatures)
    else:
        return 0


def avg_mut_rate(model):
    """Returns the average mutation rate of the current population."""
    creatures = list(model.creatures)
    if len(creatures) > 0:
        return sum(map(lambda a: a.mut_rate, creatures), ) / len(creatures)
    else:
        return 0
    
    
def energy_on_movement(model):
    """Returns total energy spent for movement by population."""
    return sum(map(lambda a: a.energy_used_for_movement, model.creatures))


def energy_on_view_range(model):
    """Returns total energy spent for view range by population."""
    return sum(map(lambda a: a.energy_spent_on_view_range, model.creatures))


def energy_on_focus_angle(model):
    """Returns total energy spent for focus angle by population."""
    return sum(map(lambda a: a.energy_spent_on_focus_angle, model.creatures))


def count_zero_eaters(model):
    """Returns the number of creatures which have eaten `0` candies."""
    return len(
        [
            a for a in model.schedule.agents
            if isinstance(a, Creature) and a.eaten_candies == 0
        ],
    )


def count_one_eaters(model):
    """Returns the number of creatures which have eaten `1` candies."""
    return len(
        [
            a for a in model.schedule.agents
            if isinstance(a, Creature) and a.eaten_candies == 1
        ],
    )


def count_two_eaters(model):
    """Returns the number of creatures which have eaten `2` candies."""
    return len(
        [
            a for a in model.schedule.agents
            if isinstance(a, Creature) and a.eaten_candies == 2
        ],
    )


def avg_steps_by_zero_eaters(model):
    """Returns average number of steps of zero eaters."""
    steps = [
            a.done_steps for a in model.schedule.agents
            if isinstance(a, Creature) and a.eaten_candies == 0
        ]
    if steps:
        return np.average(steps)
    else:
        return np.NaN
       

def avg_steps_by_one_eaters(model):
    """Returns average number of steps of zero eaters."""
    steps = [
        a.done_steps for a in model.schedule.agents
        if isinstance(a, Creature) and a.eaten_candies == 1
    ]
    if steps:
        return np.average(steps)
    else:
        return np.NaN
    

def avg_steps_by_two_eaters(model):
    """Returns average number of steps of zero eaters."""
    steps = [
        a.done_steps for a in model.schedule.agents
        if isinstance(a, Creature) and a.eaten_candies == 2
    ]
    if steps:
        return np.average(steps)
    else:
        return np.NaN


def count_creatures(model):
    """Return num of creatures in model."""
    return len(list(model.creatures))


def count_candies(model):
    """Return num of candies in model."""
    return len(list(model.candies))
