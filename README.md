# UFC fight and fighter data

- web scraped from [ufcstats](http://ufcstats.com) using [scrapy.py](https://scrapy.org/)
- data in **fights.csv**, **fighters.csv**, and their combination in **enhanced_fights.csv**
- data also stored on [kaggle](https://www.kaggle.com/datasets/cadelueker/ufc-fighter-and-fight-stats-as-of-04-9-2025/)
- *the best data is from the last 15 years, pre then there are gaps about fighters and fight stats*

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
  - event the fight was on
  - fight date
  - fighter strikes
  - fighter takedowns
  - takedowns defended by fighter

## fighters.csv

- individual fighter information
- includes (if present)
  - name
  - height
  - reach
  - stance
  - date of birth

# Scraping

- **scrapy** finished with no errors

```sh
2025-04-11 16:08:08 [scrapy.core.engine] INFO: Closing spider (finished)
2025-04-11 16:08:08 [scrapy.extensions.feedexport] INFO: Stored csv feed (8097 items) in: fights.csv
2025-04-11 16:08:08 [scrapy.extensions.feedexport] INFO: Stored csv feed (2584 items) in: fighters.csv
2025-04-11 16:08:08 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/request_bytes': 3484418,
 'downloader/request_count': 11431,
 'downloader/request_method_count/GET': 11431,
 'downloader/response_bytes': 54778499,
 'downloader/response_count': 11431,
 'downloader/response_status_count/200': 11430,
 'downloader/response_status_count/404': 1,
 'elapsed_time_seconds': 616.897215,
 'feedexport/success_count/FileFeedStorage': 2,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2025, 4, 11, 22, 8, 8, 111476, tzinfo=datetime.timezone.utc),
 'httpcompression/response_bytes': 452547876,
 'httpcompression/response_count': 11430,
 'item_scraped_count': 10681,
 'items_per_minute': None,
 'log_count/DEBUG': 22117,
 'log_count/INFO': 22,
 'memusage/max': 130875392,
 'memusage/startup': 62488576,
 'request_depth_max': 3,
 'response_received_count': 11431,
 'responses_per_minute': None,
 'robotstxt/request_count': 1,
 'robotstxt/response_count': 1,
 'robotstxt/response_status_count/404': 1,
 'scheduler/dequeued': 11430,
 'scheduler/dequeued/memory': 11430,
 'scheduler/enqueued': 11430,
 'scheduler/enqueued/memory': 11430,
 'start_time': datetime.datetime(2025, 4, 11, 21, 57, 51, 214261, tzinfo=datetime.timezone.utc)}
2025-04-11 16:08:08 [scrapy.core.engine] INFO: Spider closed (finished)
```
