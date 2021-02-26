#bot 
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import asyncio
from datetime import datetime
from threading import Thread
import threading
import time

lockedChannels = {}
events = {}
kill = False
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)
bot = commands.Bot(command_prefix = '|')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_reaction_add(reaction, user):
    print(reaction.emoji, user)
    for event in events:
        if events[event].message == reaction.message and user != bot.user:
            if reaction.emoji == '✅':
                events[event].RSVPList.add(user)
            elif reaction.emoji == '❌':
                if user in events[event].RSVPList:
                    events[event].RSVPList.remove(user)
            message = reaction.message
            await message.remove_reaction(reaction.emoji, user)
        print(events[event].RSVPList)



@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.content == 'die':
        await bot.close()
    

@bot.command(name = 'setEventChannel', brief = 'Sets the Event Channel ')
async def lockEventChannel(ctx):
    locked = False
    for role in ctx.author.roles:
        if role.id == 657010078364205086:
            lockedChannels['eventChannel'] = ctx.message.channel.id
            print(f'Done! The new locked channel is {lockedChannels["eventChannel"]}')
            locked = True
    if not locked: 
        channel = ctx.message.channel
        await channel.send("Oops! It doesn't look like you have the roles to execute that command (Fuckin loser)")


@bot.command(name = 'createEvent')
async def createEvent(ctx, eventTitle, time, requiredRSVP = 'false', eventDesc = 'No Description Given!'):
    tempEvent = eventCreate(time, requiredRSVP, eventTitle)
    channel = bot.get_channel(lockedChannels['eventChannel'])
    #Checks formatting
    if tempEvent == False:
        desc = '''It seems like you've formatted your event incorrectly. Your RSVP value should 
                be either True or False, and your date should be formatted in the form 
                YY-MM-DD-Hr-Min. Your event should be formatted Event Title, Time, RSVP, and event
                description.'''
        embed = discord.Embed(title = 'Oh no!', description = desc, color = 0x00ff00)
        embed.set_footer(text = '''I am a bot, and this action was performed automatically. If you think there may
                                be a problem, please contact TheAwesomeWizard13597#9482 with questions.''')
        await channel.send(embed = embed)
    #Creates the text for the event
    embedVar = discord.Embed(title = eventTitle, description = eventDesc, color = 0x00ff00)
    embedVar.add_field(name = 'Time', value = createTimeString(tempEvent), inline = True)
    embedVar.add_field(name = 'RSVP?', value = requiredRSVP, inline = True)
    embedVar.set_footer(text = 'To RSVP and get reminded of the event, click the check below! \n To remove your RSVP, click the x!')
    eventMessage = await channel.send(embed = embedVar)
    tempEvent.message = eventMessage
    events[eventTitle] = tempEvent
    await eventMessage.add_reaction('\N{WHITE HEAVY CHECK MARK}')
    await eventMessage.add_reaction('❌')

@bot.command(name = 'testPing')
async def testPing(event):
    channel = bot.get_channel(lockedChannels['eventChannel'])
    
    embed, message = pingAll(event)
    await channel.send(embed = embed)
    await channel.send(message)

async def checkTime():
    await bot.wait_until_ready()
    while 1 == 1:
        if 'eventChannel' not in lockedChannels:
            pass
        else:
            channel = bot.get_channel(lockedChannels['eventChannel']) # replace with channel ID that you want to send to
            now = datetime.now()
            for event in events:
                e = events[event]
                if (e.year, e.month, e.day, e.hour, e.minute) == (now.year, now.month, now.day, now.hour, now.minute) and not e.alreadyPassed:
                    embed, message = pingAll(e)
                    e.alreadyPassed = True
                    await channel.send(embed = embed)
                    await channel.send(message)
        await asyncio.sleep(1)



class event(object):
    def __init__(self, year, month, day, hour, minute, RSVP, title, message = None):
        self.month = int(month)
        self.year = int(year)
        self.day = int(day)
        self.hour = int(hour)
        self.minute = int(minute)
        self.RSVP = RSVP
        self.message = message
        self.title = title
        self.RSVPList = set()
        self.alreadyPassed = False
    
    def addRSVP(self, RSVP):
        self.RSVPList += RSVP
        print(f'Here! {self.RSVPList}')

#Time format: YY-MM-DD-HH-MM
def eventCreate(time, RSVP, title):
    timeFormat = time.split('-')
    if RSVP.lower() == 'true':
        RSVPFormat = True
    elif RSVP.lower() == 'false':
        RSVPFormat = False
    else:
        return False
    
    if len(timeFormat) < 5:
        return False
    else:
        tempEvent = event(timeFormat[0], timeFormat[1], timeFormat[2], timeFormat[3], timeFormat[4], RSVPFormat, title)
    
    return tempEvent
     
def createTimeString(event):
    Year = event.year
    Months = ['January', 'Feburary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    Month = Months[int(event.month) - 1]
    Day = event.day
    Hour = event.hour
    Minute = event.minute
    return(f'{Month} {Day}, {Year}, {Hour}:{Minute}')

def pingAll(event):
    channel = bot.get_channel(lockedChannels['eventChannel'])
    pingString = ''
    if len(event.RSVPList) == 0:
        pingString = 'Nobody RSVPed!'
    for user in event.RSVPList:
        pingString += f'<@{user.id}>'
    embed = discord.Embed(title = f'{event.title}', description = f'This is a reminder for {event.message.jump_url}')
    embed.set_footer(text = '''I am a bot, and this action was performed automatically. If you think there may
                                be a problem, please contact TheAwesomeWizard13597#9482 with questions.''')
    return embed, pingString

bot.loop.create_task(checkTime())
bot.run(TOKEN)
