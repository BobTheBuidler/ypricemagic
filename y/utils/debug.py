
import os
from collections import defaultdict
from pprint import pprint
from statistics import median
from typing import Dict, List, Union

from brownie import chain
from pandas import DataFrame

FunctionName = str
Inputs = str
Duration = float

num_recorded_durations = 0
function_durations: Dict[FunctionName,List[Dict[str,Union[Inputs,Duration]]]] = defaultdict(list)


def print_average_durations() -> None:
    average_durations = {}
    for function_name in function_durations:
        _average_duration = average_duration(function_name)
        average_durations[_average_duration] = function_name
    pprint(sorted(average_durations))

def durations(function_name: str) -> List[float]:
    return [event['duration'] for event in function_durations[function_name]]

def average_duration(function_name: str) -> float:
    _durations = durations(function_name)
    return sum(_durations) / len(_durations)

def median_duration(function_name: str) -> float:
    return median(durations(function_name))

def max_duration(function_name: str) -> float:
    return max(durations(function_name))

def _durations_dataframe() -> DataFrame:
    dataframe = DataFrame([
        {
            'function': function_name,
            'average': average_duration(function_name),
            'median': median_duration(function_name),
            'max': max_duration(function_name),
            'ct': len(durations(function_name))
        } for function_name in function_durations
    ])
    return dataframe.sort_values(by='average',ascending=False)


def export_durations() -> None:
    path = f'debug/{chain.id}/function_durations.csv'
    __prepare_directory(path)
    _durations_dataframe().to_csv(path)
    

def record_duration(function_name: str, inputs: str, duration: float) -> None:
    global num_recorded_durations
    event = {
        'inputs': inputs,
        'duration': duration,
    }
    function_durations[function_name].append(event)
    num_recorded_durations += 1
    if num_recorded_durations % 1000 == 0:
        export_durations()

def __prepare_directory(filepath: str) -> None:
    num_steps = filepath.count('/')
    for i in range(num_steps):
        path = ""

        # Split parts, put them back together.
        for chunk in filepath.split('/')[:i+1]:
            path += f'{chunk}/'

        # Get rid of trailing '/'.
        path = path[:-1]

        # Create directory if doesn't exist.
        if not os.path.exists(path):
            os.makedirs(path)
