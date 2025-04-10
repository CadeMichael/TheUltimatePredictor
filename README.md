# UFC fight and fighter data

- web scraped from [ufcstats](http://ufcstats.com) using [scrapy.py](https://scrapy.org/)
- data in **fights.csv** and **fighters.csv**
- data also stored on [kaggle](https://www.kaggle.com/datasets/cadelueker/ufc-fighter-and-fight-stats-as-of-04-9-2025/)

## fights.csv

- information on every fight 
- not in order
- includes
  - both fighters names
  - if the fight isn't a draw includes winner's and loser's name
  - weightclass
  - method of win
  - extra details if present (Submission / KO type)
  - round fight ended
  - time of last round fight ended (min:seconds)
  - total fight time in seconds

## fighters.csv

- individual fighter information
- includes (if present)
  - name
  - height
  - reach
  - stance
  - date of birth
