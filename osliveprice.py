import discord
from discord.ext import commands
from discord.ext.commands import Bot
import os
import asyncio
import logging
import json
import time
from datetime import datetime               # for dealing with unix timestamps
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from osrsreqs import osrsreqs as osrs                             # proprietary package

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

bot = commands.Bot(command_prefix = config_prefix, intents = intents, help_command = None)      # set bot command prefix
# note: we don't use client = Discord.client() because Client is subclass of Bot. Client won't let you use @bot.command()

with open('id_mapping.json') as f:                  # open id_mapping.json, so it can be called everywhere
    raw_data = f.read()                             # read the json file
    data = json.loads(raw_data)                     # json.loads() the data

''' COMMANDS ------------------------------------------ '''

# user get item info by id
@bot.command(name = 'info')
async def get_item_info(ctx, id_num):               # get item info
    for d in data:                                  # d for dictionary
        if int(id_num) == d['id']:                  # if id_num == id value in dict, get the values below. refer to id_mapping.json for keys
            if 'highalch' in d and 'limit' in d:
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

            else:
                if 'highalch' not in d:
                    if 'limit' not in d:
                        item_id = d['id']
                        item_name = d['name']
                        item_shop_value = d['value']

                        # create discord embed to display info using the values above (title, field)
                        result_item = discord.Embed(color = 0xddc000)        # create new embed result_item
                        result_item.title = "Data for Item ID #" + str(item_id)
                        field_value = "Shop value: " + str(item_shop_value) + "\n" + "High Level Alchemy value: " + "N/A" + "\n" + "GE buy limit: " + "N/A"
                        result_item.add_field(name = item_name, value = field_value, inline = True)
                        image_link = 'https://secure.runescape.com/m=itemdb_oldschool/obj_big.gif?id=' + str(id_num)
                        result_item.set_thumbnail(url = image_link)

                        await ctx.send(embed = result_item)     # send the message

                    else:
                        item_id = d['id']
                        item_name = d['name']
                        item_shop_value = d['value']
                        item_ge_limit = d['limit']

                        # create discord embed to display info using the values above (title, field)
                        result_item = discord.Embed(color = 0xddc000)        # create new embed result_item
                        result_item.title = "Data for Item ID #" + str(item_id)
                        field_value = "Shop value: " + str(item_shop_value) + "\n" + "High Level Alchemy value: " + "N/A" + "\n" + "GE buy limit: " + str(item_ge_limit)
                        result_item.add_field(name = item_name, value = field_value, inline = True)
                        image_link = 'https://secure.runescape.com/m=itemdb_oldschool/obj_big.gif?id=' + str(id_num)
                        result_item.set_thumbnail(url = image_link)

                        await ctx.send(embed = result_item)     # send the message

                elif 'limit' not in d:
                    item_id = d['id']
                    item_name = d['name']
                    item_shop_value = d['value']
                    item_high_alch = d['highalch']

                    # create discord embed to display info using the values above (title, field)
                    result_item = discord.Embed(color = 0xddc000)        # create new embed result_item
                    result_item.title = "Data for Item ID #" + str(item_id)
                    field_value = "Shop value: " + str(item_shop_value) + "\n" + "High Level Alchemy value: " + str(item_high_alch) + "\n" + "GE buy limit: " + "N/A"
                    result_item.add_field(name = item_name, value = field_value, inline = True)
                    image_link = 'https://secure.runescape.com/m=itemdb_oldschool/obj_big.gif?id=' + str(id_num)
                    result_item.set_thumbnail(url = image_link)

                    await ctx.send(embed = result_item)     # send the message
    
    if all(int(id_num) != d['id'] for d in data):   # send the "no item" message if id doesnt exist in dict
        await ctx.send('No such item id exists.')

# user get item id by name field
@bot.command(name = 'search')
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

        ''' Helpful Function -------------------------------------------------- '''
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
        
        ''' Helpful Function End --------------------------------------------- '''

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

            latest_data = osrs.get_latest(id_num)      # pull data from api and get values below
            result_high = latest_data[str(id_num)]['high']
            result_high_time = datetime.fromtimestamp(latest_data[str(id_num)]['highTime']).strftime('%d %B %Y, %H:%M:%S UTC')
            result_low = latest_data[str(id_num)]['low']
            result_low_time = datetime.fromtimestamp(latest_data[str(id_num)]['lowTime']).strftime('%d %B %Y, %H:%M:%S UTC')

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

