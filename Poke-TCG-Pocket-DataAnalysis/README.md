# Overview

The purpose of this data exploration is to find patterns within the cards of the Pokemon TCG Pocket mobile game to try and find the best cards to use.

I am analyzing a complete data set (last updated Feb 2025) of all cards available in the Pokemon TCG Pocket mobile game complete with all data from every card.

The purpose of writing this data analysis is to break down the analysis into two distinct sections: 1) a comprehensive analysis of the raw data, and make predictions based on my findings, then 2) to run simulations to find the best performing cards, and test the results agains my expectations from the data.

[Software Demo Video](https://youtu.be/_NYKfH2ae6Q)

# Data Analysis Results

Q: *Do any Pokemon types tend to have more HP than the others?*

A: Most pokemon tend to have around the same average HP, however `Dragon` and `Metal` type Pokemon have the highest HP on average, and there is a positive linear relationship between a Pokemon's stage and its HP.

---
Q: *What weaknesses do most cards tend to have?*

A: A majority of cards have `Fighting`-type weaknesses, followed closely by `Electric`-type. The least-common weakness by card type is `Metal`. 

---
Q: *Which Pokemon type has the best weakness-coverage?*

A: This is a difficult question to answer directly since there are several different factors. 

|Coverage|Best Types|Worst Types|Explanation|
|---|---|---|---|
|Card|Fighting and Electric|Metal and Psychic|Highest number of cards weak to the given type|
|Type|Electric|Water, Psychic, and Dark|Highest number of different Pokemon types containing the given weakness within its subset of cards|
|Type Max|Fighting and Fire|Electric, Grass, Dark, and Water|Count of types where the given weakness type is the most common weakness|

Given these findings, `Fighting`-types tend to have the highest overall coverage, followed by `Electric`-types. The `Fighting` type tends to perform very well against serveral types, while `Electric` tends to perform moderately well against all types except `Fighting`.

---
Q: *What stage are most Pokemons' final evolution at?*

A: `Stage 1`, followed by `Basic`, then finally `Stage 2`

# Development Environment

This software was developed inside of Visual Studio Code using a combination of standard .py Python files as well as .ipynb Notebook files.

This project was developed using Python, inclusing Pandas, JSON, and Numpy libraries.

# Useful Websites

* [Python Pandas API](https://pandas.pydata.org/pandas-docs/stable/reference/index.html)
* [TCG Pocket Card Reference](https://pocket.pokemongohub.net/en)

# Future Work

* Pokemon battle simulation
* A good way to compare attacks and damage
* A single metric to compare a card's "Usefulness" based on all of its features.