import scrapy
from tuf.items import FightItem, FighterItem


class TufSpider(scrapy.Spider):
    # site information
    name = "tuf_spider"
    allowed_domains = ["ufcstats.com"]
    start_urls = [
        "http://ufcstats.com/statistics/events/completed?page=all",
    ]

    # individual fighters whose pages we've parsed
    scraped_fighters = set()

    # --- helper methods ---
    def height_to_inches(self, height_str):
        # clean height string
        feet, inches = height_str.replace('"', "").split("' ")
        # convert to floats and calculate height in inches
        total_inches = float(feet) * 12 + float(inches)
        return total_inches

    # parsing all events
    def parse(self, response):
        # ufc events
        events = []
        # need to ignore the first listed event as it is "upcoming"
        for item in response.css(".b-statistics__table-content")[1:]:
            # get event name, link, and date
            name = item.css("a.b-link_style_black::text").get().strip()
            link = item.css("a.b-link_style_black::attr(href)").get().strip()
            date = item.css(".b-statistics__date::text").get().strip()
            if link and date:  # check for proper information
                events.append((link, name, date))  # add tuple to list of events

        # crawl each event
        for url, name, date in events:
            yield scrapy.Request(
                url,
                callback=self.parse_event,
                meta={
                    "event_url": url,
                    "event_name": name,
                    "event_date": date,
                },
            )

    def parse_event(self, response):
        # --- get event meta data ---
        # event_url = response.meta["event_url"]
        event_name = response.meta["event_name"]
        event_date = response.meta["event_date"]

        # --- scrape fights ---
        # Extract all rows (skip the first one, which is the header)
        fight_rows = response.css("tr.b-fight-details__table-row")[1:]
        # each row represents one fight of the current event
        for row in fight_rows:
            # check for draw
            draw_flags = row.css("td:nth-child(1) .b-flag__text::text").getall()
            is_draw = len(draw_flags) == 2 and all(
                flag.strip().lower() == "draw" for flag in draw_flags
            )

            # scrape fighter info
            fighters = row.css("td:nth-child(2) .b-link_style_black::text").getall()
            fighter_links = row.css(
                "td:nth-child(2) .b-link_style_black::attr(href)"
            ).getall()
            fighter1 = (fighters[0].strip().lower(), fighter_links[0])
            fighter2 = (fighters[1].strip().lower(), fighter_links[1])
            # fighters = [fighter1, fighter2]

            # check for draw
            if is_draw:
                # For draws, both fighters are considered equal
                winner = None
                loser = None
                outcome = "draw"
            else:
                # For wins, first fighter is the winner
                winner = fighter1
                loser = fighter2
                outcome = "win"

            # Extract the method of win and check if there's a second line with additional details
            method = (
                row.css("td:nth-child(8) .b-fight-details__table-text::text")
                .get()
                .strip()
            )
            # Check if there's a second <p> tag for the type of submission/KO
            method_details = row.css(
                "td:nth-child(8) .b-fight-details__table-text + .b-fight-details__table-text::text"
            ).get()
            if method_details:
                method_details = method_details.strip()

            # get weight class of fight
            weight_class = (
                row.css("td:nth-child(7) .b-fight-details__table-text::text")
                .get()
                .strip()
            )
            # get the ending round and the time in that round the fight ended
            end_round = (
                row.css("td:nth-child(9) .b-fight-details__table-text::text")
                .get()
                .strip()
            )
            time = (
                row.css("td:nth-child(10) .b-fight-details__table-text::text")
                .get()
                .strip()
            )
            # calculate the total time of the fight
            minutes, seconds = map(float, time.split(":"))
            time_in_seconds = minutes * 60 + seconds
            # calculation: (end_round-1)*5 minutes + time
            total_time = (
                float(end_round) - 1
            ) * 300 + time_in_seconds  # 300 seconds = 5 minutes

            # create a new fight item
            fight_item = FightItem()
            fight_item["event_name"] = event_name
            fight_item["event_date"] = event_date
            fight_item["outcome"] = outcome
            fight_item["winner"] = None if winner is None else winner[0]
            fight_item["loser"] = None if loser is None else loser[0]
            fight_item["f1_name"] = fighter1[0]
            # fight_item["f1_url"] = fighter1[1]
            fight_item["f2_name"] = fighter2[0]
            # fight_item["f2_url"] = fighter2[1]
            fight_item["method"] = method
            fight_item["method_details"] = method_details if method_details else None
            fight_item["end_round"] = end_round
            fight_item["time"] = time
            fight_item["total_time"] = total_time
            fight_item["weight_class"] = weight_class

            # yield current fight info
            yield fight_item

            # follow fighter links for current fight
            for name, url in [fighter1, fighter2]:
                # check if this fighter has been scraped
                if url not in self.scraped_fighters:
                    # mark fighter as scraped
                    self.scraped_fighters.add(url)
                    # crawl to fighter info page
                    yield scrapy.Request(
                        url,
                        callback=self.parse_fighter,
                        meta={
                            # "url": url,
                            "name": name,
                        },
                    )

    def parse_fighter(self, response):
        # create fighter item
        fighter_item = FighterItem()

        # get information from meta data
        # url = response.meta["url"]
        name = response.meta["name"]

        # add to fighter item
        fighter_item["name"] = name
        # fighter_item["url"] = url

        # only take the first 5 items (Height, Weight, Reach, Stance, DOB)
        stats = response.css("ul.b-list__box-list li.b-list__box-list-item")[:5]
        for item in stats:
            info = item.css("i.b-list__box-item-title::text").get().strip()
            value = item.xpath("text()").getall()[1].strip()
            title = info.lower().replace(":", "")
            # handle different titles
            match title:
                case "height":
                    # only convert if information is present
                    value = self.height_to_inches(value) if value != "--" else None
                case "reach":
                    # only convert if information is present
                    value = float(value.replace('"', "")) if value != "--" else None
                case "weight":
                    # fighters change weightclass so go by fight
                    continue
                # handle missing data
                case "":
                    continue
                case _:
                    value = value if value != "--" else None
            fighter_item[title] = value

        # yield new fighter item
        yield fighter_item
