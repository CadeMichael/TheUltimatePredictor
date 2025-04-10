import scrapy


class EventSpider(scrapy.Spider):
    name = "events"
    start_urls = [
        "http://ufcstats.com/statistics/events/completed?page=all",
    ]
