import pandas as pd
from simulation import(
    simulator as sim,
    file_loader as file_loader
)
from tqdm import tqdm

def main():
    # id_1 = 193 # magmortar
    id_1 = 33 # celebi
    
    stats = {"win": 0, "loss": 0, "draw": 0}

    progress = tqdm(range(file_loader.total_evolution_count()))
    for id_2 in progress:
        progress.set_description(f"{file_loader.get_evo_name(id_2)} vs. {file_loader.get_evo_name(id_1)}")
        winner = sim.simulate(id_2, id_1)

        index = 'draw' if winner is None else 'win' if winner == 1 else 'loss'
        stats[index] += 1

    progress = tqdm(range(file_loader.total_evolution_count()))
    for id_2 in progress:
        progress.set_description(f"{file_loader.get_evo_name(id_1)} vs. {file_loader.get_evo_name(id_2)}")
        winner = sim.simulate(id_1, id_2)

        index = 'draw' if winner is None else 'win' if winner == 0 else 'loss'
        stats[index] += 1

    print(f"Wins: {stats['win']}, Losses: {stats['loss']}, Ties: {stats['draw']}")

if __name__ == '__main__':
    main()