import pandas as pd
from simulation import(
    simulator as sim,
    file_loader as file_loader
)
from tqdm import tqdm

def get_battle_results():
    # result 0: tie, 1: p1 win, 2: p2 win
    stats = {"player1": [], "player2": [], "result": [], "p1name": [], "p2name": []}

    progress = tqdm([(p1, p2) for p1 in range(file_loader.total_evolution_count()) for p2 in range(file_loader.total_evolution_count())])
    max_count = 100000  # safety
    count = 0
    for id_1, id_2 in progress:
        p1_name = file_loader.get_evo_name(id_1)
        p2_name = file_loader.get_evo_name(id_2)
        label = f"{p1_name} vs. {p2_name}"
        progress.set_description(f"{label:<35}")
        
        winner = sim.simulate(id_1, id_2)
        result = 0 if winner is None else (winner + 1)

        stats['player1'].append(id_1)
        stats['player2'].append(id_2)
        stats['result'].append(result)
        stats['p1name'].append(p1_name)
        stats['p2name'].append(p2_name)

        count += 1
        if count >= max_count:
            break

    print("Saving results")
    results = pd.DataFrame(stats)
    path = "battle-analysis/battle_results.csv"
    results.to_csv(path)
    print(f"Results outputted to {path}")

def main():
    get_battle_results()

if __name__ == '__main__':
    main()