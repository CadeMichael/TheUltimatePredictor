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
            name = (
                item.css("a.b-link_style_black::text")
                .get()
                .strip()
                .lower()
                .replace(" ", "-")
            )
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
        # extract all rows (skip the first one, which is the header)
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
            # url for more fight information
            fight_details_url = row.css(
                "tr.b-fight-details__table-row::attr(data-link)"
            )[0].get()

            # check for draw
            if is_draw:
                # for draws, both fighters are considered equal
                winner = "N/A"
                loser = "N/A"
                outcome = "draw"
            else:
                # for wins, first fighter is the winner
                winner = fighter1
                loser = fighter2
                outcome = "win"

            # extract the method of win and check if there's a second line with additional details
            method = (
                row.css("td:nth-child(8) .b-fight-details__table-text::text")
                .get()
                .strip()
            )
            # check if there's a second <p> tag for the type of submission/KO
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
            fight_item: FightItem = FightItem()
            fight_item["event_name"] = event_name
            fight_item["event_date"] = event_date
            fight_item["outcome"] = outcome
            fight_item["winner"] = winner if winner == "N/A" else winner[0]
            fight_item["loser"] = loser if loser == "N/A" else loser[0]
            fight_item["f1_name"] = fighter1[0]
            fight_item["f1_strikes"] = '""'
            fight_item["f1_td"] = '""'
            fight_item["f1_td_def"] = '""'
            fight_item["f2_name"] = fighter2[0]
            fight_item["f2_strikes"] = '""'
            fight_item["f2_td"] = '""'
            fight_item["f2_td_def"] = '""'
            fight_item["method"] = method
            fight_item["method_details"] = method_details if method_details else "N/A"
            fight_item["end_round"] = end_round
            fight_item["time"] = time
            fight_item["total_time"] = total_time
            fight_item["weight_class"] = weight_class

            if fight_details_url: # get additional fight information
                yield scrapy.Request(
                    fight_details_url,
                    callback=self.parse_fight_details,
                    meta={
                        "fight_item": fight_item,
                        "fighter1": fighter1,
                        "fighter2": fighter2,
                    }
                )
            else: # no additional fight information
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
                                "name": name,
                            },
                        )
                

    def parse_fight_details(self, response):
        # get meta data from response
        fight_item: FightItem = response.meta["fight_item"]
        fighter1 = response.meta["fighter1"]
        fighter2 = response.meta["fighter2"]
        f1_name = fighter1[0]

        # --- helper functions ---
        def str_int(data):
            try:
                return int(data)
            except:
                return '""'

        def tk_def(td1, td2):
            no_data = ('""', '""')
            if len(td1) < 2 or not isinstance(td1[0], int):
                return no_data
            if len(td2) < 2 or not isinstance(td2[0], int):
                return no_data
            td_def_1 = td2[1] / td2[0]
            td_def_2 = td1[1] / td1[0]
            return (td_def_1, td_def_2)

        # --- get extra fight details from response ---

        # first table row contains desired stats
        table = response.css("tbody.b-fight-details__table-body")

        # some fights have a link but don't have more details
        if len(table) < 2:
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
                            "name": name,
                        },
                    )
        else:
            table_body = table[0]
            # get fighter names in order they appear on fight stat page
            fighters_from_details = table_body.css("a.b-link_style_black::text").getall()
            f1_name_details = fighters_from_details[0].strip().lower()
            f2_name_details = fighters_from_details[1].strip().lower()
            # dicts for fighters in the order they appear on fight stats page
            f1_details = {"name": f1_name_details}
            f2_details = {"name": f2_name_details}
            # columns contain statistics
            columns = table_body.css("td.b-fight-details__table-col")
            # strike data
            strike_data = columns[2].css("p.b-fight-details__table-text::text").getall()
            f1_details["d1_strikes"] = int(strike_data[0].strip().split(" ")[0])
            f2_details["d2_strikes"] = int(strike_data[1].strip().split(" ")[0])
            # takedown data
            td_data = columns[5].css("p.b-fight-details__table-text::text").getall()
            # data in the form of "completed of attempted"
            f1_td_info = list(map(str_int, td_data[0].strip().replace("of","").split()))
            f2_td_info = list(map(str_int, td_data[1].strip().replace("of","").split()))
            # completed takedowns
            f1_details["d1_td"] = f1_td_info[0]
            f2_details["d2_td"] = f2_td_info[0]
            # calculate defended takedowns
            td_defs = tk_def(f1_td_info, f2_td_info)
            # populate dict
            f1_details["d1_td_def"] = td_defs[0]
            f2_details["d2_td_def"] = td_defs[1]

            # order in fight table not always the same as order in fight details page
            if f1_name_details == f1_name: # order matches
                for k, v in f1_details.items():
                    if k != "name": # already have name field
                        # properly label fighter item data
                        fk = k.replace("d1", "f1")
                        # populate FighterItem
                        fight_item[fk] = v
                for k, v in f2_details.items():
                    if k != "name":
                        # properly label fighter item data
                        fk = k.replace("d2", "f2")
                        # populate FighterItem
                        fight_item[fk] = v
            else: # order doesn't match
                for k, v in f1_details.items():
                    if k != "name": # already have name field
                        # properly label fighter item data
                        fk = k.replace("d1", "f2")
                        # populate FighterItem
                        fight_item[fk] = v
                for k, v in f2_details.items():
                    if k != "name":
                        # properly label fighter item data
                        fk = k.replace("d2", "f1")
                        # populate FighterItem
                        fight_item[fk] = v

            # return fight with added information
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
                            "name": name,
                        },
                    )

    def parse_fighter(self, response):
        # create fighter item
        fighter_item: FighterItem = FighterItem()

        # get information from meta data
        name = response.meta["name"]

        # add to fighter item
        fighter_item["name"] = name

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
                    value = self.height_to_inches(value) if value != "--" else ""
                case "reach":
                    # only convert if information is present
                    value = float(value.replace('"', "")) if value != "--" else ""
                case "weight":
                    # fighters change weightclass so go by fight
                    continue
                # handle missing data
                case "":
                    continue
                case _:
                    value = value if value != "--" else ""
            fighter_item[title] = value

        # yield new fighter item
        yield fighter_item
