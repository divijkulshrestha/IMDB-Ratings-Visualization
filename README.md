# IMDB Ratings Visualization
Visualizing IMDb Ratings of TV Series episodes

ratings.py contains functions for scraping IMDb ratings for each episode of a series, and then plotting it in the style of visualization
made by Reddit user u/Hbenne. Credit to u/EnergyVis (https://github.com/AyrtonB/IMDB-Show-Ratings/) for the inspiration. 

The Jupyter notebook creates the IMDb Ratings chart for long-running anime series One Piece, but can be configured to do the same for
any series on IMDb.

NOTE - change "year" to "season" in the lambda function season_2_url if you are using this for a TV series that IMDb indexes by season,
not year. One Piece is indexed by year. 
