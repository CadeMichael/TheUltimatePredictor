---
# You can also start simply with 'default'
theme: default
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
# some information about your slides (markdown enabled)
title: The Ultimate Predictor
info: |
  ## T U F
  Analyzing UFC: Submission Insights and Predicting Fights
  Cade Lueker CSCI5434

# https://sli.dev/features/drawing
drawings:
  persist: false
# slide transition: https://sli.dev/guide/animations.html#slide-transitions
transition: slide-left
# enable MDC Syntax: https://sli.dev/features/mdc
mdc: true
hideInToc: true
# open graph
# seoMeta:
#  ogImage: https://cover.sli.dev
---

# The Ultimate Predictor

Cade Lueker CSCI5434

Analyzing UFC: Submission Insights and Predicting Fights

---

# The Why

<div style="
  display: flex;
  justify-content: center;
  align-items: center;
  height: 95%;
">
<img
    src="./figures/comp_throw.jpg"
    alt="Rates"
    style="max-width: 100%; max-height: 100%; height: auto;"
    />
</div>

---

# Web Scraping

````md magic-move
```python
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
    f1_strikes = scrapy.Field()
    f1_td = scrapy.Field()
    f1_td_def = scrapy.Field()
    f2_name = scrapy.Field()
    f2_strikes = scrapy.Field()
    f2_td = scrapy.Field()
    f2_td_def = scrapy.Field()
    method = scrapy.Field()
    method_details = scrapy.Field()
    end_round = scrapy.Field()
    time = scrapy.Field()
    total_time = scrapy.Field()
    weight_class = scrapy.Field()
```

```python
class FighterItem(scrapy.Item):
    """
    Information about a fighter who has at least one fight in a UFC event.
    """

    name = scrapy.Field()
    height = scrapy.Field()
    reach = scrapy.Field()
    stance = scrapy.Field()
    dob = scrapy.Field()
```

```python
class TufSpider(scrapy.Spider):
    name = "tuf_spider"
    allowed_domains = ["ufcstats.com"]
    start_urls = [
        "http://ufcstats.com/statistics/events/completed?page=all",
    ]
    scraped_fighters = set()
    # --- helper methods ---
    def height_to_inches(self, height_str): ...
    # parsing all events
    def parse(self, response): ...
    # parse individual event
    def parse_event(self, response): ...
    # if available parse fight details
    def parse_fight_details(self, response): ...
    # parse individual fighter information
    def parse_fighter(self, response): ...
```
````

---

# Cleaning and Combining the Data

```python
for fighter_num in ['f1', 'f2']:
    fights = fights.merge(
        fighters[['name', 'height', 'reach', 'stance', 'dob']],
        left_on=f'{fighter_num}_name',
        right_on='name',
        how='left',
        suffixes=('', f'_{fighter_num}')
    )
    fights = fights.rename(columns={
        'height': f'{fighter_num}_height',
        'reach': f'{fighter_num}_reach',
        'stance': f'{fighter_num}_stance',
        'dob': f'{fighter_num}_dob'
    })
    fights[f'{fighter_num}_age'] = fights.apply(
        lambda x: calculate_age(x[f'{fighter_num}_dob'], x['event_date']),
        axis=1
    )
    fights.drop(columns=['name'], inplace=True) # already have their names

fights['reach_diff'] = (fights['f1_reach'] - fights['f2_reach']).abs()
fights['height_diff'] = (fights['f1_height'] - fights['f2_height']).abs()
fights['age_diff'] = (fights['f1_age'] - fights['f2_age']).abs()
```

---

# Submission rates

<div style="
  display: flex;
  justify-content: center;
  align-items: center;
  height: 95%;
">
<img
    src="./figures/SubmissionRates.png"
    alt="Rates"
    style="max-width: 100%; max-height: 100%; height: auto;"
    />
</div>

---

# Submission Rates by Weightclass

<div style="
  display: flex;
  justify-content: center;
  align-items: center;
  height: 95%;
">
<img
    src="./figures/SubmissionDistributions.png"
    alt="Rates"
    style="max-width: 100%; max-height: 100%; height: auto;"
    />
</div>

---

# Submissions by round

<div style="
  display: flex;
  justify-content: center;
  align-items: center;
  height: 95%;
">
<img
    src="./figures/SubmissionRoundsLine.png"
    alt="Rates"
    style="max-width: 100%; max-height: 100%; height: auto;"
    />
</div>

---

# Submissions by round CDF

<div style="
  display: flex;
  justify-content: center;
  align-items: center;
  height: 95%;
">
  <img 
    src="./figures/SubmissionRoundCDF.png"
    alt="Rates" 
    style="max-width: 100%; max-height: 100%; height: auto;"
  />
</div>

---

# Submissions to Height

<div style="
  display: flex;
  justify-content: center;
  align-items: center;
  height: 95%;
">
<img
    src="./figures/HeightToSubmission.png"
    alt="Rates"
    style="max-width: 100%; max-height: 100%; height: auto;"
    />
</div>

---

# Normalizing Heights and Linear Regression

- a short heavyweight  might be a tall lightweight so normalizing by weightclass gives better insight.

````md magic-move
```python
# add heights normalized by weightclass
fights['f1_norm_height'] = fights.groupby('weight_class')['f1_height'].transform(
    lambda x: (x - x.mean()) / x.std()
)
fights['f2_norm_height'] = fights.groupby('weight_class')['f2_height'].transform(
    lambda x: (x - x.mean()) / x.std()
)
```

