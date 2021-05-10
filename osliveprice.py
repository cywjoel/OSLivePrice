import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
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

''' CONFIG --------------------------------------------- '''
with open('config.json') as f_conf:
    config = json.load(f_conf)
    config_prefix = config['prefix']
    config_token = config['token']

''' BOT TOKEN ------------------------------------------ '''
token = config_token

''' MANAGE INTENTS --------------------------------------'''
intents = discord.Intents.default()

bot = commands.Bot(command_prefix = config_prefix, intents = intents)               # set bot command prefix
# note: we don't use client = Discord.client() because Client is subclass of Bot. Client won't let you use @bot.command()

with open('id_mapping.json') as f:                  # open id_mapping.json, so it can be called everywhere
    raw_data = f.read()                             # read the json file
    data = json.loads(raw_data)                     # json.loads() the data

''' COMMANDS ------------------------------------------ '''

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
            image_link = 'https://secure.runescape.com/m=itemdb_oldschool/obj_big.gif?id=' + str(id_num)
            result_item.set_thumbnail(url = image_link)

            await ctx.send(embed = result_item)     # send the message
    
    if all(int(id_num) != d['id'] for d in data):   # send the "no item" message if id doesnt exist in dict
        await ctx.send('No such item id exists.')

# user get item id by name field
@bot.command(name = 'itemsearch')
async def search_item_by_name(ctx, *terms):         # read as many terms...
    search_term = " ".join(terms)                   # then concatenate into 1 search term
    id_list = []
    name_list = []
    for d in data:
        if search_term.lower() in d['name'].lower():    # convert to lowercase to match all cases
            id_list.append(d['id'])                     # append in list (remember to str(d['id'])!!!)
            name_list.append(d['name'])
    
    ''' Helpful Functions for this Command (used below) ----------------------------------------------------------------- '''

    # split list to circumvent discord's 1024 embed field limit. each embed should have up to 20 entries
    def split_list(l):
        list_main = []          # init list
        length = len(l)         # get length of input list
        temp = []               # init temp list
        for i in range(len(l)):
            temp.append(l[i])     # add to list l[len(l) - length]
            length -= 1                             # decrement length, to advance the length pointer
            if len(temp) == 20:                     # if the length of the temp array == 20:
                list_main.append(temp)              # append temp to the list_main
                temp = []                           # re-init temp
        if len(temp) > 0:
            list_main.append(temp)
        return list_main

    # convert list_main's sub-lists into separate embeds and combine id with name
    def make_search_result_embeds(id_list, name_list, search_term):
        embed_count = len(id_list)                  # id_list and id_list should have the same length (if id and name)
        embeds = []                                 # init list to store embeds
        for i in range(embed_count):
            # convert id_list and name_list into id_str and name_str
            id_str = ""
            name_str = ""
            for val in id_list[i]:
                id_str = id_str + str(val) + "\n"
            for val in name_list[i]:
                name_str = name_str + val + "\n"
            # create discord embed to display info using the values above (title, field)
            embed = discord.Embed(color = 0xddc000)
            embed.title = "Search results for \"" + search_term + "\""
            embed.add_field(name = "Item ID", value = id_str, inline = True)
            embed.add_field(name = "Item name", value = name_str, inline = True)
            footer_string = 'Page ' + str(i + 1) + ' of ' + str(embed_count)
            embed.set_footer(text = footer_string)
            embeds.append(embed)
        return embeds

    ''' End Helpful Functions ------------------------------------------------------------------------------------------ '''
    
    sorted_id_list = split_list(id_list)                    # split both lists into lists of 20
    sorted_name_list = split_list(name_list)
    result_items = make_search_result_embeds(sorted_id_list, sorted_name_list, search_term)
        
    if id_list == [] and name_list == []:                   # if the lists are empty, then the search obviously has no results
        await ctx.send('No items matched your search.')
    elif len(id_list) > 200 and len(name_list) > 200:
        await ctx.send('Search returned too many results. Please refine your search.')
    else:                                                   # otherwise return the embed
        emojis = ['◀️', '▶️']                              # emojis to be printed
        
        page = 0                                            # set default page
        max_page = len(result_items) - 1                    # get no. of pages - 1
        embed_msg = await ctx.send(
            content = 'Use the ◀️ and ▶️ reactions to move between pages.',
            embed = result_items[page]
        )                                                   # get embed_msg

        ''' HELPFUL FUNCTION '''
        # function for reacting to specific pages
        async def add_reaction_by_page(page, max_page, embed_msg):
            if max_page == 0:
                return
            if max_page > 0:
                if page == 0:                                   # if on first page, add > only
                    await embed_msg.add_reaction(emojis[1])
                elif page == max_page:                          # else if on last page, add < only
                    await embed_msg.add_reaction(emojis[0])
                else:                                           # otherwise, print both < and >
                    for emoji in emojis:
                        await embed_msg.add_reaction(emoji)

        await add_reaction_by_page(page, max_page, embed_msg)
        
        cmd_usr = ctx.message.author                        # get command sender
        print(cmd_usr)                                      # debug statement
        
        def check(reaction, user):                          # check function for wait_for check kwarg
            if user != cmd_usr:                             # user is command sender?
                return False
            if reaction.message.id != embed_msg.id:         # user reacted to correct message?
                return False
            if str(reaction.emoji) not in emojis:           # user reacted with one of the given emojis?
                return False
            return True
        
        while True:                                         # keep this running until timeout
            try:                                            # wait for the user to react
                reaction, user = await bot.wait_for('reaction_add', timeout = 30.0, check = check)
            except asyncio.TimeoutError:                    # if no reaction
                print('Timeout')                            # debug statement
                await embed_msg.clear_reactions()
                await embed_msg.edit(
                    content = 'Search has timed out. Please start a new search.',
                    embed = result_items[page]
                )
                break                                       # exist the while True loop
            if user != cmd_usr:
                pass
            elif '▶️' in str(reaction.emoji):                # if the forward button is pressed...
                print('Next page')                          # debug statement         
                page += 1                                   # increment page
                await embed_msg.clear_reactions()
                await embed_msg.edit(
                    content = 'Use the ◀️ and ▶️ reactions to move between pages.',
                    embed = result_items[page]
                )
                await add_reaction_by_page(page, max_page, embed_msg)
            elif '◀️' in str(reaction.emoji):                # if the backward button is pressed
                print('Previous page')                      # debug statement
                page -= 1                                   # decrement page
                await embed_msg.clear_reactions()
                await embed_msg.edit(
                    content = 'Use the ◀️ and ▶️ reactions to move between pages.',
                    embed = result_items[page]
                )
                await add_reaction_by_page(page, max_page, embed_msg)

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
            instant_buy = 'Instant buy: ' + str(result_high) + ' gp (' + result_high_time + ')'
            instant_sell = 'Instant sell: ' + str(result_low) + ' gp (' + result_low_time + ')'
            spread = 'Margin: ' + str(result_high - result_low) + ' gp'
            pop = 'Percentage of profit (PoP): ' + str(round(((result_high - result_low)/result_low * 100), 2)) + '%'
            field_value = instant_buy + '\n' + instant_sell + '\n' + spread + '\n' + pop
            image_link = 'https://secure.runescape.com/m=itemdb_oldschool/obj_big.gif?id=' + str(id_num)
            result_item.add_field(name = item_name, value = field_value, inline = True)
            result_item.set_thumbnail(url = image_link)

            await ctx.send(embed = result_item)     # send the message
    
    if all(int(id_num) != d['id'] for d in data):   # send the "no item" message if id doesnt exist in dict
        await ctx.send('No such item id exists.')