# get 5-min interval data (4 hour chart)
@bot.command(name = '5min')
async def get_five_min_prices(ctx, id_num):
    for d in data:
        if int(id_num) == d['id']:
            item_name = d['name']
            live_ts = int(time.time())                      # get current time in unix
            df = osrs.get_five_min(id_num, live_ts)         # get live prices

            if df.empty:
                await ctx.send('Item has no GE data in the last 4 hours.')
            else:
                # convert arrays to double
                hi_array = np.array(df['avgHighPrice']).astype(np.double)
                lo_array = np.array(df['avgLowPrice']).astype(np.double)

                # mask NaNs
                hi_array_m = hi_array[np.isfinite(hi_array)]            # m = masked
                lo_array_m = lo_array[np.isfinite(lo_array)]

                # timestamp to array of strings
                tsarray = np.array(df['timestamp'])              # timestamp array

                # timestamps with masking for NaN datapoints
                hi_tsarray = tsarray[np.isfinite(hi_array)]      # for hi_array_m
                lo_tsarray = tsarray[np.isfinite(lo_array)]      # for lo_array_m

                hivolarr = np.array(df['highPriceVolume'])       # hi volume arr
                lovolarr = np.array(df['lowPriceVolume'])        # lo volume arr

                # make graph

                plt.style.use('dark_background')

                fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw = {'height_ratios': (2, 1)})

                ax0.plot(hi_tsarray, hi_array_m, 'o-', color = '#47a0ff', linewidth = 3, label = 'instabuy price')
                ax0.plot(lo_tsarray, lo_array_m, 'o-', color = '#ed29ff', linewidth = 3, label = 'instasell price')
                ax0.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M')) 
                ax0.yaxis.set_major_formatter(FuncFormatter(lambda y, p: format(int(y), ','))) 
                ax0.yaxis.grid()                                    # show grid

                ax0.set_ylabel('Price (gp)')                        # didn't set xlabel because viewer can read from ax1.ylabel
                ax0.spines['top'].set_visible(False)                # setting selected graph borders to invisible
                ax0.spines['right'].set_visible(False)
                ax0.spines['left'].set_visible(False)
                ax0.legend()

                ax1.plot(tsarray, hivolarr, color = '#8ac2ff', label = 'instabuy vol.')
                ax1.plot(tsarray, lovolarr, color = '#f8adff', label = 'instasell vol.')

                ax1.set_xlabel('Date/Time')
                ax1.set_ylabel('Volume')
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M')) 
                ax1.yaxis.set_major_formatter(FuncFormatter(lambda y, p: format(int(y), ','))) 
                ax1.yaxis.grid()
                ax1.legend()

                if not os.path.exists('/images'):
                    os.makedirs('/images')

                plt.savefig('images/5m_graph.png')                      # save graph
                plt.close(fig)                                          # close graph

                # now we open and prepare to upload graph
                with open('images/5m_graph.png', 'rb') as img:
                    graph = discord.File(img, filename = '5m_graph.png')

                # make embed
                result_item = discord.Embed(color = 0xddc000)
                result_item.title = "5-minute interval chart for Item ID #" + str(id_num)
                result_item.add_field(name = item_name, value = 'Last 4 hours')
                result_item.set_image(url = 'attachment://5m_graph.png')
                await ctx.send(file = graph, embed = result_item)
        
    if all(int(id_num) != d['id'] for d in data):   # send the "no item" message if id doesnt exist in dict
        await ctx.send('No such item id exists.')

