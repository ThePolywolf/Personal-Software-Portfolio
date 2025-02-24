if __name__ == '__main__':
    import pandas as pd

    ## load data set
    df = pd.read_csv('data/pokemon-tcg-with-fossils.csv')

    ## unique pokemon
    mechanic_unique = df.groupby('name')['a1name'].value_counts().reset_index().drop(columns=['count'])
    mechanic_unique['id'] = mechanic_unique.apply(lambda row: df.loc[df[(df['name'] == row['name']) & (df['a1name'] == row['a1name'])].first_valid_index(), 'id'], axis=1)

    mechanic_unique_ids = mechanic_unique['id'].unique()

    # add fossils
    unique_fossil_ids = df[df['type'] == 'fossil'].groupby('name').first()['id'].unique()

    unique_pkmn = df[(df['id'].isin(mechanic_unique_ids)) | (df['id'].isin(unique_fossil_ids))]

    ## creature mechanic-unique evolution lines
    stage2_final = unique_pkmn[unique_pkmn['stage'] == 2]
    stage2_evolutions = stage2_final['from'].unique()

    stage1_final = unique_pkmn[(unique_pkmn['stage'] == 1) & (~unique_pkmn['name'].isin(stage2_evolutions))]
    stage1_evolutions = unique_pkmn[unique_pkmn['stage'] == 1]['from'].unique()

    basic_final = unique_pkmn[(unique_pkmn['stage'] == 0) & (~unique_pkmn['name'].isin(stage1_evolutions))]

    evolution_lines = {
        'basic'     : [],
        'stage1'    : [],
        'stage2'    : []
    }

    for id in basic_final['id']:
        evolution_lines['basic'] += [id]
        evolution_lines['stage1'] += [None]
        evolution_lines['stage2'] += [None]

    for id in stage1_final['id']:
        from_name = unique_pkmn.loc[unique_pkmn[unique_pkmn['id'] == id].first_valid_index(), 'from']
        for basic_id in unique_pkmn[unique_pkmn['name'] == from_name]['id']:
            evolution_lines['basic'] += [basic_id]
            evolution_lines['stage1'] += [id]
            evolution_lines['stage2'] += [None]

    for id in stage2_final['id']:
        stage1_name = unique_pkmn.loc[unique_pkmn[unique_pkmn['id'] == id].first_valid_index(), 'from']
        for stage1_id in unique_pkmn[unique_pkmn['name'] == stage1_name]['id']:
            basic_name = unique_pkmn.loc[unique_pkmn[unique_pkmn['id'] == stage1_id].first_valid_index(), 'from']
            for basic_id in unique_pkmn[unique_pkmn['name'] == basic_name]['id']:
                evolution_lines['basic'] += [basic_id]
                evolution_lines['stage1'] += [stage1_id]
                evolution_lines['stage2'] += [id]

    evolution_lines = pd.DataFrame(evolution_lines)

    evolution_lines['basic_name'] = evolution_lines['basic'].apply(lambda id: unique_pkmn.loc[unique_pkmn[unique_pkmn['id'] == id].first_valid_index(), 'name'])
    evolution_lines['stage1_name'] = evolution_lines['stage1'].apply(lambda id: None if id is None else unique_pkmn.loc[unique_pkmn[unique_pkmn['id'] == id].first_valid_index(), 'name'])
    evolution_lines['stage2_name'] = evolution_lines['stage2'].apply(lambda id: None if id is None else unique_pkmn.loc[unique_pkmn[unique_pkmn['id'] == id].first_valid_index(), 'name'])

    path = "data/unique_evolution_lines.csv"
    evolution_lines.to_csv(path)
    print(f'Evolution lines generated. Path: {path}')