# get high alch profit
@bot.command(name = 'highalch')
async def get_high_alch_price(ctx, id_num):
    for d in data:                                  # d for dictionary
        if int(id_num) == d['id']:                  # if id_num == id value in dict, get the values below. refer to id_mapping.json for keys
            item_id = d['id']
            item_name = d['name']
            item_highalch = d['highalch']

            item_latest = osrsreqs.get_latest(id_num)           # get input item instabuy
            result_high = item_latest['high']

            nature_rune_latest = osrsreqs.get_latest('561')     # get nature rune price (nature rune id = 561)
            nature_rune_instabuy = nature_rune_latest['high']

            result_item = discord.Embed(color = 0xddc000)
            result_item.title = 'High alchemy profit for Item ID #' + str(id_num)
            high_alch_price = 'High alch price: ' + str(item_highalch) + ' gp'
            item_high_price = 'GE price: ' + str(result_high) + ' gp'
            nature_rune_price = 'Nature rune GE price: ' + str(nature_rune_instabuy) + ' gp'
            high_alch_gain = 'High alch profit: ' + str(item_highalch - result_high - nature_rune_instabuy) + ' gp'
            field_value = high_alch_price + '\n' + item_high_price + '\n' + nature_rune_price + '\n' + high_alch_gain
            image_link = 'https://secure.runescape.com/m=itemdb_oldschool/obj_big.gif?id=' + str(id_num)
            result_item.add_field(name = item_name, value = field_value, inline = True)
            result_item.set_thumbnail(url = image_link)

            await ctx.send(embed = result_item)

    if all(int(id_num) != d['id'] for d in data):   # send the "no item" message if id doesnt exist in dict
        await ctx.send('No such item id exists.')

# probably the stupidest test command in the world
@bot.command()
async def talk(ctx, arg):
    await ctx.send('You\'re talking to me about {}?'.format(arg))
    await ctx.send(ctx.message.author.id)

# testing command for function to display multiple embeds
@bot.command(name = 'devdmb')
async def display_multi_embed(ctx):
    embed_one = discord.Embed(title = 'Embed 1', color = 0xddc000)
    embed_two = discord.Embed(title = 'Embed 2', color = 0xddc000)
    # await ctx.send(embed = embed_two)
    emojis = ['◀️', '▶️']
    count = 2
    if count == 1:
        await ctx.send(embed = embed_one)
    elif count == 2:
        message = await ctx.send(embed = embed_one)
        for emoji in emojis:
            await message.add_reaction(emoji)

''' EVENTS -------------------------------------------- '''

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