# get 5-min interval data (4 hour chart)
@bot.command(name = '1hr')
async def get_one_hour_prices(ctx, id_num):
    for d in data:
        if int(id_num) == d['id']:
            item_name = d['name']
            live_ts = int(time.time())                      # get current time in unix
            df = osrs.get_one_hour(id_num, live_ts)         # get live prices

            if df.empty:
                await ctx.send('Item has no GE data in the last 2 days.')
            else:
                # convert arrays to double
                hi_array = np.array(df['avgHighPrice']).astype(np.double)
                lo_array = np.array(df['avgLowPrice']).astype(np.double)

                # mask NaNs
                hi_array_m = hi_array[np.isfinite(hi_array)]            # m = masked
                lo_array_m = lo_array[np.isfinite(lo_array)]

                # timestamp to array of strings
                tsarray = np.array(df['timestamp'])              # timestamp array

                # timestamps with masking for NaN datapoints
                hi_tsarray = tsarray[np.isfinite(hi_array)]      # for hi_array_m
                lo_tsarray = tsarray[np.isfinite(lo_array)]      # for lo_array_m

                hivolarr = np.array(df['highPriceVolume'])       # hi volume arr
                lovolarr = np.array(df['lowPriceVolume'])        # lo volume arr

                # make graph

                plt.style.use('dark_background')

                fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw = {'height_ratios': (2, 1)})

                ax0.plot(hi_tsarray, hi_array_m, 'o-', color = '#47a0ff', linewidth = 3, label = 'instabuy price')
                ax0.plot(lo_tsarray, lo_array_m, 'o-', color = '#ed29ff', linewidth = 3, label = 'instasell price')
                ax0.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M')) 
                ax0.yaxis.set_major_formatter(FuncFormatter(lambda y, p: format(int(y), ','))) 
                ax0.yaxis.grid()                                    # show grid

                ax0.set_ylabel('Price (gp)')                        # didn't set xlabel because viewer can read from ax1.ylabel
                ax0.spines['top'].set_visible(False)                # setting selected graph borders to invisible
                ax0.spines['right'].set_visible(False)
                ax0.spines['left'].set_visible(False)
                ax0.legend()

                ax1.plot(tsarray, hivolarr, color = '#8ac2ff', label = 'instabuy vol.')
                ax1.plot(tsarray, lovolarr, color = '#f8adff', label = 'instasell vol.')

                ax1.set_xlabel('Date/Time')
                ax1.set_ylabel('Volume')
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M')) 
                ax1.yaxis.set_major_formatter(FuncFormatter(lambda y, p: format(int(y), ','))) 
                ax1.yaxis.grid()
                ax1.legend()

                if not os.path.exists('/images'):
                    os.makedirs('/images')

                plt.savefig('images/1h_graph.png')                      # save graph
                plt.close(fig)                                          # close graph

                # now we open and prepare to upload graph
                with open('images/1h_graph.png', 'rb') as img:
                    graph = discord.File(img, filename = '1h_graph.png')

                # make embed
                result_item = discord.Embed(color = 0xddc000)
                result_item.title = "1-hour interval chart for Item ID #" + str(id_num)
                result_item.add_field(name = item_name, value = 'Last 2 days')
                result_item.set_image(url = 'attachment://1h_graph.png')
                await ctx.send(file = graph, embed = result_item)
        
    if all(int(id_num) != d['id'] for d in data):   # send the "no item" message if id doesnt exist in dict
        await ctx.send('No such item id exists.')

# get high alch profit
@bot.command(name = 'highalch')
async def get_high_alch_price(ctx, id_num):
    for d in data:                                  # d for dictionary
        if int(id_num) == d['id']:                  # if id_num == id value in dict, get the values below. refer to id_mapping.json for keys
            if 'highalch' in d:
                item_id = d['id']
                item_name = d['name']
                item_highalch = d['highalch']

                item_latest = osrs.get_latest(id_num)           # get input item instabuy
                result_high = item_latest[str(id_num)]['high']

                nature_rune_latest = osrs.get_latest('561')     # get nature rune price (nature rune id = 561)
                nature_rune_instabuy = nature_rune_latest['561']['high']

                result_item = discord.Embed(color = 0xddc000)
                result_item.title = 'High alchemy profit for Item ID #' + str(id_num)
                high_alch_price = 'High alch price: ' + str(item_highalch) + ' gp'
                item_high_price = 'GE buy price: ' + str(result_high) + ' gp'
                nature_rune_price = 'Nature rune GE price: ' + str(nature_rune_instabuy) + ' gp'
                high_alch_gain = 'High alch profit: ' + str(item_highalch - result_high - nature_rune_instabuy) + ' gp'
                field_value = high_alch_price + '\n' + item_high_price + '\n' + nature_rune_price + '\n' + '**' + high_alch_gain + '**'
                image_link = 'https://secure.runescape.com/m=itemdb_oldschool/obj_big.gif?id=' + str(id_num)
                result_item.add_field(name = item_name, value = field_value, inline = True)
                result_item.set_thumbnail(url = image_link)

                await ctx.send(embed = result_item)
            else:
                await ctx.send('This item cannot be alchemized.')

    if all(int(id_num) != d['id'] for d in data):   # send the "no item" message if id doesnt exist in dict
        await ctx.send('No such item id exists.')

