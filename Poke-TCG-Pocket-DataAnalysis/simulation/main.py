import simulator as sim

def main():
    # evos = [193, 293]   # magmortar and luxray
    # evos = [159, 26]     # gyarados EX and ditto
    evos = [33, 29]     # celebi EX and mew EX

    # evos = [100, 304]   # gyarados EX and Garchomp

    sim.simulate(evos[0], evos[1])

if __name__ == '__main__':
    main()