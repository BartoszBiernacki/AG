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
    MUT_RATE = 0.25
    MAX_SPEED = 1
    VIEW_RANGE = 5

    def __init__(
        self,
        height=HEIGHT,
        width=WIDTH,
        n_creatures=CREATURES,
        n_candies=CANDIES,
        max_days=MAX_DAYS,
        energy=ENERGY,
        mut_rate=MUT_RATE,
        speed=MAX_SPEED,
        view_range=VIEW_RANGE,
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
        self.days = max_days
        self.height = height
        self.width = width

        # Base creature boundaries
        self.max_energy = energy
        self.max_speed = speed
        self.max_view_range = view_range
        self.max_mut_rate = mut_rate

        # Place creatures
        for _ in range(self.n_creatures):
            pos = (
                random.uniform(a=0, b=self.width),
                random.uniform(a=0, b=self.height),
            )
            new_creature = Creature(
                unique_id=self.next_id(),
                pos=pos,
                model=self,
            )
            self.space.place_agent(agent=new_creature, pos=pos)
            self.schedule.add(new_creature)

        # Place candies
        for _ in range(self.n_candies):
            pos = (
                random.uniform(a=0, b=self.width),
                random.uniform(a=0, b=self.height),
            )

            new_candy = Candy(unique_id=self.next_id(), pos=pos, model=self)
            self.space.place_agent(agent=new_candy, pos=pos)
            self.schedule.add(new_candy)

        self.running = True
        self.day = 0

        self.datacollector = DataCollector(
            model_reporters={
                "Energy": lambda model: model.total_energy,
                "Zero eaters": lambda model: model.count_eaters(0),
                "One eaters": lambda model: model.count_eaters(1),
                "Two eaters": lambda model: model.count_eaters(2),
            })

    def evolve(self):
        """Evolves the creatures at the end of the day.

        The creatures are processed as follows:
            a) if they ate no candies they die;
            b) if they ate 1 candy they survive, but recieve a 50% energy
               penalty the next day;
            c) if they ate 2 candies they become parents and reproduce by
               pairing randomly to produce offspring as described in
               `self.crossover()`.
        """
        # Kill the weak
        for weak in filter(
                lambda a: isinstance(a, Creature) and a.eaten_candies == 0,
                self.schedule.agents,
        ):
            self.schedule.remove(weak)

        # The strong procreate
        parents = [
            a for a in self.schedule.agents
            if isinstance(a, Creature) and a.eaten_candies == 2
        ]
        random.shuffle(parents)
        for i in range(0, len(parents), 2):
            self.crossover(parents[i], parents[i + 1])

        # If there is an odd number of parents the last one is skipped - pair
        # him with a random partner
        if len(parents) % 2 == 1:
            self.crossover(parents[-1], random.choice(parents[:-1]))

    def crossover(self, *parents):
        """Perform a crossover between `parents`.

        In each crossover a pair of children is produced by mixing the parents'
        genes in a random proportion. The offspring is also mutated according
        to a mix of parents' mutation rates and placed randomly.
        """
        mix = random.uniform(0, 1)

        for i in [0, 1]:
            p1 = parents[i]
            p2 = parents[i ^ 1]

            # Crossover
            speed = mix * p1.speed + (1 - mix) * p2.speed
            focus_angle = mix * p1.focus_angle + (1 - mix) * p2.focus_angle
            view_range = mix * p1.view_range + (1 - mix) * p2.view_range
            mut_rate = mix * p1.mut_rate + (1 - mix) * p2.mut_rate

            # Mutate
            focus_angle += mut_rate * random.gauss(0, 1)
            view_range += mut_rate * random.gauss(0, 1)
            speed += mut_rate * random.gauss(0, 1)

            pos = (
                random.uniform(0, self.width),
                random.uniform(0, self.height),
            )

            offspring = Creature(
                speed=speed,
                focus_angle=focus_angle,
                view_range=view_range,
                pos=pos,
                mut_rate=mut_rate,
                unique_id=self.next_id(),
                model=self,
            )
            self.space.place_agent(agent=offspring, pos=pos)
            self.schedule.add(offspring)

    def step(self):
        self.day += 1
        self.datacollector.collect(self)

        # Halt if all days passed
        if self.day < self.days:
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
