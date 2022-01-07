from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import ContinuousSpace
from mesa.time import StagedActivation, RandomActivation

from model_params import *
from agent import Creature, Candy
from my_math_utils import *
from collectors import *


class Evolution(Model):
    def __init__(self, height=model_height,
                 width=model_width,
                 N_creatures=5, N_candies=10,
                 max_days=30, energy=500, speed=1,
                 ):
        
        # Set up model objects
        compete_stages = ["stage_1_compete"]*100
        model_stages = compete_stages + ["stage_2_test"]
        self.schedule = StagedActivation(model=self,
                                         stage_list=model_stages,
                                         shuffle=True)
        
        # to demonstrate what is going on with staged activation
        self.schedule = RandomActivation(model=self)
        
        self.space = ContinuousSpace(x_max=width, y_max=height,
                                     torus=True, x_min=0, y_min=0)

        self.current_id = 0
        self.N_creatures = N_creatures
        self.N_candies = N_candies
        self.max_days = max_days
        self.height = height
        self.width = width
        self.energy = energy
        self.speed = speed
        
        self.day = 0
        
        # Place creatures
        for i in range(self.N_creatures):
            x_cord = random.uniform(a=0, b=self.width)
            y_cord = random.uniform(a=0, b=self.height)
            pos = (x_cord, y_cord)
            
            new_creature = Creature(unique_id=self.next_id(), pos=pos, model=self)
            self.space.place_agent(agent=new_creature, pos=pos)
            self.schedule.add(new_creature)
            
        # Place candies
        for i in range(self.N_candies):
            x_cord = random.uniform(a=0, b=self.width)
            y_cord = random.uniform(a=0, b=self.height)
            pos = (x_cord, y_cord)
    
            new_candy = Candy(unique_id=self.next_id(), pos=pos, model=self)
            self.space.place_agent(agent=new_candy, pos=pos)
            self.schedule.add(new_candy)
        
        self.running = True
        self.datacollector = DataCollector(
            model_reporters={
                "Energy": count_total_energy,
                "Zero eaters": count_zero_eaters,
                "One eaters": count_one_eaters,
                "Two eaters": count_two_eaters,
            })
    
    def evolve(self):
        agents = self.schedule.agents
        creatures = [agent for agent in agents if isinstance(agent, Creature)]
        energy = np.sum([creature.energy for creature in creatures])
        for creature in creatures:
            print(creature.unique_id, creature.energy)
        
    def step(self):
        self.day += 1
        self.datacollector.collect(self)
    
        # Halt if all days passed
        if self.day < self.max_days:
            self.schedule.step()
            self.evolve()
        else:
            self.running = False
    