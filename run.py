"""Run the visualization server."""
import cProfile
import pstats

import pandas as pd

from candied.server import server
from mesa.batchrunner import BatchRunner
from mesa.batchrunner import BatchRunnerMP

from candied.model import Evolution
from candied.avg_results import avg_model_results
from candied.avg_results import save_avg_results
from candied.avg_results import save_agent_results


def run_in_background(fixed_parameters: dict,
                      variable_parameters: dict,
                      iterations=3,
                      multithreading=True,
                      ignore_dead_populations=True,
                      print_model_data=False,
                      print_model_avg_data=False,
                      print_agent_data=False,
                      ):

    if multithreading:
        batch_run = BatchRunnerMP(
            model_cls=Evolution,
            variable_parameters=variable_parameters,
            fixed_parameters=fixed_parameters,
            iterations=iterations,
            max_steps=fixed_parameters['max_days'],
        )
    else:
        batch_run = BatchRunner(
            model_cls=Evolution,
            variable_parameters=variable_parameters,
            fixed_parameters=fixed_parameters,
            iterations=iterations,
            max_steps=fixed_parameters['max_days'],
        )
        
    batch_run.run_all()
    model_data = batch_run.get_collector_model()  # For each model reporters
    agent_data = batch_run.get_collector_agents()  # For each agent reporter

    avg_model_data = avg_model_results(model_collector_result=model_data,
                                       variable_params=variable_parameters,
                                       ignore_dead_populations=
                                       ignore_dead_populations)
    
    save_avg_results(avg_results=avg_model_data,
                     fixed_params=fixed_parameters,
                     variable_params=variable_parameters,
                     save_dir='results/avg_model_data/',
                     runs=iterations,
                     base_params=['speed',
                                  'mut_rate',
                                  'energy',
                                  'view_range',
                                  'max_days',
                                  'max_steps_per_day',
                                  ]
                     )
    
    save_agent_results(agent_data=agent_data,
                       save_dir='results/agents_data/',
                       fixed_params=fixed_parameters,
                       variable_params=variable_parameters,
                       base_params=['speed',
                                    'mut_rate',
                                    'energy',
                                    'view_range',
                                    'max_days',
                                    'max_steps_per_day',
                                    ]
                       )
    
    if print_model_data:
        print('MODEL DATACOLLECTOR RESULTS BELOW -------------------')
        for key, df in model_data.items():
            print(key)
            print(df.to_markdown())
        
    if print_model_avg_data:
        print('AVERAGE MODEL DATACOLLECTOR RESULTS BELOW -------------------')
        for key, df in avg_model_data.items():
            print(key)
            print(df.to_markdown())

    if print_agent_data:
        print('AGENT DATACOLLECTOR RESULTS BELOW -------------------')
        for key, df in agent_data.items():
            print(key)
            df = df.loc[df["Agent type"] == 'Creature']
            print(df.to_markdown())


if __name__ == '__main__':
    # Set up model parameters ---------------
    fixed_params = {
        "height": 200,
        "width": 200,
        "max_days": 800,
        "energy": 1500,
        "mut_rate": 3,
        "speed": 10,
        "view_range": 8,
        "max_steps_per_day": 100
    }
    variable_params = {
        "n_candies": [70],
        "n_creatures": [50],
    }
    iterations = 10
    multithreading = True
    
    ignore_dead_populations = True

    print_model_data = False
    print_model_avg_data = False
    print_agent_data = False
    
    run_in_browser = False
    
    # Run simulations ----------------------
    if run_in_browser:
        server.launch()
    else:
        with cProfile.Profile() as pr:
            run_in_background(
                fixed_parameters=fixed_params,
                variable_parameters=variable_params,
                iterations=iterations,
                multithreading=multithreading,
                ignore_dead_populations=ignore_dead_populations,
                print_model_data=print_model_data,
                print_model_avg_data=print_model_avg_data,
                print_agent_data=print_agent_data,
            )
            
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats(5)
        
