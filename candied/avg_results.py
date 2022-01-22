"""Averages model level DataCollector results and saves them to files."""
import itertools
import pandas as pd
import numpy as np
from pathlib import Path

from collections import namedtuple


def group_tuples_by_start(list_of_tuples, start_length):
    """
    Returns dict in which:
        Keys are unique sub-tuples of length 'start_length' created from all
        tuples in 'list_of_tuples'.
        Item is a sub-list of tuples contain tuples from 'list_of_tuples'
        that starts with a key sub-tuple.
        
    Example:
        list_of_tuples = [(1, 2, 5, 6), (1, 2, 4, 7), (1, 3, 9, 4), (2, 3, 5)]
        start_length = 2
        result = {
        (1, 2): [(1, 2, 5, 6), (1, 2, 4, 7)],
        (1, 3): [(1, 3, 9, 4)],
        (2, 3): [(2, 3, 5)]
        }
    
    
    Developed to group model DataCollector results such each group contains
    unique model calling parameters. To achieve this pass following arguments:
    
    list_of_tuples: designed to be list of tuples returned as model data
        collector keys. Such tuple has following structure:
        (variable_params_values, fixed_params_values, num_of_iteration),
        order of items in 'variable_params_values' and 'fixed_params_values'
        is the same as it was passed to BatchRunner.
        
    start_length: to properly group DataCollector results this value should
        equal to number of 'variable_parameters'.
    """
    result = {}
    tuples_starts = [[item for i, item in enumerate(tup) if i < start_length] for tup in list_of_tuples]
    tuples_starts.sort()
    unique_tuples_starts = list(tuples_starts for tuples_starts, _ in itertools.groupby(tuples_starts))

    for unique_tuple_start in unique_tuples_starts:
        tuples_grouped_by_start = []
        for tup in list_of_tuples:
            tuple_start = tup[:start_length]
            if list(tuple_start) == unique_tuple_start:
                tuples_grouped_by_start.append(tup)
        result[tuple(unique_tuple_start)] = tuples_grouped_by_start
    
    return result


def avg_model_results(model_collector_result,
                      variable_params,
                      ignore_dead_populations=True,
                      ):
    """
    Returns dict in which:
        keys are NamedTuples of variable_params
        values are dataframes averaged over all iterations
    
    Function takes:
        model collector result
        dict 'variable_parameters' passed to BatchRunner
    """
    num_of_variable_model_params = len(variable_params)
    num_of_variable_model_params = len(model_collector_result)-2
    list_of_tuples = list(model_collector_result.keys())
    tuples_grouped = group_tuples_by_start(list_of_tuples=list_of_tuples,
                                           start_length=num_of_variable_model_params)
    
    result = {}
    # Key is a tuple by which other tuples were grouped, e.g. key=(5, 2, 2)
    for key in tuples_grouped.keys():
        lis = []
        # items are full tuples, e.g. item=(5, 2, 2, ..., 0)
        for item in tuples_grouped[key]:
            if ignore_dead_populations:
                if np.array(model_collector_result[item]['Creatures'])[-1] > 0:
                    # list of results dataframes matching key_tuple=(5, 2, 2)
                    lis.append(model_collector_result[item])
            else:
                # list of results dataframes matching key_tuple=(5, 2, 2)
                lis.append(model_collector_result[item])
                
        array_with_all_iterations_results_for_specific_parameters =\
            np.array(lis)
        
        average_array = np.mean(
            array_with_all_iterations_results_for_specific_parameters, axis=0)
        df = pd.DataFrame(data=average_array)
        df.columns = model_collector_result[list_of_tuples[0]].columns
        
        # make result keys looks like: ,KeyTuple(n_candies=50, n_creatures=40)'
        KeyTuple = namedtuple('KeyTuple', variable_params)
        new_key = {}
        for i, key_name in enumerate(variable_params):
            new_key[key_name] = key[i]
        result[KeyTuple(**new_key)] = df
    
    return result


def save_avg_results(avg_results,
                     fixed_params,
                     variable_params,
                     save_dir,
                     runs,
                     base_params=None):
    """
    Saves averaged model level DataCollector results (dataframes) to csv files.
    
    base_params are responsible for folder name
    variable_params are responsible for file names.
    
    avg_results: data to be saved.
    fixed_params: fixed_params passed to BatchRunner.
    variable_params: variable_params passed to BatchRunner.
    save_dir: directory where results will be saved.
    runs: number of simulations performed for one set of parameters. It's
        useful to have that info in filename.
    base_params: sub-list of model  fixed parameters names that will be
    included in name of folder that stores the results.
    
    """
    if base_params:
        dir_name = '/' + f'Runs={runs}___'
        for param, val in {**fixed_params, **variable_params}.items():
            if param in base_params:
                try:
                    dir_name += param.capitalize() + '=' + str(
                        round(val, 3)) + '___'
                except TypeError:
                    tuple_val = tuple([round(x, 3) for x in val])
                    dir_name += param.capitalize() + '=' + str(
                        tuple_val) + '___'

        dir_name = dir_name[: -3]
        save_dir += dir_name + '/'
        save_dir += 'raw data/'

    Path(save_dir).mkdir(parents=True, exist_ok=True)

    try:
        file_id = len([path for path in Path("./" + save_dir).iterdir() if
                       path.is_file()])
    except FileNotFoundError:
        file_id = 0

    # Saving dataframes
    for tuple_key, df in avg_results.items():
        fname = f'Id={str(file_id).zfill(4)}'
        for param, val in zip(variable_params, tuple_key):
            try:
                fname += '___' + param.capitalize() + '=' + str(round(val, 3))
            except TypeError:
                tuple_val = tuple([round(x, 3) for x in val])
                fname += '___' + param.capitalize() + '=' + str(tuple_val)

        df.to_csv(path_or_buf=save_dir + fname + '.csv', index=False)
        file_id += 1

        