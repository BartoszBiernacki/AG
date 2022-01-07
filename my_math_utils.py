import random
import numpy as np
import math


def get_random_angle(moving_angle, view_angle):
    if not moving_angle:
        moving_angle = 0
    
    if view_angle > 2*np.pi:
        view_angle = 2*np.pi
        
    left = moving_angle - view_angle/2
    right = moving_angle + view_angle/2
    
    theta = random.uniform(a=left, b=right)
    if theta < 0:
        theta = 2*np.pi - theta
        
    if theta > 2*np.pi:
        theta = theta % (2*np.pi)
        
    return theta
