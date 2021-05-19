# OSLivePrice

### A Discord bot for fetching live *Old School RuneScape* item prices from the *RuneLite/OSRS Wiki* API

This bot is a work in progress, and more functions will be added in due time.

Set your command prefix and Discord bot token and save as config.json to use the bot:

```
{
    "prefix": "<your command prefix here>",
    "token": "<your bot token here>"
}
```

Current functions (assume prefix is "r."):
* `r.info <id>`: returns basic info for item
* `r.search <search term>`: returns all items which match the search term (can use spaces between terms)
* `r.latest <id>`: returns latest prices for item
* `r.highalch <id>`: returns high alch profit for item
* `r.topalch`: returns all items with positive high alch profit
* `r.5min <id>`: returns a chart of item's price over the last 4 hours, in 5-minute intervals
* `r.1hr <id>`: returns a chart of item's price over the last 2 days, in 1-hour intervals

*Note: Run `getmapping.py` to update the id_mapping.json.*