from mesa import Agent
from my_math_utils import *


class Creature(Agent):
    def __init__(self, unique_id, pos, model):
        
        super().__init__(unique_id=unique_id, model=model)
        
        self.energy = model.energy
        self.speed = model.speed
        self.pos = pos
        
        self.view_angle = 2*np.pi
        self.view_range = 5

        self.eaten_candies = 0
        self.moving_angle = None
        
    def search_for_food(self):
        neighbours = self.model.space.get_neighbors(pos=self.pos,
                                                    radius=self.view_range,
                                                    include_center=True)
        
        candies = [neighbour for neighbour in neighbours if isinstance(neighbour, Candy)]
        min_distance = 1e9
        nearest_candy = None
        for candy in candies:
            if not candy.eaten:
                distance = self.model.space.get_distance(
                    pos_1=self.pos,
                    pos_2=candy.pos)
                
                if distance < min_distance:
                    nearest_candy = candy
                    min_distance = distance
                    
        if min_distance > self.view_range:
            nearest_candy = False
        # if nearest_candy:
        #     print("Food found at ", nearest_candy.pos,
        #           "dist=", distance)
        return nearest_candy

    def decrease_energy(self):
        dE = self.speed ** 2
    
        self.energy -= dE
        
    def move(self, food):
        
        r = self.speed
        
        if food:
            x_creature = self.pos[0]
            y_creature = self.pos[1]
            x_food = food.pos[0]
            y_food = food.pos[1]
        
            slope = (y_food - y_creature) / (x_food - x_creature)
            theta = math.atan(slope)
            
            # decide in which direction among line creature should go
            theta_1 = theta
            dx = r * np.cos(theta_1)
            dy = r * np.sin(theta_1)
            
            new_x = self.pos[0] + dx
            new_y = self.pos[1] + dy
            new_pos_1 = (new_x, new_y)
            dist_1 = self.model.space.get_distance(
                        pos_1=new_pos_1,
                        pos_2=food.pos)
    
            theta_2 = theta + np.pi
            dx = r * np.cos(theta_2)
            dy = r * np.sin(theta_2)
    
            new_x = self.pos[0] + dx
            new_y = self.pos[1] + dy
            new_pos_2 = (new_x, new_y)
            dist_2 = self.model.space.get_distance(
                pos_1=new_pos_2,
                pos_2=food.pos)
            
            new_pos = new_pos_1
            if dist_2 < dist_1:
                new_pos = new_pos_2
                
        else:
            theta = get_random_angle(moving_angle=self.moving_angle,
                                     view_angle=self.view_angle)
            dx = r * np.cos(theta)
            dy = r * np.sin(theta)

            new_x = self.pos[0] + dx
            new_y = self.pos[1] + dy
            new_pos = (new_x, new_y)
            
        self.pos = new_pos
        self.model.space.move_agent(agent=self, pos=self.pos)
        self.moving_angle = theta
        
    def eat_candy(self, food):
        if food:
            distance = self.model.space.get_distance(
                pos_1=self.pos,
                pos_2=food.pos)
            if distance < self.speed * 2:
                food.eaten = True
                self.eaten_candies += 1
        
    def stage_1_compete(self):
        if self.energy > 0 and self.eaten_candies < 2:
            food = self.search_for_food()
            self.decrease_energy()
            self.move(food)
            self.eat_candy(food=food)
            
    def stage_2_evolve(self):
        d_speed = random.uniform(-1, 1)
        d_view_range = random.uniform(-1, 1)
        print('A kuku')
        # self.pos = (90, 90)
        
        
    def step(self):
        if self.energy > 0 and self.eaten_candies < 2:
            food = self.search_for_food()
            self.decrease_energy()
            self.move(food)
            self.eat_candy(food=food)


class Candy(Agent):
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id=unique_id, model=model)
        
        self.pos = pos
        self.eaten = False

    def stage_1_compete(self):
        pass

    def stage_2_test(self):
        pass

    def step(self):
        pass