```python
# regression values
slope, _, r_value, p_value, _ = stats.linregress(
    sub_df['norm_height'], sub_df['sub_percent']
)
```
````

---

# Submissions to Normalized Height

<div style="
  display: flex;
  justify-content: center;
  align-items: center;
  height: 95%;
">
<img
    src="./figures/NormHeightToSubmission.png"
    alt="Rates"
    style="max-width: 100%; max-height: 100%; height: auto;"
    />
</div>

---

# Submissions to Normalized Reach

<div style="
  display: flex;
  justify-content: center;
  align-items: center;
  height: 95%;
">
<img
    src="./figures/NormReachToSubmission.png"
    alt="Rates"
    style="max-width: 100%; max-height: 100%; height: auto;"
    />
</div>

---

# Takedowns to Normalized Height

<div style="
  display: flex;
  justify-content: center;
  align-items: center;
  height: 95%;
">
<img
    src="./figures/NormHeightToTakedowns.png"
    alt="Rates"
    style="max-width: 100%; max-height: 100%; height: auto;"
    />
</div>

---

# Age of Winning Fighter CDF

Code to calculate CDF

```python
# convert into df for better manipulation
win_ages = pd.DataFrame(winners_age, columns=['age'])

# sort ages and remove nonexistant data (fighters pre 2000 sometimes don't have their ages recorded)
sorted_ages = np.sort(win_ages['age'].dropna())

# normalize the data
mu, sigma = stats.norm.fit(win_ages['age'].dropna())

# get points for cdf
x = np.linspace(min(sorted_ages), max(sorted_ages), 100)
y = np.arange(1, len(sorted_ages) + 1) / len(sorted_ages)

# get CDF
cdf_fitted = stats.norm.cdf(x, mu, sigma)
```

---

# Age of Winning CDF Plotted

<div style="
  display: flex;
  justify-content: center;
  align-items: center;
  height: 95%;
">
<img
    src="./figures/AgeOfWinCDF.png"
    alt="Rates"
    style="max-width: 100%; max-height: 100%; height: auto;"
    />
</div>

---

# Prediction

- creating a new dataframe with historical data for each fighter

```python
def build_fighter_history(fights):
    rows = []

    for _, row in fights.iterrows():
        event_date = row['event_date']
        previous_fights = fights[fights['event_date'] < event_date]

        # fighter 1 stats from previous fights
        past_f1 = previous_fights[(previous_fights['f1_name'] == row['f1_name']) | (previous_fights['f2_name'] == row['f1_name'])]
        # fighter 2 stats from previous fights
        past_f2 = previous_fights[(previous_fights['f1_name'] == row['f2_name']) | (previous_fights['f2_name'] == row['f2_name'])]
        
        # fighter 1
        # strikes
        avg_f1_strikes = past_f1['f1_strikes'].mean()
        # takedowns
        avg_f1_td = past_f1['f1_td'].mean()
        avg_f1_td_def = past_f1['f1_td_def'].mean()
        avg_f1_td_rate = past_f1['f1_td_rate'].mean()
        avg_f1_td_def_rate = past_f1['f1_td_def_rate'].mean()
        ...
```

---

# All possible features

```python
features = [
    # strikes
    # 'strikes',
    # takedown
    # 'td', # 'td_def', # 'td_rate', # 'td_def_rate',
    # metrics
    # 'height', # 'reach', # 'age', # 'stance',
    # record
    'last',
    'last_3',
    'record',
    'ko_loss',
    'ko_rate',
    # 'already_beat', # 'opp_strikes', # 'opp_td', # 'opp_td_def',
    # 'opp_td_rate', # 'opp_td_def_rate', # 'opp_height', # 'opp_reach',
    # 'opp_age', # 'opp_stance', # opponent record
    'opp_last',
    'opp_last_3',
    'opp_record',
    'opp_ko_loss',
    'opp_ko_rate',
    # 'opp_already_beat',
    # differentials
    'age_diff', 'strikes_diff', 'td_diff', 'reach_diff', 'height_diff',
]
```

---

# Splitting the data

- because each fight contains historical data we need to split by date otherwise we could see leakage in our model

```python
# start with oldest now
df = df.sort_values('event_date', ascending=True)
print(df.head(1))

# 80% train, 20% test
split_idx = int(len(df) * 0.8)
train_df = df.iloc[:split_idx]
test_df = df.iloc[split_idx:]
```

---

# xgboost

```python
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

xgb_model = xgb.XGBClassifier(
    objective='binary:logistic',
    eval_metric='auc',
    max_depth=3,
    learning_rate=0.01,
    n_estimators=1000,
    subsample=0.7,
    colsample_bytree=0.7,
    reg_alpha=0.5,
    reg_lambda=0.5,
    early_stopping_rounds=20,
)

xgb_model.fit(
    X_train_scaled, y_train,
    eval_set=[(X_train_scaled, y_train), (X_test_scaled, y_test)],
)


y_pred = xgb_model.predict(X_test_scaled)
y_pred_proba = xgb_model.predict_proba(X_test_scaled)[:, 1]
```

---

# Random Forest

```python
forest_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    random_state=5
)

forest_model.fit(X_train, y_train)
preds = forest_model.predict(X_test)
pred_probs = forest_model.predict_proba(X_test)[:, 1]
```

---

# Results

- **xgboost**
    + Accuracy: *0.6139*
    + ROC AUC: *0.6475*
- **Random Forest**
    + Accuracy: *0.6094*
    + ROC AUC: *0.6463*
---
