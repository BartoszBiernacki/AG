"""Run the visualization server."""
import cProfile
import pstats

from candied.server import server
from mesa.batchrunner import BatchRunner
from mesa.batchrunner import BatchRunnerMP

from candied.model import Evolution


def run_in_background():
    fixed_params = {
        "height": 200,
        "width": 200,
        "n_creatures": 10,
        "max_days": 5,
        "energy": 500,
        "mut_rate": 3,
        "speed": 7,
        "view_range": 8,
        "max_steps_per_day": 100
    }

    variable_params = {
        "n_candies": [100]
    }
    
    batch_run = BatchRunnerMP(
        model_cls=Evolution,
        variable_parameters=variable_params,
        fixed_parameters=fixed_params,
        iterations=1,
        max_steps=fixed_params['max_days'],
    )
    
    batch_run.run_all()
    model_data = batch_run.get_collector_model()  # For each model reporters
    agent_data = batch_run.get_collector_agents()  # For each agent reporter
    
    # for key, df in model_data.items():
    #     print(key)
    #
    #     print(df.to_markdown())
    #     # fig, ax = plt.subplots(111)
    #     # df.plot[]

    for key, df in agent_data.items():
        # print(key)
        df = df.loc[df["Agent type"] == 'Creature']
        print(df.to_markdown())


run_in_browser = False


if __name__ == '__main__':
    if run_in_browser:
        server.launch()
    else:
        with cProfile.Profile() as pr:
            run_in_background()
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats(5)
        
