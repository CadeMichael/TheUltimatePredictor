import scrapy as sp


class EventSpider(sp.Spider):
    name = "events"
    start_urls = [
        "http://ufcstats.com/statistics/events/completed?page=all",
    ]
