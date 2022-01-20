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

        # Genes
        self.speed = speed or random.uniform(0, model.max_speed)
        self.mut_rate = mut_rate or random.uniform(0, model.max_mut_rate)
        self.focus_angle = focus_angle or random.uniform(0, np.pi)
        self.view_range = view_range or random.uniform(0, model.max_view_range)

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
        self.energy -= self.speed**2

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
                pos_1=new_pos_2, pos_2=food.pos)

            new_pos = new_pos_1
            if dist_2 < dist_1:
                new_pos = new_pos_2

        else:
            theta = self.moving_angle + random.uniform(-0.5 * np.pi , 0.5 * np.pi)
            dx = r * np.cos(theta)
            dy = r * np.sin(theta)
            new_pos = (self.pos[0] + dx, self.pos[1] + dy)

        self.pos = new_pos
        self.model.space.move_agent(agent=self, pos=self.pos)
        self.moving_angle = theta

    def eat_candy(self, food):
        """Consume the `food` if it's not `None`.

        A no-op otherwise.
        """
        if food:
            distance = self.model.space.get_distance(
                pos_1=self.pos, pos_2=food.pos)
            if distance < self.speed * 2:
                food.eaten = True
                self.eaten_candies += 1

    def stage_1_compete(self):
        """Only run around and eat, do not evolve."""
        self.step()

    def stage_2_evolve(self):
        """Compete AND evolve."""
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
            food = self.find_candy()
            if food:
                print(food.pos)
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
        self.pos = pos
        self.eaten = False

    def stage_1_compete(self):
        """No-op, the candy does not act."""

    def stage_2_test(self):
        """No-op, the candy does not act."""

    def step(self):
        """No-op, the candy does not act."""
