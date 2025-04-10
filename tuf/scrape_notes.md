# Events

## getting links and dates

```python
# getting text
>>> response.css(".b-link_style_black::text")[0].get()
'\n                          UFC Fight Night: Emmett vs. Murphy\n                        '
>>> response.css(".b-statistics__date::text")[0].get()
'\n                          April 12, 2025\n

# getting all html data
>>> response.css(".b-link_style_black")[0].get()
'<a href="http://ufcstats.com/event-details/86b30a86664cb6e4" class="b-link b-link_style_black">\n                          UFC Fight Night: Emmett vs. Murphy\n                        </a>'

# getting all links to *Events*
response.css(".b-link_style_black::attr(href)").getall()

# getting all events except the first (upcoming) event
>>> len(response.css('tr a.b-link_style_black::attr(href)')[1:].getall())
726

# getting event links + event dates
events = []
for item in response.css('.b-statistics__table-content')[1:]:
    name = item.css('a.b-link_style_black::text').get().strip()
    link = item.css('a.b-link_style_black::attr(href)').get().strip()
    date = item.css('.b-statistics__date::text').get().strip()
    if link and date:
        events.append([link,date])
return events

```

# Fights

```python
# get all fights for an event (checking for draws)
def allEventFights(response):
    # Extract all rows (skip the first one, which is the header)
    fight_rows = response.css('tr.b-fight-details__table-row')[1:]  # Exclude the first row (header)
    # Initialize an empty list to store fight details
    fights = []
    # Loop over all fight rows
    for row in fight_rows:
        # Check if it's a draw by looking for two "draw" flags in the first column
        draw_flags = row.css('td:nth-child(1) .b-flag__text::text').getall()
        is_draw = len(draw_flags) == 2 and all(flag.strip().lower() == 'draw' for flag in draw_flags)
        # Extract the fighter names
        fighters = row.css('td:nth-child(2) .b-link_style_black::text').getall()
        fighter_links = row.css('td:nth-child(2) .b-link_style_black::attr(href)').getall()
        fighter1 = (fighters[0].strip().lower(), fighter_links[0])
        fighter2 = (fighters[1].strip().lower(), fighter_links[1])
        # check for draw
        if is_draw:
            # For draws, both fighters are considered equal
            winner = None
            loser = None
            fighters = [fighter1, fighter2]
            outcome = "draw"
        else:
            # For wins, first fighter is the winner
            winner = fighter1
            loser = fighter2
            fighters = None
            outcome = "win"
        # Extract the method of win and check if there's a second line with additional details
        method = [row.css('td:nth-child(8) .b-fight-details__table-text::text').get().strip()]
        method_type = None
        # Check if there's a second <p> tag for the type of submission/KO
        method_details = row.css('td:nth-child(8) .b-fight-details__table-text + .b-fight-details__table-text::text').get()
        if method_details:
            method_type = method_details.strip()
        # Combine method and method_type (if available)
        if method_type:
            method.append(method_type)
        # get the rest of the info
        round_ = row.css('td:nth-child(9) .b-fight-details__table-text::text').get().strip()
        time = row.css('td:nth-child(10) .b-fight-details__table-text::text').get().strip()
        weight_class = row.css('td:nth-child(7) .b-fight-details__table-text::text').get().strip()
        # Convert time from "M:SS" format to total seconds
        minutes, seconds = map(float, time.split(':'))
        time_in_seconds = minutes * 60 + seconds
        # Calculate total time: (round-1)*5 minutes + current round time
        total_time = (float(round_) - 1) * 300 + time_in_seconds  # 300 seconds = 5 minutes
        # Store the extracted data in a dictionary
        fight_info = {
            "outcome": outcome,  # "win" or "draw"
            "winner": winner,
            "loser": loser,
            "fighters": fighters if is_draw else None,  # Only populated for draws
            "method": method,
            "round": round_,
            "time": time,
            "total_time": total_time,
            "weight_class": weight_class,
        }
        # Append the fight information to the list
        fights.append(fight_info)
        if is_draw:
            print(f"Draw between {fighter1[0]} and {fighter2[0]} via {method} @ {time} of round {round_}\n->fight time of {total_time} seconds")
        else:
            print(f"{winner[0]} via {method} @ {time} of round {round_}\n->fight time of {total_time} seconds")
    return fights
```

# Fighters

```python
# when clicking on a fight get the links to the two fighters
def getFighterLinks(response):
    links = response.css("a.b-fight-details__person-link::attr(href)").getall()
    fighters = response.css("a.b-fight-details__person-link::text").getall()
    fighter_links = {
        fighters[0] : links[0],
        fighters[1] : links[1],
    }
    # print(fighter_links)
    return fighter_links

# response.css(".b-list__box-list")[0].get() # first "box" contains data
# helper for calculating height in inches
def height_to_inches(height_str):
    # Remove quotes and split into feet and inches
    feet, inches = height_str.replace('"', '').split("' ")
    # Convert to integers and calculate total inches
    total_inches = float(feet) * 12 + float(inches)
    return total_inches
# get a fighters info from their page
def getFighterStats(response):
    # title conversion for cleaner data
    reference = {
        "height:" : "height",
        "weight:" : "weight",
        "reach:" : "reach",
        "stance:" : "stance",
        "dob:" : "dob",
    }
    # individual fighter stats
    stats = {}
    # get fighter name
    fighter = response.css(".b-content__title-highlight::text")[0].get()
    stats["fighter"] = fighter.strip().lower()
    # only take the first 5 items (Height, Weight, Reach, Stance, DOB)
    first_box_list = response.css('ul.b-list__box-list li.b-list__box-list-item')[:5]
    for item in first_box_list:
        info = item.css('i.b-list__box-item-title::text').get().strip()
        value = item.xpath('text()').getall()[1].strip()
        title = reference[info.lower()]
        # handle different titles
        match title:
            case "":
                continue
            case "height":
                value = height_to_inches(value)
            case "reach":
                value = float(value.replace('"',''))
            case "weight":
                # fighters change weightclass so go by fight
                continue
        stats[title] = value if value != "--" else None
    return stats
```
