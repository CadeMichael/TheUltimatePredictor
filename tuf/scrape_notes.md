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
        # events.append([link,date])
        print({name: [link, date]})
len(events)

```

# Fights

```python
# get a specific fight (can't be 0)
def getFight(i):
    row = response.css('tr.b-fight-details__table-row')[i]
    # extract the winner and loser names
    fighters = row.css('td:nth-child(2) .b-link_style_black::text').getall()
    winner = fighters[0].strip()  # First fighter is the winner
    loser = fighters[1].strip()   # Second fighter is the loser
    # extract the method of win, round, time, and weight class
    method = row.css('td:nth-child(8) .b-fight-details__table-text::text').get().strip()
    round_ = row.css('td:nth-child(9) .b-fight-details__table-text::text').get().strip()
    time = row.css('td:nth-child(10) .b-fight-details__table-text::text').get().strip()
    weight_class = row.css('td:nth-child(7) .b-fight-details__table-text::text').get().strip()
    # print the results
    print({
        "win": winner,
        "loss": loser,
        "method": method,
        "round": round_,
        "time": time,
        "weight_class": weight_class,
    })

# get all fights in an event
def allEventFights(response):
    # Extract all rows (skip the first one, which is the header)
    fight_rows = response.css('tr.b-fight-details__table-row')[1:]  # Exclude the first row (header)
    # Initialize an empty list to store fight details
    fights = []
    # Loop over all fight rows
    for row in fight_rows:
        # Extract the winner and loser names
        fighters = row.css('td:nth-child(2) .b-link_style_black::text').getall()
        winner = fighters[0].strip()  # First fighter is the winner
        loser = fighters[1].strip()   # Second fighter is the loser
        # Extract the method of win and check if there's a second line with additional details
        method = [row.css('td:nth-child(8) .b-fight-details__table-text::text').get().strip()]
        method_type = None
        # Check if there's a second <p> tag for the type of submission/KO
        method_details = row.css('td:nth-child(8) .b-fight-details__table-text + .b-fight-details__table-text::text').get()
        if method_details:
            method_type = method_details.strip()  # The second line is the method type (e.g., "Arm Triangle")
        # Combine method and method_type (if available)
        if method_type:
            method.append(method_type)
        round_ = row.css('td:nth-child(9) .b-fight-details__table-text::text').get().strip()
        time = row.css('td:nth-child(10) .b-fight-details__table-text::text').get().strip()
        weight_class = row.css('td:nth-child(7) .b-fight-details__table-text::text').get().strip()
        # Store the extracted data in a dictionary
        fight_info = {
            "winner": winner,
            "loser": loser,
            "method": method,
            "round": round_,
            "time": time,
            "weight_class": weight_class,
        }
        # Append the fight information to the list
        fights.append(fight_info)
        print(f"{winner} via {method} @ {time} of round {round_}")
    # Now 'fights' contains all the extracted fight details
    # print(fights)
    return fights

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
        fighter1 = fighters[0].strip()
        fighter2 = fighters[1].strip() if len(fighters) > 1 else None
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
            print(f"Draw between {fighter1} and {fighter2} via {method} @ {time} of round {round_}\n->fight time of {total_time} seconds")
        else:
            print(f"{winner} via {method} @ {time} of round {round_}\n->fight time of {total_time} seconds")
    return fights
```

# Fighters
