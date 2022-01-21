"""Evolution model module.

Defines the Evolution model class.
"""
import random

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import ContinuousSpace
from mesa.time import RandomActivation, StagedActivation

from .agent import Candy, Creature
from .collectors import *


class Evolution(Model):
    """Evolution model class.

    HEIGHT, WIDTH: size of the grid on which agents live.
    CREATURES, CANDIES: initial number of creatures and candies.
    MAX_DAYS: number of generations to cover.
    ENERGY: default energy which agent has at the beginning of each day.
    MUT_RATE: probability that creature's child will be mutated right
        after creation.
    MAX_SPEED: in initial population creature's speed is a random number
    from uniform distribution from range (0, MAX_SPEED).
    VIEW_RANGE: in initial population creature's view range is a random
        number from uniform distribution from range (0, MAX_VIEW_RANGE).
    MAX_STEPS_PER_DAY: quantized day length. It is the max number of small
         moves creature can do during day while looking for food. If creature
         does not find food in these moves, rest of it's energy is lost. This
         approach penalizes ,,lazy'' creatures: those who move slowly and have
         a short view range.
    """
    HEIGHT = 200
    WIDTH = 200
    CREATURES = 5
    CANDIES = 10
    MAX_DAYS = 30
    ENERGY = 500
    MUT_RATE = 0.25
    MAX_SPEED = 10
    MAX_VIEW_RANGE = 5
    MAX_STEPS_PER_DAY = 100

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
        view_range=MAX_VIEW_RANGE,
        max_steps_per_day=MAX_STEPS_PER_DAY
    ):
        super().__init__()

        # Set up model objects
        preparation_stage = ['stage_0_prepare_for_new_day']
        compete_stages = ["stage_1_compete"] * max_steps_per_day
        report_stage = ['stage_2_report']
        model_stages = preparation_stage + compete_stages + report_stage
        self.schedule = StagedActivation(
            model=self,
            stage_list=model_stages,
            shuffle=True,
        )

        # to demonstrate what is going on with staged activation
        # self.schedule = RandomActivation(model=self)

        self.space = ContinuousSpace(
            x_max=width,
            y_max=height,
            torus=True,
            x_min=0,
            y_min=0,
        )

        self.current_id = 0
        self.n_creatures = n_creatures
        self.n_candies = n_candies
        self.last_day = max_days
        self.height = height
        self.width = width

        # Base creature boundaries
        self.max_energy = energy
        self.max_speed = speed
        self.max_view_range = view_range
        self.max_mut_rate = mut_rate

        # Place creatures
        for _ in range(self.n_creatures):
            pos = self.random_pos()
            new_creature = Creature(
                unique_id=self.next_id(),
                pos=pos,
                model=self,
            )
            self.space.place_agent(agent=new_creature, pos=pos)
            self.schedule.add(new_creature)

        # Allow to run simulations in background by using BatchRunner
        self.running = True
        self.day = 0

        # Collect some model data at the end of each day
        self.datacollector = DataCollector(
            model_reporters={
                "Energy": total_energy,
                "Speed": avg_speed,
                "View": avg_view_range,
                "Focus": avg_focus_angle,
                "Mut": avg_mut_rate,
                "Creatures": count_creatures,
                "Candies": count_candies,
                "Zero eaters": count_zero_eaters,
                "One eaters": count_one_eaters,
                "Two eaters": count_two_eaters,
            },
            agent_reporters={
                "Agent type": 'agent_type',
                "Done steps": "done_steps",
                'Energy used for movement': 'energy_used_for_movement',
                'Energy spent on view range': 'energy_spent_on_view_range',
                'Energy spent on focus angle': 'energy_spent_on_focus_angle',
                'Energy lost': 'energy_lost',
                'Energy of happiness': 'energy_of_happiness',
                'Moment of first consumption': 'moment_of_first_consumption',
                'Moment of second consumption': 'moment_of_second_consumption'
            }
        )

    def random_pos(self):
        """Returns a tuple of ranodmized `(x,y)` coordinates."""
        return (
            random.uniform(0, self.width),
            random.uniform(0, self.height),
        )

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

            pos = self.random_pos()

            offspring = Creature(
                speed=speed,
                focus_angle=focus_angle,
                view_range=view_range,
                pos=pos,
                mut_rate=mut_rate,
                unique_id=self.next_id(),
                model=self,
            )
            offspring.mutate()
            self.space.place_agent(agent=offspring, pos=pos)
            self.schedule.add(offspring)

    def evolve(self):
        """Evolves the creatures at the end of the day.

        The creatures are processed as follows:
            a) if they ate no candies they die;
            b) if they ate 1 candy they survive, but receive a flat 25% energy
               penalty the next day. If the penalty reaches 100% they are
               killed off;
            c) if they ate 2 candies they become parents reproduce by pairing
               randomly to produce offspring as described in `self.crossover()`.
               Their penalty is reset.
        """
        # Deal with the creatures appropriately
        parents = []
        for creature in self.creatures:

            if creature.eaten_candies == 0:
                self.schedule.remove(creature)

            elif creature.eaten_candies == 1:
                creature.penalty += 0.25
                if creature.penalty >= 0.999999:
                    self.schedule.remove(creature)

            else:
                creature.penalty = 0
                parents.append(creature)

        random.shuffle(parents)
        # print(f"In day {self.day} there are {len(parents)} parents")

        if len(parents) == 1:
            # Clone the single parent and mutate the offspring
            parent = parents[0]

            pos = self.random_pos()
            offspring = Creature(
                speed=parent.speed,
                focus_angle=parent.focus_angle,
                view_range=parent.view_range,
                pos=pos,
                mut_rate=parent.mut_rate,
                unique_id=self.next_id(),
                model=self,
            )
            offspring.mutate()
            self.space.place_agent(agent=offspring, pos=pos)
            self.schedule.add(offspring)

        elif len(parents) > 1:
            # Iterate over every pair of parents.
            # 2*(len(parents)//2) to avoid paring last parent if there is an
            # odd number of them.
            for i in range(0, 2 * (len(parents) // 2), 2):
                self.crossover(parents[i], parents[i + 1])

            # If there is an odd number of parents the last one was skipped
            # so pair him with a random partner.
            if len(parents) % 2 == 1:
                self.crossover(parents[-1], random.choice(parents[:-1]))

    def step(self):
        """Determines what will happened in one full step of simulation.

        If self.schedule is RandomActivation (good for visualising one full
        day) than step is an elementary update of all agents.

        If self.schedule is StagedActivation (good for visualisation progress
        of population) than step is an entire day.
        """
        self.day += 1
        if self.day == 1 or isinstance(self.schedule, StagedActivation):
            # Place new candies
            for _ in range(self.n_candies):
                pos = self.random_pos()
                new_candy = Candy(
                    unique_id=self.next_id(), pos=pos, model=self)
                self.space.place_agent(agent=new_candy, pos=pos)
                self.schedule.add(new_candy)

        # Halt if all days passed
        if self.day < self.last_day:
            self.schedule.step()
            if isinstance(self.schedule, StagedActivation):
                self.datacollector.collect(self)
                self.evolve()
                # Remove old candies
                for candy in self.candies:
                    self.schedule.remove(candy)
        else:
            self.running = False

    @property
    def creatures(self):
        """Iterator over creature-agents."""
        return filter(lambda a: isinstance(a, Creature), self.schedule.agents)

    @property
    def candies(self):
        """Iterator over candy-agents."""
        return filter(lambda a: isinstance(a, Candy), self.schedule.agents)