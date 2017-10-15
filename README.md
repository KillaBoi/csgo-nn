
# Counter-Strike: GO Predictor

Hello cool person, this is a machine learning predictor I made for professional counter-strike matches. This latest version can predict about 66% of matches using stats from HLTV.org and a multilayer perceptron neural network. 


## Installing & Running

I used beautifulsoup, numpy, pandas, sklearn, trueskill, progressbar, MySQLdb just run the pip command and you should be all set.

```
pip install beautifulsoup4 numpy sklearn pandas trueskill progressbar2

```
Next you need to import the database of games included in the data folder and update the database.py file with your mysql user,pass, and db name.

Now you can just run predict.py and it will pull any missing games, recalculate everything, get a list of upcoming games and print out a list of matches with win percentages. This may take a few minutes depending while it pulls and processes everything. 

```
python predict.py

astralis ( 69.0 )  vs  faze ( 31.0 )
vegasquadron ( 62.0 )  vs  panthers ( 38.0 )
entity ( 59.0 )  vs  brutality ( 41.0 )
mousesports ( 70.0 )  vs  alternateattax ( 30.0 )

```

## Features & Fixes & TODO's

The code for this is a compendium of other projects I've been tinkering with and needs a bunch of cleaning up and commenting. 

### Files & DB

* train.py - has 2 functions train_mlp & search_mlp, train dumps out the optimized MLP model, and search does a gridsearch for optimum MLP parameters.
* scrape.py - Scrapes HLTV for juicy data, and upcoming matches
* process.py - Chews through raw match data and computes all the useful stats to feed into the neural network. 
* predict.py - Run this to get your predictions for upcoming matches
* database.py - A simple database wrapper I wrote a while ago and need to clean up
* data/training.csv - for simplicy and portability I dump all the training games from the 'games' table to a csv

The database is made up of 4 tables:
* teams - a list of every professional counter-strike team for about the past 10 years.
* raw - unprocessed matches from HLTV
* processed - all the calculated features, elo, trueskill, etc..
* games - this is the final list of matches that gets fed into the neural network. 


### TODO

* Add comments to all files
* Remove unused feature calulcations ie. rating
* Improve process_totals() by keeping running totals, so no need to reprocess totals every run.
* Remove legacy functions from database.py
* rewrite setup_teams() 
* remove a bunch of redundency in fields across the db, alot is just holdover from other projects I need to clean up.


## Author

Wyatt Ferguson
[Github](https://github.com/wyattferguson)
[Twitter](https://twitter.com/wyattferguson)

