from SimpleContinuousModule import SimpleCanvas
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule

from model_params import *
from model import Evolution
from agent import Creature, Candy

canvas_height = 500
canvas_width = 500


def agent_portrayal(agent):
    portrayal = {"Shape": "circle"}
    if isinstance(agent, Creature):
        portrayal["r"] = agent.view_range * canvas_height / model_height
        eaten_candies = agent.eaten_candies
        if eaten_candies == 0:
            portrayal["Color"] = "Red"
            portrayal['Layer'] = 2
        elif eaten_candies == 1:
            portrayal["Color"] = "Yellow"
            portrayal['Layer'] = 1
        elif eaten_candies == 2:
            portrayal["Color"] = "Green"
            portrayal['Layer'] = 0
            
    if isinstance(agent, Candy):
        portrayal['Layer'] = 10
        portrayal['Color'] = "Blue"
        portrayal['Filled'] = "True"
        portrayal['r'] = 2
        if agent.eaten:
            portrayal['r'] = 0
            
    return portrayal


canvas_element = SimpleCanvas(portrayal_method=agent_portrayal,
                              canvas_height=canvas_height,
                              canvas_width=canvas_width)

creatures_slider = UserSettableParameter('slider',
                                         "Creatures",
                                         value=5,
                                         min_value=1,
                                         max_value=20,
                                         step=1)

candies_slider = UserSettableParameter('slider',
                                       "Candies",
                                       value=20,
                                       min_value=0,
                                       max_value=100,
                                       step=1)

energy_graph = ChartModule(
    series=[{"Label": "Energy", "Color": "Yellow"}],
    data_collector_name='datacollector')


eaters_graph = ChartModule(
    series=[{"Label": "Zero eaters", "Color": "Red"},
            {"Label": "One eaters", "Color": "Yellow"},
            {"Label": "Two eaters", "Color": "Green"}],
    data_collector_name='datacollector')

model_params = {
    "height": model_height,
    "width": model_width,
    "N_creatures": creatures_slider,
    "N_candies": candies_slider,
    "max_days": 3000,
}

server = ModularServer(model_cls=Evolution,
                       visualization_elements=[canvas_element,
                                               energy_graph,
                                               eaters_graph],
                       name="Evolution model",
                       model_params=model_params)
