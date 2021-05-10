# OSLivePrice

### A Discord bot for fetching live *Old School RuneScape* item prices

This bot is a work in progress, and more functions will be added in due time.

Set your command prefix and Discord bot token and save as config.json to use the bot:

```
{
    "prefix": "<your command prefix here>",
    "token": "<your bot token here>"
}
```

Current functions (assume prefix is "r."):
* r.iteminfo <id>: returns basic info for item
* r.itemsearch <search term>: returns all items which match the search term (can use spaces between terms)
* r.latest <id>: returns latest prices for item
* r.highalch <id>: returns high alch profit for item