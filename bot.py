#bot 
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

lockedChannels = {}
events = {}
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)
bot = commands.Bot(command_prefix = '|')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')





@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.content == 'die':
        await bot.close()
    print(message.channel.id)
    

@bot.command(name = 'setEventChannel')
async def lockEventChannel(ctx):
    lockedChannels['eventChannel'] = ctx.message.channel.id
    print(f'Done! The new locked channel is {lockedChannels["eventChannel"]}')

@bot.command(name = 'createEvent')
async def createEvent(ctx, eventTitle, time, requiredRSVP = False, eventDesc = 'No Description Given!'):
    embedVar = discord.Embed(title = eventTitle, description = eventDesc, color = 0x00ff00)
    embedVar.add_field(name = 'Time', value = time, inline = True)
    embedVar.add_field(name = 'RSVP?', value = requiredRSVP, inline = True)
    embedVar.set_footer(text = 'To RSVP and get reminded of the event, click the check below!')
    channel = bot.get_channel(lockedChannels['eventChannel'])
    eventMessage = await channel.send(embed = embedVar)
    await eventMessage.add_reaction('\N{WHITE HEAVY CHECK MARK}')
bot.run(TOKEN)
