# earthquake-swarm-finder
 Python module that groups earthquakes into swarms.
## Swarm Finder
 The `swarms.py` module contains the function `find_swarms()`, which groups earthquakes into swarms based on three criteria set by the user:
 * maximum time between successive earthquakes in a swarm
 * maximum distance between an earthquake and the nearest preceding earthquake in the same swarm
 * minimum number of earthquakes considered to constitute a swarm
## Inputs
 Earthquake data from the United States Geological Survey. Earthquakes occur between 2000-01-01 and 2024-09-01 and within 50 km of the Mid-Atlantic Ridge (MAR). The four files correspond to four sections of the MAR: Reykjanes Ridge (52.27 N to 63 N), Northern MAR (15 N to 52.27 N), Central MAR (2 S to 15 N), and Southern MAR (55 S to 2 S) indicated by the letters 'r', 'n', 'c', and 's', respectively.

**Source:**
 U. S. Geological Survey. (2024). ANSS Comprehensive Earthquake Catalog (ComCat) [CSV]. Retrieved September 10, 2024.
