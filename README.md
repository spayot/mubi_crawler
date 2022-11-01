# Mubi Crawler
**Problem statement**: MUBI has a great collection of art house movies, but pretty limited filtering functionalities, it also misses relevant movie information for my decision making such as MetaCritic's score (aka metaScore)  
**Goal**: make Mubi's collection easy to query by converting it into a structured dataset (CSV) 
**Example of queries** (e.g. show me Comedies with MetaScores higher than 80 available on Mubi.)

## Steps
* Extract list of movies available to watch on Mubi, query MetaCritic to access meta_score, 

## Install
`pip install -r requirements.txt`

## How to Use

`python main.py`   
When executing the above, you will:
* crawl all movies available on Mubi (more specifically, all movies in the top 40 collections displayed on https://mubi.com/showing), 
* query metacritic's APIs to get metascores 
* and store all the results in a CSV file named `data/{current_date}_mubi.csv`


## List of Fields Extracted
| field | type | example value | source |
|--|--|--|--|
| title | str | Drug War | mubi |
| duration | int | 106 | mubi |
| year | int | 2012 | mubi |
| web_url | str | https://mubi.com/films/drug-war | mubi |
| critic_review_rating | float | 4.85 | mubi |
| director | str | Johnie To | mubi |
| genres | list[str] | ['Crime'] | mubi |
| historic_countries | list[str] | ['Hong Kong', 'China'] | mubi |
| meta_score | int | 86 | metacritic |
