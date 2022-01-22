"""Run the visualization server."""
import cProfile
import pstats

from candied.server import server
from mesa.batchrunner import BatchRunner
from mesa.batchrunner import BatchRunnerMP

from candied.model import Evolution
from candied.avg_results import avg_model_results
from candied.avg_results import save_avg_results


def run_in_background(fixed_parameters: dict,
                      variable_parameters: dict,
                      iterations=3,
                      multithreading=True,
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
                                       variable_params=variable_parameters)
    
    save_avg_results(avg_results=avg_model_data,
                     fixed_params=fixed_parameters,
                     variable_params=variable_parameters,
                     save_dir='results/',
                     runs=iterations,
                     base_params=['speed',
                                  'mut_rate',
                                  'energy',
                                  'view_range',
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
        "max_days": 100,
        "energy": 1500,
        "mut_rate": 3,
        "speed": 10,
        "view_range": 8,
        "max_steps_per_day": 100
    }
    variable_params = {
        "n_candies": [50, 60, 100],
        "n_creatures": [40, 50, 80],
    }
    multithreading = False

    print_model_data = False
    print_model_avg_data = True
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
                iterations=5,
                multithreading=multithreading,
                print_model_data=print_model_data,
                print_model_avg_data=print_model_avg_data,
                print_agent_data=print_agent_data,
            )
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats(5)
        
