"""Agent module.

This module defines the behavior of agents seen in the simulation.
"""
import math
import random

import numpy as np
from mesa import Agent


class Creature(Agent):
    """Creature is an agent that searches for candies, as it needs at least one
    to survive and two to procreate.

    The creature's chromosome consists of just 3 genes - speed, view range and
    focus. If kwargs of the constructor are `None` the genes are chosen
    randomly from `(0, max_value)`, where `max_value` is defined in the parent
    model.
    """

    def __init__(
        self,
        unique_id,
        pos,
        model,
        speed=None,
        focus_angle=None,
        view_range=None,
        mut_rate=None,
    ):
        super().__init__(unique_id=unique_id, model=model)
        self.pos = pos
        self.energy = model.max_energy
        self.moving_angle = random.uniform(0, 2 * np.pi)
        self.eaten_candies = 0
        self.penalty = 0

        # Genes
        self.speed = speed or random.uniform(0, model.max_speed)
        self.mut_rate = mut_rate or random.uniform(0, model.max_mut_rate)
        self.focus_angle = focus_angle or random.uniform(0, np.pi)
        self.view_range = view_range or random.uniform(0, model.max_view_range)
        
        # Data that will be collected at the end of each day for each agent
        self.agent_type = 'Creature'
        self.done_steps = 0
        self.energy_used_for_movement = 0
        self.energy_spent_on_observations = 0
        self.energy_lost = 0
        self.energy_of_happiness = 0
        self.moment_of_first_consumption = None
        self.moment_of_second_consumption = None
        
    def find_candy(self):
        """Locates and returns the nearest candy, `None` if there isn't one."""
        neighbours = self.model.space.get_neighbors(
            pos=self.pos,
            radius=self.view_range,
            include_center=True,
        )
        candies = [
            neighbour for neighbour in neighbours
            if isinstance(neighbour, Candy) and not neighbour.eaten
        ]

        nearest_candy = min(
            candies,
            key=lambda c: self.model.space.get_distance(self.pos, c.pos),
            default=None,
        )
        return nearest_candy

    def expend_energy(self):
        """Expend energy according to the genes.

        Energy spend is a sum of:
            1) kinetic energy, proportional to speed^2;
            2) focus, proportional to the tan(focus angle)
            3) vision energy, proportional to sqrt(vision_range)
        """
        dE = self.speed**2
        self.energy -= dE
        self.energy_used_for_movement += dE

    def move(self, food):
        """Moves `self.speed` units ahead.

        If `food` is not `None` the creature will try to move closer to it, by
        taking a step in the direction of a cone centered at the candy and with
        spread angle equal to `self.focus_angle`.
        """
        r = self.speed
        if food:
            slope = (food.pos[1] - self.pos[1]) / (food.pos[0] - self.pos[0])
            theta = math.atan(slope)

            # decide in which direction among line creature should go
            # TODO: there surely is a better way of doing this?
            theta_1 = theta
            dx = r * np.cos(theta_1)
            dy = r * np.sin(theta_1)

            new_x = self.pos[0] + dx
            new_y = self.pos[1] + dy
            new_pos_1 = (new_x, new_y)
            dist_1 = self.model.space.get_distance(
                pos_1=new_pos_1, pos_2=food.pos)

            theta_2 = theta + np.pi
            dx = r * np.cos(theta_2)
            dy = r * np.sin(theta_2)

            new_x = self.pos[0] + dx
            new_y = self.pos[1] + dy
            new_pos_2 = (new_x, new_y)
            dist_2 = self.model.space.get_distance(
                pos_1=new_pos_2,
                pos_2=food.pos,
            )

            new_pos = new_pos_1
            if dist_2 < dist_1:
                new_pos = new_pos_2

        else:
            theta = self.moving_angle + random.uniform(
                -0.5 * np.pi,
                0.5 * np.pi,
            )
            dx = r * np.cos(theta)
            dy = r * np.sin(theta)
            new_pos = (self.pos[0] + dx, self.pos[1] + dy)

        self.pos = new_pos
        self.model.space.move_agent(agent=self, pos=self.pos)
        self.moving_angle = theta
        self.done_steps += 1

    def mutate(self):
        """Change the genes according to `self.mut_rate`."""
        self.focus_angle += self.mut_rate * random.gauss(0, 1)
        self.view_range += self.mut_rate * random.gauss(0, 1)
        self.speed += self.mut_rate * random.gauss(0, 1)

    def eat_candy(self, food):
        """Consume the `food` if it's not `None`.

        A no-op otherwise.
        """
        if food:
            distance = self.model.space.get_distance(
                pos_1=self.pos, pos_2=food.pos)
            if distance < self.speed * 2:
                # print(f"Agent {self} ate candy!")
                food.eaten = True
                self.eaten_candies += 1
                if not self.moment_of_first_consumption:
                    self.moment_of_first_consumption = self.done_steps
                else:
                    self.moment_of_second_consumption = self.done_steps

    def stage_0_prepare_for_new_day(self):
        """Preparation step.

        The number of candies eaten is reset and the energy is set to
        `(1 - penalty) * max_energy`.
        """
        self.energy = (1 - self.penalty) * self.model.max_energy
        self.eaten_candies = 0

        self.done_steps = 0
        self.energy_used_for_movement = 0
        self.energy_spent_on_observations = 0
        self.energy_lost = 0
        self.energy_of_happiness = 0
        self.moment_of_first_consumption = None
        self.moment_of_second_consumption = None

    def stage_1_compete(self):
        """Single simulation time step. Only run around and eat, do not evolve.

        Repeat this stage a bunch of time in model scheduler =
        StagedActivation to achieve full one day of competition among all
        creatures.

        Do repetition in StagedActivation with shuffle=True, to obtain
        simultaneous move of all creatures. If repetition would be done here
        by: for _ in range(100): self.step
        than in particular day agents would be moving in order of call, which
        would be unfair.
        """
        self.step()

    def stage_2_report(self):
        """Report some agent characteristics at the end of the day.
        Used in DataCollector
        """
        if self.eaten_candies < 2:
            self.energy_lost = self.energy
        else:
            self.energy_of_happiness = self.energy
        
        # TODO: implement this
        self.step()
        print('EVOLUTION NOT IMPLEMENTED')

    def step(self):
        """Single simulation time step.

        If the creature hasn't eaten 2 candies and has energy left it will:
            1) search for nearby candies
            2) expend energy and move towards it
            3) eat the candy if it gets close enough
        Steps are repeated over the course of a day.
        """
        if self.energy > 0 and self.eaten_candies < 2:
            # print(f"Creature {self} has {self.energy} energy.")
            food = self.find_candy()
            # if food:
            #     print(f"Food found at {food.pos} by creature {self}!")
            self.expend_energy()
            self.move(food)
            self.eat_candy(food)


class Candy(Agent):
    """Candy is an agent that serves only as food for the creatures.

    It gets placed in a random spot on the board and does not evolve nor move
    around during each day, disappearing at dawn.
    """
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id=unique_id, model=model)
        # Data used in simulation
        self.pos = pos
        self.eaten = False

        # Data that will be collected at the end of each day for each agent
        # We care of creature's data, but for compatibility to DataCollector
        # all agents must have the same fields.
        self.agent_type = 'Candy'
        self.done_steps = None
        self.energy_used_for_movement = None
        self.energy_spent_on_observations = None
        self.energy_lost = None
        self.energy_of_happiness = None
        self.moment_of_first_consumption = None
        self.moment_of_second_consumption = None

    def stage_0_prepare_for_new_day(self):
        """No-op, the candy does not act."""

    def stage_1_compete(self):
        """No-op, the candy does not act."""

    def stage_2_report(self):
        """No-op, the candy does not act."""

    def step(self):
        """No-op, the candy does not act."""
