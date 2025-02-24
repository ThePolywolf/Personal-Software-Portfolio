import pandas as pd
from simulation.simulator import simulate 

def main():
    id_1 = 0
    stats = {0: 0, 1: 0, None: 0}

    print(f"Wins: {stats[0]}, Losses: {stats[1]}, Ties: {stats[None]}")

if __name__ == '__main__':
    main()