# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FightItem(scrapy.Item):
    """
    Information about a fight from a UFC event.
    """

    event_name = scrapy.Field()
    event_date = scrapy.Field()
    outcome = scrapy.Field()
    winner = scrapy.Field()
    loser = scrapy.Field()
    f1_name = scrapy.Field()
    f2_name = scrapy.Field()
    method = scrapy.Field()
    method_details = scrapy.Field()
    end_round = scrapy.Field()
    time = scrapy.Field()
    total_time = scrapy.Field()
    weight_class = scrapy.Field()


class FighterItem(scrapy.Item):
    """
    Information about a fighter who has at least one fight in a UFC event.
    """

    name = scrapy.Field()
    height = scrapy.Field()
    reach = scrapy.Field()
    stance = scrapy.Field()
    dob = scrapy.Field()
