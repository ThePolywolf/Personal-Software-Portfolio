"""
Module to load all csv files and gather data
"""

import os
import pandas as pd
import numpy as np

curr_path = os.path.dirname(os.path.abspath(__file__))
evo_lines_df = pd.read_csv(os.path.join(curr_path, './data/unique_evolution_lines.csv'))
pokemon = pd.read_csv(os.path.join(curr_path, './data/pokemon-tcg-with-fossils.csv'))

def total_evolution_count():
    """
    return the total number evolution lines in the data
    """
    return evo_lines_df.shape[0]

def get_evo_name(evo_id: int) -> str:
    """
    Returns the name of a given evolution line
    """
    name = "None"
    columns = ['basic_name', 'stage1_name', 'stage2_name']
    for col in columns:
        cell = evo_lines_df.loc[evo_id, col]
        if isinstance(cell, float) and np.isnan(cell):
            return name
        name = str(cell)
    return name.title()

def get_evolution_line(index) -> list[str]:
    """
    returns the stage progression at the given index as an ordered list from [basic, stage2]
    """

    if index >= evo_lines_df.shape[0]:
        raise Exception(f'Index {index} out-of-range {evo_lines_df.shape[0]}')
    
    line = []
    
    basic = evo_lines_df.loc[index, 'basic']
    line += [basic]

    stage1 = evo_lines_df.loc[index, 'stage1']
    if isinstance(stage1, float) and np.isnan(stage1): return line
    line += [stage1]

    stage2 = evo_lines_df.loc[index, 'stage2']
    if isinstance(stage2, float) and np.isnan(stage2): return line
    line += [stage2]

    return line

def get_pokemon(id):
    """
    returns the pokemon that matches the given id
    """
    pkmn = pokemon[pokemon['id'] == id]
    
    if pkmn.shape[1] == 0:
        raise Exception(f"Pokemon with id '{id}' does not exist")
    
    return pkmn.iloc[0]

def is_nan(to_check):
    return isinstance(to_check, float) and np.isnan(to_check)