# get all positive high alch items, ranked
@bot.command(name = 'topalch')
async def get_profitable_high_alch(ctx):
    # get buy limit, instant buy price, nature rune price
    nature_rune_latest = osrs.get_latest('561')         # id 561 = nature rune
    nature_rune_instabuy = nature_rune_latest['561']['high']       # nature rune instabuy price
    print(nature_rune_instabuy)

    id_list = []
    name_list = []
    highalch_list = []
    buylimit_list = []

    items_latest = osrs.get_latest_all()
    for d in data:                                          # populate the lists
        if str(d['id']) in items_latest and 'highalch' in d and 'limit' in d:
            item_id = d['id']                                   # item id
            item_name = d['name']                               # item name
            item_highalch = d['highalch']                       # item high alch value
            item_ge_limit = d['limit']                          # item GE limit

            result_high = items_latest[str(item_id)]['high']                   # item instabuy price

            profit = item_highalch - result_high - nature_rune_instabuy
            if profit > 0:
                id_list.append(item_id)
                name_list.append(item_name)
                highalch_list.append(profit)
                buylimit_list.append(item_ge_limit)
        else:
            pass                                                # avoid key error
        
    ''' Helpful Functions for this Command (used below) ----------------------------------------------------------------- '''

    def sort_descending(id_list, name_list, highalch_list, buylimit_list):
        zipper = list(zip(highalch_list, id_list, name_list, buylimit_list))
        zipper.sort(reverse = True)
        highalch_list, id_list, name_list, buylimit_list = zip(*zipper)
        return list(id_list), list(name_list), list(highalch_list), list(buylimit_list)
    
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
    def make_alch_rank_embeds(id_list, name_list, highalch_list, buylimit_list):
        embed_count = len(id_list)                  # id_list and id_list should have the same length (if id and name)
        embeds = []                                 # init list to store embeds
        for i in range(embed_count):
            # convert id_list and name_list into id_str and name_str
            id_str = ""
            name_str = ""
            highalch_str = ""
            for val in id_list[i]:
                id_str = id_str + str(val) + "\n"
            for val in name_list[i]:
                name_str = name_str + val + "\n"
            for val, lim in zip(highalch_list[i], buylimit_list[i]):
                highalch_str = highalch_str + "**" + str(val) + "** (Buy limit: " + str(lim) + ")\n"
            # create discord embed to display info using the values above (title, field)
            embed = discord.Embed(color = 0xddc000)
            embed.title = "Top high alchemy items (by profit)"
            embed.add_field(name = "Profit formula =", value = "(high alch price) - (GE buy price) - (nature rune buy price)", inline = False)
            embed.add_field(name = "Item ID", value = id_str, inline = True)
            embed.add_field(name = "Item name", value = name_str, inline = True)
            embed.add_field(name = "Profit (gp)", value = highalch_str, inline = True)
            footer_string = 'Page ' + str(i + 1) + ' of ' + str(embed_count)
            embed.set_footer(text = footer_string)
            embeds.append(embed)
        return embeds

    ''' End Helpful Functions ------------------------------------------------------------------------------------------ '''

    id_list, name_list, highalch_list, buylimit_list = sort_descending(id_list, name_list, highalch_list, buylimit_list)
    print(highalch_list)

    sorted_id_list = split_list(id_list)
    sorted_name_list = split_list(name_list)
    sorted_highalch_list = split_list(highalch_list)
    sorted_buylimit_list = split_list(buylimit_list)

    result_items = make_alch_rank_embeds(sorted_id_list, sorted_name_list, sorted_highalch_list, sorted_buylimit_list)

    # print pages
    emojis = ['◀️', '▶️']                              # emojis to be printed
        
    page = 0                                            # set default page
    max_page = len(result_items) - 1                    # get no. of pages - 1
    embed_msg = await ctx.send(
        content = 'Use the ◀️ and ▶️ reactions to move between pages.',
        embed = result_items[page]
    )

    ''' Helpful Function -------------------------------------------------- '''
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
    
    ''' Helpful Function End --------------------------------------------- '''

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
                content = 'Result has timed out. Type ' + config_prefix + 'topalch again for the latest data.',
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

@bot.command()
async def help(ctx):
    await ctx.send('**Command list:** \n' +
        '`' + config_prefix + 'info <item-id>`: Displays shop price, high alch price and GE buy limit for selected item \n' +
        '`' + config_prefix + 'search <search-terms>`: Searches for item ids and names that match the input terms \n' +
        '`' + config_prefix + 'latest <item-id>`: Displays the latest GE prices (buy and sell), as well as profit \n' + 
        '`' + config_prefix + 'highalch <item-id>`: Displays the potential profit per high alch cast for selected item \n' + 
        '`' + config_prefix + 'topalch`: Displays all items with positive profit per high alch cast in descending order \n' +
        '`' + config_prefix + '5min <item-id>`: Displays a chart of then item\'s prices over the last 4 hours, at 5-minute intervals \n' +
        '`' + config_prefix + '1hr <item-id>`: Displays a chart of then item\'s prices over the last 2 days, at 1-hour intervals')

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