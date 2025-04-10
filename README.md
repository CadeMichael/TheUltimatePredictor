# UFC fight and fighter data

- web scraped from [ufcstats](http://ufcstats.com) using [scrapy.py](https://scrapy.org/)
- data in **fights.csv**, **fighters.csv**, and their combination in **enhanced_fights.csv**
- data also stored on [kaggle](https://www.kaggle.com/datasets/cadelueker/ufc-fighter-and-fight-stats-as-of-04-9-2025/)

## enhanced_fights.csv

- the same as fights.csv but with fighter metrics and differentials (if they are present for a fighter) for each fight includes
  - age and age diff
  - height and height diff
  - reach and reach diff
  - fighter stance

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
