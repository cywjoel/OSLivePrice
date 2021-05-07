import discord
from discord.ext import commands
from discord.ext.commands import Bot
import logging
import json
from datetime import datetime               # for dealing with unix timestamps
from osrsreqs import osrsreqs                             # proprietary package

''' NOTES ----------------------------------

data = id_mapping.json
data_latest = data pulled from the /latest API

---------------------------------------- '''

# START LOGGING ----------------------------
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
# END LOGginG ------------------------------

''' CONFIG '''
with open('config.json') as f_conf:
    config = json.load(f_conf)
    config_prefix = config['prefix']
    config_token = config['token']

''' BOT TOKEN '''
token = config_token

''' MANAGE INTENTS '''
intents = discord.Intents.default()

bot = commands.Bot(command_prefix = config_prefix, intents = intents)               # set bot command prefix
# note: we don't use client = Discord.client() because Client is subclass of Bot. Client won't let you use @bot.command()

with open('id_mapping.json') as f:                  # open id_mapping.json, so it can be called everywhere
    raw_data = f.read()                             # read the json file
    data = json.loads(raw_data)                     # json.loads() the data

''' COMMANDS '''

# user get item info by id
@bot.command(name = 'iteminfo')
async def get_item_info(ctx, id_num):               # get item info
    for d in data:                                  # d for dictionary
        if int(id_num) == d['id']:                  # if id_num == id value in dict, get the values below. refer to id_mapping.json for keys
            item_id = d['id']
            item_name = d['name']
            item_shop_value = d['value']
            item_high_alch = d['highalch']
            item_ge_limit = d['limit']

            # create discord embed to display info using the values above (title, field)
            result_item = discord.Embed(color = 0xddc000)        # create new embed result_item
            result_item.title = "Data for Item ID #" + str(item_id)
            field_value = "Shop value: " + str(item_shop_value) + "\n" + "High Level Alchemy value: " + str(item_high_alch) + "\n" + "GE buy limit: " + str(item_ge_limit)
            result_item.add_field(name = item_name, value = field_value, inline = True)

            await ctx.send(embed = result_item)     # send the message
    
    if all(int(id_num) != d['id'] for d in data):   # send the "no item" message if id doesnt exist in dict
        await ctx.send('No such item id exists.')

# user get item id by name field
@bot.command(name = 'itemsearch')
async def search_item_by_name(ctx, *terms):         # read as many terms...
    search_term = " ".join(terms)                   # then concatenate into 1 search term
    id_list = ""
    name_list = ""
    for d in data:
        if search_term.lower() in d['name'].lower():    # convert to lowercase to match all cases
            id_list = id_list + str(d['id']) + "\n"     # basically how this list is displayed in the embed:
            name_list = name_list + d['name'] + "\n"    # it's not a list, but it's a string with line breaks

    result_item = discord.Embed(color = 0xddc000)           # create a new embed item
    result_item.title = "Search results for \"" + search_term + "\""
    result_item.add_field(name = "Item ID", value = id_list, inline = True)
    result_item.add_field(name = "Item name", value = name_list, inline = True)
        
    if id_list == "" and name_list == "":                   # id the lists are empty, then the search obviously has no results
        await ctx.send('No items matched your search.')
    else:                                                   # otherwise return the embed
        await ctx.send(embed = result_item)

# user get latest prices from API /latest
@bot.command(name = 'latest')
async def get_latest_price(ctx, id_num):
    for d in data:
        if int(id_num) == d['id']:
            item_name = d['name']                 # get name from mapping.json

            latest_data = osrsreqs.get_latest(id_num)      # pull data from api and get values below
            result_high = latest_data['high']
            result_high_time = datetime.fromtimestamp(latest_data['highTime']).strftime('%d %B %Y, %H:%M:%S UTC')
            result_low = latest_data['low']
            result_low_time = datetime.fromtimestamp(latest_data['lowTime']).strftime('%d %B %Y, %H:%M:%S UTC')

            # create discord embed
            result_item = discord.Embed(color = 0xddc000)
            result_item.title = "Latest prices for Item ID #" + str(id_num)
            field_value = "High price: " + str(result_high) + " gp (" + result_high_time + ")" + "\n" + "Low price: " + str(result_low) + " gp (" + result_low_time + ")"
            result_item.add_field(name = item_name, value = field_value, inline = True)

            await ctx.send(embed = result_item)     # send the message
    
    if all(int(id_num) != d['id'] for d in data):   # send the "no item" message if id doesnt exist in dict
        await ctx.send('No such item id exists.')

# probably the stupidest test command in the world
@bot.command()
async def talk(ctx, arg):
    await ctx.send('You\'re talking to me about {}?'.format(arg))

''' EVENTS '''

@bot.event
async def on_ready():                                   # called when the bot has successfully logged into discord
    print('Logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.author == bot.user:                   # check if message is sent by this bot; if yes, don't send message
        return
    
    if message.content.startswith('r.hello'):           # test hello message
        await message.channel.send('Hello')

    await bot.process_commands(message)                 # allow commands to be processed

bot.run(token)