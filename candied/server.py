"""Defines the visualization server."""
from mesa.visualization.ModularVisualization import (ModularServer,
                                                     VisualizationElement)
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter

from .agent import Candy, Creature
from .model import Evolution


class SimpleCanvas(VisualizationElement):
    """Continuous canvas."""
    HEIGHT = 500
    WIDTH = 500
    local_includes = ["candied/simple_continuous_canvas.js"]

    def __init__(self):
        super().__init__()
        new_element = f"new Continuous_Module({self.WIDTH}, {self.HEIGHT})"
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        space_state = []
        for obj in model.schedule.agents:
            portrayal = self.portrayal_method(obj)
            x, y = obj.pos
            x = (x -
                 model.space.x_min) / (model.space.x_max - model.space.x_min)
            y = (y -
                 model.space.y_min) / (model.space.y_max - model.space.y_min)
            portrayal["x"] = x
            portrayal["y"] = y
            space_state.append(portrayal)
        return space_state

    @staticmethod
    def portrayal_method(agent):
        """Defines how agents are portrayed in the visualization."""
        portrayal = {"Shape": "circle"}
        if isinstance(agent, Creature):
            r = agent.view_range
            portrayal["r"] = r * SimpleCanvas.HEIGHT / Evolution.HEIGHT
            eaten_candies = agent.eaten_candies
            if eaten_candies == 0:
                portrayal["Color"] = "Red"
                portrayal['Layer'] = 2
            elif eaten_candies == 1:
                portrayal["Color"] = "Orange"
                portrayal['Layer'] = 1
            elif eaten_candies == 2:
                portrayal["Color"] = "Green"
                portrayal['Layer'] = 0
                portrayal["Filled"] = "true"

        if isinstance(agent, Candy):
            portrayal['Layer'] = 10
            portrayal['Color'] = "Blue"
            portrayal['Filled'] = "True"
            portrayal['r'] = 2
            if agent.eaten:
                portrayal['r'] = 0

        return portrayal


canvas_element = SimpleCanvas()

creatures_slider = UserSettableParameter(
    'slider',
    "Creatures",
    value=20,
    min_value=1,
    max_value=100,
    step=1,
)

candies_slider = UserSettableParameter(
    'slider',
    "Candies",
    value=100,
    min_value=0,
    max_value=1000,
    step=1,
)

energy_graph = ChartModule(
    series=[{"Label": "Energy", "Color": "Yellow"}],
    data_collector_name='datacollector',
)

eaters_graph = ChartModule(
    series=[
        {"Label": "Zero eaters", "Color":
         "Red"}, {"Label": "One eaters", "Color": "Yellow"},
        {"Label": "Two eaters", "Color": "Green"}
    ],
    data_collector_name='datacollector',
)

display_params = {
    "height": Evolution.HEIGHT,
    "width": Evolution.WIDTH,
    "n_creatures": creatures_slider,
    "n_candies": candies_slider,
    "max_days": 3000,
}

server = ModularServer(
    model_cls=Evolution,
    visualization_elements=[canvas_element, energy_graph, eaters_graph],
    name="Evolution model",
    model_params=display_params,
)
