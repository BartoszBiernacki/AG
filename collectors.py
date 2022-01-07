from agent import Creature


def count_total_energy(model):
    agents = model.schedule.agents
    creatures = [agent for agent in agents if isinstance(agent, Creature)]
    energy = 0
    for creature in creatures:
        energy += creature.energy
        
    return energy


def count_zero_eaters(model):
    agents = model.schedule.agents
    creatures = [agent for agent in agents if isinstance(agent, Creature)]
    zero_eaters = 0
    for creature in creatures:
        if creature.eaten_candies == 0:
            zero_eaters += 1
    
    return zero_eaters


def count_one_eaters(model):
    agents = model.schedule.agents
    creatures = [agent for agent in agents if isinstance(agent, Creature)]
    one_eaters = 0
    for creature in creatures:
        if creature.eaten_candies == 1:
            one_eaters += 1
    
    return one_eaters


def count_two_eaters(model):
    agents = model.schedule.agents
    creatures = [agent for agent in agents if isinstance(agent, Creature)]
    two_eaters = 0
    for creature in creatures:
        if creature.eaten_candies == 2:
            two_eaters += 1
    
    return two_eaters
