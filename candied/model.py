"""Evolution model module.

Defines the Evolution model class.
"""
import random

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation, StagedActivation

from .agent import Candy, Creature


class Evolution(Model):
    """Evolution model class.

    TODO: describe this better.
    """
    HEIGHT = 200
    WIDTH = 200
    CREATURES = 5
    CANDIES = 10
    MAX_DAYS = 30
    ENERGY = 500

    def __init__(
        self,
        height=HEIGHT,
        width=WIDTH,
        n_creatures=CREATURES,
        n_candies=CANDIES,
        max_days=MAX_DAYS,
        energy=ENERGY,
        speed=1,
    ):
        super().__init__()

        # Set up model objects
        compete_stages = ["stage_1_compete"] * 100
        model_stages = compete_stages + ["stage_2_test"]
        self.schedule = StagedActivation(
            model=self, stage_list=model_stages, shuffle=True)

        # to demonstrate what is going on with staged activation
        self.schedule = RandomActivation(model=self)

        self.space = ContinuousSpace(
            x_max=width, y_max=height, torus=True, x_min=0, y_min=0)

        self.current_id = 0
        self.n_creatures = n_creatures
        self.n_candies = n_candies
        self.max_days = max_days
        self.height = height
        self.width = width
        self.energy = energy
        self.speed = speed

        self.day = 0

        # Place creatures
        for _ in range(self.n_creatures):
            x_cord = random.uniform(a=0, b=self.width)
            y_cord = random.uniform(a=0, b=self.height)
            pos = (x_cord, y_cord)

            new_creature = Creature(
                unique_id=self.next_id(),
                pos=pos,
                model=self,
            )
            self.space.place_agent(agent=new_creature, pos=pos)
            self.schedule.add(new_creature)

        # Place candies
        for _ in range(self.n_candies):
            x_cord = random.uniform(a=0, b=self.width)
            y_cord = random.uniform(a=0, b=self.height)
            pos = (x_cord, y_cord)

            new_candy = Candy(unique_id=self.next_id(), pos=pos, model=self)
            self.space.place_agent(agent=new_candy, pos=pos)
            self.schedule.add(new_candy)

        self.running = True
        self.datacollector = DataCollector(
            model_reporters={
                "Energy": lambda model: model.total_energy,
                "Zero eaters": lambda model: model.count_eaters(0),
                "One eaters": lambda model: model.count_eaters(1),
                "Two eaters": lambda model: model.count_eaters(2),
            })

    def evolve(self):
        """Evolves the agents at the end of the day."""
        # agents = self.schedule.agents
        # creatures = [agent for agent in agents if isinstance(agent, Creature)]
        # energy = self.total_energy
        # for creature in creatures:
        #     print(creature.unique_id, creature.energy)

    def step(self):
        self.day += 1
        self.datacollector.collect(self)

        # Halt if all days passed
        if self.day < self.max_days:
            self.schedule.step()
            self.evolve()
        else:
            self.running = False

    @property
    def total_energy(self):
        """Returns total energy of the population."""
        return sum(
            [
                a.energy
                for a in self.schedule.agents
                if isinstance(a, Creature)
            ],
        )

    def count_eaters(self, i):
        """Returns the number of creatures which have eaten `i` candies."""
        return len(
            [
                a for a in self.schedule.agents
                if isinstance(a, Creature) and a.eaten_candies == i
            ],
        )
