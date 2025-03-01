# Overview

This data analysis builds on the simulations built in the previous directory. The purpose of this analysis is to analyze the battle reuslts after simulating all Pokemon from the original data exploration, and compare the findings from pre-simulation with the post-simulation results.

[Software Demo Video](https://youtu.be/o7fGZ8Yqm9s)

# Data Analysis Results

## Q: What traits contribute to a Pokemon haivng a high win-rate?

A: After analyzing the top-20 performing pokemon, a few key traits stick out:

|Trait|Explaination|
|----|---|
|High HP|Higher HP allows the Pokemon to survive more attacks and deal more damage before they are KOed|
|High-Damage|Higher damage allows them to knock out the opposing Pokemon sooner and revceive less damage|
|EX|EX Pokemon tend to have both high HP and high-damage attacks|
|Special status|Status effects - especially that relate to dealing lots of extra damage or preventing damage recieved -- both increase a Pokemon's survivability and how quickly the KO the opposing Pokemon|

## Q: What traits make a Pokemon have a lower win-rate?

A: The following traits tend to contribute to a lower win-rate:

|Trait|Explaination|
|-|-|
|Non-Damaging Moves|Moves that have non-damaging attacks will never win since they can never KO another Pokemon|
|Bench-Targeting Moves|Pokemon that can only target the opponent's bench can never win since they will be unable to KO the active Pokemon|
|Low HP|With lower HP, this Pokemon is quicker to KO before it can deal any damage|

## Q: How much betterare EX Pokemon than non-EX Pokemon?

A: EX Pokemon, on average, win 1.5x as much as non-EX.

## Q: If you could design a Pokemon, what key choices would you make to maximize its win-rate?

A: Given the effectiveness of individual Pokemon features tested by the simulation, I would design a Pokemon with the following:

|Trait|Choice|Explaination|
|-|-|-|
|EX?|Yes|More plausible for giving high-HP and high-damage attacks|
|Type|Fighting or Grass|Both are in the top-2 types by win-rate. Fighting tends to have higher-damage moves, while grass tends to have higher HP|
|Final Evolution|Stage 2|Higher stages have a higher win-rate due to stronger moves and higher HP|
|Ability?|Yes, Status or Defense|Status will help us KO faster, while defensive abilities will increase the Pokemon's survivability|
|HP|160|Highest-performing HP. Pokemon try to balance between damage and health, and 160 has a good balance|

# Development Environment

All code was developed inside of VSCode

- Python
- Jupyter Notebooks
- Pandas
- Numpy
- LetsPlot / GG-Plot

# Future Work

- More intersectional analysis between original data analysis and battle results
- Improve the simulation, and do a deeper dive into the results when comparing an entire Pokemon team (Deck of 20 cards)
- Add supporter and item cards, and analyze how much more effective decks become when they are added in